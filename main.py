import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession

# .env yuklash
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

# Bot va Dispatcher
bot = Bot(token=API_TOKEN, session=AiohttpSession())
dp = Dispatcher()

# Guruh a'zolarini vaqtincha saqlash uchun lug'at
group_database = {}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Faqat shaxsiy yozishmada (lichkada) javob beradi
    if message.chat.type == "private":
        bot_info = await bot.get_me()

        # Guruhga qo'shish tugmasi
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text="➕ Guruhga qo'shish",
            url=f"https://t.me/{bot_info.username}?startgroup=true")
        )

        text = (
            "👋 **Salom! Men Mention Botman.**\n\n"
            "Meni guruhingizga qo'shing, men a'zolarni eslab qolaman.\n"
            "Hamma a'zolarni chaqirish uchun guruhda `@all` deb yozing."
        )
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="Markdown")


@dp.message(F.chat.type.in_({"group", "supergroup"}))
async def handle_group(message: types.Message):
    chat_id = message.chat.id

    if chat_id not in group_database:
        group_database[chat_id] = {}

    # Xabar yozgan odamni bazaga qo'shish
    user = message.from_user
    if user.username:
        mention = f"@{user.username}"
    else:
        mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    group_database[chat_id][user.id] = mention

    # @all yoki /all buyrug'ini tekshirish
    if message.text:
        msg_text = message.text.lower()
        if msg_text in ["/all", "@all", "safi hamma"]:
            members = list(group_database[chat_id].values())

            if len(members) <= 1:
                await message.reply("Hozircha ro'yxat bo'sh. Bir ozdan so'ng qayta urinib ko'ring.")
                return

            # Odamlarni 20 tadan bo'lib chaqirish
            for i in range(0, len(members), 20):
                chunk = members[i:i + 20]
                response = "📢 **Diqqat hamma diqqat!**\n\n" + " ".join(chunk)
                await message.answer(response, parse_mode="HTML")


async def main():
    print("Bot muvaffaqiyatli ishga tushdi...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi")
