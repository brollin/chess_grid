from talon import Module, Context, canvas, ui, ctrl, screen
from talon.skia import Paint, Image
from talon.types import point
import chess
import cv2
import numpy as np
import subprocess
import time
import typing

mod = Module()
mod.tag("chess_grid_activated",
        desc="Tag indicates whether the chess grid is showing")
ctx = Context()

files = ["a", "b", "c", "d", "e", "f", "g", "h"]
ranks = ["1", "2", "3", "4", "5", "6", "7", "8"]

# where in the starting position to find each piece
piece_positions = [
    ["r", "n", "b", "q", "k", "", "", ""],
    ["p", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["P", "", "", "", "", "", "", ""],
    ["R", "N", "B", "Q", "K", "", "", ""],
]
flipped_piece_positions = [row[::-1] for row in piece_positions[::-1]]

BLACK = 0.2 # how black are the pieces? may have to adjust
WHITE = 0.08 # how white are the pieces? may have to adjust

BOARD_DARKNESS = 80 # how dark are dark squares? may have to adjust
BOARD_LIGHTNESS = 150 # how light are light squares? may have to adjust

def mse(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


def view_image(image_array, name):
    # open the image (macOS only)
    Image.from_array(image_array).write_file(f"/tmp/{name}.jpg")
    subprocess.run(("open", f"/tmp/{name}.jpg"))


class ChessGrid:
    def __init__(self):
        self.active = False
        self.board = chess.Board()
        self.board_size = 0
        self.flipped = False
        self.mcanvas = None
        self.piece_set = {}
        self.rect = None
        self.screen = None
        self.show_text = True
        self.square_size = 0
        self.visible = False

    def setup(self, *, rect: ui.Rect = None, visible: bool = True):
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

        if visible:
            self.mcanvas.register("draw", self.draw)
            self.mcanvas.freeze()
            self.visible = True
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
                    background_rect.center = point.Point2d(
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
                        self.rect.y + self.square_size * 3 / 4 + row *
                        self.square_size + text_rect.height / 2,
                    )

        paint.stroke_width = 1
        paint.color = "ff0000ff"
        draw_grid()

        paint.textsize = 16
        if self.show_text:
            draw_text()

    def flip_board(self, orientation: str = ""):
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

    def click_squares(self, coordinates: typing.List[str]):
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

    def make_move(self, move: typing.List[str], color: str):
        if self.piece_set is None:
            print("cannot make a move without referencing a board first")
            return

        self.detect_position()

        # it will be white's turn by default, so pass the turn if it should be black's turn
        if color == "black":
            self.board.push(chess.Move.null())

        # process the move into a more proper form of SAN
        move_san = "".join(move)
        move_san = move_san.replace("n", "N").replace("r", "R").replace(
            "q", "Q").replace("k", "K").replace("o", "O")
        # TODO this is not perfect because of the pawn taking case
        if move_san.startswith("b") and len(move_san) == 3:
            move_san = move_san.replace("b", "B", 1)
        # TODO promotion

        try:
            uci_move = self.board.parse_san(move_san).uci()
        except ValueError:
            # try again by passing the turn and attempting the move again
            try:
                self.board.push(chess.Move.null())
                uci_move = self.board.parse_san(move_san).uci()
            except ValueError:
                print("invalid move: " + move_san)
                return
        self.click_squares([char for char in uci_move])

    def find_chessboard(self):
        if self.active:
            self.close()

        # find the chessboard by first applying a threshold filter to the grayscale window
        window_rect = ui.active_window().rect
        img = np.array(screen.capture_rect(window_rect))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 215, 255, cv2.THRESH_BINARY)
        # apply a threshold for the dark mode case
        _, thresh2 = cv2.threshold(gray, 115, 255, cv2.THRESH_BINARY)

        # use a close morphology transform to filter out thin lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 8))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        morph2 = cv2.morphologyEx(thresh2, cv2.MORPH_CLOSE, kernel)

        # now search all of the contours for a large square-ish thing; that is hopefully the board
        contours, _ = cv2.findContours(
            morph, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours2, _ = cv2.findContours(
            morph2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours + contours2:
            (x, y, w, h) = cv2.boundingRect(c)
            if (w >= 270 and w < 1500) and (h > 270 and h < 1500) and (abs(w - h) < 60):
                # crop_img = thresh[y:y+h, x:x+w]

                # find the largest centered square in the rectangle
                board_size = min(w, h)
                centered_x = window_rect.x + x + (w - board_size) / 2
                centered_y = window_rect.y + y + (h - board_size) / 2
                return ui.Rect(centered_x, centered_y, board_size, board_size)

        return None

    def apply_thresholds(self):
        """Return the grayscale and whiteness and blackness thresholds for the board"""
        img = np.array(screen.capture_rect(self.rect))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        _, whiteness_thresh = cv2.threshold(gray, BOARD_LIGHTNESS, 255, cv2.THRESH_BINARY)
        _, blackness_thresh = cv2.threshold(gray, BOARD_DARKNESS, 255, cv2.THRESH_BINARY)

        return (gray, whiteness_thresh, blackness_thresh)

    def reference(self):
        """Assume the chess pieces are in the starting positions and generate a reference piece set"""
        thresholds = self.apply_thresholds()
        (_, whiteness_thresh, blackness_thresh) = thresholds
        square_size = self.square_size
        oriented_piece_positions = flipped_piece_positions if self.flipped else piece_positions
        detection_error = False
        for row in range(8):
            for column in range(8):
                piece = oriented_piece_positions[row][column]
                if piece.islower():
                    potential_black_piece = np.asarray(blackness_thresh[row * square_size:(row + 1)
                                                                        * square_size, column * square_size:(column + 1) * square_size])
                    blackness = 1 - np.sum(potential_black_piece) / \
                        potential_black_piece.size / 255.0
                    if blackness > BLACK:
                        self.piece_set[piece] = potential_black_piece
                        # this square is a black piece so we don't need to check white
                        continue
                    else:
                        print("issue detecting the black " + piece)
                        detection_error = True

                if piece.isupper():
                    potential_white_piece = np.asarray(whiteness_thresh[row * square_size:(row + 1)
                                                                        * square_size, column * square_size:(column + 1) * square_size])
                    whiteness = np.sum(potential_white_piece) / \
                        potential_white_piece.size / 255.0
                    if whiteness > WHITE:
                        self.piece_set[piece] = potential_white_piece
                    else:
                        print("issue detecting the white " + piece)
                        detection_error = True

        if not detection_error:
            self.detect_position(thresholds=thresholds)

    def detect_position(self, *, thresholds=None):
        if self.piece_set is None:
            print("cannot detect position without referencing a board first")
            return

        if thresholds is not None:
            (_, whiteness_thresh, blackness_thresh) = thresholds
        else:
            (_, whiteness_thresh, blackness_thresh) = self.apply_thresholds()

        def row_column_to_square(row, column):
            if self.flipped:
                return chess.parse_square(files[7 - column] + str(row + 1))
            return chess.parse_square(files[column] + str(8 - row))

        self.board.clear()
        square_size = self.square_size
        for row in range(8):
            for column in range(8):
                square = row_column_to_square(row, column)

                # check for a black piece on this square
                potential_black_piece = np.asarray(blackness_thresh[row * square_size:(row + 1)
                                                                    * square_size, column * square_size:(column + 1) * square_size])
                blackness = 1 - np.sum(potential_black_piece) / \
                    potential_black_piece.size / 255.0
                if blackness > BLACK:
                    for piece in ["p", "n", "b", "r", "k", "q"]:
                        if mse(self.piece_set[piece], potential_black_piece) < 3000:
                            self.board.set_piece_at(
                                square, chess.Piece.from_symbol(piece))
                            break

                # if a black piece was found on this square, we don't need to check for a white piece
                if self.board.piece_type_at(square) is not None:
                    continue

                # now check for a white piece
                potential_white_piece = np.asarray(whiteness_thresh[row * square_size:(row + 1)
                                                                    * square_size, column * square_size:(column + 1) * square_size])
                whiteness = np.sum(potential_white_piece) / \
                    potential_white_piece.size / 255.0
                if whiteness > WHITE:
                    for piece in ["P", "N", "B", "R", "K", "Q"]:
                        if mse(self.piece_set[piece], potential_white_piece) < 2000:
                            self.board.set_piece_at(
                                square, chess.Piece.from_symbol(piece))
                            break

        # assume all castling rights
        self.board.set_castling_fen("QKqk")

        # display a pretty, oriented board in the terminal
        if self.flipped:
            display_board = self.board.transform(
                chess.flip_vertical).transform(chess.flip_horizontal)
        else:
            display_board = self.board
        print("board state:\n" +
              display_board.unicode(invert_color=True, empty_square="_"))


cg = ChessGrid()


@mod.action_class
class ChessGridActions:
    def chess_grid_activate():
        """Searches for a chessboard on the screen and overlays the grid on it"""
        rect = cg.find_chessboard()
        if rect is None:
            # TODO: give the user some indication that no board was found
            ctx.tags = []
            print("no chessboard found")
            return

        cg.setup(rect=rect)
        ctx.tags = ["user.chess_grid_activated"]

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

        cg.click_squares(coordinates)

    def chess_grid_move(move: typing.List[str], color: str):
        """Make a move via SAN notation (e.g. Nc3)"""
        cg.make_move(move, color)

    def chess_grid_flip_board(orientation: str):
        """Flips the orientation of the board"""
        cg.flip_board(orientation)

    def chess_grid_toggle_text():
        """Toggles whether the text is shown"""
        cg.toggle_text()

    def chess_reference(orientation: str):
        """Activate the chess grid and reference the board for later piece detection"""
        rect = cg.find_chessboard()
        if rect is None:
            # TODO: give the user some indication that no board was found
            ctx.tags = []
            print("no chessboard found")
            return

        cg.setup(rect=rect, visible=False)
        cg.flip_board("black" if orientation == "black" else "white")
        cg.reference()
        ctx.tags = ["user.chess_grid_activated"]

    def chess_detect():
        """Detect the position of the chess board. Requires a reference first"""
        cg.detect_position()
