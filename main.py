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
pygame.display.set_caption("Chess Game")

# Fonts and colors
font = pygame.font.SysFont(None, 36)
button_font = pygame.font.SysFont(None, 40)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (170, 170, 170)
DARK_GRAY = (100, 100, 100)
RED = (255, 0, 0)

# Starting FEN position
initial_fen_string = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

def draw_button(x, y, width, height, text, action=None):
    """Draw a button and return if clicked."""
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    color = DARK_GRAY if (x < mouse[0] < x + width and y < mouse[1] < y + height) else GRAY
    pygame.draw.rect(screen, color, (x, y, width, height), border_radius=10)

    text_surface = button_font.render(text, True, WHITE)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))

    if click[0] == 1 and action and (x < mouse[0] < x + width and y < mouse[1] < y + height):
        pygame.time.delay(150)
        return action()
    return None

def main_menu():
    """Main menu with buttons for PvP and Computer mode."""
    while True:
        screen.fill(BLACK)
        title_text = font.render("Welcome to Chess!", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

        if draw_button(WIDTH // 2 - 100, 200, 200, 60, "PvP Mode", lambda: 'pvp'):
            return 'pvp'
        if draw_button(WIDTH // 2 - 100, 280, 200, 60, "Vs Computer", lambda: 'computer'):
            screen.fill(BLACK)
            coming_soon_text = font.render("Coming Soon...", True, RED)
            screen.blit(coming_soon_text, (WIDTH // 2 - coming_soon_text.get_width() // 2, 350))
            pygame.display.flip()
            pygame.time.delay(2000)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def game_over_popup(winner):
    """Game Over screen with Play Again, Main Menu, or Exit buttons."""
    while True:
        screen.fill(BLACK)
        message = f"GAME OVER! Winner: {winner}"
        text_surface = font.render(message, True, RED)
        screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, 100))

        if draw_button(WIDTH // 2 - 100, 200, 200, 60, "Play Again", lambda: 'play_again'):
            return 'play_again'
        if draw_button(WIDTH // 2 - 100, 280, 200, 60, "Main Menu", lambda: 'main_menu'):
            return 'main_menu'
        if draw_button(WIDTH // 2 - 100, 360, 200, 60, "Exit", pygame.quit):
            sys.exit()

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def main():
    """Main game loop with PvP mode, drag-and-drop, and game over handling."""
    board = Board()
    board.load_positions_from_fen(initial_fen_string)
    precomputed_moves()  # Precompute move information.

    dragging = False
    piece_drag_x, piece_drag_y = None, None

    # Show Main Menu
    menu_choice = main_menu()
    if menu_choice == 'computer':
        pygame.quit()
        sys.exit()

    while True:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if board.game_over:
                result = game_over_popup(board.winner)
                if result == 'play_again':
                    board.load_positions_from_fen(initial_fen_string)
                    board.game_over = False
                    board.winner = None
                elif result == 'main_menu':
                    menu_choice = main_menu()
                    if menu_choice == 'computer':
                        pygame.quit()
                        sys.exit()
                    else:
                        board.load_positions_from_fen(initial_fen_string)
                        board.game_over = False
                        board.winner = None

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
        
        # Show turn or game over message.
        if board.game_over:
            turn_text = font.render(f"GAME OVER! Winner: {board.winner}", True, RED)
        else:
            turn = "White" if board.color_to_move == Pieces.white else "Black"
            turn_text = font.render(f"Turn: {turn}", True, WHITE)
        screen.blit(turn_text, (10, HEIGHT + 10))
        pygame.display.flip()

if __name__ == "__main__":
    main()
