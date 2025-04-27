LIGHT_MODE_COLORS = [
    (40, 40, 80),     # Dark blue
    (70, 30, 70),     # Dark purple
    (80, 40, 40),     # Dark red
    (30, 70, 50),     # Dark green
    (60, 50, 20),     # Dark brown
    (20, 60, 90),     # Navy blue
    (80, 30, 60),     # Dark magenta
    (50, 50, 60),     # Dark slate
    (70, 50, 10),     # Dark gold
    (30, 50, 70)     # Dark teal
]

DARK_MODE_COLORS = [
    (255, 204, 153),  # Peach
    (153, 255, 204),  # Mint
    (204, 153, 255),  # Lavender
    (255, 255, 153),  # Light yellow
    (153, 204, 255),  # Sky blue
    (255, 179, 102),  # Orange
    (204, 102, 255),  # Purple
    (255, 215, 0),    # Gold
    (0, 204, 204),    # Teal
    (255, 182, 193)   # Pink
]

def get_box_palette(index, theme):
    if theme == 'dark':
        bg = DARK_MODE_COLORS[index % 10]
        text = (0, 0, 0)
    else:
        bg = LIGHT_MODE_COLORS[index % 10]
        text = (255, 255, 255)
    return bg, text
