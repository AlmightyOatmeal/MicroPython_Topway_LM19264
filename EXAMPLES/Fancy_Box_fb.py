from topway.LM19264framebuf import LM19264
from topway.font import Aclonica_size12 as font12


lcd = LM19264(
    db0=8, db1=7, db2=6, db3=5, db4=4, db5=3, db6=2, db7=1,  # DB7–DB0
    e=9, rw=10, rs=11, csa=13, csb=12, rstb=14
)

lcd.initialize()

left_indent = 14
text = "Foxy Boxy"

# Iterate over each character in the formatted string and call the font's `get_ch()` function to get a tuple
# that contains the character's width
empty_width = sum([r[2] + 1 for r in [font12.get_ch(c) for c in text]]) + 4
print(f'[DEBUG] empty characters pixel width: {empty_width}')

# Outside box
lcd.line(0, 0, left_indent, 0, 1)  # Top left horizontal
lcd.line(left_indent + empty_width + 1, 0, lcd.width - 1, 0, 1)  # Top right horizontal
lcd.line(0, 1, 0, lcd.height - 1, 1)  # Left vertical
lcd.line(lcd.width - 1, 0, lcd.width - 1, lcd.height - 1, 1)  # Right vertical
lcd.line(0, lcd.height - 1, lcd.width - 1, lcd.height - 1, 1)  # Bottom horizontal

# inner 1
lcd.line(2, 2, left_indent, 2, 1)  # Top left horizontal
lcd.line(left_indent + empty_width + 1, 2, lcd.width - 3, 2, 1)  # Top right horizontal
lcd.line(2, 3, 2, lcd.height - 3, 1)  # Left vertical
lcd.line(lcd.width - 3, 2, lcd.width - 3, lcd.height - 3, 1)  # Right vertical
lcd.line(2, lcd.height - 3, lcd.width - 3, lcd.height - 3, 1)  # Bottom horizontal

# inner 2
lcd.line(4, 4, left_indent, 4, 1)  # Top left horizontal
lcd.line(left_indent + empty_width + 1, 4, lcd.width - 5, 4, 1)  # Top right horizontal
lcd.line(4, 5, 4, lcd.height - 5, 1)  # Left vertical
lcd.line(lcd.width - 5, 4, lcd.width - 5, lcd.height - 5, 1)  # Right vertical
lcd.line(4, lcd.height - 5, lcd.width - 5, lcd.height - 5, 1)  # Bottom horizontal

# inner 3
lcd.line(6, 6, left_indent, 6, 1)  # Top left horizontal
lcd.line(left_indent + empty_width + 1, 6, lcd.width - 7, 6, 1)  # Top right horizontal
lcd.line(6, 7, 6, lcd.height - 7, 1)  # Left vertical
lcd.line(lcd.width - 7, 6, lcd.width - 7, lcd.height - 7, 1)  # Right vertical
lcd.line(6, lcd.height - 7, lcd.width - 7, lcd.height - 7, 1)  # Bottom horizontal

# Vert bars
lcd.line(left_indent, 0, left_indent, 6, 1)  # Top left pipe
lcd.line(left_indent + empty_width + 1, 0, left_indent + empty_width + 1, 6, 1)   # Top right pipe

lcd.draw_text(text=text, x=left_indent + 3, y=0, font_map=font12)

lcd.display()
