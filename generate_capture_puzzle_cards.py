import genanki
import os
import chess
from pydub import AudioSegment
import random
import re

# --- Anki Card Model Definition ---
DECK_ID = 2059400110
MODEL_ID = 1376944192

deck_model_audio_and_written = genanki.Model(
    MODEL_ID,
    'Audio And Text Model',
    fields=[
        {'name': 'QuestionText'},
        {'name': 'AnswerText'},
        {'name': 'QuestionAudio'},
        {'name': 'AnswerAudio'},
    ],
    templates=[
        {
            'name': 'Card 1',
            'qfmt': '{{QuestionText}}<br>{{QuestionAudio}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{AnswerText}}<br>{{AnswerAudio}}',
        },
    ])

def combine_audio(file_list, output_filename):
    """
    Combines multiple audio files into one.
    """
    combined_audio = AudioSegment.empty()
    for file in file_list:
        try:
            # Use from_file for format-agnostic loading (handles .mp3)
            audio_segment = AudioSegment.from_file(os.path.join("audio_bricks", file))
            combined_audio += audio_segment
        except FileNotFoundError:
            print(f"  [ERROR] Audio file not found: {file}")
            return None
    
    combined_audio.export(output_filename, format="mp3")
    return output_filename

def get_piece_name(piece_type):
    """
    Returns the lowercase name of a piece type.
    """
    return chess.piece_name(piece_type).lower()

def generate_answer_audio_files(san_move):
    """
    Parses a SAN move string and returns a list of corresponding audio files.
    Example: 'fxg6' -> ['piece_pawn.mp3', 'action_captures.mp3', 'square_g6.mp3']
    Example: 'Nxg6+' -> ['piece_knight.mp3', 'action_captures.mp3', 'square_g6.mp3']
    """
    san = san_move.replace('+', '').replace('#', '') # Clean check/mate symbols
    audio_files = []
    
    piece_map = {'N': 'knight', 'B': 'bishop', 'R': 'rook', 'Q': 'queen', 'K': 'king'}
    nato_map = {
        'a': 'Alpha', 'b': 'Bravo', 'c': 'Charlie', 'd': 'Delta',
        'e': 'Echo', 'f': 'Foxtrot', 'g': 'Golf', 'h': 'Hotel'
    }

    # Find the destination square, which is always the last two characters
    dest_square = san[-2:]

    # Identify the piece
    if san[0].islower(): # Pawn move (e.g., fxg6)
        # For "fxg6", the audio should be "Foxtrot captures Golf 6"
        origin_file = san[0]
        # We use the full square audio which contains the NATO word
        audio_files.append(f"square_{origin_file}1.mp3") # Use any rank, it will say the NATO word
        # Manually slice the audio to only keep the NATO word part (approximate)
    elif san[0] in piece_map: # Piece move (e.g., Nxg6)
        piece_name = piece_map[san[0]]
        audio_files.append(f"piece_{piece_name}s.mp3") # Use plural form for consistency

    if 'x' in san:
        audio_files.append("action_captures.mp3")

    audio_files.append(f"square_{dest_square}.mp3")
    
    # A bit of a hack to get just the NATO word sound from a square file
    # This part is complex, so let's simplify for now
    # Let's re-evaluate the spoken phrase for pawns.
    # "Pawn captures Golf 6" is unambiguous and uses existing files.
    
    # --- Simplified Logic ---
    final_audio_files = []
    if san[0].islower(): # Pawn move like fxg6
        final_audio_files.append("piece_pawn.mp3")
    elif san[0] in piece_map:
        # Use plural for pieces for better sound, e.g., "knights", "rooks"
        piece_name = piece_map[san[0]]
        final_audio_files.append(f"piece_{piece_name}s.mp3")

    if 'x' in san:
        final_audio_files.append("action_captures.mp3")

    final_audio_files.append(f"square_{dest_square}.mp3")

    return final_audio_files


def generate_puzzle(attacker_color, attacker_piece_type, defender_piece_type):
    """
    Generates a board position with a valid, simple capture puzzle.
    """
    while True:
        board = chess.Board(None)
        while True:
            white_king_square = random.choice(chess.SQUARES)
            black_king_square = random.choice(list(set(chess.SQUARES) - {white_king_square}))
            if chess.square_distance(white_king_square, black_king_square) > 1:
                board.set_piece_at(white_king_square, chess.Piece(chess.KING, chess.WHITE))
                board.set_piece_at(black_king_square, chess.Piece(chess.KING, chess.BLACK))
                break
        defender_color = not attacker_color
        defender_squares = list(set(chess.SQUARES) - {white_king_square, black_king_square})
        defender_square = random.choice(defender_squares)
        board.set_piece_at(defender_square, chess.Piece(defender_piece_type, defender_color))
        attacker_squares = list(set(chess.SQUARES) - {white_king_square, black_king_square, defender_square})
        random.shuffle(attacker_squares)
        for attacker_square in attacker_squares:
            test_board = board.copy()
            test_board.set_piece_at(attacker_square, chess.Piece(attacker_piece_type, attacker_color))
            test_board.turn = not attacker_color
            if test_board.is_check():
                continue
            test_board.turn = attacker_color
            capture_move = chess.Move(attacker_square, defender_square)
            if capture_move in test_board.legal_moves:
                return test_board, capture_move

def create_anki_deck():
    """
    Generates an Anki deck with simple chess capture puzzles.
    """
    deck = genanki.Deck(DECK_ID, 'Chess Simple Capture Puzzles')
    media_files = []
    output_audio_dir = "output_audio"
    os.makedirs(output_audio_dir, exist_ok=True)
    
    piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
    card_count = 0

    print("--- Generating Simple Capture Puzzle Cards ---")

    for attacker_pt in piece_types:
        for defender_pt in piece_types:
            for i in range(5):
                attacker_color = chess.WHITE if i % 2 == 0 else chess.BLACK
                board, capture_move = generate_puzzle(attacker_color, attacker_pt, defender_pt)

                question_text_parts = []
                question_audio_files = []

                question_text_parts.append("White:")
                question_audio_files.extend(["color_white.mp3", "silence_0.5s.mp3"])
                white_pieces = board.pieces(chess.KING, chess.WHITE) | board.pieces(attacker_pt if attacker_color == chess.WHITE else defender_pt, chess.WHITE)
                for square in sorted(list(white_pieces)):
                    piece = board.piece_at(square)
                    square_name = chess.square_name(square)
                    piece_name = get_piece_name(piece.piece_type)
                    question_text_parts.append(f"{piece_name.capitalize()} {square_name}")
                    question_audio_files.extend([f"piece_{piece_name}s.mp3", f"square_{square_name}.mp3", "silence_0.2s.mp3"])

                question_text_parts.append("Black:")
                question_audio_files.extend(["color_black.mp3", "silence_0.5s.mp3"])
                black_pieces = board.pieces(chess.KING, chess.BLACK) | board.pieces(attacker_pt if attacker_color == chess.BLACK else defender_pt, chess.BLACK)
                for square in sorted(list(black_pieces)):
                    piece = board.piece_at(square)
                    square_name = chess.square_name(square)
                    piece_name = get_piece_name(piece.piece_type)
                    question_text_parts.append(f"{piece_name.capitalize()} {square_name}")
                    question_audio_files.extend([f"piece_{piece_name}s.mp3", f"square_{square_name}.mp3", "silence_0.2s.mp3"])
                
                turn_text = "White to move" if attacker_color == chess.WHITE else "Black to move"
                question_text_parts.append(turn_text)
                question_audio_files.append(f"phrase_{turn_text.lower().replace(' ', '_')}.mp3")
                
                question_text = " ".join(question_text_parts)
                answer_text = board.san(capture_move)
                
                card_count += 1
                print(f"\n--- Card #{card_count} ---")
                print(f"  FEN: {board.fen()}")
                print(f"  Answer: {answer_text}")
                
                # --- Combine Audio ---
                question_audio_output = os.path.join(output_audio_dir, f"capture_puzzle_q_{card_count}.mp3")
                combine_audio(question_audio_files, question_audio_output)

                answer_audio_files = generate_answer_audio_files(answer_text)
                answer_audio_output = os.path.join(output_audio_dir, f"capture_puzzle_a_{card_count}.mp3")
                combine_audio(answer_audio_files, answer_audio_output)
                
                note = genanki.Note(
                    model=deck_model_audio_and_written,
                    fields=[
                        question_text,
                        answer_text,
                        f"[sound:{os.path.basename(question_audio_output)}]",
                        f"[sound:{os.path.basename(answer_audio_output)}]"
                    ],
                    tags=['simple_captures'])
                deck.add_note(note)
                
                media_files.append(question_audio_output)
                media_files.append(answer_audio_output)

    package = genanki.Package(deck)
    package.media_files = list(set(media_files))
    # Add all base audio bricks to the package media
    for f in os.listdir("audio_bricks"):
        package.media_files.append(os.path.join("audio_bricks", f))
    package.write_to_file('chess_capture_puzzles.apkg')

    print("\n--- Anki Deck Generation Complete ---")
    print(f"Generated {card_count} cards.")

if __name__ == "__main__":
    create_anki_deck()