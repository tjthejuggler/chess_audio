# Deepgram TTS Setup Instructions

To use the updated `generate_square_audio.py` script, you'll need to configure your local environment with your Deepgram API key.

## 1. Get Your Deepgram API Key

If you haven't already, sign up for a Deepgram account at [https://deepgram.com/](https://deepgram.com/) and create an API key.

## 2. Set the Environment Variable

The Python script reads your API key from an environment variable. You'll need to set this in your terminal before running the script.

**On Linux or macOS:**

```bash
export DEEPGRAM_API_KEY="your_deepgram_api_key"
```

**On Windows:**

```powershell
$Env:DEEPGRAM_API_KEY="your_deepgram_api_key"
```

Replace `"your_deepgram_api_key"` with your actual Deepgram API key.

## 3. Run the Script

Once you've set the environment variable, you can run the script:

```bash
python generate_square_audio.py
```

The script will now use your Deepgram account to generate the audio files.