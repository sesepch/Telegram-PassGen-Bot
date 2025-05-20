from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
import aiohttp
import asyncio
import config
import random
import string

LM_API_URL = "http://localhost:1234/v1/completions"  # Adjust port if needed
MODEL_NAME = "gemma-3-1b-it-qat"
# Initialize bot and dispatcher
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
user_messages = {}
# Create a router for handlers
router = Router()
dp.include_router(router)

# Function to generate a password
def format_prompt(user_message: str) -> str:
    return f"""You are a friendly and helpful assistant.
User: {user_message}
Assistant:"""

async def query_lm_studio(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 200,
        "stop": ["User:", "Assistant:"]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(LM_API_URL, json=payload) as response:
            data = await response.json()
            return data.get("choices", [{}])[0].get("text", "").strip()
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# Define keyboards

main_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Сгенирировать пароль')],
        [KeyboardButton(text='/id')],
        [KeyboardButton(text='Приложение')]
    ],
    resize_keyboard=True
)

# Start command handler
@router.message(Command('start'))
async def start(message: types.Message):
        await message.answer_sticker('CAACAgIAAxkBAAEMYIZnqIWwZ0Bi-ofAswlID2sBP22FaQAClyUAAncmKEpUlw3HOgpDKTYE')
        await message.answer(f'Привет, {message.from_user.first_name}. Этот бот умеет генерировать пароли', reply_markup=main_admin)

# ID command handler
@router.message(Command('id'))
async def getid(message: types.Message):
    await message.answer(f'{message.from_user.id}')

# Generate password handler
@router.message(lambda message: message.text == 'Сгенирировать пароль')
async def generate_pass(message: types.Message):
    await message.answer(generate_password())

@router.message(lambda message: message.text == 'Домой')
async def home(message: types.Message):
    await message.answer('Ты дома', reply_markup=main_admin)

@router.message(lambda message: message.text == 'Приложение')
async def app(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="Открыть приложение",
                web_app=types.WebAppInfo(url="https://sesepch.github.io/telegram-test-app/")
            )], [KeyboardButton(text='Домой')]
        ],
        resize_keyboard=True
    )
    await message.answer("Нажмите ниже чтобы открыть приложение!", reply_markup=keyboard)
@router.message()
async def on_user_message(message: types.Message):
    user_messages[message.chat.id] = message.text.strip()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Спросить нейросеть", callback_data="ask_ai")]
    ])

    await message.answer("Хотите спросить нейросеть? Нажмите на кнопку внизу:", reply_markup=keyboard)


# Handle button press
@dp.callback_query(F.data == "ask_ai")
async def on_ask_ai(callback: CallbackQuery):
    user_input = user_messages.get(callback.message.chat.id)

    if not user_input:
        await callback.message.answer("⚠️ Нет сообщения на обработку")
        return

    await callback.message.answer("🤖 Генерация")

    try:
        prompt = format_prompt(user_input)
        response = await query_lm_studio(prompt)
        await callback.message.answer(response or "🤷 Ответ не был сгенерирован")
    except Exception as e:
        await callback.message.answer(f"❌ Error: {str(e)}")




# Main function to start polling
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())