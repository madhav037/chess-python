# moves.py
# Precomputed values for sliding pieces
direction_offsets = [8, -8, -1, 1, 7, -7, 9, -9]
num_squares_to_edge = [0] * 64

def precomputed_moves():
    for row in range(8):
        for col in range(8):
            num_north = 7 - row
            num_south = row
            num_west = col
            num_east = 7 - col
            square_idx = row * 8 + col
            num_squares_to_edge[square_idx] = [
                num_north, 
                num_south, 
                num_west, 
                num_east, 
                min(num_north, num_west), 
                min(num_south, num_east),
                min(num_north, num_east), 
                min(num_south, num_west)
            ]

class Move:
    def __init__(self, startSquare, targetSquare):
        self.startSquare = startSquare
        self.targetSquare = targetSquare

# Global moves list (used by the move generators)
moves = []

def generate_sliding_piece_moves(board):
    from GUI import Pieces
    moves.clear()
    for startSquare in range(64):
        piece = board.get_piece(startSquare)
        if piece is None:
            continue
        if Pieces.get_piece_color(piece) == board.color_to_move:
            if Pieces.is_sliding_piece(piece):
                generate_sliding_moves(startSquare, piece, board)
    return moves

def generate_sliding_moves(startSquare, piece, board):
    from GUI import Pieces
    # For bishops, start at direction index 4; for rooks, use indices 0–3;
    # for queens, use all 8 directions.
    start_direction_index = 4 if Pieces.is_type(piece) == Pieces.bishop else 0
    end_direction_index = 4 if Pieces.is_type(piece) == Pieces.rook else 8
    for directionIndex in range(start_direction_index, end_direction_index):
        for n in range(num_squares_to_edge[startSquare][directionIndex]):
            target_square = startSquare + direction_offsets[directionIndex] * (n + 1)
            if target_square < 0 or target_square > 63:
                continue
            target_piece = board.get_piece(target_square)
            if target_piece is None:
                moves.append(Move(startSquare, target_square))
                continue
            if Pieces.get_piece_color(target_piece) == Pieces.get_piece_color(piece):
                break
            if Pieces.get_piece_color(target_piece) != Pieces.get_piece_color(piece):
                moves.append(Move(startSquare, target_square))
                break

def generate_pawn_moves(board):
    from GUI import Pieces
    moves.clear()
    for startSquare in range(64):
        piece = board.get_piece(startSquare)
        if piece is None:
            continue
        if Pieces.get_piece_color(piece) == board.color_to_move:
            if Pieces.is_type(piece) == Pieces.pawn:
                generate_pawn_move(startSquare, piece, board)
    return moves

def generate_pawn_move(startSquare, piece, board):
    from GUI import Pieces
    direction = -1 if Pieces.get_piece_color(piece) == Pieces.white else 1
    target_square = startSquare + 8 * direction
    if target_square < 0 or target_square > 63:
        return
    if board.get_piece(target_square) is None:
        moves.append(Move(startSquare, target_square))
    # Check for double move
    if (startSquare // 8 == 6 and Pieces.get_piece_color(piece) == Pieces.white) or \
       (startSquare // 8 == 1 and Pieces.get_piece_color(piece) == Pieces.black):
        target_square2 = startSquare + 16 * direction
        if board.get_piece(target_square2) is None:
            moves.append(Move(startSquare, target_square2))
    # Captures
    for cross in [7, 9]:
        target_square = startSquare + cross * direction
        if target_square < 0 or target_square > 63:
            continue
        if abs((startSquare % 8) - (target_square % 8)) > 1:
            continue
        target_piece = board.get_piece(target_square)
        if target_piece is not None and Pieces.get_piece_color(target_piece) != Pieces.get_piece_color(piece):
            moves.append(Move(startSquare, target_square))

def generate_knight_moves(board):
    from GUI import Pieces
    moves.clear()
    for startSquare in range(64):
        piece = board.get_piece(startSquare)
        if piece is None:
            continue
        if Pieces.get_piece_color(piece) == board.color_to_move:
            if Pieces.is_type(piece) == Pieces.knight:
                generate_knight_move(startSquare, piece, board)
    return moves

def generate_knight_move(startSquare, piece, board):
    from GUI import Pieces
    knight_offsets = [-17, -15, -10, -6, 6, 10, 15, 17]
    for offset in knight_offsets:
        target_square = startSquare + offset
        if target_square < 0 or target_square > 63:
            continue
        if abs((startSquare % 8) - (target_square % 8)) > 2:
            continue
        target_piece = board.get_piece(target_square)
        if target_piece is None or Pieces.get_piece_color(target_piece) != Pieces.get_piece_color(piece):
            moves.append(Move(startSquare, target_square))

def generate_king_moves(board):
    from GUI import Pieces
    moves.clear()
    for startSquare in range(64):
        piece = board.get_piece(startSquare)
        if piece is None:
            continue
        if Pieces.get_piece_color(piece) == board.color_to_move:
            if Pieces.is_type(piece) == Pieces.king:
                generate_king_move(startSquare, piece, board)
    return moves

def generate_king_move(startSquare, piece, board):
    from GUI import Pieces
    king_offsets = [-9, -8, -7, -1, 1, 7, 8, 9]
    for offset in king_offsets:
        target_square = startSquare + offset
        if target_square < 0 or target_square > 63:
            continue
        target_piece = board.get_piece(target_square)
        if target_piece is None or Pieces.get_piece_color(target_piece) != Pieces.get_piece_color(piece):
            moves.append(Move(startSquare, target_square))
    # # Simplified castling moves (for example only kingside)
    # if startSquare == 4 and piece == "k":
    #     moves.append(Move(startSquare, 6))
    # if startSquare == 60 and piece == "K":
    #     moves.append(Move(startSquare, 62))

def special_moves(board, startSquare, targetSquare, allow_castling, piece):
    from GUI import Pieces
    
    # Pawn promotion: promote to queen when reaching the back rank.
    if Pieces.is_type(piece) == Pieces.pawn:
        if (targetSquare < 8 and Pieces.get_piece_color(piece) == Pieces.white) or \
           (targetSquare > 55 and Pieces.get_piece_color(piece) == Pieces.black):
            return (targetSquare, "Q" if Pieces.get_piece_color(piece) == Pieces.white else "q")
    
    # Castling (simplified example)
    if Pieces.is_type(piece) == Pieces.king:
        if castling(board=board, startSquare=startSquare, targetSquare=targetSquare) == True:
            if piece == "k":
                # Black kingside castling: move rook from square 7 to 5
                return ((targetSquare - 1, board.get_piece(7)), (7, None), (targetSquare, piece))
            elif piece == "K":
                # White kingside castling: move rook from square 63 to 61
                return ((targetSquare - 1, board.get_piece(63)), (63, None), (targetSquare, piece))
    return None

def is_check(board, color):
    from GUI import Pieces
    king_square = None
    for square in range(64):
        piece = board.get_piece(square)
        if piece is not None and Pieces.get_piece_color(piece) == color and Pieces.is_type(piece) == Pieces.king:
            king_square = square
            break
    if king_square is None:
        return False
    opponent_color = Pieces.black if color == Pieces.white else Pieces.white
    opponent_moves = generate_all_moves(board, opponent_color)
    for move in opponent_moves:
        if move.targetSquare == king_square:
            return True
    return False

def checkmate(board, color):
    from GUI import Pieces
    if not is_check(board, color):
        return False
    legal_moves = generate_all_moves(board, color)
    for move in legal_moves:
        board_copy = board.copy()
        piece = board_copy.get_piece(move.startSquare)
        board_copy.set_piece(move.startSquare, None)
        board_copy.set_piece(move.targetSquare, piece)
        if not is_check(board_copy, color):
            return False
    return True

def generate_all_moves(board, color):
    from GUI import Pieces
    all_moves = []
    # Temporarily set the board’s color to the given color
    original_color = board.color_to_move
    board.color_to_move = color
    for square in range(64):
        piece = board.get_piece(square)
        if piece is not None and Pieces.get_piece_color(piece) == color:
            piece_type = Pieces.is_type(piece)
            if piece_type in [Pieces.queen, Pieces.rook, Pieces.bishop]:
                all_moves.extend(generate_sliding_piece_moves(board))
            elif piece_type == Pieces.knight:
                all_moves.extend(generate_knight_moves(board))
            elif piece_type == Pieces.pawn:
                all_moves.extend(generate_pawn_moves(board))
            elif piece_type == Pieces.king:
                all_moves.extend(generate_king_moves(board))
    board.color_to_move = original_color
    return all_moves

def is_game_over(board):
    """
    Determines if the game is over. The game is over if either king
    is missing (i.e. captured) or if the current side is checkmated.
    """
    from GUI import Pieces

    white_king_found = False
    black_king_found = False

    # Loop through all squares to check for the kings.
    for square in range(64):
        piece = board.get_piece(square)
        if piece is not None and Pieces.is_type(piece) == Pieces.king:
            if Pieces.get_piece_color(piece) == Pieces.white:
                white_king_found = True
            elif Pieces.get_piece_color(piece) == Pieces.black:
                black_king_found = True

    # If either king is missing, the game is over.
    if not white_king_found:
        board.winner = "Black"
        return True
    if not black_king_found:
        board.winner = "White"
        return True

    # Otherwise, if the current side is checkmated, the game is over.
    if checkmate(board, board.color_to_move):
        # If the current side (whose turn it is) is checkmated,
        # the opponent wins.
        board.winner = "White" if board.color_to_move == Pieces.black else "Black"
        return True

    return False


def castling(board, startSquare, targetSquare):
    from GUI import Pieces
    piece = board.get_piece(startSquare)
    
    if Pieces.is_type(piece) != Pieces.king:
        return None
    
    if board.color_to_move == Pieces.white:    
        if startSquare != 60:
            return None
        if board.get_piece(63) != "R":
            return None
        if board.get_piece(61) is not None or board.get_piece(62) is not None:
            return None
        return True
    elif board.color_to_move == Pieces.black:
        if startSquare != 4:
            return None
        if board.get_piece(7) != "r":
            return None
        if board.get_piece(5) is not None or board.get_piece(6) is not None:
            return None
        return True
    return None