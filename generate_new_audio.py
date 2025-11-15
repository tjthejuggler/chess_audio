import os
import torch
from TTS.api import TTS

def generate_audio(text, filename):
    """
    Generates an audio file from the given text using Coqui TTS.
    """
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

    output_path = os.path.join(output_dir, filename)
    print(f"Generating: {output_path} -> '{text}'")
    try:
        # Single-speaker models don't require the 'speaker' argument.
        tts.tts_to_file(text=text, file_path=output_path)
    except Exception as e:
        print(f"  [ERROR] Could not generate audio for '{text}'. Reason: {e}")

    print("\n--- Generation Complete ---")
    print(f"The audio file '{filename}' has been created.")

if __name__ == "__main__":
    generate_audio("dark", "color_dark.wav")