import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
# 1. НОВІ ІМПОРТИ ДЛЯ СТАНІВ
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.client.session.aiohttp import AiohttpSession

API_TOKEN = '8652491541:AAEJftjZCS7X_Hs06BiTLpC5JzaxRdDJb-Y'
ADMIN_ID = 1492545732 # Твій ID сюди

# 2. СТВОРЮЄМО КЛАС СТАНУ (це як назва режиму)
class OrderState(StatesGroup):
    waiting_for_order = State()

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        kb = [
            [KeyboardButton(text="Інформація")],
            [KeyboardButton(text="Інструкція")],
            [KeyboardButton(text="Прайс")],
            [KeyboardButton(text="Замовити")],
            [KeyboardButton(text="Підтримка")]
        ]
        keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer("В цьому боті ви можете зробити замовлення свого власного сайта чи телеграм бота.", reply_markup=keyboard)

    # 3. КОМАНДА ЗАМОВЛЕННЯ (вмикає режим очікування)
    @dp.message(F.text == "Замовити")
    @dp.message(Command("order"))
    async def cmd_order(message: types.Message, state: FSMContext):
        await message.answer("Напишіть опис вашого замовлення. Зараз я збережу все, що ви напишете наступним повідомленням!")
        # Цей рядок каже боту: "Чекай на текст!"
        await state.set_state(OrderState.waiting_for_order)

    # 4. ОБРОБНИК, ЯКИЙ СПРАЦЮЄ ТІЛЬКИ ЯКЩО УВІМКНЕНО РЕЖИМ ЗАМОВЛЕННЯ
    @dp.message(OrderState.waiting_for_order)
    async def process_order(message: types.Message, state: FSMContext):
        # Пересилаємо адміну
        await bot.send_message(ADMIN_ID, f"ЗАМОВЛЕННЯ від @{message.from_user.username}:\n{message.text}")
        
        await message.answer("Дякуємо! Ваше замовлення надіслано розробнику.")
        # ВИМИКАЄМО режим очікування (обов'язково!)
        await state.clear()

    # РЕШТА КОМАНД (вони тепер не будуть перехоплювати текст замовлення)
    @dp.message(F.text == "Інформація")
    @dp.message(Command("info"))
    async def cmd_info(message: types.Message):
        text = "В цьому боті ви можете замовити сайт або бота для будь-яких потреб."
        await message.answer(text)
        
    @dp.message(F.text == "Інструкція")
    @dp.message(Command("instruction"))
    async def cmd_instruction(message: types.Message):
        text = ("1. ознайомтесь з цінами.\n" "2. зробіть бажане замовлення.\n" "3. почекайте поки воно буде виконано.\n" "4. оплатіть і моментально отримайте готовий проєкт.")
        await message.answer(text)
        
    @dp.message(F.text == "Прайс")
    @dp.message(Command("price"))
    async def cmd_price(message: types.Message):
        await message.answer("бот візитка - 700 грн.\n" "бот для запису - 2500 грн.\n" "бот для реєстрації - 3500 грн.\n" "сайт - 1500 грн.")

    @dp.message(F.text == "Підтримка")
    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        kb_h = [[InlineKeyboardButton(text="Менеджер", url="https://t.me/ilkka324")]]
        await message.answer("Зв'язок:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_h))

    print("Бот знову в строю")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
