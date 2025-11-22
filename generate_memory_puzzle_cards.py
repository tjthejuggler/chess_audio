import genanki
import os
import chess
from pydub import AudioSegment
import random
import re
import argparse

# --- Anki Card Model Definition ---
DECK_ID_BASE = 2059400111
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

def generate_puzzle(num_pieces):
    """
    Generates a board position with a random number of pieces.
    """
    board = chess.Board(None)
    pieces = [
        chess.Piece(chess.PAWN, chess.WHITE), chess.Piece(chess.KNIGHT, chess.WHITE),
        chess.Piece(chess.BISHOP, chess.WHITE), chess.Piece(chess.ROOK, chess.WHITE),
        chess.Piece(chess.QUEEN, chess.WHITE), chess.Piece(chess.KING, chess.WHITE),
        chess.Piece(chess.PAWN, chess.BLACK), chess.Piece(chess.KNIGHT, chess.BLACK),
        chess.Piece(chess.BISHOP, chess.BLACK), chess.Piece(chess.ROOK, chess.BLACK),
        chess.Piece(chess.QUEEN, chess.BLACK), chess.Piece(chess.KING, chess.BLACK)
    ]
    
    squares = list(chess.SQUARES)
    random.shuffle(squares)
    
    placed_pieces = 0
    white_pieces_count = 0
    black_pieces_count = 0
    
    while placed_pieces < num_pieces and squares:
        square = squares.pop()
        piece = random.choice(pieces)
        
        if piece.color == chess.WHITE and white_pieces_count >= 16:
            continue
        if piece.color == chess.BLACK and black_pieces_count >= 16:
            continue

        # Ensure kings are placed for a valid position, if not already
        if placed_pieces == num_pieces - 2 and not board.king(chess.WHITE):
            piece = chess.Piece(chess.KING, chess.WHITE)
        if placed_pieces == num_pieces - 1 and not board.king(chess.BLACK):
             piece = chess.Piece(chess.KING, chess.BLACK)

        if not board.piece_at(square):
            board.set_piece_at(square, piece)
            if piece.color == chess.WHITE:
                white_pieces_count += 1
            else:
                black_pieces_count += 1
            placed_pieces += 1
            
    # Ensure there is at least one king of each color
    if not board.king(chess.WHITE):
        square = squares.pop()
        board.set_piece_at(square, chess.Piece(chess.KING, chess.WHITE))
    if not board.king(chess.BLACK):
        square = squares.pop()
        board.set_piece_at(square, chess.Piece(chess.KING, chess.BLACK))

    return board

def create_anki_deck(num_pieces):
    """
    Generates an Anki deck with chess memory puzzles.
    """
    deck_id = DECK_ID_BASE + num_pieces
    deck_name = f'Chess Memory Puzzles - {num_pieces} Pieces'
    deck = genanki.Deck(deck_id, deck_name)
    media_files = []
    output_audio_dir = "output_audio"
    os.makedirs(output_audio_dir, exist_ok=True)
    
    card_count = 0
    num_cards_to_generate = 50  # Generate 50 cards per deck

    print(f"--- Generating Memory Puzzle Cards ({num_pieces} pieces) ---")

    for i in range(num_cards_to_generate):
        board = generate_puzzle(num_pieces)
        all_pieces = []
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                all_pieces.append((square, piece))
        
        if not all_pieces:
            continue

        # Decide on the question type
        if random.choice([True, False]):
            # Ask for the piece on a given square
            square, piece = random.choice(all_pieces)
            square_name = chess.square_name(square)
            question_text = f"What piece is on {square_name}?"
            question_audio_files = ["phrase_what_piece_is_on.mp3", f"square_{square_name}.mp3"]
            
            piece_name_str = get_piece_name(piece.piece_type)
            if piece.piece_type == chess.BISHOP:
                square_color = "light" if (chess.square_file(square) + chess.square_rank(square)) % 2 != 0 else "dark"
                piece_name_str = f"{square_color}-squared bishop"

            answer_text = f"{'White' if piece.color == chess.WHITE else 'Black'} {piece_name_str.capitalize()}"
            answer_audio_files = [f"color_{'white' if piece.color == chess.WHITE else 'black'}.mp3", f"piece_{get_piece_name(piece.piece_type)}.mp3"]
            if piece.piece_type == chess.BISHOP:
                answer_audio_files.insert(0, f"phrase_{square_color}_squared.mp3")

        else:
            # Ask for the square(s) of a given piece type
            square, piece = random.choice(all_pieces)
            piece_type = piece.piece_type
            color = piece.color
            color_name = 'White' if color == chess.WHITE else 'Black'
            piece_name = get_piece_name(piece_type)

            # Find all pieces of the same type and color
            matching_pieces = [(s, p) for s, p in all_pieces if p.piece_type == piece_type and p.color == color]

            if piece_type == chess.BISHOP:
                # Handle bishops separately to specify square color
                is_light = (chess.square_file(square) + chess.square_rank(square)) % 2 != 0
                square_color_str = "light squared" if is_light else "dark squared"
                question_text = f"Where is the {color_name} {square_color_str} bishop?"
                question_audio_files = ["phrase_where_is_the.mp3", f"color_{color_name.lower()}.mp3", f"phrase_{square_color_str.replace(' ', '_')}.mp3", "piece_bishop.mp3"]
                answer_text = chess.square_name(square)
                answer_audio_files = [f"square_{answer_text}.mp3"]
            else:
                if len(matching_pieces) > 1:
                    question_text = f"Where are the {color_name} {piece_name}s?"
                    question_audio_files = ["phrase_where_are_the.mp3", f"color_{color_name.lower()}.mp3", f"piece_{piece_name}s.mp3"]
                    answer_text = ", ".join(sorted([chess.square_name(s) for s, p in matching_pieces]))
                    answer_audio_files = []
                    for s, p in sorted(matching_pieces, key=lambda item: item[0]):
                        answer_audio_files.extend([f"square_{chess.square_name(s)}.mp3", "silence_0.2s.mp3"])
                else:
                    question_text = f"Where is the {color_name} {piece_name}?"
                    question_audio_files = ["phrase_where_is_the.mp3", f"color_{color_name.lower()}.mp3", f"piece_{piece_name}.mp3"]
                    answer_text = chess.square_name(square)
                    answer_audio_files = [f"square_{answer_text}.mp3"]

        # --- Generate Board State Audio and Text ---
        board_text_parts = []
        board_audio_files = []
        
        # White pieces
        board_text_parts.append("White:")
        board_audio_files.extend(["color_white.mp3", "silence_0.5s.mp3"])
        white_squares = [s for s in chess.SQUARES if board.piece_at(s) and board.piece_at(s).color == chess.WHITE]
        for square in sorted(white_squares):
            piece = board.piece_at(square)
            square_name = chess.square_name(square)
            piece_name = get_piece_name(piece.piece_type)
            board_text_parts.append(f"{piece_name.capitalize()} {square_name}")
            board_audio_files.extend([f"piece_{piece_name}.mp3", f"square_{square_name}.mp3", "silence_0.2s.mp3"])

        # Black pieces
        board_text_parts.append("Black:")
        board_audio_files.extend(["color_black.mp3", "silence_0.5s.mp3"])
        black_squares = [s for s in chess.SQUARES if board.piece_at(s) and board.piece_at(s).color == chess.BLACK]
        for square in sorted(black_squares):
            piece = board.piece_at(square)
            square_name = chess.square_name(square)
            piece_name = get_piece_name(piece.piece_type)
            board_text_parts.append(f"{piece_name.capitalize()} {square_name}")
            board_audio_files.extend([f"piece_{piece_name}.mp3", f"square_{square_name}.mp3", "silence_0.2s.mp3"])
            
        full_question_text = " ".join(board_text_parts) + f" --- {question_text}"
        
        card_count += 1
        print(f"\n--- Card #{card_count} ---")
        print(f"  FEN: {board.fen()}")
        print(f"  Question: {question_text}")
        print(f"  Answer: {answer_text}")
        
        # --- Combine Audio ---
        question_audio_output = os.path.join(output_audio_dir, f"memory_puzzle_q_{num_pieces}_{card_count}.mp3")
        combine_audio(board_audio_files + question_audio_files, question_audio_output)

        answer_audio_output = os.path.join(output_audio_dir, f"memory_puzzle_a_{num_pieces}_{card_count}.mp3")
        combine_audio(answer_audio_files, answer_audio_output)
        
        note = genanki.Note(
            model=deck_model_audio_and_written,
            fields=[
                full_question_text,
                answer_text,
                f"[sound:{os.path.basename(question_audio_output)}]",
                f"[sound:{os.path.basename(answer_audio_output)}]"
            ],
            tags=[f'memory_{num_pieces}_pieces'])
        deck.add_note(note)
        
        media_files.append(question_audio_output)
        media_files.append(answer_audio_output)

    package = genanki.Package(deck)
    package.media_files = list(set(media_files))
    for f in os.listdir("audio_bricks"):
        package.media_files.append(os.path.join("audio_bricks", f))
    package.write_to_file(f'chess_memory_puzzles_{num_pieces}_pieces.apkg')

    print("\n--- Anki Deck Generation Complete ---")
    print(f"Generated {card_count} cards for a {num_pieces}-piece deck.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Anki decks for chess memory puzzles.")
    parser.add_argument("num_pieces", type=int, help="The number of pieces to include in the puzzles (2-32).")
    args = parser.parse_args()

    if 2 <= args.num_pieces <= 32:
        create_anki_deck(args.num_pieces)
    else:
        print("Error: Number of pieces must be between 2 and 32.")