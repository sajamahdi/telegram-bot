from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = "8743669525:AAH-9RnxPFwyOy7jOBeh_IidPcKj5mnJ3Zkp"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("البوت شغال ✔ جاهز نبدأ الحجز")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)