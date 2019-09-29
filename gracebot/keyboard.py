from aiogram import types
from more_itertools import chunked


class InlineKeyboard(types.InlineKeyboardMarkup):
    def __init__(self, keys: list = [], rows: int = 1, columns: int = 2):
        super().__init__()
        self._keys = keys
        self._columns = columns
        self._increment = rows * columns
        self._start: int = 0
        self._make_keyboard()

    @property
    def all_keys(self):
        return self._keys

    @property
    def visible_keys(self):
        return self._keys[self._start : self._start + self._increment]

    async def update(self, query: types.CallbackQuery):
        if query.data == "previous":
            self._start += self._increment
        elif query.data == "next":
            self._start -= self._increment

        self.inline_keyboard: list = []
        self._make_keyboard()

        await query.message.edit_reply_markup(reply_markup=self)

    def _navigation_buttons(self) -> list:
        navigation_buttons = []

        if self._start < (len(self._keys) - self._increment):
            navigation_buttons.append(
                types.InlineKeyboardButton("<<", callback_data="previous")
            )
        if self._start > 0:
            navigation_buttons.append(
                types.InlineKeyboardButton(">>", callback_data="next")
            )

        return navigation_buttons

    def _make_keyboard(self):
        for keys in chunked(self.visible_keys, self._columns):
            row = []
            for key in keys:
                row.append(
                    types.InlineKeyboardButton(key.replace("_", " "), callback_data=key)
                )
            self.row(*row)

        self.row(*self._navigation_buttons())
