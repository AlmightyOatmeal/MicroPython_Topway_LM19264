from topway import LM19264


lcd = LM19264(
    db0=8, db1=7, db2=6, db3=5, db4=4, db5=3, db6=2, db7=1,  # DB7–DB0
    e=9, rw=10, rs=11, csa=13, csb=12, rstb=14
)

lcd.initialize()

width = 192
height = 64
bitmap = [[0 for _ in range(width)] for _ in range(height)]

# Display box outline
bitmap = lcd.draw_graphic_box(bitmap=bitmap, x=0, y=0, width=30, height=10)
# Display filled-in box
bitmap = lcd.draw_graphic_box(bitmap=bitmap, x=35, y=0, width=30, height=10, fill=True)
# Display box with rounded corners
bitmap = lcd.draw_graphic_box(bitmap=bitmap, x=10, y=15, width=30, height=20, radius=5)
# Display filled-in box with rounded corners
bitmap = lcd.draw_graphic_box(bitmap=bitmap, x=55, y=15, width=30, height=20, radius=10, fill=True)

packed = lcd.pack_bitmap(bitmap=bitmap)

lcd.display_bitmap(bitmap=packed)

