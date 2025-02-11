from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import asyncio
import config
import random
import string

# Initialize bot and dispatcher
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Create a router for handlers
router = Router()
dp.include_router(router)

# Function to generate a password
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# Define keyboards

main_admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Сгенирировать пароль')],
        [KeyboardButton(text='/id')],
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

# Admin panel handler
@router.message(lambda message: message.text == 'Админ')
async def admin_panel(message: types.Message):
    if message.from_user.id == int(config.ADMIN_ID):
        await message.answer('Ты админ, круто!', reply_markup=main_admin)
    else:
        await message.answer('<b>Пожалуйста, используй кнопки</b>', parse_mode='html', reply_markup=main)

# Generate password handler
@router.message(lambda message: message.text == 'Сгенирировать пароль')
async def generate_pass(message: types.Message):
    await message.answer(generate_password())

# Unknown message handler
@router.message()
async def unknown_message(message: types.Message):
    await message.answer('<b>Пожалуйста, используй кнопки</b>', parse_mode='html')

# Main function to start polling
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())