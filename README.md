# Chess Audio Anki Card Generator

This project is a collection of Python scripts designed to generate custom Anki decks for chess training, with a strong focus on audio-based learning. The scripts can be used to create cards for memorizing square colors, practicing simple tactics, and more.

## Features

- **Audio-First Learning**: Cards are designed with audio prompts for questions, reinforcing learning through sound.
- **Highly Customizable**: The framework is modular, making it easy to create new types of chess-related Anki decks.
- **Automated Puzzle Generation**: The `generate_capture_puzzle_cards.py` script procedurally generates simple capture puzzles, providing a nearly endless supply of unique training material.

## File Structure

- **`generate_chess_color_cards.py`**: A script to generate an Anki deck for learning the color of each square on the chessboard.
- **`generate_capture_puzzle_cards.py`**: A script that creates an Anki deck of simple puzzles where the goal is to find the one legal capture on the board.
- **`generate_new_audio.py`**: A utility script that uses Coqui TTS to generate new `.wav` files from text. These audio "bricks" are the building blocks for the audio prompts on the Anki cards.
- **`requirements.txt`**: A list of all the Python dependencies required to run the scripts.
- **`audio_bricks/`**: This directory contains all the small, individual audio clips (e.g., "white", "king", "a1") that are combined to create the full audio prompts.
- **`output_audio/`**: When the generator scripts are run, the combined question audio files (in `.mp3` format) are saved here.
- **`*.apkg`**: These are the generated Anki deck files, which can be directly imported into Anki.

## Setup and Installation

1.  **Clone the Repository**
    ```bash
    git clone <repository_url>
    cd chess_audio
    ```

2.  **Create a Virtual Environment**
    It is highly recommended to use a virtual environment to manage the project's dependencies.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies**
    Install all the necessary packages using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### 1. Generating New Audio Bricks

If you need new audio clips for a custom deck, you can use the `generate_new_audio.py` script.

1.  Open `generate_new_audio.py` in a text editor.
2.  Modify the `generate_audio()` function call at the bottom of the file with the text you want to convert to speech and the desired output filename.
    ```python
    # Example
    generate_audio("Your text here", "new_audio_file.wav")
    ```
3.  Run the script:
    ```bash
    python3 generate_new_audio.py
    ```
    The new `.wav` file will be saved in the `audio_bricks/` directory.

### 2. Generating Anki Decks

To generate the Anki decks, simply run the desired generator script:

-   **For Chess Square Colors:**
    ```bash
    python3 generate_chess_color_cards.py
    ```
    This will create a file named `chess_square_colors.apkg`.

-   **For Simple Capture Puzzles:**
    ```bash
    python3 generate_capture_puzzle_cards.py
    ```
    This will create a file named `chess_capture_puzzles.apkg`.

After running the script, you can import the resulting `.apkg` file into your Anki application.

## How to Create a New Anki Deck

The easiest way to create a new type of deck is to adapt one of the existing generator scripts.

1.  **Duplicate an Existing Script**: Copy `generate_chess_color_cards.py` or `generate_capture_puzzle_cards.py` to a new file (e.g., `generate_my_new_deck.py`).
2.  **Change the Deck ID**: In the new script, change the `DECK_ID` to a new, unique random number. This is crucial to prevent conflicts with existing decks in Anki. You can generate one in the Python console with `import random; print(random.randint(10**9, 10**10 - 1))`.
3.  **Implement Your Logic**: Modify the `create_anki_deck` function to implement the logic for your new cards. This will involve:
    -   Generating the board positions, questions, or other data for your cards.
    -   Defining the `question_text` and `answer_text`.
    -   Assembling the list of `question_audio_files` from the `audio_bricks/` directory.
    -   Generating any new audio bricks you might need using `generate_new_audio.py`.
4.  **Run the New Script**:
    ```bash
    python3 generate_my_new_deck.py
    ```
    This will create your new `my_new_deck.apkg` file, ready for import into Anki.
