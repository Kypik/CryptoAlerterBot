from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

import kb
import db
import utils

router = Router()

coin_data = {
    'Bitcoin (BTC)': "BTC",
    'Ethereum (ETH)': "ETH",
    'Solana (SOL)': "SOL"
}
user_data = {'in_process': 1}
text = {}

class Percent(StatesGroup):
    waiting_for_text = State()

@router.message(Command("start"))
async def start(msg: Message, state: FSMContext):
    await state.clear()
    id = msg.chat.id
    user_data['tg_id'] = id

    try:
        has_id = await db.select_by_users_id(id)
    except:
        return await err(msg)

    if len(has_id) == 0:
        has_id = False
    else:
        has_id = True

    if not has_id:
        await msg.answer("Это бот для уведомлений об изменениях на рынке!")
        await new_reminder(msg)
    else:
        await show_reminders(msg)

async def show_reminders(msg: Message):
    kbn = await kb.reminders()

    try:
        list_reminders = await user_reminders_list()
    except:
        return await err(msg)

    text[''] = f"Текущие оповещения:\n{''.join(str(el) for el in list_reminders)}"
    try:
        await msg.answer(text[''], parse_mode=ParseMode.HTML, reply_markup=kbn)
    except:
        return await err(msg)

async def user_reminders_list():
    all_reminders = await db.select_by_users_id(user_data['tg_id'])
    reminders_in_process = [el for el in all_reminders if el[-1] == 1]
    list_reminders = []

    if len(reminders_in_process) == 0:
        list_reminders = "Нет текущих оповещений"

    else:
        for el in reminders_in_process:
            reminder = list(el[1:-1])
            reminder[0] = f"<b>💎{reminder[0]}</b>"
            reminder[1] = "📈" if reminder[1] == 'Long' else "📉"
            reminder[2] = f"<b>{reminder[2]}%</b>" 
            reminder[3] = f"<b>📊 {reminder[3]}$</b>"
            reminder.append(f"- текущее состояние: <b>{await utils.calculation(el[1], el[2], el[4]):.2f}%</b>")

            reminder = ' '.join(reminder)
            list_reminders.append(f'{reminder}\n')
    
    return list_reminders

async def new_reminder(msg: Message):
    kbn = await kb.new_reminder()
    await msg.answer("Выберете криптовалюту для которой вам нужно оповещение", reply_markup=kbn)

async def long_or_short(msg: Message):
    kbn = await kb.ask_long_or_short()
    await msg.answer("Выберете Long/Short", reply_markup=kbn)

@router.callback_query(F.data == 'Мои оповещания')
async def show_reminders_from_cb(cb: CallbackQuery):
    try:
        await cb.message.edit_text(text[''], parse_mode=ParseMode.HTML)
    except:
        return await err(cb.message)
    kbn = await kb.reminders()
    try:
        list_reminders = await user_reminders_list()
    except:
        return await err(cb.message)

    text[''] = f"Текущие оповещения:\n{''.join(str(el) for el in list_reminders)}"
    await cb.message.answer(text[''], parse_mode=ParseMode.HTML, reply_markup=kbn)

@router.callback_query(F.data == 'Создать новое оповещание')
async def new_reminder_from_cb(cb: CallbackQuery):
    try:
        await cb.message.edit_text(text[''], parse_mode=ParseMode.HTML)
    except:
        return await err(cb.message)
    kbn = await kb.new_reminder()
    await cb.message.answer("Выберете криптовалюту для которой вам нужно оповещение", reply_markup=kbn)

@router.callback_query(F.data.in_(coin_data.keys()))
async def coin_selection(cb: CallbackQuery):
    await cb.message.delete()
    try:
        coin = coin_data[cb.data]
        start_rate = await utils.coin_rate(coin)
    except:
        return await err(cb.message)

    try:
        start_rate = float(start_rate)
    except:
        cb.message.answer(f'Ошибка при запросе: {start_rate}')
        return await err(cb.message)
    
    user_data['coin'] = coin
    user_data['start_rate'] = start_rate
    await cb.message.answer(f"Цена {user_data['coin']} на данный момент: {start_rate}")
    await long_or_short(cb.message)

@router.callback_query(F.data.in_(('Long', 'Short')))
async def choice(cb: CallbackQuery, state: FSMContext):
    await cb.message.delete()
    choice = cb.data
    user_data['choice'] = choice
    await cb.message.answer("Введите процент изменения, по достяжению которого, вам придет оповещение (Пример: 10 или 0.1)")
    await state.set_state(Percent.waiting_for_text)

@router.message(Percent.waiting_for_text)
async def percent(msg: Message, state: FSMContext):
    try:
        perc = float(msg.text)
        if perc > 0:
            kbn = await kb.complete_settings()
            user_data['percent'] = perc
            text[''] = f"Уведомление придет вам, как только курс изменится на {perc}%"
            try:
                await db.add_info(tuple(user_data.keys()), tuple(user_data.values()))
                await msg.answer(text[''], reply_markup=kbn)
                await state.clear()
            except:
                msg.answer("Неудалось внести данные, повторите запрос")
        else:
            await msg.answer("Введите положительное число")
    except:
        await msg.answer("Неверный ввод, попробуйте еще раз")

async def err(msg):
    await msg.answer('Ошибка! Пропишите /start')