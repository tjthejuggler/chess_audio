import os
import httpx
import argparse

def generate_audio(text, filename):
    """
    Generates an audio file from the given text using Deepgram TTS.
    """
    output_dir = "audio_bricks"
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open("deepgram_apikey.txt", "r") as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print("Error: deepgram_apikey.txt not found.")
        return

    if not api_key:
        print("Error: DEEPGRAM_API_KEY is missing from deepgram_apikey.txt.")
        return

    url = "https://api.deepgram.com/v1/speak?model=aura-2-thalia-en"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

    output_path = os.path.join(output_dir, filename)
    
    if os.path.exists(output_path):
        print(f"Skipping existing file: {output_path}")
        return

    print(f"Generating: {output_path} -> '{text}'")
    try:
        payload = {"text": text}
        response = httpx.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"Successfully generated {filename}")
        else:
            print(f"  [ERROR] API Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"  [ERROR] Could not generate audio for '{text}'. Reason: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an audio file from text using Deepgram TTS.")
    parser.add_argument("text", type=str, help="The text to convert to speech.")
    parser.add_argument("filename", type=str, help="The output filename (e.g., 'my_audio.mp3').")
    args = parser.parse_args()
    
    generate_audio(args.text, args.filename)