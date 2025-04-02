import uuid

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from cache_client import CacheClient
from sudoku import Sudoku, SudokuException
from utils import get_cache_client, get_binary_file, extract_sudoku, frames

keyboard = [
    [
        InlineKeyboardButton("Section 1", callback_data="s1"),
        InlineKeyboardButton("Section 2", callback_data="s2"),
        InlineKeyboardButton("Section 3", callback_data="s3"),
        InlineKeyboardButton("Section 4", callback_data="s4"),
        InlineKeyboardButton("Section 5", callback_data="s5"),
        InlineKeyboardButton("Section 6", callback_data="s6"),
        InlineKeyboardButton("Section 7", callback_data="s7"),
        InlineKeyboardButton("Section 8", callback_data="s8"),
        InlineKeyboardButton("Section 9", callback_data="s9"),
    ],
    [
        InlineKeyboardButton("Row 1", callback_data="r1"),
        InlineKeyboardButton("Row 2", callback_data="r2"),
        InlineKeyboardButton("Row 3", callback_data="r3"),
        InlineKeyboardButton("Row 4", callback_data="r4"),
        InlineKeyboardButton("Row 5", callback_data="r5"),
        InlineKeyboardButton("Row 6", callback_data="r6"),
        InlineKeyboardButton("Row 7", callback_data="r7"),
        InlineKeyboardButton("Row 8", callback_data="r8"),
        InlineKeyboardButton("Row 9", callback_data="r9"),
    ],
    [
        InlineKeyboardButton("Column 1", callback_data="c1"),
        InlineKeyboardButton("Column 2", callback_data="c2"),
        InlineKeyboardButton("Column 3", callback_data="c3"),
        InlineKeyboardButton("Column 4", callback_data="c4"),
        InlineKeyboardButton("Column 5", callback_data="c5"),
        InlineKeyboardButton("Column 6", callback_data="c6"),
        InlineKeyboardButton("Column 7", callback_data="c7"),
        InlineKeyboardButton("Column 8", callback_data="c8"),
        InlineKeyboardButton("Column 9", callback_data="c9"),
    ],
    [
        InlineKeyboardButton("Complete Solution", callback_data="f0"),
    ],
]

reply_markup = InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm Sudoku bot, upload the sudoku puzzle and see part of/full solved version",
    )


async def solution(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    cache = CacheClient(client=get_cache_client())
    result = cache.get_matrix(key=str(update.callback_query.from_user.id))
    if result is None:
        return await context.bot.send_message(chat_id=update.effective_chat.id, text='No solution found.')
    attr = query.data
    section = attr[0]
    number = int(attr[1])
    sudoku = Sudoku(matrix=result)
    # if attr == 'f0':
    #     await query.edit_message_text(text=Sudoku.humanized_board(sudoku.get_section(section, number)))
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=Sudoku.humanized_board(sudoku.get_section(section, number)),
    )


async def solve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        binary_photo = await get_binary_file(update=update, context=context)
        data = extract_sudoku(binary_photo)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Couldn't extract sudoku. Please try again.")

        return
    try:
        sudoku = Sudoku(matrix=Sudoku.list_to_matrix(data))
        solved_sudoku = sudoku.solve()
    except SudokuException as e:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=str(e))
        return

    cache = CacheClient(client=get_cache_client())
    cache.set_matrix(key=str(update.message.from_user.id), matrix=solved_sudoku)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Your Sudoku Has been solved')
    await update.message.reply_text("Please choose solution part you want to see:", reply_markup=reply_markup)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

