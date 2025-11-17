import os
import httpx

def fix_light_audio():
    """
    Regenerates the 'color_light.mp3' audio file with alternative spelling.
    """
    output_dir = "audio_bricks"
    
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

    # --- Regenerate the 'color_light.mp3' file ---
    print("--- Fixing 'color_light.mp3' ---")
    text = "lite"
    output_path = os.path.join(output_dir, "color_light.mp3")
    print(f"Generating: {output_path} -> '{text}'")
    try:
        payload = {"text": text}
        response = httpx.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print("  Success!")
        else:
            print(f"  [ERROR] API Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"  [ERROR] Could not generate audio for '{text}'. Reason: {e}")

if __name__ == "__main__":
    fix_light_audio()