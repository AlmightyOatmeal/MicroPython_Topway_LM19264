from topway import LM19264
from topway.font import Aclonica_size12 as font12


lcd = LM19264(
    db0=8, db1=7, db2=6, db3=5, db4=4, db5=3, db6=2, db7=1,  # DB7–DB0
    e=9, rw=10, rs=11, csa=13, csb=12, rstb=14
)

lcd.initialize()

# Create blank bitmap
width = 192
height = 64
bitmap = [[0 for _ in range(width)] for _ in range(height)]

left_indent = 14
text = "Foxy Boxy"

start_x = 0
start_y = 0
hor_l_to_r = 0
vert_t_to_b = 270

# Iterate over each character in the formatted string and call the font's `get_ch()` function to get a tuple
# that contains the character's width
empty_width = sum([r[2] + 1 for r in [font12.get_ch(c) for c in text]]) + 4
print(f'[DEBUG] empty characters pixel width: {empty_width}')

# (x, y, angle_deg, length)
# tuples
bitmap = lcd.draw_graphic_lines(bitmap=bitmap, lines=[
    # Outer
    (start_x, start_y, hor_l_to_r, left_indent),                                                     # Top left horizontal
    (left_indent + empty_width + 1, hor_l_to_r, hor_l_to_r, width - 1 - empty_width - left_indent),  # Top right horizontal
    (start_x, 1, vert_t_to_b, height - 2),                                                           # Left vertical
    (width - 1, hor_l_to_r, vert_t_to_b, height),                                                    # Right vertical
    (start_x, height - 1, hor_l_to_r, width),                                                        # Bottom horizontal

    # Inner 1
    (start_x + 2, start_y + 2, hor_l_to_r, left_indent - 2),                                          # Top left horizontal
    (left_indent + empty_width + 1, start_y + 2, hor_l_to_r, width - 3 - empty_width - left_indent),  # Top right horizontal
    (start_x + 2, start_y + 2, vert_t_to_b, height - 6),                                              # Left vertical
    (width - 3, start_y + 2, vert_t_to_b, height - 4),                                                # Right vertical
    (start_x + 2, height - 3, hor_l_to_r, width - 4),                                                 # Bottom horizontal

    # Inner 2
    (start_x + 4, start_y + 4, hor_l_to_r, left_indent - 4),                                          # Top left horizontal
    (left_indent + empty_width + 1, start_y + 4, hor_l_to_r, width - 5 - empty_width - left_indent),  # Top right horizontal
    (start_x + 4, start_y + 4, vert_t_to_b, height - 9),                                              # Left vertical
    (width - 5, start_y + 4, vert_t_to_b, height - 8),                                                # Right vertical
    (start_x + 4, height - 5, hor_l_to_r, width - 8),                                                 # Bottom horizontal

    # Inner 3
    (start_x + 6, start_x + 6, hor_l_to_r, left_indent - 6),                                          # Top left horizontal
    (left_indent + empty_width + 1, start_y + 6, hor_l_to_r, width - 7 - empty_width - left_indent),  # Top right horizontal
    (start_x + 6, start_y + 6, vert_t_to_b, height - 13),                                             # Left vertical
    (width - 7, start_y + 6, vert_t_to_b, height - 12),                                               # Right vertical
    (start_x + 6, height - 7, hor_l_to_r, width - 12),                                                # Bottom horizontal

    (left_indent, start_y, vert_t_to_b, 7),                # Top left pipe
    (left_indent + empty_width + 1, start_y, vert_t_to_b, 7),  # Top right pipe
])


# Move the cursor inside the vertical pipes, make sure there is a 2px buffer
bitmap = lcd.draw_text(bitmap=bitmap, text=text, x=left_indent + 3, y=0, font_map=font12)

packed = lcd.pack_bitmap(bitmap=bitmap)

lcd.display_bitmap(bitmap=packed)

