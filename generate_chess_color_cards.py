import genanki
import os
import chess
from pydub import AudioSegment
import random

# --- Anki Card Model Definition ---
# This model is a simplified version of the one found in anki_helper.py
# It is tailored for audio-focused cards with text on both sides.

DECK_ID = 1633354192  # Custom deck ID for "Chess Square Colors"
MODEL_ID = 1376944192 # Custom model ID for "Audio And Text Model"

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

def get_square_color(square_name):
    """
    Determines if a chess square is light or dark.
    """
    square_index = chess.parse_square(square_name)
    file_index = chess.square_file(square_index)
    rank_index = chess.square_rank(square_index)
    # A square is light if the sum of its file and rank indices is odd.
    return "light" if (file_index + rank_index) % 2 != 0 else "dark"

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
    
    # Export the combined audio to a temporary file
    combined_audio.export(output_filename, format="mp3")
    return output_filename

def create_anki_deck():
    """
    Generates an Anki deck with cards for each square on the chessboard.
    """
    deck = genanki.Deck(DECK_ID, 'Chess Square Colors')
    media_files = []

    # Ensure the output directory for combined audio exists
    output_audio_dir = "output_audio"
    os.makedirs(output_audio_dir, exist_ok=True)

    # Shuffle the squares to randomize the card order in the deck
    square_list = list(chess.SQUARE_NAMES)
    random.shuffle(square_list)

    for square_name in square_list:
        color = get_square_color(square_name)
        
        # --- Create Question Audio ---
        question_audio_files = [
            "phrase_what_color_is.mp3",
            f"square_{square_name}.mp3",
        ]
        question_audio_output = os.path.join(output_audio_dir, f"what_color_is_{square_name}.mp3")
        combine_audio(question_audio_files, question_audio_output)
        
        # --- Create Answer Audio ---
        answer_audio_file = f"color_{color}.mp3"
        
        # --- Create Anki Note ---
        question_text = f"What color is {square_name}?"
        answer_text = color.capitalize()
        
        note = genanki.Note(
            model=deck_model_audio_and_written,
            fields=[
                question_text,
                answer_text,
                f"[sound:what_color_is_{square_name}.mp3]",
                f"[sound:{answer_audio_file}]"
            ],
            tags=['square_color'])
        deck.add_note(note)
        
        # Add all required media files to the list
        media_files.append(question_audio_output)
        media_files.append(os.path.join("audio_bricks", "color_light.mp3"))
        media_files.append(os.path.join("audio_bricks", "color_dark.mp3"))
        # Add the base audio bricks to the media files list
        for f in question_audio_files:
            media_files.append(os.path.join("audio_bricks", f))


    # --- Generate Anki Package ---
    package = genanki.Package(deck)
    # Add all unique media files to the package
    package.media_files = list(set(media_files))
    package.write_to_file('chess_square_colors.apkg')

    print("\n--- Anki Deck Generation Complete ---")
    print("The deck 'chess_square_colors.apkg' has been created.")

if __name__ == "__main__":
    create_anki_deck()