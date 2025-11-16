import os
import httpx
from pydub import AudioSegment

def get_text_from_filename(filename):
    """
    Parses the filename to get the text to be synthesized.
    Example: 'piece_king.wav' -> 'king'
    """
    # Remove extension and the prefix (e.g., 'action_', 'piece_')
    name = os.path.splitext(filename)[0]
    if '_' in name:
        parts = name.split('_')
        # Handle cases like 'phrase_black_to_move' -> 'black to move'
        return ' '.join(parts[1:])
    return name

def create_silence_file(output_path, duration_ms):
    """Creates a silent audio file."""
    silence = AudioSegment.silent(duration=duration_ms)
    silence.export(output_path, format="mp3")
    print(f"Generated silence file: {output_path}")

def regenerate_all_audio_bricks():
    """
    Regenerates all audio files in the audio_bricks directory using Deepgram TTS.
    """
    output_dir = "audio_bricks"
    os.makedirs(output_dir, exist_ok=True)

    # Reads the API key from deepgram_apikey.txt
    try:
        with open("deepgram_apikey.txt", "r") as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print("Error: deepgram_apikey.txt not found.")
        return

    if not api_key:
        print("Error: DEEPGRAM_API_KEY is missing from deepgram_apikey.txt.")
        return
    
    # --- HTTP Request Configuration ---
    url = "https://api.deepgram.com/v1/speak?model=aura-2-thalia-en"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

    # List of original filenames to regenerate (excluding squares, ranks, and files)
    filenames_to_regenerate = [
        "action_and.wav", "action_captures.wav", "action_check.wav", "action_checkmate.wav",
        "action_on.wav", "action_promote.wav", "action_promotes.wav", "action_takes.wav",
        "action_to.wav", "color_black.wav", "color_dark.wav", "color_light.wav",
        "color_white.wav", "phrase_black_to_move.wav", "phrase_no_pieces.wav",
        "phrase_what_color_is.wav", "phrase_white_to_move.wav", "piece_bishop.wav",
        "piece_bishops.wav", "piece_king.wav", "piece_kings.wav", "piece_knight.wav",
        "piece_knights.wav", "piece_pawn.wav", "piece_pawns.wav", "piece_queen.wav",
        "piece_queens.wav", "piece_rook.wav", "piece_rooks.wav", "silence_0.2s.wav",
        "silence_0.5s.wav"
    ]

    files_to_delete = [
        "file_a.wav", "file_b.wav", "file_c.wav", "file_d.wav", "file_e.wav",
        "file_f.wav", "file_g.wav", "file_h.wav", "rank_1.wav", "rank_2.wav",
        "rank_3.wav", "rank_4.wav", "rank_5.wav", "rank_6.wav", "rank_7.wav",
        "rank_8.wav"
    ]

    print("--- Deleting Obsolete Rank and File Audio ---")
    for filename in files_to_delete:
        path = os.path.join(output_dir, filename)
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted: {path}")

    print("\n--- Starting Regeneration of Audio Bricks ---")

    for old_filename in filenames_to_regenerate:
        text = get_text_from_filename(old_filename)
        new_filename = os.path.splitext(old_filename)[0] + ".mp3"
        output_path = os.path.join(output_dir, new_filename)

        # Handle silence files separately
        if "silence_0.2s" in old_filename:
            create_silence_file(output_path, 200)
            continue
        if "silence_0.5s" in old_filename:
            create_silence_file(output_path, 500)
            continue

        print(f"Generating: {output_path} -> '{text}'")
        try:
            payload = {"text": text}
            response = httpx.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
            else:
                print(f"  [ERROR] API Error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"  [ERROR] Could not generate audio for '{text}'. Reason: {e}")

    print("\n--- All Audio Brick Regeneration Complete ---")


if __name__ == "__main__":
    regenerate_all_audio_bricks()