import random

from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

Config.set("graphics", "resizable", "0")
Config.set("graphics", "width", "600")
Config.set("graphics", "height", "700")


class ButtonCoord(Button):
    coord: tuple

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MainApp(App):
    def __init__(self, *, dimension=10, to_win=0):
        super().__init__()
        self.dimension = dimension
        self.to_win = to_win if to_win != 0 else dimension
        self.size = 600
        self.symbol = 'X'
        self.pc = 'O'
        self.buttons: list[Button] = []
        self.btn_matrix = self.make_matrix()
        self.end = False

        self.colors = {
            "red": [1, 0, 0, 1],
            "green": [0, 1, 0, 1],
            "blue": [0, 0, 1, 1],
            "black": [0, 0, 0, 1],
            "white": [1, 1, 1, 1],
        }

        self.root = BoxLayout(orientation="vertical", padding=5)
        self.grid = GridLayout(cols=self.dimension)
        self.button_x = Button()
        self.button_o = Button()
        self.role_layout = BoxLayout(
            size_hint=(None, None),
            size=(self.size, 75),
        )

        self.grid.disabled = True

    def make_matrix(self):
        matrix = [[''] * self.dimension for _ in range(self.dimension)]
        for btn in self.buttons:
            matrix[btn.coord[0]][btn.coord[1]] = btn.text
        return matrix

    def select_symbol(self, select_btn: Button):
        if select_btn.text == "Нолик":
            self.symbol = "O"
            self.pc = 'X'
            self.make_pc_move()
        else:
            self.symbol = "X"
            self.pc = "O"

        self.grid.disabled = False
        select_btn.disabled_color = self.colors["green"]
        self.role_layout.disabled = True

    def calc_coordinates(self, index: int):
        return index // self.dimension, index % self.dimension

    def make_pc_move(self) -> Button:
        empty_cells = [index for index, cell in enumerate(self.buttons) if cell.text == '']
        index = random.choice(empty_cells)
        self.put_symbol_cell(self.buttons[index], self.pc)
        return self.buttons[index]

    def put_symbol_cell(self, btn: Button, symbol: str):
        btn.text = symbol
        btn.disabled = True
        self.btn_matrix[btn.coord[0]][btn.coord[1]] = btn.text

    def play_tic_tac_toe(self, btn: Button):
        self.put_symbol_cell(btn, self.symbol)
        self.check_win(btn)

        if not self.check_end():
            pc_move = self.make_pc_move()
            self.check_win(pc_move)

    def check_end(self):
        return all(btn.text != "" for btn in self.buttons)

    def make_diagonal(self, point):
        min_delta = min(point)
        start_point = (point[0] - min_delta, point[1] - min_delta)
        max_delta = self.dimension - max(start_point)
        return [(start_point[0] + i, start_point[1] + i) for i in range(max_delta)]

    def make_vectors(self, btn: Button):
        row_vector = self.btn_matrix[btn.coord[0]]
        col_vector = [matrix_row[btn.coord[1]] for matrix_row in self.btn_matrix]
        vector_45 = self.make_diagonal(btn.coord)
        # vector_135 = self.make_diagonal(row, col)

    def check_win(self, btn: Button, field=None):
        if field is None:
            field = self.buttons
        self.make_vectors(btn)
        if self.check_end():
            self.call_popup("Ничья")

    def call_popup(self, message: str, color: str = "white"):
        """Show result popup."""
        print(self.make_diagonal((1, 2)))
        self.grid.disabled = True

        content = GridLayout(cols=1)
        content_cancel = Button(text='Cancel', size_hint_y=None, height=40)
        content_label = Label(text=message,
                              font_size=30,
                              disabled_color=self.colors.get(color))
        content.add_widget(content_label)
        content.add_widget(content_cancel)
        popup = Popup(title='Результат',
                      size_hint=(None, None), size=(256, 256),
                      content=content, disabled=True)
        content_cancel.bind(on_release=popup.dismiss)
        popup.open()

    def restart(self, _):
        """Restart game."""
        self.grid.disabled = True
        self.button_x.disabled_color = self.colors["white"]
        self.button_o.disabled_color = self.colors["white"]
        self.role_layout.disabled = False

        for button in self.buttons:
            button.color = self.colors["black"]
            button.text = ""
            button.disabled = False

        self.btn_matrix = self.make_matrix()

    def build(self):
        """Build app."""
        self.title = "Крестики-нолики"

        for index in range(0, self.dimension ** 2):
            button = Button(
                color=self.colors["black"],
                font_size=26,
                disabled=False,
                on_press=self.play_tic_tac_toe,
            )
            button.coord = self.calc_coordinates(index)
            self.buttons.append(button)
            self.grid.add_widget(button)

        self.root.add_widget(self.grid)

        restart_button = Button(
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

        self.button_x = Button(
            text="Крестик",
            size_hint=[.5, 1],
            font_size=30,
            on_press=self.select_symbol)

        self.button_o = Button(
            text="Нолик",
            size_hint=[.5, 1],
            font_size=30,
            on_press=self.select_symbol)

        self.role_layout.add_widget(self.button_x)
        self.role_layout.add_widget(self.button_o)
        self.root.add_widget(self.role_layout)

        return self.root


if __name__ == "__main__":
    MainApp(dimension=3).run()
