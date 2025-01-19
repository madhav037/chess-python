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