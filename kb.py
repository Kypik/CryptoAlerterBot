from aiogram import Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

async def new_inline_button(*text):
    kb = InlineKeyboardBuilder()
    for t in text:
        kb.add(InlineKeyboardButton(text=t, callback_data=t))
    return kb.as_markup()
    
async def reminders():
    return await new_inline_button('Создать новое оповещание')

async def new_reminder():
    return await new_inline_button('Bitcoin (BTC)', 'Ethereum (ETH)', 'Solana (SOL)')

async def ask_long_or_short():
    return await new_inline_button('Long', 'Short')

async def complete_settings():
    return await new_inline_button('Создать новое оповещание', 'Мои оповещания')