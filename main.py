import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Update

# Зчитуємо змінні з сервера
API_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = os.getenv("ADMIN_ID", 1492545732)

WEBHOOK_URL = "https://tg-bot-1-9a5t://"

# Ініціалізація бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class OrderState(StatesGroup):
    waiting_for_order = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [KeyboardButton(text="Інформація")], [KeyboardButton(text="Інструкція")],
        [KeyboardButton(text="Прайс")], [KeyboardButton(text="Замовити")],
        [KeyboardButton(text="Підтримка")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("В цьому боті ви можете зробити замовлення свого власного сайта чи телеграм бота.", reply_markup=keyboard)

@dp.message(F.text == "Замовити")
@dp.message(Command("order"))
async def cmd_order(message: types.Message, state: FSMContext):
    await message.answer("Напишіть опис вашого замовлення. Зараз я збережу все, що ви напишете наступним повідомленням!")
    await state.set_state(OrderState.waiting_for_order)

@dp.message(OrderState.waiting_for_order)
async def process_order(message: types.Message, state: FSMContext):
    username_text = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    try:
        await bot.send_message(ADMIN_ID, f"ЗАМОВЛЕННЯ від {username_text}:\n{message.text}")
        await message.answer("Дякуємо! Ваше замовлення надіслано розробнику.")
    except Exception as e:
        print(f"Помилка відправки замовлення адміну: {e}")
        await message.answer("Сталася помилка при відправці замовлення. Спробуйте пізніше або зверніться в підтримку.")
    await state.clear()

@dp.message(F.text == "Інформація")
@dp.message(Command("info"))
async def cmd_info(message: types.Message):
    await message.answer("В цьому боті ви можете замовити сайт або бота для будь-яких потреб.")

@dp.message(F.text == "Інструкція")
@dp.message(Command("instruction"))
async def cmd_instruction(message: types.Message):
    text = ("1. ознайомтесь з цінами.\n2. зробіть бажане замовлення.\n3. почекайте поки воно буде виконано.\n4. оплатіть і моментально отримайте готовий проєкт.")
    await message.answer(text)

@dp.message(F.text == "Прайс")
@dp.message(Command("price"))
async def cmd_price(message: types.Message):
    await message.answer("бот візитка - 700 грн.\nбот для запису - 2500 грн.\nбот для реєстрації - 3500 грн.\nсайт - 1500 грн.")

@dp.message(F.text == "Підтримка")
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    kb_h = [[InlineKeyboardButton(text="Менеджер", url="https://t.me")]] # <--- Зміни url на свій лінк
    await message.answer("Зв'язок:", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_h))

# --- ЗАХИЩЕНЕ КЕРУВАННЯ ВЕБХУКОМ ПРИ СТАРТІ ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🤖 Намагаємось встановити Webhook на адресу: {WEBHOOK_URL}")
    try:
        await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
        print("✅ Webhook успішно зареєстровано в Telegram!")
    except Exception as e:
        print(f"❌ Помилка встановлення Webhook: {e}")
    yield
    try:
        await bot.delete_webhook()
        await bot.session.close() # Закриваємо сесію, щоб не було помилок в логах
        print("Бот зупинено, Webhook видалено, сесію закрито.")
    except Exception as e:
        print(f"Помилка при зупинці бота: {e}")

# Створення FastAPI додатка
app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        json_data = await request.json()
        update = Update.model_validate(json_data, context={"bot": bot})
        await dp.feed_update(bot, update)
    except Exception as e:
        print(f"Помилка обробки апдейту: {e}")
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "Бот активний!", "webhook_url": WEBHOOK_URL}
