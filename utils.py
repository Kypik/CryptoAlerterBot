from aiogram import Bot
import asyncio
import aiohttp
import db
import handlers

async def coin_rate(coin: str):
    url = "https://api.binance.com/api/v3/ticker/price?symbol="  # Часть URL которое возвращает JSON с данными о монете  # Вторая часть URL из доступных монет
    user_url = url + coin.upper() + "USDT"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(user_url) as response:
            if response.status == 200:
                data = await response.json()
                coin_price = data['price'] # Получение стоимости монеты
                return coin_price
            else:
                return f"Ошибка при запросе: {response.status}"

async def calculation(coin, choice, rate):
    temp = {'Long': 1, "Short": -1}
    try:
        print(new_rate[coin])
        perc_change = temp[choice] * ((float(new_rate[coin]) - rate) / rate) * 100
        print(perc_change)

    except:
        print(f'Неизвестный коин {coin}\nДобавляю...')
        new_coin = await coin_rate(coin)
        try:
            perc_change = temp[choice] * ((float(new_coin) - rate) / rate) * 100
            print("Успешно!")
        except:
            print(f"Не удалось добавить коин, ошибка: {new_coin}")

    return perc_change

async def check_reminders(bot: Bot):
    reminders = await db.get_active_reminders()
    for reminder in reminders:
        id = reminder[0]
        coin = reminder[1]
        choice = reminder[2]
        perc = reminder[3]
        rate = reminder[4]
        
        perc_change = await calculation(coin, choice, rate)
        if perc_change >= perc:
            await bot.send_message(chat_id=id, text=f"{coin} изменился на {perc_change:.2f}%")
        else:
            print(coin, choice, perc, rate, perc_change)

async def start_check(bot):
    global new_rate
    while True:
        new_rate = {'BTC': await coin_rate('BTC'),
                'ETH': await coin_rate('ETH'),
                'SOL': await coin_rate('SOL')}
        await check_reminders(bot)
        await asyncio.sleep(300)
