from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def make_amount_kb():
    kb = InlineKeyboardMarkup(row_width=3)
    for a in (10, 20, 50, 100, 200, 500):
        kb.add(InlineKeyboardButton(text=str(a), callback_data=f"amount:{a}"))
    return kb

def make_choice_kb():
    kb = InlineKeyboardMarkup(row_width=3)
    for i in range(1,7):
        kb.add(InlineKeyboardButton(text=str(i), callback_data=f"pick:{i}"))
    return kb
