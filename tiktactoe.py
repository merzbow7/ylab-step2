import random
import re
from collections import namedtuple
from collections.abc import Sequence

from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

CoordTuple = namedtuple("CoordTuple", ("row", "col"))
Vector = list[CoordTuple]

Config.set("graphics", "resizable", "0")
Config.set("graphics", "width", "600")
Config.set("graphics", "height", "700")


class ButtonCoord(Button):
    coord: CoordTuple

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TicTacToe():
    def __init__(self, *, dimension=10, to_win=0, ai=False):
        self.dimension = dimension
        self.to_win = to_win if 0 < to_win < dimension else dimension
        self.ai = ai
        self.symbol = "X"
        self.pc = "O"
        self.result_callback = None
        self.buttons: list[ButtonCoord] = []
        self.btn_matrix = self.make_matrix()

    def make_matrix(self):
        """Make empty matrix self.dimension x self.dimension."""
        matrix = [[""] * self.dimension for _ in range(self.dimension)]
        for btn in self.buttons:
            matrix[btn.coord.row][btn.coord.col] = btn.text
        return matrix

    def calc_coordinates(self, index: int) -> CoordTuple:
        """Calc coordinates from index button."""
        return index // self.dimension, index % self.dimension

    def play_tic_tac_toe(self, btn: ButtonCoord):
        """Move and check for win."""
        result = self.check_win(self.put_symbol_cell(btn, self.symbol))
        if result and self.result_callback:
            return self.result_callback("Поражение", result)

        if not self.check_end():
            pc_move = self.make_pc_move()
            result = self.check_win(pc_move)
            if result and self.result_callback:
                return self.result_callback("Победа", result)

    def make_pc_move(self) -> ButtonCoord:
        """Make a move with the pc."""
        empty_cells = [index for index, cell in enumerate(self.buttons)
                       if cell.text == ""]
        index = random.choice(empty_cells)
        is_loss = True
        while len(empty_cells) > 1 and is_loss and self.ai:
            btn = self.buttons[index]
            self.btn_matrix[btn.coord.row][btn.coord.col] = self.pc
            is_loss = self.check_win(self.buttons[index])
            if is_loss:
                empty_cells.remove(index)
                index = random.choice(empty_cells)
            self.btn_matrix[btn.coord.row][btn.coord.col] = ""
        return self.put_symbol_cell(self.buttons[index], self.pc)

    def put_symbol_cell(self, btn: ButtonCoord, symbol: str):
        """Put symbol to cell."""
        btn.text = symbol
        btn.disabled = True
        self.btn_matrix[btn.coord.row][btn.coord.col] = btn.text
        return btn

    def check_end(self):
        """Check the fullness of all cells on the field."""
        return all(btn.text != "" for btn in self.buttons)

    def make_diagonal(self, point: CoordTuple, incline=1) -> Vector:
        """Make diagonal vector."""
        if incline == 1:
            start_point = CoordTuple(point.row - min(point),
                                     point.col - min(point))
            length = self.dimension - max(start_point)
        else:
            delta = min(self.dimension - 1 - point.row, point.col)
            start_point = CoordTuple(point.row - delta * incline,
                                     point.col - delta)
            length = max(start_point) - min(start_point) + 1
        return [CoordTuple(start_point.row + i * incline, start_point.col + i)
                for i in range(length)]

    def make_text_vector(self, arr: Sequence):
        """Make cell content vector from coordinate vector."""
        return tuple(self.btn_matrix[btn[0]][btn[1]] for btn in arr)

    def make_vectors(self, btn: ButtonCoord):
        """Make in all direction vectors from the current button."""
        row_vector = [CoordTuple(btn.coord[0], i)
                      for i in range(self.dimension)]
        col_vector = [CoordTuple(i, btn.coord[1])
                      for i in range(self.dimension)]
        vector_45 = self.make_diagonal(btn.coord)
        vector_135 = self.make_diagonal(btn.coord, incline=-1)
        return {"row": row_vector,
                "col": col_vector,
                "45": vector_45,
                "135": vector_135,
                }

    def check_vector(self, vector: Sequence):
        """Check win combination in vector."""
        vector_str = "".join([let if let else "*" for let in vector])
        pattern = rf"X{{{self.to_win}}}|O{{{self.to_win}}}"
        result = re.search(pattern, vector_str)
        return result.span() if result else False

    def check_win(self, btn: ButtonCoord):
        """Check win after move."""
        vectors = self.make_vectors(btn)
        for vector in vectors.values():
            win = self.check_vector(self.make_text_vector(vector))
            if win:
                return vector[win[0]:win[1]]
        return False


class MainApp(App, TicTacToe):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = 600
        self.title = "TicTacToe"
        self.result_callback = self.call_popup

        self.root = BoxLayout(orientation="vertical", padding=5)
        self.grid = GridLayout(cols=self.dimension)
        self.button_x = ButtonCoord()
        self.button_o = ButtonCoord()
        self.role_layout = BoxLayout(
            size_hint=(None, None),
            size=(self.size, 75),
        )

    def select_symbol(self, select_btn: ButtonCoord):
        """Select a symbol to play."""
        if select_btn.text == "O":
            self.symbol = "O"
            self.pc = "X"
            self.make_pc_move()
        else:
            self.symbol = "X"
            self.pc = "O"

        self.grid.disabled = False
        select_btn.disabled_color = self.get_color("green")
        self.role_layout.disabled = True

    def highlight_vector(self, vector: Vector, color: str):
        """Highlight win vector."""
        for btn in vector:
            btn_index = btn[0] * self.dimension + btn[1]
            self.buttons[btn_index].color = self.get_color(color)

    @staticmethod
    def get_color(color: str = "white") -> list[int]:
        colors = {
            "red": [1, 0, 0, 1],
            "green": [0, 1, 0, 1],
            "blue": [0, 0, 1, 1],
            "black": [0, 0, 0, 1],
            "white": [1, 1, 1, 1],
        }
        return colors.get(color)

    def call_popup(self, message: str, vector: Vector = None):
        """Show result popup."""
        self.grid.disabled = True
        result_color = "green" if message == "Победа" else "red"
        if vector:
            self.highlight_vector(vector, result_color)
        content = GridLayout(cols=1)
        content_cancel = ButtonCoord(text="Cancel",
                                     size_hint_y=None,
                                     height=40)
        content_label = Label(text=message,
                              font_size=30,
                              disabled_color=self.get_color(result_color))
        content.add_widget(content_label)
        content.add_widget(content_cancel)
        popup = Popup(title="Результат",
                      size_hint=(None, None), size=(256, 256),
                      content=content, disabled=True)
        content_cancel.bind(on_release=popup.dismiss)
        popup.open()

    def restart(self, _):
        """Restart game."""
        self.grid.disabled = True
        self.button_x.disabled_color = self.get_color()
        self.button_o.disabled_color = self.get_color()
        self.role_layout.disabled = False

        for button in self.buttons:
            button.color = self.get_color("black")
            button.text = ""
            button.disabled = False

        self.btn_matrix = self.make_matrix()

    def build(self):
        """Build app."""
        self.grid.disabled = True

        for index in range(0, self.dimension ** 2):
            button = ButtonCoord(
                color=self.get_color("black"),
                font_size=26,
                disabled=False,
                on_press=self.play_tic_tac_toe,
            )
            button.coord = CoordTuple(*self.calc_coordinates(index))
            self.buttons.append(button)
            self.grid.add_widget(button)

        self.root.add_widget(self.grid)

        restart_button = ButtonCoord(
            text="Restart",
            size_hint=[1, .15],
            font_size=25,
            on_press=self.restart)

        delimiter = BoxLayout(
            size_hint=(None, None),
            size=(self.size, 25),
        )

        self.root.add_widget(delimiter)
        self.root.add_widget(restart_button)

        self.button_x = ButtonCoord(
            text="X",
            size_hint=[.5, 1],
            font_size=30,
            on_press=self.select_symbol)

        self.button_o = ButtonCoord(
            text="O",
            size_hint=[.5, 1],
            font_size=30,
            on_press=self.select_symbol)

        self.role_layout.add_widget(self.button_x)
        self.role_layout.add_widget(self.button_o)
        self.root.add_widget(self.role_layout)

        return self.root


if __name__ == "__main__":
    MainApp(dimension=10, to_win=5, ai=True).run()
