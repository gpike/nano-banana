# 🍌 Nano Banana CLI

A local tool to generate personalized holiday designs using AI image generation.

## Features

- 🎨 **Dual AI Provider Support**: Works with Google Gemini or OpenAI DALL-E 3
- 🎄 **Multiple Templates**: christmas_round, holiday_card, festive_scene
- ✨ **AI-Generated Text**: Text naturally blended into the design
- 🔄 **Auto-Detection**: Automatically uses available API key
- 🎯 **Circular Masking**: Perfect round ornaments with transparent backgrounds

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Configure API key (choose one):

   **Option A: Google Gemini (Recommended)**

   - Get your API key at [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Add to `.env` file: `GOOGLE_API_KEY=your_key_here`

   **Option B: OpenAI DALL-E 3**

   - Get your API key at [OpenAI Platform](https://platform.openai.com/api-keys)
   - Add to `.env` file: `OPENAI_API_KEY=your_key_here`

## Usage

**Basic:**

```bash
python main.py --subject assets/subject.png --text "Justin 2025"
```

**Custom Template:**

```bash
python main.py --subject assets/photo.png --text "Happy Holidays" --template holiday_card
```

**Custom Clothing:**

```bash
python main.py --subject assets/photo.png --clothes "festive sweater" --text "2025"
```

## Options

- `--subject`: Path to person/pet photo (required)
- `--text`: Text to include in design (required)
- `--template`: Design template: christmas_round (default), holiday_card, festive_scene
- `--clothes`: Clothing description (default: "Santa suit")
- `--output`: Output filename (default: "final_banana.jpg")
- `--bg`: Background image path (optional, for style reference)

## Templates

- **christmas_round**: Circular ornament design with lights border (1:1 aspect, transparent background)
- **holiday_card**: Traditional card layout with festive borders
- **festive_scene**: Full Christmas scene with decorations

## How It Works

1. **AI Generation**: Uses Google Gemini 3 Pro or OpenAI DALL-E 3 to generate complete design
2. **Text Integration**: AI renders text naturally into the scene (not overlaid)
3. **Post-Processing**: Applies circular mask for ornament designs
4. **Output**: Saves final image with proper aspect ratio

## Requirements

- Python 3.9+
- Either Google Gemini API key OR OpenAI API key
- PIL/Pillow for image processing
