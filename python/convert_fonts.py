import os
from PIL import Image
import freetype
import time
from fontTools.ttLib import TTFont

def find_glyphs_with_duplicate_outlines(font, code):
    duplicate_chars = []
    cmap = font.getBestCmap()

    if 'glyf' in font:
        glyph_table = font['glyf']

        if code in cmap:
            glyph_name = cmap[code]
            glyph1 = glyph_table[glyph_name].getCoordinates(glyph_table)

            for code2 in cmap:
                if code != code2:
                    glyph_name2 = cmap[code2]
                    glyph2 = glyph_table[glyph_name2].getCoordinates(glyph_table)

                    if glyph1 == glyph2 and glyph_name != glyph_name2:
                        duplicate_chars.append(glyph_name)
                        duplicate_chars.append(glyph_name2)

    elif 'CFF ' in font or 'CFF2' in font:
        cff_table = font['CFF '] if 'CFF ' in font else font['CFF2']
        top_dict = cff_table.cff.topDictIndex[0]
        char_strings = top_dict.CharStrings

        if code in cmap:
            glyph_name = cmap[code]
            char_string1 = char_strings[glyph_name]

            for code2 in cmap:
                if code != code2:
                    glyph_name2 = cmap[code2]
                    char_string2 = char_strings[glyph_name2]

                    if char_string1.bytecode == char_string2.bytecode and glyph_name != glyph_name2:
                        duplicate_chars.append(glyph_name)
                        duplicate_chars.append(glyph_name2)

    duplicate_chars = list(set(duplicate_chars))
    return duplicate_chars

def render_font(font_path, output_base_dir="glyphs", min_size=512, render_size=1024):
    font_name = os.path.splitext(os.path.basename(font_path))[0]
    output_dir = os.path.join(output_base_dir, font_name)
    os.makedirs(output_dir, exist_ok=True)

    face = freetype.Face(font_path)
    face.set_char_size(render_size * 64)  # Render at a high resolution first

    font = TTFont(font_path)
    cmap = font.getBestCmap()

    if cmap is None:
        print(f"No valid cmap found for font: {font_name}")
        return

    unique_characters = []
    processed_glyphs = set()

    for code in cmap:
        if code not in processed_glyphs:
            duplicate_glyphs = find_glyphs_with_duplicate_outlines(font, code)
            if len(duplicate_glyphs) > 0:
                processed_glyphs.update(duplicate_glyphs)
            else:
                unique_characters.append(code)
                processed_glyphs.add(code)

    def render_character(char, face, min_size):
        try:
            face.load_char(char)
            bitmap = face.glyph.bitmap
            width = bitmap.width
            rows = bitmap.rows

            if width == 0 or rows == 0:
                return None

            print(f"Rendering character: '{char}' (U+{ord(char):04X}), width: {width}, height: {rows}")

            # Create an image with the exact size of the glyph
            image = Image.new("RGBA", (width, rows), (0, 0, 0, 0))
            buffer = bytes(bitmap.buffer)
            mask = Image.frombytes("L", (width, rows), buffer)
            image.paste((255, 255, 255, 255), (0, 0), mask)

            # Scale the image to ensure the larger dimension is at least min_size
            if max(width, rows) < min_size:
                scale_factor = max(min_size / width, min_size / rows)
                new_width = int(width * scale_factor)
                new_height = int(rows * scale_factor)
                image = image.resize((new_width, new_height), Image.LANCZOS)

            return image
        except Exception as e:
            print(f"Error rendering character '{char}' (U+{ord(char):04X}): {e}")
            return None

    start_time = time.time()
    for idx, code in enumerate(unique_characters):
        char = chr(code)
        if idx % 10 == 0:
            elapsed_time = time.time() - start_time
            print(f"Rendering character {idx}/{len(unique_characters)} - Elapsed time: {elapsed_time:.2f} seconds")
        image = render_character(char, face, min_size)
        if image:
            try:
                safe_char = char if char.isalnum() else f"U{ord(char):04X}"
                image.save(os.path.join(output_dir, f"{safe_char}.png"))
            except Exception as e:
                print(f"Error saving character '{char}' (U+{ord(char):04X}): {e}")

    print(f"Glyphs rendered and saved to {output_dir}")

def batch_convert_fonts(fonts_dir, output_base_dir="glyphs", min_size=512, render_size=1024):
    for font_file in os.listdir(fonts_dir):
        if font_file.lower().endswith(('.ttf', '.otf')):
            font_path = os.path.join(fonts_dir, font_file)
            print(f"Processing font: {font_file}")
            try:
                render_font(font_path, output_base_dir, min_size, render_size)
            except Exception as e:
                print(f"Error processing font {font_file}: {e}")

# Update with the path to your folder containing fonts
fonts_directory = "testfonts"
batch_convert_fonts(fonts_directory)
