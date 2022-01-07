from clavier.keyboard import Keyboard


def load_qwerty(**kwargs):
    return Keyboard.from_grid(
        """
        1 2 3 4 5 6 7 8 9 0 - =
        q w e r t y u i o p [ ] \\
        a s d f g h j k l ; '
        z x c v b n m , . /
        """,
        **kwargs
    )


def load_dvorak(**kwargs):
    return Keyboard.from_grid(
        """
        ` 1 2 3 4 5 6 7 8 9 0 [ ]
        ' , . p y f g c r l / = \\
        a o e u i d h t n s -
        ; q j k x b m w v z
        """,
        **kwargs
    )
