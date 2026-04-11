import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1492545732

async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")
    
class OrderState(StatesGroup):
    waiting_for_order = State()

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    await start_web_server()

    # --- ХЕНДЛЕРИ КОМАНД ---

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message, state: FSMContext = None):
        if state: await state.clear()
        kb = [
            [KeyboardButton(text="Інформація")],
            [KeyboardButton(text="Інструкція")],
            [KeyboardButton(text="Прайс")],
            [KeyboardButton(text="Замовити")],
            [KeyboardButton(text="Підтримка")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("В цьому боті ви можете зробити замовлення свого власного сайта чи телеграм бота.", reply_markup=keyboard)

    @dp.message(F.text == "Інформація")
    @dp.message(Command("info"))
    async def cmd_info(message: types.Message, state: FSMContext = None):
        if state: await state.clear()
        await message.answer("В цьому боті ви можете замовити сайт або бота для будь-яких потреб.")
        
    @dp.message(F.text == "Інструкція")
    @dp.message(Command("instruction"))
    async def cmd_instruction(message: types.Message, state: FSMContext = None):
        if state: await state.clear()
        text = ("1. ознайомтесь з цінами.\n" "2. зробіть бажане замовлення.\n" "3. почекайте поки воно буде виконано.\n" "4. оплатіть і моментально отримайте готовий проєкт.")
        await message.answer(text)
        
    @dp.message(F.text == "Прайс")
    @dp.message(Command("price"))
    async def cmd_price(message: types.Message, state: FSMContext = None):
        if state: await state.clear()
        await message.answer("бот візитка - 700 грн.\n" "бот для запису - 2500 грн.\n" "бот для реєстрації - 3500 грн.\n" "сайт - 1500 грн.")

    @dp.message(F.text == "Підтримка")
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message, state: FSMContext = None):
        if state: await state.clear()
        kb_h = [[InlineKeyboardButton(text="Менеджер", url="https://t.me/ilkka324")]]
        await message.answer("Зв'язок:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_h))

    @dp.message(F.text == "Замовити")
    @dp.message(Command("order"))
    async def cmd_order(message: types.Message, state: FSMContext):
        await message.answer("Напишіть опис вашого замовлення. Зараз я збережу все, що ви напишете наступним повідомленням!")
        await state.set_state(OrderState.waiting_for_order)

    # --- ОБРОБКА ЗАМОВЛЕННЯ (РОЗУМНА) ---

    @dp.message(OrderState.waiting_for_order)
    async def process_order(message: types.Message, state: FSMContext):
        menu_buttons = ["Інформація", "Інструкція", "Прайс", "Замовити", "Підтримка"]
        
        # Перевірка на переривання замовлення іншою командою
        if message.text and (message.text.startswith("/") or message.text in menu_buttons):
            await state.clear()
            if message.text in ["Інформація", "/info"]: await cmd_info(message)
            elif message.text in ["Інструкція", "/instruction"]: await cmd_instruction(message)
            elif message.text in ["Прайс", "/price"]: await cmd_price(message)
            elif message.text in ["Замовити", "/order"]: await cmd_order(message, state)
            elif message.text in ["Підтримка", "/help"]: await cmd_help(message)
            elif message.text == "/start": await cmd_start(message)
            return

        # Надсилання замовлення адміну
        username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
        await bot.send_message(ADMIN_ID, f"ЗАМОВЛЕННЯ від {username}:\n{message.text}")
        await message.answer("Дякуємо! Ваше замовлення надіслано розробнику.")
        await state.clear()

    print("Бот знову в строю")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
