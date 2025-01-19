# generating precomputed moves
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
                min(num_south, num_west), 
            ]
            
            
class Move:
    startSquare = None
    targetSquare = None
    
    def __init__(self, startSquare, targetSquare):
        self.startSquare = startSquare
        self.targetSquare = targetSquare


moves = []

def generate_sliding_piece_moves(board):
    from GUI.pieces import Pieces

    global moves
    moves.clear()
    for startSquare in range(64):
        piece = board.get_piece(startSquare)
        if piece == None:
            continue
        if Pieces.get_piece_color(piece) == board.color_to_move:
            # print("inside if 1")
            if Pieces.is_sliding_piece(piece):
                # print("indide if 2")    
                generate_sliding_moves(startSquare, piece, board)
    print("got moves in 1 : ", len(moves))
    return moves

def generate_sliding_moves(startSquare, piece, board):
    global moves
    from GUI.pieces import Pieces

    # print("inside generate_sliding_moves")
    start_direction_index = 4 if Pieces.is_type(piece) == Pieces.bishop else 0
    end_direction_index = 4 if Pieces.is_type(piece) == Pieces.rook else 8
    
    for directionIndex in range(start_direction_index, end_direction_index):
        
        for n in range(num_squares_to_edge[startSquare][directionIndex]):
            # Calculate the target square
            target_square = startSquare + direction_offsets[directionIndex] * (n + 1)
            
            if target_square < 0 or target_square > 63:
                continue
            piece_on_target_square = board.get_piece(target_square)
            
            # If the square is empty, add it as a valid move
            if piece_on_target_square is None:
                moves.append(Move(startSquare, target_square))
                continue
            
            # If the square is occupied by a friendly piece, stop this direction
            if Pieces.get_piece_color(piece_on_target_square) == Pieces.get_piece_color(piece):
                break

            # If the square is occupied by an enemy piece, add it as a capture move and stop this direction
            if Pieces.get_piece_color(piece_on_target_square) != Pieces.get_piece_color(piece):
                moves.append(Move(startSquare, target_square))
                break
    print("got moves in 2 : ", len(moves))
    
    
def generate_pawn_moves(board):
    from GUI.pieces import Pieces
    global moves
    moves.clear()
    for startSquare in range(64):
        piece = board.get_piece(startSquare)
        if piece == None:
            continue
        if Pieces.get_piece_color(piece) == board.color_to_move:
            if Pieces.is_type(piece) == Pieces.pawn:
                generate_pawn_move(startSquare, piece, board)
    return moves

def generate_pawn_move(startSquare, piece, board):
    from GUI.pieces import Pieces
    direction = -1 if Pieces.get_piece_color(piece) == Pieces.white else 1
    target_square = startSquare + 8 * direction
    
    # ? Error may happen 🤷‍♂️
    if target_square < 0 or target_square > 63:
        return
    if board.get_piece(target_square) is None:
        moves.append(Move(startSquare, target_square))

    # Check for double move
    if (startSquare // 8 == 6 and Pieces.get_piece_color(piece) == Pieces.white) or (startSquare // 8 == 1 and Pieces.get_piece_color(piece) == Pieces.black):
        target_square = startSquare + 16 * direction
        if board.get_piece(target_square) is None:
            moves.append(Move(startSquare, target_square))
    
    # Check for captures
    for cross in [7, 9]:
        target_square = startSquare + cross * direction
        if Pieces.get_piece_color(board.get_piece(target_square)) != Pieces.get_piece_color(piece) and board.get_piece(target_square) is not None:
            moves.append(Move(startSquare, target_square))
    
    print("got moves in 3 : ", len(moves))

def generate_knight_moves(board):
    from GUI.pieces import Pieces
    global moves
    moves.clear()
    for startSquare in range(64):
        piece = board.get_piece(startSquare)
        if piece == None:
            continue
        if Pieces.get_piece_color(piece) == board.color_to_move:
            if Pieces.is_type(piece) == Pieces.knight:
                generate_knight_move(startSquare, piece, board)
    return moves

def generate_knight_move(startSquare, piece, board):
    from GUI.pieces import Pieces
    for direction in [-17, -15, -10, -6, 6, 10, 15, 17]:
        target_square = startSquare + direction
        if target_square < 0 or target_square > 63:
            continue
        if Pieces.get_piece_color(board.get_piece(target_square)) != Pieces.get_piece_color(piece):
            moves.append(Move(startSquare, target_square))
    print("got moves in 4 : ", len(moves))
    
def generate_king_moves(board):
    from GUI.pieces import Pieces
    global moves
    moves.clear()
    for startSquare in range(64):
        piece = board.get_piece(startSquare)
        if piece == None:
            continue
        if Pieces.get_piece_color(piece) == board.color_to_move:
            if Pieces.is_type(piece) == Pieces.king:
                generate_king_move(startSquare, piece, board)
    return moves

def generate_king_move(startSquare, piece, board):
    from GUI.pieces import Pieces
    for direction in [-9, -8, -7, -1, 1, 7, 8, 9]:
        target_square = startSquare + direction
        if target_square < 0 or target_square > 63:
            continue
        if Pieces.get_piece_color(board.get_piece(target_square)) != Pieces.get_piece_color(piece):
            moves.append(Move(startSquare, target_square))
        
        if startSquare == 4 and piece == "k":
            moves.append(Move(startSquare, 6))
        if startSquare == 60 and piece == "K":
            moves.append(Move(startSquare, 62))
    print("got moves in 5 : ", len(moves))
    

# this function is used to convert pawn into [queen, rook, bishop, knight] and do castling
def special_moves(board, startSquare, targetSquare, allow_castling, piece):
    from GUI.pieces import Pieces
    # piece = board.get_piece(startSquare)
    print("inside special_moves", startSquare, targetSquare, piece)
    can_castle = None
    if piece == "k":
        can_castle = allow_castling[1]
    elif piece == "K":
        can_castle = allow_castling[0]
    print(can_castle)
    if Pieces.is_type(piece) == Pieces.pawn:
        if (targetSquare < 8 and Pieces.get_piece_color(piece) == Pieces.white) or (targetSquare > 55 and Pieces.get_piece_color(piece) == Pieces.black):
            board.set_piece(targetSquare, "Q" if Pieces.get_piece_color(piece) == Pieces.white else "q")
            print(board.get_piece(targetSquare))
            return True
    elif Pieces.is_type(piece) == Pieces.king and can_castle:
        if abs(startSquare - targetSquare) == 2 and Pieces.is_type(board.get_piece(targetSquare+1)) == Pieces.rook and Pieces.is_type(board.get_piece(targetSquare-1)) == Pieces.none:
            board.set_piece(targetSquare-1, board.get_piece(targetSquare+1))
            board.set_piece(targetSquare+1, None)
            board.set_piece(targetSquare, piece)
            return True
    return False
    print("got moves in 6 : ", len(moves))
    
    
def is_game_over(board, target_square):
    if board.dragged_piece not in ['k', 'K'] and board.get_piece(target_square) in ['k', 'K']:
        board.winner = "White" if board.color_to_move == 8 else "Black"
        return True
        
