import pygame
import sys
from GUI import Board
from GUI import piece_images
from engine import precomputed_moves

pygame.init()

# Constants for the window dimensions
BOARD_SIZE = 8
SQUARE_SIZE = 80
WIDTH = HEIGHT = BOARD_SIZE * SQUARE_SIZE

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT+40))
pygame.display.set_caption("CHESSBOARD")

# Initial FEN string
# initial_fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
initial_fen_string = "rq/8/q4Kk/6B/8/8/8/Q3R"

# Initialize font for text rendering
font = pygame.font.SysFont(None, 36)  # Default font, size 36

# Main game loop
def main():
    # Create a Board instance and load pieces from the FEN string
    board = Board()
    board.load_positions_from_fen(initial_fen_string)
    precomputed_moves()
    
    dragging = False  # Flag to track dragging state
    piece_drag_x, piece_drag_y = None, None

    # Game loop
    running = True
    while running:
        # Draw the board with pieces
        screen.fill((0, 0, 0))  # Optional: fill the screen with black before drawing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Get the square indices where the mouse clicked
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col_idx, row_idx = mouse_x // SQUARE_SIZE, mouse_y // SQUARE_SIZE
                
                # Handle piece click
                board.clicked_piece(col_idx, row_idx, board)
                
                # Start dragging if a piece is present
                board.start_dragging(col_idx, row_idx, board)
                
                if board.dragged_piece is not None:  # Only set dragging if there's a piece
                    dragging = True
                    piece_drag_x, piece_drag_y = mouse_x, mouse_y  # Initialize drag position

                # Immediately redraw the board to show available moves
                board.draw_board_with_pieces()
                pygame.display.flip()

            elif event.type == pygame.MOUSEMOTION and dragging:
                # Update drag position while dragging
                piece_drag_x, piece_drag_y = pygame.mouse.get_pos()

            elif event.type == pygame.MOUSEBUTTONUP:
                # Stop dragging when mouse button is released
                board.remove_avaliable_moves()
                if dragging:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    col_idx, row_idx = mouse_x // SQUARE_SIZE, mouse_y // SQUARE_SIZE
                    board.stop_dragging(col_idx, row_idx)
                    dragging = False

        # Draw the board and any pieces
        board.draw_board_with_pieces()

        if dragging and board.dragged_piece is not None:
            # Draw the dragged piece
            piece_image = piece_images.get(board.dragged_piece, None)
            if piece_image:
                piece_x = piece_drag_x - piece_image.get_width() // 2
                piece_y = piece_drag_y - piece_image.get_height() // 2
                screen.blit(piece_image, (piece_x, piece_y))
        
        # Display current turn
        turn = "White" if board.color_to_move == 8 else "Black"
        turn_text = font.render(f"Turn: {turn}", True, (255, 255, 255))  # White text
        screen.blit(turn_text, (10, HEIGHT + 10))  # Position text below the board

        pygame.display.flip()
    pygame.quit()
    sys.exit()

# Run the game
if __name__ == "__main__":
    main()
