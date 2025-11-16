import os
import chess
import httpx

def generate_all_square_audio():
    """
    Generates audio files for each square on the chessboard using Deepgram's REST API.
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

    print("Initializing Deepgram TTS request...")

    for square_name in chess.SQUARE_NAMES:
        # Format text for better TTS pronunciation, e.g., "b1" -> "b 1"
        file = square_name[0]
        rank = square_name[1]

        # Handle the "a" file pronunciation issue
        if file == 'a':
            text = f"A. {rank}"
        else:
            text = f"{file} {rank}"
        filename = f"square_{square_name}.mp3"
        output_path = os.path.join(output_dir, filename)

        if os.path.exists(output_path):
            print(f"Skipping existing file: {output_path}")
            continue

        print(f"Generating: {output_path} -> '{text}'")
        try:
            payload = {"text": text}
            
            # Make the request and get the entire response
            response = httpx.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                # Write the complete audio content at once
                with open(output_path, "wb") as f:
                    f.write(response.content)
            else:
                # Print the error details from the response body
                print(f"  [ERROR] API Error: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"  [ERROR] Could not generate audio for '{text}'. Reason: {e}")

    print("\n--- All Square Audio Generation Complete ---")


if __name__ == "__main__":
    generate_all_square_audio()