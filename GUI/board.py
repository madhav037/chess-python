import pygame
from .pieces import piece_images, Pieces
from engine import generate_sliding_piece_moves

# CONSTANTS AND COLORS
BOARD_SIZE = 8
SQUARE_SIZE = 80
WIDTH = HEIGHT = BOARD_SIZE * SQUARE_SIZE

LIGHT_COLOR = (240, 217, 181)
DARK_COLOR = (181, 136, 99)
HIGHLIGHT_COLOR_SOURCE = (152, 108, 90) # Brown  
HIGHLIGHT_COLOR_DESTINATION = (172, 107, 70) # Light Brown
AVALIABLE_MOVES_COLOR = (165, 123, 105) # some brown
OPPONENT_COLOR = (131, 66, 49) # Red

# Initialization of screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

class Board:
    square = []
    
    def __init__(self):
        self.square = [None for _ in range(64)]  # Initialize with None, no piece initially
        self.dragged_piece = None  # Track which piece is being dragged
        self.drag_start_pos = None
        self.color_to_move = Pieces.white  # White to move first
        self.avaliable_moves = []
        self.opponent_pieces = []
        
    def get_piece(self, square):
        return self.square[square]
    
    def set_piece(self, square, piece):
        self.square[square] = piece

    
    def draw_square(self, col_idx, row_idx, color=None, make_transparent=False, border_color=None, border_width=2, update=False):
        # Calculate square position
        x = col_idx * SQUARE_SIZE
        y = row_idx * SQUARE_SIZE
        if color is None:
            color = LIGHT_COLOR if (row_idx + col_idx) % 2 == 0 else DARK_COLOR
        if update:
            surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            surface.fill(color)
            screen.blit(surface, (x, y))
        else:
            if make_transparent:
                translucent_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                translucent_surface.fill(AVALIABLE_MOVES_COLOR)
                screen.blit(translucent_surface, (x, y))
            else:
                pygame.draw.rect(screen, color, pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE))
            
        if border_color is not None:
            pygame.draw.rect(screen, border_color, pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE), border_width)

    def load_positions_from_fen(self, fen):
        
        rows = fen.split("/")
        for row_idx, row in enumerate(rows):
            col_idx = 0
            for char in row:
                if char.isdigit():
                    col_idx += int(char)
                else:
                    self.square[row_idx * 8 + col_idx] = char
                    col_idx += 1
        print(self.square)
    
    def draw_board_with_pieces(self):
        for row_idx in range(BOARD_SIZE):
            for col_idx in range(BOARD_SIZE):
                piece = self.get_piece(row_idx * 8 + col_idx)
                x = col_idx * SQUARE_SIZE
                y = row_idx * SQUARE_SIZE

                # Determine if this square should be highlighted
                is_source = hasattr(self, "highlight_source") and self.highlight_source == (col_idx, row_idx)
                is_destination = hasattr(self, "highlight_destination") and self.highlight_destination == (col_idx, row_idx)

                # Choose the square color
                if is_source:
                    self.draw_square(col_idx, row_idx, color=HIGHLIGHT_COLOR_SOURCE, border_color=HIGHLIGHT_COLOR_DESTINATION)
                elif is_destination:
                    self.draw_square(col_idx, row_idx, color=HIGHLIGHT_COLOR_DESTINATION, border_color=HIGHLIGHT_COLOR_DESTINATION)
                else:
                    self.draw_square(col_idx, row_idx)  # Default square

        # Draw available moves AFTER setting up the board
        for move in self.avaliable_moves:
            target_col = move % 8
            target_row = move // 8
            if move in self.opponent_pieces:
                self.draw_square(
                    target_col, target_row, color=OPPONENT_COLOR, border_color=(53, 0, 0), border_width=1, update=True
                )
            else:
                self.draw_square(
                    target_col, target_row, color=AVALIABLE_MOVES_COLOR, border_color=(155, 113, 95), border_width=1, update=True
                )

        # Draw pieces AFTER highlighting moves
        for row_idx in range(BOARD_SIZE):
            for col_idx in range(BOARD_SIZE):
                piece = self.get_piece(row_idx * 8 + col_idx)
                if piece is not None:
                    piece_image = piece_images[piece]  # Get the piece image
                    piece_x = col_idx * SQUARE_SIZE + (SQUARE_SIZE - piece_images[piece].get_width()) // 2
                    piece_y = row_idx * SQUARE_SIZE + (SQUARE_SIZE - piece_images[piece].get_height()) // 2
                    screen.blit(piece_image, (piece_x, piece_y))  # Draw the piece

        
    def start_dragging(self, col_idx, row_idx, board):
        piece = self.get_piece(row_idx * 8 + col_idx)
        if piece is not None:
            self.dragged_piece = piece
            self.drag_start_pos = (col_idx, row_idx)
            
            # Temporarily remove the piece from the board
            self.set_piece(row_idx * 8 + col_idx, None)
            
    def stop_dragging(self, col_idx, row_idx):
        if self.dragged_piece is not None:
            # If the drop position is different from the starting position
            if (col_idx, row_idx) != self.drag_start_pos:
                # Place the piece in the new square
                self.set_piece(row_idx * 8 + col_idx, self.dragged_piece)
                # Store the squares to highlight
                self.highlight_source = self.drag_start_pos
                self.highlight_destination = (col_idx, row_idx)
                self.color_to_move = Pieces.black if self.color_to_move == Pieces.white else Pieces.white
            else:
                # If the piece is dropped back to the original square
                self.set_piece(self.drag_start_pos[1] * 8 + self.drag_start_pos[0], self.dragged_piece)
            
            # Reset dragging state
            self.dragged_piece = None
            self.drag_start_pos = None
            
            # change the color to move

    def clicked_piece(self, col_idx, row_idx, board):
        """Handle logic for when a piece is clicked."""
        self.avaliable_moves = []  # Clear previous available moves
        self.opponent_pieces = []  # Clear previous opponent pieces
        piece = self.get_piece(row_idx * 8 + col_idx)
        
        if piece is None:
            print(f"No piece at ({col_idx}, {row_idx})")
            return

        print(f"Clicked piece: {piece} at ({col_idx}, {row_idx})")
        
        # Generate legal moves for all pieces
        moves_list = generate_sliding_piece_moves(board)
        # print(moves_list)
        
        # Filter moves for the selected piece
        for move in moves_list:
            if move.startSquare == row_idx * 8 + col_idx:
                self.avaliable_moves.append(move.targetSquare)
            piece_on_target_square = self.get_piece(move.targetSquare)
            if piece_on_target_square is not None:
                if Pieces.get_piece_color(piece_on_target_square) != Pieces.get_piece_color(piece):
                    self.opponent_pieces.append(move.targetSquare)
        
        
        if not self.avaliable_moves:
            print(f"No available moves for {piece}")
        else:
            print(f"Available moves for {piece}: {self.avaliable_moves}")

    
    def remove_avaliable_moves(self):
        print("Remove avaliable moves")
        self.avaliable_moves = []
        print(self.avaliable_moves)