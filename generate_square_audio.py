import os
import chess
import httpx

def generate_all_square_audio():
    """
    Generates audio files for each square on the chessboard using Deepgram TTS
    and the NATO phonetic alphabet for files.
    """
    output_dir = "audio_bricks"
    os.makedirs(output_dir, exist_ok=True)

    # NATO phonetic alphabet mapping
    nato_map = {
        'a': 'Alpha', 'b': 'Bravo', 'c': 'Charlie', 'd': 'Delta',
        'e': 'Echo', 'f': 'Foxtrot', 'g': 'Golf', 'h': 'Hotel'
    }

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

    print("--- Generating Square Audio with NATO Phonetic Alphabet ---")

    for square_name in chess.SQUARE_NAMES:
        file = square_name[0]
        rank = square_name[1]
        
        # Use NATO word for the file
        nato_file = nato_map[file]
        text = f"{nato_file} {rank}"

        filename = f"square_{square_name}.mp3"
        output_path = os.path.join(output_dir, filename)

        if os.path.exists(output_path):
            print(f"Skipping existing file: {output_path}")
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

    print("\n--- All Square Audio Generation Complete ---")


if __name__ == "__main__":
    generate_all_square_audio()