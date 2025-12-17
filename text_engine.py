from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math
from collections import Counter

def get_dominant_colors(image, num_colors=5):
    """Extract dominant colors from the image"""
    # Resize for faster processing
    img_small = image.resize((150, 150))
    pixels = list(img_small.getdata())

    # Filter out near-white and near-black pixels
    filtered_pixels = []
    for pixel in pixels:
        if len(pixel) >= 3:
            r, g, b = pixel[:3]
            brightness = (r + g + b) / 3
            # Skip very light (>240) or very dark (<30) pixels
            if 30 < brightness < 240:
                filtered_pixels.append((r, g, b))

    if not filtered_pixels:
        filtered_pixels = [(r, g, b) for r, g, b, *_ in pixels]

    # Get most common colors
    color_counts = Counter(filtered_pixels)
    return [color for color, count in color_counts.most_common(num_colors)]

def add_festive_text(image_path, text, output_path):
    print(f"🎨 Painting festive text '{text}' onto image...")

    # Open the image
    try:
        base = Image.open(image_path).convert("RGBA")
    except IOError:
        raise ValueError("Could not open the source image.")

    # Sample colors from the design
    dominant_colors = get_dominant_colors(base, num_colors=5)
    print(f"🎨 Sampled colors from design")

    # Choose complementary colors from the design
    # Use the most saturated/vibrant colors for text
    outline_color = dominant_colors[0] if len(dominant_colors) > 0 else (139, 0, 0)
    accent_color = dominant_colors[1] if len(dominant_colors) > 1 else (255, 215, 0)

    # Create a transparent layer for text effects
    txt_layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    # Dynamic font size - smaller to fit better in circle (10% of width)
    W, H = base.size
    font_size = int(W * 0.10)

    # Try to load a bold/decorative font for festive look
    font = None
    font_attempts = [
        ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size),
        ("/System/Library/Fonts/Supplemental/Impact.ttf", font_size),
        ("Arial Bold.ttf", font_size),
        ("ArialBold.ttf", font_size),
        ("Arial.ttf", font_size),
        ("arial.ttf", font_size),
    ]

    for font_path, size in font_attempts:
        try:
            font = ImageFont.truetype(font_path, size)
            break
        except:
            continue

    if font is None:
        print("⚠️ Using default font")
        font = ImageFont.load_default()

    # Calculate text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Position text to fit within circular boundary
    center_x = W / 2
    center_y = H / 2
    radius = min(W, H) / 2

    # Calculate safe position that keeps text inside circle
    # Text at bottom of circle: y = center + radius - text_height - safety_margin
    safety_margin = radius * 0.15  # 15% margin from circle edge
    text_y_target = center_y + radius - text_h - safety_margin

    # Verify text width fits within circle at this y position
    # At distance d from center, circle width = 2 * sqrt(r^2 - d^2)
    y_dist_from_center = abs(text_y_target - center_y)
    if y_dist_from_center < radius:
        max_width_at_y = 2 * math.sqrt(radius**2 - y_dist_from_center**2)
        # Add horizontal margin
        safe_width = max_width_at_y * 0.85  # Use 85% of available width

        # If text is too wide, reduce font size
        if text_w > safe_width:
            scale_factor = safe_width / text_w
            font_size = int(font_size * scale_factor)
            # Reload font with new size
            for font_path, _ in font_attempts:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]

    x = center_x - (text_w / 2)
    y = text_y_target

    # Create multiple layers for depth effect
    stroke_width = max(3, int(font_size * 0.12))

    # 1. Outer glow/shadow using design color
    glow_layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    for offset in range(stroke_width + 3, stroke_width, -1):
        alpha = int(100 * (1 - offset / (stroke_width + 3)))
        glow_color = (*outline_color, alpha)
        for adj_x in range(-offset, offset + 1):
            for adj_y in range(-offset, offset + 1):
                if adj_x*adj_x + adj_y*adj_y <= offset*offset:
                    glow_draw.text((x+adj_x, y+adj_y), text, font=font, fill=glow_color)
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(2))
    txt_layer = Image.alpha_composite(txt_layer, glow_layer)
    draw = ImageDraw.Draw(txt_layer)

    # 2. Thick stroke using design color
    for adj_x in range(-stroke_width, stroke_width + 1):
        for adj_y in range(-stroke_width, stroke_width + 1):
            if adj_x*adj_x + adj_y*adj_y <= stroke_width*stroke_width:
                draw.text((x+adj_x, y+adj_y), text, font=font, fill=outline_color)

    # 3. Inner stroke using accent color from design
    inner_stroke = max(2, int(stroke_width * 0.4))
    for adj_x in range(-inner_stroke, inner_stroke + 1):
        for adj_y in range(-inner_stroke, inner_stroke + 1):
            if adj_x*adj_x + adj_y*adj_y <= inner_stroke*inner_stroke:
                draw.text((x+adj_x, y+adj_y), text, font=font, fill=accent_color)

    # 4. Main text (White for maximum contrast and readability)
    draw.text((x, y), text, font=font, fill="#FFFFFF")

    # 5. Add subtle highlight on top
    highlight_offset = max(1, int(stroke_width * 0.25))
    draw.text((x, y - highlight_offset), text, font=font, fill=(255, 255, 255, 50))

    # Composite and save
    out = Image.alpha_composite(base, txt_layer)
    out = out.convert("RGB")
    out.save(output_path)
    print(f"✨ Text styled with design colors and fitted to circle")
    return output_path
