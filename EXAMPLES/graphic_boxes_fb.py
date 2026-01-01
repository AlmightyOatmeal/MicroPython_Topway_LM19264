from topway.LM19264framebuf import LM19264


lcd = LM19264(
    db0=8, db1=7, db2=6, db3=5, db4=4, db5=3, db6=2, db7=1,  # DB7–DB0
    e=9, rw=10, rs=11, csa=13, csb=12, rstb=14
)

lcd.initialize()

# Display box outline
lcd.draw_graphic_box(x=0, y=0, width=30, height=10)
# Display filled-in box
lcd.draw_graphic_box(x=35, y=0, width=30, height=10, fill=True)
# Display box with rounded corners
lcd.draw_graphic_box(x=10, y=15, width=30, height=20, radius=5)
# Display filled-in box with rounded corners
lcd.draw_graphic_box(x=55, y=15, width=30, height=20, radius=10, fill=True)

lcd.display()
