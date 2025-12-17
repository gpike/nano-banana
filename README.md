# 🍌 Nano Banana CLI

A local tool to generate personalized circular designs using AI.

## Setup

1. Open this folder in VS Code.
2. Open a terminal (`Ctrl+~`) and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your [Google API Key](https://aistudio.google.com/app/apikey).

## Usage

**Basic Run:**

```bash
python main.py --bg assets/background.jpg --subject assets/subject.jpg --text "Justin 2025"
```

**With Custom Clothing:**

```bash
python main.py --bg assets/background.jpg --subject assets/subject.jpg --clothes "red Santa suit" --text "Justin 2025"
```

**VS Code Debugging:**
Press `F5`. This is pre-configured to run a test using the placeholder assets in the `assets/` folder.

## Options

- `--bg`: Path to background image (required)
- `--subject`: Path to person/pet photo (required)
- `--clothes`: Description of clothing (default: "Santa suit")
- `--text`: Text to add to design (required)
- `--output`: Output filename (default: "final_banana.jpg")

## How It Works

1. **AI Processing**: Uses Google Gemini 2.0 Flash to blend your subject with the background style while applying clothing changes
2. **Text Overlay**: Adds festive text with automatic sizing and styling (banana yellow with black outline)
3. **Output**: Saves the final image and opens it automatically

## Requirements

- Python 3.9+
- Google Cloud account with Gemini API access
- Google API Key from [AI Studio](https://aistudio.google.com/app/apikey)
- Valid background and subject images
