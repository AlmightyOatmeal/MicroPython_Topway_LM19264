from framebuf import FrameBuffer, MONO_VLSB
from machine import Pin
import micropython
import math
import time


def timed_function(f, *args, **kwargs):
    myname = str(f).split(' ')[1]

    def new_func(*args, **kwargs):
        t = time.ticks_us()
        result = f(*args, **kwargs)
        delta = time.ticks_diff(time.ticks_us(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
        return result

    return new_func


# noinspection GrazieInspection
class LM19264(FrameBuffer):
    width = 192
    height = 64

    def __init__(self, db0: int | Pin, db1: int | Pin, db2: int | Pin, db3: int | Pin, db4: int | Pin, db5: int | Pin,
                 db6: int | Pin, db7: int | Pin, rs: int | Pin, rw: int | Pin, e: int | Pin, rstb: int | Pin,
                 csa: int | Pin, csb: int | Pin, debug: bool = False):
        """
        Driver for LM19264 192x64 LCD with framebuffer.

        :param db0: GPIO pin for DB0.
        :type db0: int | Pin
        :param db1: GPIO pin for DB1.
        :type db1: int | Pin
        :param db2: GPIO pin for DB2.
        :type db2: int | Pin
        :param db3: GPIO pin for DB3.
        :type db3: int | Pin
        :param db4: GPIO pin for DB4.
        :type db4: int | Pin
        :param db5: GPIO pin for DB5.
        :type db5: int | Pin
        :param db6: GPIO pin for DB6.
        :type db6: int | Pin
        :param db7: GPIO pin for DB7.
        :type db7: int | Pin
        :param rs: GPIO pin for RS (Register Select).
        :type rs: int | Pin
        :param rw: GPIO pin for RW (Read/Write).
        :type rw: int | Pin
        :param e: GPIO pin for E (Enable).
        :type e: int | Pin
        :param rstb: GPIO pin for RSTB (Reset).
        :type rstb: int | Pin
        :param csa: GPIO pin for CSA (Chip Select A).
        :type csa: int | Pin
        :param csb: GPIO pin for CSB (Chip Select B).
        :type csb: int | Pin
        :param debug: True to enable debug output.
        :type debug: bool
        """
        self.db0 = Pin(db0, Pin.OUT) if not isinstance(db0, Pin) else db0
        self.db1 = Pin(db1, Pin.OUT) if not isinstance(db1, Pin) else db1
        self.db2 = Pin(db2, Pin.OUT) if not isinstance(db2, Pin) else db2
        self.db3 = Pin(db3, Pin.OUT) if not isinstance(db3, Pin) else db3
        self.db4 = Pin(db4, Pin.OUT) if not isinstance(db4, Pin) else db4
        self.db5 = Pin(db5, Pin.OUT) if not isinstance(db5, Pin) else db5
        self.db6 = Pin(db6, Pin.OUT) if not isinstance(db6, Pin) else db6
        self.db7 = Pin(db7, Pin.OUT) if not isinstance(db7, Pin) else db7

        self.rs = Pin(rs, Pin.OUT) if not isinstance(rs, Pin) else rs
        self.rw = Pin(rw, Pin.OUT) if not isinstance(rw, Pin) else rw
        self.e = Pin(e, Pin.OUT) if not isinstance(e, Pin) else e
        self.rstb = Pin(rstb, Pin.OUT) if not isinstance(rstb, Pin) else rstb
        self.csa = Pin(csa, Pin.OUT) if not isinstance(csa, Pin) else csa
        self.csb = Pin(csb, Pin.OUT) if not isinstance(csb, Pin) else csb

        self.debug = debug

        self.buffer = bytearray(192 * 64 // 8)  # 1536 bytes
        super().__init__(self.buffer, 192, 64, MONO_VLSB)

        self.init_pins()
        self.do_reset()
        self.initialize()

    @micropython.native
    def init_pins(self) -> None:
        """Initialize all control and data pins to default states."""
        self.db0.off()
        self.db1.off()
        self.db2.off()
        self.db3.off()
        self.db4.off()
        self.db5.off()
        self.db6.off()
        self.db7.off()

        self.rs.off()
        self.rw.off()
        self.e.off()

        self.rstb.on()

        self.csa.off()
        self.csb.off()

    @micropython.native
    def pulse_e(self) -> None:
        """Generate a valid Enable (E) pulse to latch data/command."""
        self.e.on()
        # time.sleep_us(1)
        self.e.off()
        # time.sleep_us(1)

    @micropython.native
    def send_bytes(self, value: int, is_command: bool = False) -> None:
        """
        Write a command byte to the LCD controller.

        :param value: 8-bit command value.
        :type value: int
        :param is_command: True to send as command, False to send as data.
        :type is_command: bool
        """
        if is_command:
            self.rs.off()
            self.rw.off()
        else:
            self.rs.on()
            self.rw.off()

        # Set the pins to the bit value using bit shifting
        self.db0.value((value >> 0) & 1)
        self.db1.value((value >> 1) & 1)
        self.db2.value((value >> 2) & 1)
        self.db3.value((value >> 3) & 1)
        self.db4.value((value >> 4) & 1)
        self.db5.value((value >> 5) & 1)
        self.db6.value((value >> 6) & 1)
        self.db7.value((value >> 7) & 1)

        # Pulse `e`
        self.e.on()
        self.e.off()
        # self.pulse_e()

    @micropython.native
    def read_data(self) -> int:
        self.rs.on()  # RS = 1 (data)
        self.rw.on()  # RW = 1 (read)
        self.e.on()  # Pulse E high
        time.sleep_us(1)

        value = 0
        if self.db0.value():
            value |= 1 << 0
        if self.db1.value():
            value |= 1 << 1
        if self.db2.value():
            value |= 1 << 2
        if self.db3.value():
            value |= 1 << 3
        if self.db4.value():
            value |= 1 << 4
        if self.db5.value():
            value |= 1 << 5
        if self.db6.value():
            value |= 1 << 6
        if self.db7.value():
            value |= 1 << 7

        self.e.off()  # Pulse E low
        return value

    @micropython.native
    def set_db_outputs(self) -> None:
        """Configure DB0–DB7 pins as outputs (for writing commands/data)."""
        self.db0.init(Pin.OUT)
        self.db1.init(Pin.OUT)
        self.db2.init(Pin.OUT)
        self.db3.init(Pin.OUT)
        self.db4.init(Pin.OUT)
        self.db5.init(Pin.OUT)
        self.db6.init(Pin.OUT)
        self.db7.init(Pin.OUT)

    @micropython.native
    def set_db_inputs(self) -> None:
        """Configure DB0–DB7 pins as inputs (for reading data)."""
        self.db0.init(Pin.IN, Pin.PULL_DOWN)
        self.db1.init(Pin.IN, Pin.PULL_DOWN)
        self.db2.init(Pin.IN, Pin.PULL_DOWN)
        self.db3.init(Pin.IN, Pin.PULL_DOWN)
        self.db4.init(Pin.IN, Pin.PULL_DOWN)
        self.db5.init(Pin.IN, Pin.PULL_DOWN)
        self.db6.init(Pin.IN, Pin.PULL_DOWN)
        self.db7.init(Pin.IN, Pin.PULL_DOWN)

    @micropython.native
    def read_display_to_bitmap(self) -> list[list[int]]:
        """Reads the entire display memory (CSA, CSB, CSC) and updates the provided 2D bitmap array."""
        bitmap = [[0 for _ in range(self.width)] for _ in range(self.height)]

        for page in range(8):  # 8 pages of 8 pixels each = 64 rows
            for chip, x_base in ((0, 0), (1, 64), (2, 128)):  # CSA, CSB, CSC
                self.do_select_chip(chip)

                self.set_db_outputs()

                self.send_command(0xB8 | page)  # Set page address
                self.send_command(0x40)  # Set column address to 0

                self.set_db_inputs()
                _ = self.read_data()  # Dummy read (discard), per the datasheet

                for col in range(self.height):
                    data = self.read_data()
                    x = x_base + col
                    for bit in range(8):
                        y = page * 8 + bit
                        if 0 <= x < self.width and 0 <= y < self.height:
                            bitmap[y][x] = (data >> bit) & 1

        # Restore DB lines to outputs for normal driver operation
        self.set_db_outputs()
        return bitmap

    @micropython.native
    def send_command(self, value: int) -> None:
        """
        Write a command byte to the LCD controller.

        :param value: 8-bit command value.
        :type value: int
        """
        self.send_bytes(value=value, is_command=True)

    @micropython.native
    def send_data(self, value: int) -> None:
        """
        Write a data byte to the LCD display RAM.

        :param value: 8-bit data value.
        :type value: int
        """
        self.send_bytes(value=value, is_command=False)

    @micropython.native
    def read_status(self, region: int) -> dict:
        """
        Read the status byte from a specific chip region.

        :param region: Region index (0 = left, 1 = middle, 2 = right).
        :type region: int
        :return: Dictionary with raw byte and decoded flags.
        :rtype: dict
        """
        self.do_select_chip(region)
        self.rs.off()
        self.rw.on()

        # Change the output pins to input
        self.db0.init(Pin.IN, Pin.PULL_DOWN)
        self.db1.init(Pin.IN, Pin.PULL_DOWN)
        self.db2.init(Pin.IN, Pin.PULL_DOWN)
        self.db3.init(Pin.IN, Pin.PULL_DOWN)
        self.db4.init(Pin.IN, Pin.PULL_DOWN)
        self.db5.init(Pin.IN, Pin.PULL_DOWN)
        self.db6.init(Pin.IN, Pin.PULL_DOWN)
        self.db7.init(Pin.IN, Pin.PULL_DOWN)
        time.sleep_us(1)

        self.e.on()
        time.sleep_us(2)

        # Read the values from each pin and bit shift
        value = 0
        if self.db0.value():
            value |= (1 << 0)
        if self.db1.value():
            value |= (1 << 1)
        if self.db2.value():
            value |= (1 << 2)
        if self.db3.value():
            value |= (1 << 3)
        if self.db4.value():
            value |= (1 << 4)
        if self.db5.value():
            value |= (1 << 5)
        if self.db6.value():
            value |= (1 << 6)
        if self.db7.value():
            value |= (1 << 7)

        self.e.off()
        time.sleep_us(2)

        # Change the pins to output again.
        self.db0.init(Pin.OUT)
        self.db1.init(Pin.OUT)
        self.db2.init(Pin.OUT)
        self.db3.init(Pin.OUT)
        self.db4.init(Pin.OUT)
        self.db5.init(Pin.OUT)
        self.db6.init(Pin.OUT)
        self.db7.init(Pin.OUT)

        return {
            "raw": value,
            "busy": bool(value & 0x80),
            "display_on": not bool(value & 0x40),
            "reset": bool(value & 0x10)
        }

    @micropython.native
    def do_reset(self) -> None:
        """Perform hardware reset using RSTB pin."""
        self.rstb.off()
        time.sleep_ms(5)
        self.rstb.on()
        time.sleep_ms(5)

    @micropython.native
    def do_select_chip(self, region: int) -> None:
        """
        Select one of the three chip regions.

        :param region: Region index (0 = left, 1 = middle, 2 = right).
        :type region: int
        """
        self.csa.off()
        self.csb.off()
        # time.sleep_us(1)
        cs_map = [(0, 0), (1, 0), (0, 1)]
        self.csa.value(cs_map[region][0])
        self.csb.value(cs_map[region][1])
        # time.sleep_us(1)

    @micropython.native
    def do_clear_display(self) -> None:
        """Clear all bitmap across all regions and pages."""
        self.fill(0)
        self.display()

    @micropython.native
    def set_display_on(self, region: int, on: bool = True) -> None:
        """
        Turn display on or off for a specific region.

        :param region: Region index (0 = left, 1 = middle, 2 = right).
        :type region: int
        :param on: True to turn on, False to turn off.
        :type on: bool
        """
        self.do_select_chip(region=region)
        self.send_command(value=0x3F if on else 0x3E)

    @micropython.native
    def set_start_line(self, region: int, line: int) -> None:
        """
        Set the display start line (Z address).

        :param region: Region index (0 = left, 1 = middle, 2 = right).
        :type region: int
        :param line: Line number (0–63).
        :type line: int
        """
        self.do_select_chip(region)
        self.send_command(0xC0 | (line & 0x3F))

    @micropython.native
    def set_page(self, page: int) -> None:
        """
        Set the page (X address) for display RAM access.

        :param page: Page number (0–7).
        :type page: int
        """
        self.send_command(0xB8 | (page & 0x07))

    @micropython.native
    def set_column(self, col: int) -> None:
        """
        Set the column (Y address) for display RAM access.

        :param col: Column number (0–63).
        :type col: int
        """
        self.send_command(0x40 | (col & 0x3F))

    @micropython.native
    def initialize(self) -> None:
        """Initialize all regions: display ON and start line = 0."""
        for region in range(3):
            self.set_display_on(region=region, on=True)
            self.set_start_line(region=region, line=0)

    @micropython.native
    def display(self) -> None:
        """Send framebuffer content to the LCD."""
        for page in range(8):
            for region in range(3):
                self.do_select_chip(region)
                self.set_page(page)
                for col in range(64):
                    index = (region * 64) + col + (page * 192)
                    self.set_column(col)
                    self.send_data(self.buffer[index])

    @micropython.native
    def draw_text(self, text: str, x: int, y: int, font_map: object, spacing: int = 1, invert: bool = False) -> None:
        """
        Render a string of text onto the frame buffer.

        :param text: String to render.
        :type text: str
        :param x: Horizontal pixel offset (starting column).
        :type x: int
        :param y: Vertical pixel offset (starting row).
        :type y: int
        :param font_map: Font module with `get_ch(char)` function.
        :type font_map: object
        :param spacing: Horizontal space between characters (default: 1).
        :type spacing: int
        :param invert: If True, invert glyph pixels (1 → 0, 0 → 1).
        :type invert: bool
        """
        for char in text:
            # Retrieve glyph data for the character
            glyph, glyph_height, glyph_width = font_map.get_ch(char)
            if glyph is None:
                x += spacing  # Skip unknown characters
                continue

            # Each column may span multiple bytes depending on glyph height
            bytes_per_column = (glyph_height + 7) // 8  # Round up to the nearest byte

            # Iterate over each column in the glyph
            for col in range(glyph_width):
                # For each row in the glyph height
                for row in range(glyph_height):
                    # Determine which byte contains the bit for this row
                    byte_index = col * bytes_per_column + (row // 8)
                    bit_index = row % 8  # Bit position within the byte

                    # Safety check: avoid out-of-bounds access
                    if byte_index >= len(glyph):
                        continue

                    # Check if the bit is set (i.e., pixel should be drawn)
                    bit_set = glyph[byte_index] & (1 << bit_index)

                    # Compute final pixel coordinates
                    bx = x + col  # Horizontal position on bitmap
                    by = y + row  # Vertical position on bitmap

                    # Bounds check before writing to bitmap
                    if 0 <= by < self.height and 0 <= bx < self.width:
                        if invert:
                            # Inverted mode
                            self.pixel(bx, by, 0 if bit_set else 1)
                        else:
                            # Normal mode
                            if bit_set:
                                self.pixel(bx, by, 1)

            # Advance x position for next character
            x += glyph_width + spacing

    @micropython.native
    def draw_graphic_lines(self, lines: list | tuple[list | tuple[int]]) -> None:
        """
        Draws lines based on [x, y, angle_deg, length] specs directly onto the internal framebuffer.

        This method takes a list of lines, where each line is defined by its starting coordinates, angle (measured
        counter-clockwise from the positive x-axis), and length.

        * - **IMPORTANT:**
        * - Degrees are measured counter-clockwise from the positive x-axis. This means 90 degrees from left to right is actually 0 and 180 degrees top to bottom is actually 270.

        :param lines: A list or tuple of lines, each defined as [x0, y0, angle_deg, length].
        :type lines: list | tuple
        """
        for x0, y0, angle_deg, length in lines:
            angle_rad = math.radians(angle_deg)
            dx = math.cos(angle_rad)
            dy = -math.sin(angle_rad)  # negative because y increases downward

            for i in range(length):
                x = int(round(x0 + dx * i))
                y = int(round(y0 + dy * i))
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.pixel(x, y, 1)

    @micropython.native
    def draw_graphic_circle(self, cx: int, cy: int, radius: int) -> None:
        """
        Draw a circle on the internal framebuffer using the midpoint circle algorithm.

        :param cx: Integer coordinate for the x-center of the circle.
        :type cx: int
        :param cy: Integer coordinate for the y-center of the circle.
        :type cy: int
        :param radius: Radius of the circle, specified as an integer.
        :type radius: int
        """
        x = radius
        y = 0
        d = 1 - radius

        def plot(px, py):
            if 0 <= px < self.width and 0 <= py < self.height:
                self.pixel(px, py, 1)

        while x >= y:
            # Plot all 8 symmetrical points around the center
            plot(cx + x, cy + y)
            plot(cx + y, cy + x)
            plot(cx - y, cy + x)
            plot(cx - x, cy + y)
            plot(cx - x, cy - y)
            plot(cx - y, cy - x)
            plot(cx + y, cy - x)
            plot(cx + x, cy - y)

            y += 1
            if d < 0:
                d += 2 * y + 1
            else:
                x -= 1
                d += 2 * (y - x) + 1

    @micropython.native
    def draw_graphic_circle_filled(self, cx: int, cy: int, radius: int) -> None:
        """
        Draw a filled circle on the internal framebuffer using the midpoint circle algorithm.

        This method modifies the given bitmap to draw a circle centered at the specified coordinates (x, y) with the
        specified radius. The algorithm calculates the circle's points for only one octant and uses symmetry to
        replicate the points across the other octants. The algorithm takes into account the constraints of the
        display dimensions (width and height) to ensure that the circle does not exceed the bitmap's boundaries.

        :param cx: Integer coordinate for the x-center of the circle.
        :type cx: int
        :param cy: Integer coordinate for the y-center of the circle.
        :type cy: int
        :param radius: Radius of the circle, specified as an integer.
        :type radius: int
        """
        x = radius
        y = 0
        d = 1 - radius

        def draw_span(y_offset: int, x_left: int, x_right: int):
            """
            Draws a horizontal span at a specified vertical offset relative to a central point
            with defined left and right horizontal lengths.

            :param y_offset: Vertical offset, relative to the center `cy`, where the span should be drawn.
            :type y_offset: int
            :param x_left: Number of pixels to extend to the left of the center `cx`.
            :type x_left: int
            :param x_right: Number of pixels to extend to the right of the center `cx`.
            :type x_right: int
            """
            y_pos = cy + y_offset
            if 0 <= y_pos < self.height:  # Check vertical bounds
                for x_pos in range(cx - x_left, cx + x_right + 1):
                    if 0 <= x_pos < self.width:  # Check horizontal bounds
                        self.pixel(x_pos, y_pos, 1)  # Set pixel ON

        # Loop through each vertical slice of the circle
        while x >= y:
            # Draw horizontal spans for each symmetrical row
            draw_span(+y, x, x)  # Top half
            draw_span(-y, x, x)  # Bottom half
            draw_span(+x, y, y)  # Right half
            draw_span(-x, y, y)  # Left half

            y += 1  # Move down one row

            # Update the decision variable to determine whether to shrink x
            if d < 0:
                d += 2 * y + 1
            else:
                x -= 1
                d += 2 * (y - x) + 1

    @micropython.native
    def draw_graphic_circles(self, circles: list | tuple[list | tuple[int]]) -> None:
        """
        Draw one or more circles directly onto the internal framebuffer.

        Each circle is defined as a tuple: (cx, cy, radius, filled).

        :param circles: A list or tuple containing the definitions of circles.
        type circles: list | tuple
        """
        for cx, cy, radius, filled in circles:
            if filled:
                self.draw_graphic_circle_filled(cx, cy, radius)
            else:
                self.draw_graphic_circle(cx, cy, radius)

    @micropython.native
    def draw_graphic_box(self, x: int, y: int, width: int, height: int, radius: int = 0, fill: bool = False) -> None:
        """
        Draws a box with quarter-circle rounded corners directly onto the internal framebuffer.

        :param x: Top-left x-coordinate.
        :param y: Top-left y-coordinate.
        :param width: Width of the box.
        :param height: Height of the box.
        :param radius: Radius of the rounded corners.
        :param fill: Whether to fill the interior of the box.
        """
        x0 = max(0, min(x, self.width - 1))
        x1 = max(0, min(x + width - 1, self.width - 1))
        y0 = max(0, min(y, self.height - 1))
        y1 = max(0, min(y + height - 1, self.height - 1))
        radius = max(1, min(radius, min((x1 - x0) // 2, (y1 - y0) // 2)))

        # Fill interior rectangle (excluding corners)
        if fill:
            for yi in range(y0 + radius, y1 - radius + 1):
                for xi in range(x0 + 1, x1):
                    self.pixel(xi, yi, 1)
            for yi in range(y0 + 1, y0 + radius):
                for xi in range(x0 + radius, x1 - radius + 1):
                    self.pixel(xi, yi, 1)
            for yi in range(y1 - radius + 1, y1):
                for xi in range(x0 + radius, x1 - radius + 1):
                    self.pixel(xi, yi, 1)

        # Horizontal edges
        for xi in range(x0 + radius, x1 - radius + 1):
            self.pixel(xi, y0, 1)
            self.pixel(xi, y1, 1)

        # Vertical edges
        for yi in range(y0 + radius, y1 - radius + 1):
            self.pixel(x0, yi, 1)
            self.pixel(x1, yi, 1)

        # Quarter-circle corners
        steps = radius * 2
        for i in range(steps + 1):
            theta = (math.pi / 2) * (i / steps)
            dx = int(round(radius * math.cos(theta)))
            dy = int(round(radius * math.sin(theta)))

            # Top-left
            px = x0 + radius - dx
            py = y0 + radius - dy
            self.pixel(px, py, 1)
            if fill:
                for fy in range(py + 1, y0 + radius):
                    self.pixel(px, fy, 1)

            # Top-right
            px = x1 - radius + dx
            py = y0 + radius - dy
            self.pixel(px, py, 1)
            if fill:
                for fy in range(py + 1, y0 + radius):
                    self.pixel(px, fy, 1)

            # Bottom-left
            px = x0 + radius - dx
            py = y1 - radius + dy
            self.pixel(px, py, 1)
            if fill:
                for fy in range(y1 - radius + 1, py):
                    self.pixel(px, fy, 1)

            # Bottom-right
            px = x1 - radius + dx
            py = y1 - radius + dy
            self.pixel(px, py, 1)
            if fill:
                for fy in range(y1 - radius + 1, py):
                    self.pixel(px, fy, 1)

    @micropython.native
    def draw_bitmap_array(self, bitmap: list[list[int]], x_offset: int = 0, y_offset: int = 0) -> None:
        """
        Draw a 2D bitmap array onto the framebuffer at a given offset.

        :param bitmap: 2D list of rows × columns with binary pixel values (0 or 1).
        :type bitmap: list
        :param x_offset: Horizontal offset where the bitmap should be drawn.
        :type x_offset: int
        :param y_offset: Vertical offset where the bitmap should be drawn.
        :type y_offset: int
        """
        height = len(bitmap)
        width = len(bitmap[0]) if height > 0 else 0

        for row in range(height):
            for col in range(width):
                pixel = bitmap[row][col]
                x = x_offset + col
                y = y_offset + row
                if 0 <= x < width and 0 <= y < height:
                    self.pixel(x, y, pixel)

    # Some legacy logic
    @micropython.native
    def write_pixel_data(self, page: int, col: int, region: int, data: int) -> None:
        """
        Write a single byte to a specific page/column in a region.

        :param page: Page number (0–7).
        :type page: int
        :param col: Column number (0–63).
        :type col: int
        :param region: Region index (0–2).
        :type region: int
        :param data: 8-bit pixel data.
        :type data: int
        """
        self.do_select_chip(region)
        self.set_page(page)
        self.set_column(col)
        self.send_data(data)

    @micropython.native
    def pack_bitmap(self, bitmap: list | tuple[list | tuple[int]]) -> bytearray:
        """
        Pack a 2D pixel array into display-ready format.

        :param bitmap: List of 64 rows, each containing 192 binary pixel values (0 or 1).
        :type bitmap: list
        :return: Bytearray, packed for the display.
        """
        if len(bitmap) != self.height or any(len(row) != self.width for row in bitmap):
            raise ValueError("Input must be 64 rows of 192 columns each.")

        packed = bytearray(self.width * 8)  # 8 pages × 192 columns

        for page in range(8):  # Each page is 8 rows tall
            for col in range(self.width):
                byte = 0
                for bit in range(8):
                    row = page * 8 + bit
                    if bitmap[row][col]:
                        byte |= (1 << bit)
                packed[page * self.width + col] = byte

        return packed

    @micropython.native
    def overlay_bitmap(self, base_bitmap: list | tuple[list | tuple[int]],
                       overlay_bitmap: list | tuple[list | tuple[int]],
                       x: int, y: int, mode: str = "or") -> list | tuple[list | tuple[int]]:
        """
        Overlay a 2D pixel array onto another at a given (x, y) position.

        :param base_bitmap: 2D list of 64 rows × 192 columns (0 or 1), the target display buffer.
        :type base_bitmap: list | tuple
        :param overlay_bitmap: 2D list of rows × columns (0 or 1), the overlay image.
        :type overlay_bitmap: list | tuple
        :param x: Horizontal offset (0–191) where overlay starts.
        :type x: int
        :param y: Vertical offset (0–63) where overlay starts.
        :type y: int
        :param mode: Bitwise mode: "or", "and", "xor", or "replace".
        :type mode: str
        :return: New 2D list of 64×192 bitmap with overlay applied.
        :rtype: list
        """
        height = len(overlay_bitmap)
        width = len(overlay_bitmap[0])

        # Deep copy base to avoid modifying original
        result = [row[:] for row in base_bitmap]

        for row in range(height):
            for col in range(width):
                pixel = overlay_bitmap[row][col]
                target_x = x + col
                target_y = y + row

                if 0 <= target_x < self.width and 0 <= target_y < self.height:
                    if mode == "or":
                        result[target_y][target_x] |= pixel
                    elif mode == "and":
                        result[target_y][target_x] &= pixel
                    elif mode == "xor":
                        result[target_y][target_x] ^= pixel
                    elif mode == "replace":
                        result[target_y][target_x] = pixel
                    else:
                        raise ValueError(f"Unknown mode: {mode}")

        return result

    @micropython.native
    def display_bitmap(self, bitmap: bytearray) -> None:
        """
        Draw a full-screen bitmap to the display.

        :param bitmap: Bytearray of 1536 bytes (192×64 bitmap).
        :type bitmap: bytearray
        """
        if len(bitmap) != self.width * 8:
            raise ValueError(f"Bitmap must be 1536 bytes (192×64 bitmap), received width {len(bitmap)}")

        for page in range(8):
            for region in range(3):
                self.do_select_chip(region)
                self.set_page(page)
                # Iterates columns; sends bitmap data to selected chip
                for col in range(self.height):
                    index = (region * self.height) + col + (page * self.width)
                    self.set_column(col)
                    self.send_data(bitmap[index])
