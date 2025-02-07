import pygame
import sys
from GUI import Board
from GUI import piece_images
from engine import precomputed_moves, is_check
from GUI import Pieces

pygame.init()

# Board dimensions
BOARD_SIZE = 8
SQUARE_SIZE = 80
WIDTH = HEIGHT = BOARD_SIZE * SQUARE_SIZE

# Set up the display (extra 40 pixels for text)
screen = pygame.display.set_mode((WIDTH, HEIGHT + 40))
pygame.display.set_caption("CHESSBOARD")

# Starting FEN (standard initial chess position)
initial_fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
# testing_fen_string = "4k/8/8/8/8/5Q/8/6QK"

# Set up font for messages
font = pygame.font.SysFont(None, 36)

def main():
    board = Board()
    board.load_positions_from_fen(initial_fen_string)
    precomputed_moves()  # Precompute any necessary move information.
    
    dragging = False
    piece_drag_x, piece_drag_y = None, None

    while True:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # If the game is over, skip processing further events.
            if board.game_over:
                continue
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col_idx, row_idx = mouse_x // SQUARE_SIZE, mouse_y // SQUARE_SIZE
                board.clicked_piece(col_idx, row_idx)
                board.start_dragging(col_idx, row_idx)
                if board.dragged_piece is not None:
                    dragging = True
                    piece_drag_x, piece_drag_y = mouse_x, mouse_y
                board.draw_board_with_pieces()
                pygame.display.flip()
            elif event.type == pygame.MOUSEMOTION and dragging:
                piece_drag_x, piece_drag_y = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    col_idx, row_idx = mouse_x // SQUARE_SIZE, mouse_y // SQUARE_SIZE
                    board.stop_dragging(col_idx, row_idx)
                    dragging = False
                board.remove_avaliable_moves()

        board.draw_board_with_pieces()

        if dragging and board.dragged_piece is not None:
            piece_image = piece_images.get(board.dragged_piece)
            if piece_image:
                piece_x = piece_drag_x - piece_image.get_width() // 2
                piece_y = piece_drag_y - piece_image.get_height() // 2
                screen.blit(piece_image, (piece_x, piece_y))
        
        # Display turn or game over message.
        if board.game_over:
            turn_text = font.render(f"GAME OVER! Winner: {board.winner}", True, (255, 0, 0))
        else:
            turn = "White" if board.color_to_move == Pieces.white else "Black"
            if is_check(board, board.color_to_move):
                turn_text = font.render(f"Check! {turn}'s turn", True, (255, 0, 0))
            else:
                turn_text = font.render(f"Turn: {turn}", True, (255, 255, 255))
        screen.blit(turn_text, (10, HEIGHT + 10))
        pygame.display.flip()

if __name__ == "__main__":
    main()
