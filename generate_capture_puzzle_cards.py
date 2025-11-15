import genanki
import os
import chess
from pydub import AudioSegment
import random

# --- Anki Card Model Definition ---
DECK_ID = 2059400110  # A new ID for this deck
MODEL_ID = 1376944192 # Reusing the same model ID

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
            audio_segment = AudioSegment.from_wav(os.path.join("audio_bricks", file))
            combined_audio += audio_segment
        except FileNotFoundError:
            print(f"  [ERROR] Audio file not found: {file}")
            return None
    
    # Export the combined audio to a temporary file
    combined_audio.export(output_filename, format="mp3")
    return output_filename

def get_piece_name(piece_type):
    """
    Returns the lowercase name of a piece type.
    """
    return chess.piece_name(piece_type).lower()

def generate_puzzle(attacker_color, attacker_piece_type, defender_piece_type):
    """
    Generates a board position with a valid, simple capture puzzle.
    Returns the board state and the correct capture move.
    """
    while True:
        board = chess.Board(None)  # Start with an empty board

        # 1. Place kings randomly, ensuring they are not adjacent
        while True:
            white_king_square = random.choice(chess.SQUARES)
            black_king_square = random.choice(list(set(chess.SQUARES) - {white_king_square}))
            if chess.square_distance(white_king_square, black_king_square) > 1:
                board.set_piece_at(white_king_square, chess.Piece(chess.KING, chess.WHITE))
                board.set_piece_at(black_king_square, chess.Piece(chess.KING, chess.BLACK))
                break

        # 2. Place the defending piece
        defender_color = not attacker_color
        defender_squares = list(set(chess.SQUARES) - {white_king_square, black_king_square})
        defender_square = random.choice(defender_squares)
        board.set_piece_at(defender_square, chess.Piece(defender_piece_type, defender_color))

        # 3. Find a valid square for the attacking piece
        attacker_squares = list(set(chess.SQUARES) - {white_king_square, black_king_square, defender_square})
        random.shuffle(attacker_squares)  # Try squares in a random order

        for attacker_square in attacker_squares:
            test_board = board.copy()
            test_board.set_piece_at(attacker_square, chess.Piece(attacker_piece_type, attacker_color))

            # Rule 1: The position must be legal. The king of the side NOT to move cannot be in check.
            test_board.turn = not attacker_color
            if test_board.is_check():
                continue

            # Rule 2: There must be a legal capture of the defender.
            test_board.turn = attacker_color
            capture_move = chess.Move(attacker_square, defender_square)
            if capture_move in test_board.legal_moves:
                # This is a valid puzzle. Return the board and the move.
                return test_board, capture_move
        
        # If the loop completes, no valid attacker square was found. The main while loop will try again.

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
            for i in range(5):  # Create 5 cards for each piece combination
                
                # Alternate who starts, to get a mix of puzzles
                attacker_color = chess.WHITE if i % 2 == 0 else chess.BLACK

                board, capture_move = generate_puzzle(attacker_color, attacker_pt, defender_pt)

                # --- Build Question Text & Audio ---
                question_text_parts = []
                question_audio_files = []

                # White's pieces
                question_text_parts.append("White:")
                question_audio_files.extend(["color_white.wav", "silence_0.5s.wav"])
                white_pieces = board.pieces(chess.KING, chess.WHITE) | board.pieces(attacker_pt if attacker_color == chess.WHITE else defender_pt, chess.WHITE)
                for square in sorted(list(white_pieces)):
                    piece = board.piece_at(square)
                    square_name = chess.square_name(square)
                    piece_name = get_piece_name(piece.piece_type)
                    question_text_parts.append(f"{piece_name.capitalize()} on {square_name}")
                    question_audio_files.extend([f"piece_{piece_name}.wav", "action_on.wav", f"file_{square_name[0]}.wav", f"rank_{square_name[1]}.wav", "silence_0.2s.wav"])

                # Black's pieces
                question_text_parts.append("Black:")
                question_audio_files.extend(["color_black.wav", "silence_0.5s.wav"])
                black_pieces = board.pieces(chess.KING, chess.BLACK) | board.pieces(attacker_pt if attacker_color == chess.BLACK else defender_pt, chess.BLACK)
                for square in sorted(list(black_pieces)):
                    piece = board.piece_at(square)
                    square_name = chess.square_name(square)
                    piece_name = get_piece_name(piece.piece_type)
                    question_text_parts.append(f"{piece_name.capitalize()} on {square_name}")
                    question_audio_files.extend([f"piece_{piece_name}.wav", "action_on.wav", f"file_{square_name[0]}.wav", f"rank_{square_name[1]}.wav", "silence_0.2s.wav"])
                
                # Whose turn
                turn_text = "White to move" if attacker_color == chess.WHITE else "Black to move"
                question_text_parts.append(turn_text)
                question_audio_files.append(f"phrase_{turn_text.lower().replace(' ', '_')}.wav")
                
                question_text = " ".join(question_text_parts)
                answer_text = board.san(capture_move)
                
                # --- Print to Console ---
                card_count += 1
                print(f"\n--- Card #{card_count} ---")
                print(f"  Puzzle: {get_piece_name(attacker_pt).capitalize()} captures {get_piece_name(defender_pt).capitalize()}")
                print(f"  FEN: {board.fen()}")
                print(f"  Question: {question_text}")
                print(f"  Answer: {answer_text}")
                
                # --- Combine Audio and Create Anki Note ---
                question_audio_output = os.path.join(output_audio_dir, f"capture_puzzle_{card_count}.mp3")
                combine_audio(question_audio_files, question_audio_output)
                
                note = genanki.Note(
                    model=deck_model_audio_and_written,
                    fields=[
                        question_text,
                        answer_text,
                        f"[sound:{os.path.basename(question_audio_output)}]",
                        "[sound:silence_0.2s.wav]"  # Placeholder for answer audio
                    ],
                    tags=['simple_captures'])
                deck.add_note(note)
                
                # Add media files to the list for packaging
                media_files.append(question_audio_output)
                media_files.extend([os.path.join("audio_bricks", f) for f in question_audio_files if os.path.exists(os.path.join("audio_bricks", f))])

    # --- Generate Anki Package ---
    package = genanki.Package(deck)
    package.media_files = list(set(media_files))
    package.write_to_file('chess_capture_puzzles.apkg')

    print("\n--- Anki Deck Generation Complete ---")
    print(f"Generated {card_count} cards.")
    print("The deck 'chess_capture_puzzles.apkg' has been created.")

if __name__ == "__main__":
    create_anki_deck()