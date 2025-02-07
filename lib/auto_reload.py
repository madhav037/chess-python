import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"File {event.src_path} changed. Restarting...")
            os.system('python main.py')  # Replace with your game start command
            sys.exit()

def watch_files():
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    watch_files()


# def clicked_piece(self, col_idx, row_idx):
#         """When the user clicks a square, show available moves for that piece."""
#         from engine import generate_sliding_piece_moves, generate_knight_moves, generate_pawn_moves, generate_king_moves, is_check
#         self.avaliable_moves = []
#         self.opponent_pieces = []
#         piece = self.get_piece(row_idx * 8 + col_idx)
#         if piece is None:
#             print(f"No piece at ({col_idx}, {row_idx})")
#             return
#         print(f"Clicked piece: {piece} at ({col_idx}, {row_idx})")
#         # from pieces import Pieces
#         if Pieces.is_type(piece) in [Pieces.queen, Pieces.rook, Pieces.bishop]:
#             moves_list = generate_sliding_piece_moves(self)
#         elif Pieces.is_type(piece) == Pieces.knight:
#             moves_list = generate_knight_moves(self)
#         elif Pieces.is_type(piece) == Pieces.pawn:
#             moves_list = generate_pawn_moves(self)
#         elif Pieces.is_type(piece) == Pieces.king:
#             moves_list = generate_king_moves(self)
#             # Remove castling moves if castling is no longer allowed
#             if not self.allow_castling[0]:
#                 moves_list = [m for m in moves_list if m.targetSquare != 62]
#             if not self.allow_castling[1]:
#                 moves_list = [m for m in moves_list if m.targetSquare != 6]
#         # Filter moves belonging to the clicked piece
#         for move in moves_list:
#             if move.startSquare == row_idx * 8 + col_idx:
#                 self.avaliable_moves.append(move.targetSquare)
#             target_piece = self.get_piece(move.targetSquare)
#             if target_piece is not None:
#                 if Pieces.get_piece_color(target_piece) != Pieces.get_piece_color(piece):
#                     if move.targetSquare not in self.opponent_pieces:
#                         self.opponent_pieces.append(move.targetSquare)
#         if not self.avaliable_moves:
#             print(f"No available moves for {piece}")
#         else:
#             print(f"Available moves for {piece}: {self.avaliable_moves}")