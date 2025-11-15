import chess
import os
import torch
import numpy as np
import soundfile as sf
from TTS.api import TTS

def generate_word_list():
    """
    Generates a complete list of all unique audio "bricks"
    needed for chess visualization, with suggested filenames.
    """
    all_words = {}

    # --- 1. Colors ---
    colors = ["White", "Black"]
    for word in colors:
        all_words[f"color_{word.lower()}.wav"] = word

    # --- 2. Pieces (Singular) ---
    pieces_singular = {
        chess.PAWN: "Pawn",
        chess.KNIGHT: "Knight",
        chess.BISHOP: "Bishop",
        chess.ROOK: "Rook",
        chess.QUEEN: "Queen",
        chess.KING: "King",
    }
    for piece_type, name in pieces_singular.items():
        all_words[f"piece_{name.lower()}.wav"] = name

    # --- 3. Pieces (Plural) ---
    pieces_plural = [
        "Pawns", "Knights", "Bishops", "Rooks", "Queens", "Kings",
    ]
    for word in pieces_plural:
        all_words[f"piece_{word.lower()}.wav"] = word

    # --- 4. Board Files (Letters) ---
    files = list(chess.FILE_NAMES)
    for file_name in files:
        all_words[f"file_{file_name}.wav"] = file_name

    # --- 5. Board Ranks (Numbers) ---
    ranks = [str(r) for r in range(1, 9)]
    for rank_name in ranks:
        all_words[f"rank_{rank_name}.wav"] = rank_name

    # --- 6. Action Words ---
    actions = [
        "captures",
        "takes",
        "to",
        "on",
        "and",
        "check",
        "checkmate",
        "promotes",
        "promote",
    ]
    for word in actions:
        all_words[f"action_{word.lower()}.wav"] = word

    # --- 7. Common Phrases ---
    phrases = [
        "White to move",
        "Black to move",
        "no pieces",
    ]
    for phrase in phrases:
        filename = phrase.lower().replace(" ", "_")
        all_words[f"phrase_{filename}.wav"] = phrase

    return all_words

if __name__ == "__main__":
    output_dir = "audio_bricks"
    os.makedirs(output_dir, exist_ok=True)

    # Determine the device to use
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # --- Initialize Coqui TTS with an American English voice ---
    print("Initializing Coqui TTS engine with an American English voice...")
    # This model is a high-quality, single-speaker American female voice.
    model_name = "tts_models/en/ljspeech/vits"
    try:
        tts = TTS(model_name).to(device)
    except Exception as e:
        print(f"Error initializing TTS model: {e}")
        print("Please check your internet connection or the model name.")
        exit()

    # --- Regenerate specific files with the new voice ---
    files_to_regenerate = {
        "file_a.wav": "ae",
        "file_d.wav": "dea"
    }

    print("\nRegenerating specific audio files with the new voice...")
    for filename, text in files_to_regenerate.items():


    #all_words = generate_word_list()

    #for filename, text in all_words.items():
        output_path = os.path.join(output_dir, filename)
        print(f"Generating: {output_path} -> '{text}'")
        try:
            # Single-speaker models don't require the 'speaker' argument.
            tts.tts_to_file(text=text, file_path=output_path)
        except Exception as e:
            print(f"  [ERROR] Could not generate audio for '{text}'. Reason: {e}")

    print("\n--- Regeneration Complete ---")
    print("The specified audio files have been updated.")