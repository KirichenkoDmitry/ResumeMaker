import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, PhotoSize
from aiogram.filters import Command
from config import BOT_TOKEN
from generate_pdf import create_pdf_with_photo

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временное хранилище данных пользователя
user_data = {}

# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message):
    user_data[message.from_user.id] = {}  # Создаем пустой профиль пользователя
    await message.answer("Привет! Давайте начнем создавать резюме. Введите ваше ФИО.")

# Получение данных пользователя пошагово
@dp.message(F.text)
async def handle_user_input(message: Message):
    user_id = message.from_user.id

    if user_id not in user_data:
        await message.answer("Пожалуйста, начните с команды /start.")
        return

    # Проверяем текущий этап и переходим к следующему
    if "fio" not in user_data[user_id]:
        user_data[user_id]["fio"] = message.text
        await message.answer("Введите вашу дату рождения (например, 01.01.1990).")
    elif "birth_date" not in user_data[user_id]:
        user_data[user_id]["birth_date"] = message.text
        await message.answer("Введите вашу профессию.")
    elif "profession" not in user_data[user_id]:
        user_data[user_id]["profession"] = message.text
        await message.answer("Введите ваш опыт работы в годах (например, 5).")
    elif "experience" not in user_data[user_id]:
        user_data[user_id]["experience"] = message.text
        await message.answer("Теперь загрузите ваше фото (отправьте его как изображение, а не как файл).")
        user_data[user_id]["awaiting_photo"] = True  # Ожидаем фото

# Получение фото от пользователя
@dp.message(F.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id

    if user_id not in user_data or not user_data[user_id].get("awaiting_photo"):
        await message.answer("Пожалуйста, начните с команды /start.")
        return

    # Получаем фото с наибольшим разрешением
    photo = message.photo[-1]

    # Получаем file_id фото
    file_id = photo.file_id

    # Получаем объект файла
    file = await bot.get_file(file_id)

    # Сохраняем фото на диск
    photo_path = f"user_photos/{user_id}.jpg"
    os.makedirs("user_photos", exist_ok=True)  # Создаём папку, если её нет

    # Загружаем фото с помощью download_file
    await bot.download_file(file.file_path, photo_path)

    # Сохраняем путь к фото
    user_data[user_id]["photo_path"] = photo_path
    user_data[user_id].pop("awaiting_photo")  # Убираем флаг ожидания фото

    # Все данные собраны, генерируем PDF
    pdf_path = create_pdf_with_photo(user_data[user_id])

    # Отправка PDF
    from aiogram.types import FSInputFile
    pdf_file = FSInputFile(pdf_path)
    await message.answer_document(pdf_file, caption="Ваше резюме готово!")

    # Удаляем данные пользователя
    user_data.pop(user_id)


# Главная асинхронная функция запуска бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
