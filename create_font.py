import fontforge
import os

# alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
alphabet = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдеєжзиіїйклмнопрстуфхцчшщьюя123456789"
bearing_table = {
    "Default": [60, 60],
    "A": [60, -50],
    "a": [30, 40],
    "B": [60, 0],
    "C": [60, -30],
    "c": [60, 40],
    "b": [60, 40],
    "D": [60, 10],
    "d": [30, -20],
    "e": [30, 40],
    "E": [70, 10],
    "F": [70, 0],
    "f": [0, -20],
    "G": [60, 30],
    "g": [20, 60],
    "h": [40, 40],
    "I": [80, 50],
    "i": [60, 60],
    "J": [40, 30],
    "j": [-70, 40],
    "k": [40, 20],
    "K": [80, 0],
    "H": [60, 10],
    "L": [80, 10],
    "l": [60, 0],
    "M": [60, 30],
    "m": [40, 60],
    "N": [70, 10],
    "n": [30, 40],
    "O": [70, 10],
    "o": [40, 40],
    "P": [70, 0],
    "p": [60, 40],
    "Q": [70, 10],
    "q": [20, 30],
    "R": [70, -10],
    "r": [60, 40],
    "S": [60, 60],
    "s": [20, 40],
    "T": [60, -10],
    "t": [-10, 20],
    "U": [70, 20],
    "u": [40, 40],
    "V": [60, -10],
    "v": [20, 20],
    "W": [70, 20],
    "w": [40, 40],
    "X": [60, -10],
    "x": [10, 20],
    "y": [20, 30],
    "Y": [40, 0],
    "Z": [60, -10],
    "z": [10, 20],
    "1": [-10, 30],
    "2": [-10, 30],
    "3": [10, 40],
    "4": [30, 30],
    "5": [30, 40],
    "6": [20, 20],
    "7": [30, 20],
    "8": [30, 20],
    "9": [30, 30],
    "0": [50, 40],
    ".": [60, 10],
    ",": [60, 10],
    ";": [60, 10],
    ":": [60, 20],
    "!": [60, 20],
    "?": [60, 30],
    "\"": [60, 20],
    "'": [60, 10],
    "-": [60, 20],
    "+": [60, 20],
    "=": [60, 20],
    "/": [60, 20],
    "%": [40, 40],
    "&": [40, 40],
    "(": [10, 10],
    ")": [10, 10],
    "[": [10, 10],
    "]": [10, 10]
}
descenders_shift = {
    "g": 500,
    "j": 600,
    "p": 500,
    "q": 600,
    "y": 500,
    "f": 400,
    "з": 300,
    "р": 200,
    "у": 300,
    "ф": 300,
    "д": 300,
    "щ": 100,
    "ц": 100,
}
# the quick brown fox jumps over the lazy dog

def create_font_from_images(image_folder, output_font_path):
    # Create a new font
    font = fontforge.font()
    font.fontname = "handwriting"
    font.fullname = "Custom Handwriting Font"
    font.familyname = "CustomHandwriting"
    font.encoding = "UnicodeFull"


    # Loop over image files in the image folder
    for image_file in os.listdir(image_folder):
        if image_file.endswith(".svg"):
            file_name = os.path.splitext(image_file)[0]
            letter_index = int(file_name.split("_")[-1])
            if letter_index >= len(alphabet):
                continue

            char_name = alphabet[letter_index]

            # Skip files not matching a valid character
            if len(char_name) != 1:
                continue

            # Create a new glyph for the character
            glyph = font.createChar(ord(char_name), char_name)

            # Import the PNG image as a glyph outline
            glyph.importOutlines(os.path.join(image_folder, image_file), scale=False)

            glyph.left_side_bearing = bearing_table.get(char_name, (2, 2))[0]
            glyph.right_side_bearing = bearing_table.get(char_name, (2, 2))[1]

            glyph.transform([6, 0, 0, 6, 0, 0])

            # Move glyph to align with the baseline
            x_min, y_min, x_max, y_max = glyph.boundingBox()
            y_min = y_min + descenders_shift.get(char_name, 0)
            glyph.transform([1, 0, 0, 1, 0, -y_min])


    # Generate the font file (TTF or OTF)
    font.generate(output_font_path)
    print(f"Font created successfully and saved to {output_font_path}")

if __name__ == "__main__":
    create_font_from_images("result", "custom_handwriting.ttf")
