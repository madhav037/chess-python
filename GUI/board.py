import pygame 
from .pieces import piece_images, Pieces
from engine import (
    generate_sliding_piece_moves, generate_pawn_moves, generate_knight_moves, 
    generate_king_moves, special_moves, is_game_over
)

# CONSTANTS AND COLORS
BOARD_SIZE = 8
SQUARE_SIZE = 80
WIDTH = HEIGHT = BOARD_SIZE * SQUARE_SIZE

LIGHT_COLOR = (240, 217, 181)
DARK_COLOR = (181, 136, 99)
HIGHLIGHT_COLOR_SOURCE = (152, 108, 90)  # Brown  
HIGHLIGHT_COLOR_DESTINATION = (172, 107, 70)  # Light Brown
AVALIABLE_MOVES_COLOR = (164, 24, 48)  # Some brown
OPPONENT_COLOR = (255, 0, 0)  # Red

# Initialization of screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))

class Board:
    def __init__(self):
        self.square = [None for _ in range(64)]  # 64 squares
        self.dragged_piece = None    # Which piece is being dragged
        self.drag_start_pos = None   # (col, row)
        self.color_to_move = Pieces.white  # White moves first
        self.avaliable_moves = []   # List of target square indices
        self.opponent_pieces = []   # For highlighting captures
        self.game_state = []        # History (for undo/validation)
        self.last_moved_piece = None
        self.allow_castling = [True, True]  # [White, Black]
        self.game_over = False
        self.winner = None
        self.highlight_source = None
        self.highlight_destination = None
        self.castle_data = None
        
    def copy(self):
        """Return a shallow copy of the board (sufficient for our simulation)."""
        new_board = Board()
        new_board.square = self.square.copy()
        new_board.color_to_move = self.color_to_move
        new_board.avaliable_moves = self.avaliable_moves.copy()
        new_board.opponent_pieces = self.opponent_pieces.copy()
        new_board.game_state = self.game_state.copy()
        new_board.allow_castling = self.allow_castling.copy()
        new_board.game_over = self.game_over
        new_board.winner = self.winner
        new_board.highlight_source = self.highlight_source
        new_board.highlight_destination = self.highlight_destination
        return new_board

    def get_piece(self, square):
        return self.square[square]
    
    def set_piece(self, square, piece):
        self.square[square] = piece

    def draw_square(self, col_idx, row_idx, color=None, make_transparent=False, border_color=None, border_width=2, update=False):
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
        print("Loaded FEN:", self.square)
        
    def highlight_king(self):
        """If the current side’s king is in check, redraw its square with a highlight."""
        from engine import is_check

        current_color = self.color_to_move
        if is_check(self, current_color):
            # Find the king belonging to current_color.
            for square in range(64):
                piece = self.get_piece(square)
                if piece is not None and Pieces.is_type(piece) == Pieces.king and Pieces.get_piece_color(piece) == current_color:
                    king_col = square % 8
                    king_row = square // 8
                    # Redraw the square with a highlighted color and a bold red border.
                    # (You can adjust the color and border_width as desired.)
                    self.draw_square(king_col, king_row, color=(255, 200, 200), border_color=(255, 0, 0), border_width=4, update=True)
                    break
    
    def draw_board_with_pieces(self):
        # Draw squares and highlights
        for row_idx in range(BOARD_SIZE):
            for col_idx in range(BOARD_SIZE):
                piece = self.get_piece(row_idx * 8 + col_idx)
                is_source = (self.highlight_source == (col_idx, row_idx))
                is_destination = (self.highlight_destination == (col_idx, row_idx))
                if is_source:
                    self.draw_square(col_idx, row_idx, color=HIGHLIGHT_COLOR_SOURCE, border_color=HIGHLIGHT_COLOR_DESTINATION)
                elif is_destination:
                    self.draw_square(col_idx, row_idx, color=HIGHLIGHT_COLOR_DESTINATION, border_color=HIGHLIGHT_COLOR_DESTINATION)
                else:
                    self.draw_square(col_idx, row_idx)
        
        # Next, highlight the king's square if in check.
        self.highlight_king()
        
        # Highlight available moves
        for move in self.avaliable_moves:
            target_col = move % 8
            target_row = move // 8
            if move in self.opponent_pieces:
                self.draw_square(target_col, target_row, color=OPPONENT_COLOR, border_color=(53, 0, 0), border_width=1, update=True)
            else:
                self.draw_square(target_col, target_row, color=AVALIABLE_MOVES_COLOR, border_color=(155, 113, 95), border_width=1, update=True)
        
        # Draw all pieces
        for row_idx in range(BOARD_SIZE):
            for col_idx in range(BOARD_SIZE):
                piece = self.get_piece(row_idx * 8 + col_idx)
                if piece is not None:
                    piece_image = piece_images[piece]
                    piece_x = col_idx * SQUARE_SIZE + (SQUARE_SIZE - piece_image.get_width()) // 2
                    piece_y = row_idx * SQUARE_SIZE + (SQUARE_SIZE - piece_image.get_height()) // 2
                    screen.blit(piece_image, (piece_x, piece_y))

    def start_dragging(self, col_idx, row_idx):
        piece = self.get_piece(row_idx * 8 + col_idx)
        if piece is not None:
            self.dragged_piece = piece
            self.drag_start_pos = (col_idx, row_idx)
            # Remove piece temporarily
            self.set_piece(row_idx * 8 + col_idx, None)
            
    def stop_dragging(self, col_idx, row_idx):
        # Compute starting and target square indices
        target_square = row_idx * 8 + col_idx
        start_square = self.drag_start_pos[1] * 8 + self.drag_start_pos[0]
        if self.dragged_piece is not None:
            # If valid move (different square and among available moves)
            if (col_idx, row_idx) != self.drag_start_pos and target_square in self.avaliable_moves:
                print(f"Moved {self.dragged_piece} from {self.drag_start_pos} to {(col_idx, row_idx)}")
                if target_square == 62 and self.dragged_piece == "K":
                    self.set_piece(self.castle_data[0][0], self.castle_data[0][1])
                    self.set_piece(self.castle_data[1][0], self.castle_data[1][1])
                    self.set_piece(self.castle_data[2][0], self.castle_data[2][1])
                elif target_square == 6 and self.dragged_piece == "k":
                    self.set_piece(self.castle_data[0][0], self.castle_data[0][1])
                    self.set_piece(self.castle_data[1][0], self.castle_data[1][1])
                    self.set_piece(self.castle_data[2][0], self.castle_data[2][1])
                else:
                    self.set_piece(target_square, self.dragged_piece)
                # Update castling rights (simplified)
                if self.dragged_piece == "K" or start_square == 63:
                    self.allow_castling[0] = False
                elif self.dragged_piece == "k" or start_square == 56:
                    self.allow_castling[1] = False
                self.highlight_source = self.drag_start_pos
                self.highlight_destination = (col_idx, row_idx)
                
                # Save the new board state and switch turn
                self.game_state.append(self.square.copy())
                self.last_moved_piece = self.dragged_piece
                self.color_to_move = Pieces.black if self.color_to_move == Pieces.white else Pieces.white

                # Check if the move causes checkmate
                if is_game_over(self):
                    self.game_over = True
            else:
                # Invalid move; return the piece to its original square
                self.set_piece(start_square, self.dragged_piece)
            
            self.dragged_piece = None
            self.drag_start_pos = None
            self.avaliable_moves = []

    def clicked_piece(self, col_idx, row_idx):
        """When the user clicks a square, show only legal moves for that piece.
        A legal move is one that (if the king is in check) resolves the check.
        Otherwise, all candidate moves are allowed.
        """
        from engine import (
            generate_sliding_piece_moves, generate_knight_moves,
            generate_pawn_moves, generate_king_moves, is_check, Move
        )

        # Reset available moves and opponent capture highlighting.
        self.avaliable_moves = []
        self.opponent_pieces = []

        # Determine the clicked square’s index and get the piece.
        square_index = row_idx * 8 + col_idx
        piece = self.get_piece(square_index)
        if piece is None:
            print(f"No piece at ({col_idx}, {row_idx})")
            return

        print(f"Clicked piece: {piece} at ({col_idx}, {row_idx})")

        # Generate candidate moves based on the piece type.
        if Pieces.is_type(piece) in [Pieces.queen, Pieces.rook, Pieces.bishop]:
            moves_list = generate_sliding_piece_moves(self)
        elif Pieces.is_type(piece) == Pieces.knight:
            moves_list = generate_knight_moves(self)
        elif Pieces.is_type(piece) == Pieces.pawn:
            moves_list = generate_pawn_moves(self)
        elif Pieces.is_type(piece) == Pieces.king:
            moves_list = generate_king_moves(self)
            for move in moves_list:
                print(move.startSquare, move.targetSquare)
                
            # Remove castling moves if castling is not allowed.
            if self.allow_castling[0] and row_idx*8+col_idx == 60 and self.color_to_move == Pieces.white:
                move = special_moves(self, 60, 62, self.allow_castling, "K")
                print("move : ", move)
                if move is not None:
                    moves_list.append(Move(60, 62))
                    self.castle_data = move
            if self.allow_castling[1] and row_idx*8+col_idx == 4 and self.color_to_move == Pieces.black:
                move = special_moves(self, 4, 6, self.allow_castling, "k")
                if move is not None:
                    moves_list.append(Move(4, 6))
                    self.castle_data = move
            
                
        # Filter moves so that we only have moves for the clicked piece.
        candidate_moves = [move for move in moves_list if move.startSquare == square_index]
        
        legal_moves = []
        current_color = self.color_to_move

        # Check if the king is currently in check.
        if not is_check(self, current_color):
            # If the king is safe, all candidate moves are allowed.
            for move in candidate_moves:
                legal_moves.append(move.targetSquare)
                # Also record opponent pieces on target squares.
                target_piece = self.get_piece(move.targetSquare)
                if target_piece is not None and Pieces.get_piece_color(target_piece) != current_color:
                    if move.targetSquare not in self.opponent_pieces:
                        self.opponent_pieces.append(move.targetSquare)
        else:
            # King is in check: simulate each candidate move and only keep those that resolve the check.
            for move in candidate_moves:
                board_copy = self.copy()
                moving_piece = board_copy.get_piece(move.startSquare)
                board_copy.set_piece(move.startSquare, None)
                board_copy.set_piece(move.targetSquare, moving_piece)
                if not is_check(board_copy, current_color):
                    legal_moves.append(move.targetSquare)
                    target_piece = self.get_piece(move.targetSquare)
                    if target_piece is not None and Pieces.get_piece_color(target_piece) != current_color:
                        if move.targetSquare not in self.opponent_pieces:
                            self.opponent_pieces.append(move.targetSquare)

        self.avaliable_moves = legal_moves

        if not self.avaliable_moves:
            print(f"No available moves for {piece}")
        else:
            print(f"Available moves for {piece}: {self.avaliable_moves}")


    def remove_avaliable_moves(self):
        self.avaliable_moves = []
