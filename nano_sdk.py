import os
import tempfile
import base64
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFilter
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()

class NanoBananaSDK:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("❌ Missing API Key. Please add GOOGLE_API_KEY to your .env file.")

        self.client = genai.Client(api_key=self.api_key)

    def create_design(self, background_path, subject_path, text="", clothing_prompt="Santa suit", design_template="christmas_round"):
        """
        Generate a professional festive design using Gemini's image generation.

        Args:
            background_path: Path to background image (optional, not used in current implementation)
            subject_path: Path to subject image (person/baby/pet)
            text: Text to include in the design (Gemini will render it naturally)
            clothing_prompt: Clothing to add (e.g., "Santa suit")
            design_template: Design style ("christmas_round", "holiday_card", "festive_scene")
        """
        print(f"🍌 SDK: Creating AI design with Gemini Image Generation...")

        try:
            # Load subject image and convert to base64
            with open(subject_path, 'rb') as f:
                subject_data = f.read()
            subject_b64 = base64.b64encode(subject_data).decode('utf-8')

            # Load template from file
            template_file = os.path.join(os.path.dirname(__file__), "templates", f"{design_template}.md")

            if not os.path.exists(template_file):
                # Fallback to christmas_round if template not found
                template_file = os.path.join(os.path.dirname(__file__), "templates", "christmas_round.md")

            with open(template_file, 'r') as f:
                template_content = f.read()

            # Build text instruction
            text_instruction = ""
            if text:
                text_instruction = f"""
TEXT INTEGRATION (CRITICAL):
- Include the text "{text}" in the design
- Style the text to blend naturally with the holiday theme
- Position text at the bottom of the composition, curved or integrated into the design
- Use festive fonts and colors that complement the overall design (gold, white, red, green with glows/shadows)
- Add subtle effects like glow, snow sparkles, or light rays around the text
- Make the text clearly readable but feeling like part of the magical scene, not overlaid
- The text should look like it belongs in the image, with proper lighting and depth
"""

            # Format template with variables
            prompt = template_content.format(
                clothing_prompt=clothing_prompt,
                text_instruction=text_instruction
            )

            print(f"📝 Using template: {design_template}")
            print(f"🎨 Generating AI design...")

            # Create contents with subject image
            with open(subject_path, 'rb') as f:
                subject_bytes = f.read()

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type="image/png",
                                data=subject_bytes
                            )
                        ),
                    ],
                ),
            ]

            # Configure for image generation
            generate_content_config = types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )

            # Generate image with streaming
            temp_file = None
            for chunk in self.client.models.generate_content_stream(
                model="gemini-3-pro-image-preview",
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue

                part = chunk.candidates[0].content.parts[0]
                if part.inline_data and part.inline_data.data:
                    # Create temp file and save image data
                    if temp_file is None:
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', mode='wb')

                    temp_file.write(part.inline_data.data)

            if temp_file:
                temp_file.close()
                temp_path = temp_file.name

                # Verify the image
                try:
                    test_img = Image.open(temp_path)
                    print(f"✨ AI design generated: {test_img.size} pixels")

                    # Apply circular mask for christmas_round template
                    if design_template == "christmas_round":
                        print(f"🎯 Applying circular mask...")
                        masked_path = self._apply_circular_mask(temp_path)
                        test_img.close()
                        os.remove(temp_path)  # Remove unmasked version
                        return masked_path

                    test_img.close()
                    return temp_path
                except Exception as e:
                    print(f"❌ Generated file verification failed: {e}")
                    return self._create_composite(background_path, subject_path, clothing_prompt)
            else:
                print(f"⚠️ No image data received, falling back to compositing...")
                return self._create_composite(background_path, subject_path, clothing_prompt)

        except Exception as e:
            print(f"⚠️ AI generation failed: {e}")
            print(f"📝 Falling back to basic compositing...")
            return self._create_composite(background_path, subject_path, clothing_prompt)

    def _apply_circular_mask(self, image_path):
        """Apply a circular mask and crop to 1:1 aspect ratio for perfect round design"""
        # Load the image
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size

        # Crop to square (1:1 aspect ratio) - take the center
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size

        img_square = img.crop((left, top, right, bottom))

        # Create a circular mask for the square image
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)

        # Draw a circle with slight margin for clean edges
        margin = int(size * 0.01)  # 1% margin
        draw.ellipse([margin, margin, size - margin, size - margin], fill=255)

        # Apply slight blur for smooth edges
        mask = mask.filter(ImageFilter.GaussianBlur(2))

        # Create a new square image with transparent background
        result = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        result.paste(img_square, (0, 0), mask)

        # Save to new temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', mode='wb')
        result.save(temp_file.name, 'PNG')
        temp_file.close()

        print(f"📐 Cropped to 1:1 aspect ratio: {size}x{size} pixels")

        return temp_file.name

    def _create_composite(self, background_path, subject_path, clothing_prompt):
        """Fallback: Create a basic composite image"""
        from PIL import ImageDraw, ImageFilter

        # Load images
        background = Image.open(background_path).convert("RGBA")
        subject = Image.open(subject_path).convert("RGBA")

        # Get target size from background
        bg_width, bg_height = background.size

        # Resize subject to fit nicely (60% of background height)
        target_height = int(bg_height * 0.6)
        aspect_ratio = subject.width / subject.height
        target_width = int(target_height * aspect_ratio)
        subject_resized = subject.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # Create a circular mask
        mask = Image.new('L', subject_resized.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, subject_resized.width, subject_resized.height), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(3))

        # Calculate position (center-bottom)
        x_pos = (bg_width - target_width) // 2
        y_pos = bg_height - target_height - int(bg_height * 0.1)

        # Composite
        background.paste(subject_resized, (x_pos, y_pos), mask)

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', mode='wb')
        background_rgb = background.convert("RGB")
        background_rgb.save(temp_file.name, 'PNG')
        temp_file.close()

        return temp_file.name
