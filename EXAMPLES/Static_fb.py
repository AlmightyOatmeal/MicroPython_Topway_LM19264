from topway.LM19264framebuf import LM19264
import random
import micropython


@micropython.native
def draw_block_pattern(driver, block_size: int = 1):
    """
    Draw a randomized block pattern directly onto the internal framebuffer.

    Each block is a square of size block_size × block_size filled with either 0 or 1.

    :param block_size: Size of each block in pixels (1, 2, or 4).
    :param width: Width of the drawing area (default: full display width).
    :param height: Height of the drawing area (default: full display height).
    :raises ValueError: If block_size is not one of the valid options.
    """
    if block_size not in [1, 2, 4]:
        raise ValueError("block_size must be 1, 2 or 4")

    block_w = driver.width // block_size
    block_h = driver.height // block_size

    for by in range(block_h):
        for bx in range(block_w):
            bit = random.getrandbits(1)
            for dy in range(block_size):
                for dx in range(block_size):
                    x = bx * block_size + dx
                    y = by * block_size + dy
                    if 0 <= x < driver.width and 0 <= y < driver.height:
                        driver.pixel(x, y, bit)


lcd = LM19264(
    db0=8, db1=7, db2=6, db3=5, db4=4, db5=3, db6=2, db7=1,  # DB7–DB0
    e=9, rw=10, rs=11, csa=13, csb=12, rstb=14
)

lcd.initialize()

block_size = 1
loop = 0
while True:
    random_bytes = draw_block_pattern(driver=lcd, block_size=block_size)
    lcd.display()

    if loop >= 5:
        loop = 0

        if block_size == 1:
            block_size = 2
        elif block_size == 2:
            block_size = 4
        else:
            block_size = 1

    loop += 1
