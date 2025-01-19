import pygame

# Load piece images with error handling
try:
    piece_images = {
        "K": pygame.image.load("GUI/assets/white_raja.png"),  # White King
        "Q": pygame.image.load("GUI/assets/white_rani.png"),  # White Queen
        "B": pygame.image.load("GUI/assets/white_ooth.png"),  # White Bishop
        "N": pygame.image.load("GUI/assets/white_ghodo.png"),  # White Knight
        "R": pygame.image.load("GUI/assets/white_hathi.png"),  # White Rook
        "P": pygame.image.load("GUI/assets/white_paidad.png"),  # White Pawn
        "k": pygame.image.load("GUI/assets/black_raja.png"),  # Black King
        "q": pygame.image.load("GUI/assets/black_rani.png"),  # Black Queen
        "b": pygame.image.load("GUI/assets/black_ooth.png"),  # Black Bishop
        "n": pygame.image.load("GUI/assets/black_ghodo.png"),  # Black Knight
        "r": pygame.image.load("GUI/assets/black_hathi.png"),  # Black Rook
        "p": pygame.image.load("GUI/assets/black_paidad.png"),  # Black Pawn
    }
except pygame.error as e:
    print(f"Error loading piece images: {e}")

class Pieces:
    PIECE_SIZE = 40
    none = None
    king = 1
    pawn = 2
    knight = 3
    bishop = 4
    rook = 5
    queen = 6

    white = 8
    black = 16
    
    @staticmethod
    def get_piece_color(piece):
        if not piece or not isinstance(piece, str):
            print(f"Invalid piece passed to get_piece_color: {piece}")
            return None
        return Pieces.white if piece.isupper() else Pieces.black
    
    @staticmethod
    def is_sliding_piece(piece):
        if not piece or not isinstance(piece, str):
            print(f"Invalid piece passed to is_sliding_piece: {piece}")
            return False
        print("inside is_sliding_piece", piece, piece.lower() in ["b", "r", "q"])
        return piece.lower() in ["b", "r", "q"]
    
    @staticmethod
    def is_type(piece):
        if not piece or not isinstance(piece, str):
            print(f"Invalid piece passed to is_type: {piece}")
            return None
        piece = piece.lower()
        if piece == "k":
            return Pieces.king
        elif piece == "p":
            return Pieces.pawn
        elif piece == "n":
            return Pieces.knight
        elif piece == "b":
            return Pieces.bishop
        elif piece == "r":
            return Pieces.rook
        elif piece == "q":
            return Pieces.queen
        return None
