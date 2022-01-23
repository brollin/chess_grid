import subprocess
from talon import Module, Context, canvas, ui, ctrl, screen
from talon.skia import Paint, Rect, Image
from talon.types.point import Point2d
import time
import typing
import cv2
import numpy as np

mod = Module()

mod.tag("chess_grid_showing", desc="Tag indicates whether the chess grid is showing")
ctx = Context()

files = ["a", "b", "c", "d", "e", "f", "g", "h"]
ranks = ["1", "2", "3", "4", "5", "6", "7", "8"]

default_position = [
    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
    ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
]


class ChessGrid:
    def __init__(self):
        self.screen = None
        self.rect = None
        self.board_size = 0
        self.square_size = 0
        self.flipped = False
        self.show_text = True
        self.mcanvas = None
        self.active = False
        self.visible = False

    def setup(self, *, rect: ui.Rect = None):
        screens = ui.screens()
        screen = screens[0]  # TODO: multiple screen support
        self.screen = screen

        if rect is not None:
            self.rect = rect
            self.board_size = rect.height
            self.square_size = self.board_size // 8

        if self.mcanvas is None:
            self.mcanvas = canvas.Canvas.from_screen(screen)
        else:
            self.mcanvas.unregister("draw", self.draw)
        # self.mcanvas.register("draw", self.draw)
        # self.mcanvas.freeze()
        # self.visible = True
        self.active = True

    def show(self):
        if self.visible:
            return
        self.mcanvas.register("draw", self.draw)
        self.mcanvas.freeze()
        self.visible = True

    def hide(self):
        if not self.visible:
            return
        self.mcanvas.unregister("draw", self.draw)
        self.visible = False

    def close(self):
        if not self.active:
            return
        self.mcanvas.unregister("draw", self.draw)
        self.mcanvas.close()
        self.mcanvas = None
        self.visible = False
        self.active = False

    def draw(self, canvas):
        paint = canvas.paint

        def draw_grid():
            for i in range(9):
                canvas.draw_line(
                    self.rect.x + i * self.square_size,
                    self.rect.y,
                    self.rect.x + i * self.square_size,
                    self.rect.y + 8 * self.square_size,
                )
                canvas.draw_line(
                    self.rect.x,
                    self.rect.y + i * self.square_size,
                    self.rect.x + 8 * self.square_size,
                    self.rect.y + i * self.square_size,
                )

        grid_stroke = 1

        def draw_text():
            canvas.paint.text_align = canvas.paint.TextAlign.CENTER
            for row in range(8):
                for col in range(8):
                    text_string = ""
                    if self.flipped:
                        text_string = chr(104 - col) + f"{row + 1}"
                    else:
                        text_string = chr(97 + col) + f"{8 - row}"
                    text_rect = canvas.paint.measure_text(text_string)[1]
                    background_rect = text_rect.copy()
                    background_rect.center = Point2d(
                        self.rect.x + self.square_size * 3 / 4 + col * self.square_size,
                        self.rect.y + self.square_size * 3 / 4 + row * self.square_size,
                    )
                    background_rect = background_rect.inset(-4)
                    paint.color = "999999bf"
                    paint.style = Paint.Style.FILL
                    canvas.draw_rect(background_rect)
                    paint.color = "ffff00ff"
                    canvas.draw_text(
                        text_string,
                        self.rect.x + self.square_size * 3 / 4 + col * self.square_size,
                        self.rect.y + self.square_size * 3 / 4 + row * self.square_size + text_rect.height / 2,
                    )

        paint.stroke_width = grid_stroke
        paint.color = "ff0000ff"
        draw_grid()

        paint.textsize = 16
        if self.show_text:
            draw_text()

    def flip_board(self, orientation: str):
        if orientation == "":
            self.flipped = not self.flipped
        elif orientation == "white":
            self.flipped = False
        elif orientation == "black":
            self.flipped = True
        else:
            return

        if self.visible and self.show_text:
            self.setup()

    def toggle_text(self):
        if not self.visible:
            self.show_text = True
        else:
            self.show_text = not self.show_text
        self.setup()


cg = ChessGrid()


@mod.action_class
class ChessGridActions:
    def chess_grid_activate():
        """Searches for a chessboard on the screen and overlays the grid on it"""
        def find_chessboard():
            if cg.active:
                cg.close()
                ctx.tags = []

            window_rect = ui.active_window().rect
            img = screen.capture_rect(window_rect)

            imgUmat = np.array(img)
            gray = cv2.cvtColor(imgUmat, cv2.COLOR_BGR2GRAY)
            ret, thresh = cv2.threshold(gray, 215, 255, cv2.THRESH_BINARY)
            # Image.from_array(thresh).write_file('/tmp/threshold.jpg')
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for c in contours:
                (x, y, w, h) = cv2.boundingRect(c)
                if (w >= 400 and w < 1000) and (h > 400 and h < 1000) and (abs(w - h) < 40):
                    # crop_img = imgUmat[y:y+h, x:x+w]
                    # Image.from_array(crop_img).write_file('/tmp/contour.jpg')

                    board_size = min(w, h)
                    centered_x = window_rect.x + x + (w - board_size) / 2
                    centered_y = window_rect.y + y + (h - board_size) / 2
                    return ui.Rect(centered_x, centered_y, board_size, board_size)

            return None

        rect = find_chessboard()
        if rect is None:
            # TODO: give the user some indication that no board was found
            print("no chessboard found")
            return

        cg.setup(rect=rect)
        ctx.tags = ["user.chess_grid_showing"]

    def chess_grid_show():
        """Show the grid"""
        cg.show()

    def chess_grid_hide():
        """Hide the grid while remaining activated"""
        cg.hide()

    def chess_grid_close():
        """Close the active grid"""
        ctx.tags = []
        cg.close()

    def chess_grid_click_square(coordinates: typing.List[str]):
        """Click a square or squares on the chessboard"""
        if len(coordinates) not in [2, 4]:
            return
        if not coordinates[0] in files \
            or not coordinates[1] in ranks \
            or len(coordinates) == 4 and \
            (not coordinates[2] in files
             or not coordinates[3] in ranks):
            return

        def coordinate_to_position(coordinate: typing.List[str]):
            row = 8 - int(coordinate[1])
            column = files.index(coordinate[0])
            if cg.flipped:
                row = 7 - row
                column = 7 - column

            x = cg.rect.x + column * cg.square_size + cg.square_size // 2
            y = cg.rect.y + row * cg.square_size + cg.square_size // 2
            return (x, y)

        def click_position(x: int, y: int):
            ctrl.mouse_move(x, y)
            ctrl.mouse_click(button=0, down=True)
            time.sleep(0.1)
            ctrl.mouse_click(button=0, up=True)

        click_position(*coordinate_to_position(coordinates))
        if len(coordinates) == 4:
            click_position(*coordinate_to_position(coordinates[2:]))

    def chess_grid_flip_board(orientation: str):
        """Flips the orientation of the board"""
        cg.flip_board(orientation)

    def chess_grid_toggle_text():
        """Toggles whether the text is shown"""
        cg.toggle_text()

    def chess_testing():
        """Testing"""
        ChessGridActions.chess_grid_activate()
        img = screen.capture_rect(cg.rect)

        imgUmat = np.array(img)
        gray = cv2.cvtColor(imgUmat, cv2.COLOR_BGR2GRAY)
        ret, whiteness_thresh = cv2.threshold(gray, 215, 255, cv2.THRESH_BINARY)
        Image.from_array(whiteness_thresh).write_file('/tmp/findwhite.jpg')
        subprocess.run(("open", "/tmp/findwhite.jpg"))

        ret, blackness_thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)
        Image.from_array(blackness_thresh).write_file('/tmp/findblack.jpg')
        subprocess.run(("open", "/tmp/findblack.jpg"))

        def mse(imageA, imageB):
            # the 'Mean Squared Error' between the two images is the
            # sum of the squared difference between the two images;
            # NOTE: the two images must have the same dimension
            err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
            err /= float(imageA.shape[0] * imageA.shape[1])

            # return the MSE, the lower the error, the more "similar"
            # the two images are
            return err

        square_size = int(len(gray[0]) / 8)
        board = [["_"] * 8 for _ in range(8)]
        piece_set = {}
        for row in range(8):
            for column in range(8):
                square = np.asarray(blackness_thresh[row * square_size:(row + 1)
                                    * square_size, column * square_size:(column + 1) * square_size])
                blackness = 1 - np.sum(square) / square.size / 255.0
                if blackness > 0.2:
                    board[row][column] = "B"
                    if default_position[row][column].startswith("b"):
                        piece_set[default_position[row][column]] = square

                square = np.asarray(whiteness_thresh[row * square_size:(row + 1)
                                    * square_size, column * square_size:(column + 1) * square_size])
                whiteness = np.sum(square) / square.size / 255.0
                if whiteness > 0.1:
                    board[row][column] = "W"
                    if default_position[row][column].startswith("w"):
                        piece_set[default_position[row][column]] = square
        print('\n' + '\n'.join([''.join(row) for row in board]))

        print("check for accuracy")
        for row in range(8):
            for column in range(8):
                square = np.asarray(blackness_thresh[row * square_size:(row + 1)
                                    * square_size, column * square_size:(column + 1) * square_size])
                blackness = 1 - np.sum(square) / square.size / 255.0
                if blackness > 0.2:
                    for p in ["bP", "bN", "bB", "bR", "bK", "bQ"]:
                        if mse(piece_set[p], square) < 1000:
                            board[row][column] = p
                square = np.asarray(whiteness_thresh[row * square_size:(row + 1)
                                    * square_size, column * square_size:(column + 1) * square_size])
                whiteness = np.sum(square) / square.size / 255.0
                if whiteness > 0.1:
                    for p in ["wP", "wN", "wB", "wR", "wK", "wQ"]:
                        if mse(piece_set[p], square) < 2000:
                            board[row][column] = p
        print('\n' + '\n'.join(['\t'.join(row) for row in board]))
