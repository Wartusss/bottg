from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ChatMemberHandler,
)
from telegram.constants import ChatType

BOT_TOKEN = '7780876920:AAHc-GJyuHSo0tomlgnUB_BwWx1BvowrNyY'

TARGET_CHAT_IDS = [-1002556063658]
ADMIN_IDS = [603397648]

message_map = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! 👋\n\nТи на зв’язку з ботом Студентського парламенту Університету!\n\n"
        "Маєш питання, ідею, пропозицію чи зауваження? Ми завжди готові допомогти! 💬\n\nЗвертайся :)"
    )

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"{update.effective_chat.id}")

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or message.from_user.id == context.bot.id:
        return

    user = message.from_user

    is_forwarded = False
    if hasattr(message, "forward_from") and message.forward_from:
        is_forwarded = True
    elif hasattr(message, "forward_origin") and message.forward_origin:
        is_forwarded = True

    if is_forwarded:
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.forward_message(
                    chat_id=admin_id,
                    from_chat_id=message.chat_id,
                    message_id=message.message_id
                )

                forwarder_info = f"➡️ Переслане повідомлення відправив [{user.full_name}](tg://user?id={user.id})"
                if user.username:
                    forwarder_info += f" (@{user.username})"
                forwarder_info += f" #id{user.id}"

                await context.bot.send_message(
                    chat_id=admin_id,
                    text=forwarder_info,
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"❌ Не вдалося переслати адміну: {e}")

        if message.chat.type == ChatType.PRIVATE:
            await message.reply_text(
                "Дякуємо за звернення!\n\n"
                "🔹 Впродовж доби намагатимемося надіслати відповідь, проте пам'ятай, команда СПУ — живі люди, тому можливі затримки."
                "\n\nУ разі тривалого очікування — не соромся написати ще раз 🙃"
            )
        return

    full_name = user.full_name or "Невідомий"
    user_line = f"👤 [{full_name}](tg://user?id={user.id})"
    if user.username:
        user_line += f" @{user.username}"
    user_line += f" #id{user.id}"

    header = user_line

    for chat_id in TARGET_CHAT_IDS + ADMIN_IDS:
        try:
            sent = None
            if message.text:
                sent = await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"{header}\n\n{message.text}",
                    parse_mode="Markdown"
                )
            elif message.photo:
                sent = await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=message.photo[-1].file_id,
                    caption=f"{header}\n\n{message.caption or ''}",
                    parse_mode="Markdown"
                )
            elif message.document:
                sent = await context.bot.send_document(
                    chat_id=chat_id,
                    document=message.document.file_id,
                    caption=f"{header}\n\n{message.caption or ''}",
                    parse_mode="Markdown"
                )
            elif message.voice:
                sent = await context.bot.send_voice(
                    chat_id=chat_id,
                    voice=message.voice.file_id,
                    caption=header,
                    parse_mode="Markdown"
                )
            elif message.video:
                sent = await context.bot.send_video(
                    chat_id=chat_id,
                    video=message.video.file_id,
                    caption=f"{header}\n\n{message.caption or ''}",
                    parse_mode="Markdown"
                )
            else:
                sent = await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"{header}\n\n[Надіслано повідомлення, яке не підтримується для перегляду]",
                    parse_mode="Markdown"
                )

            if sent:
                message_map[(sent.chat_id, sent.message_id)] = user.id

        except Exception as e:
            print(f"❌ Не вдалося надіслати в чат {chat_id}: {e}")

    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text(
            "Дякуємо за звернення!\n\n"
            "🔹 Впродовж доби намагатимемося надіслати відповідь, проте пам'ятай, команда СПУ — живі люди, тому можливі затримки."
            "\n\nУ разі тривалого очікування — не соромся написати ще раз 🙃"
        )

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if message.chat_id not in ADMIN_IDS or not message.reply_to_message:
        await message.reply_text("Щоб відповісти студенту, натисни 'Відповісти' під зверненням 💬")
        return

    key = (message.chat_id, message.reply_to_message.message_id)
    user_id = message_map.get(key)

    if not user_id:
        await message.reply_text("Не вдалося знайти користувача для цієї відповіді.")
        return

    try:
        if message.text:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 Відповідь від команди СПУ:\n{message.text}"
            )
        elif message.photo:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=message.photo[-1].file_id,
                caption=message.caption or "📢 Відповідь від команди СПУ:"
            )
        elif message.document:
            await context.bot.send_document(
                chat_id=user_id,
                document=message.document.file_id,
                caption=message.caption or "📢 Відповідь від команди СПУ:"
            )
        elif message.voice:
            await context.bot.send_voice(
                chat_id=user_id,
                voice=message.voice.file_id,
                caption=message.caption or None
            )
        elif message.video:
            await context.bot.send_video(
                chat_id=user_id,
                video=message.video.file_id,
                caption=message.caption or "📢 Відповідь від команди СПУ:"
            )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text="Отримано відповідь, але її тип поки не підтримується 😅"
            )

        await message.reply_text("✅ Відповідь надіслано студенту.")
    except:
        await message.reply_text("Не вдалося доставити повідомлення студенту.")

async def new_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = update.my_chat_member.new_chat_member
        if member.user.id == context.bot.id:
            chat = update.my_chat_member.chat
            await context.bot.send_message(
                chat_id=chat.id,
                text="Бот активовано в цьому чаті ✅ Він прийматиме звернення й дозволить відповідати на них."
            )
    except:
        pass

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chatid", get_chat_id))

    app.add_handler(MessageHandler(
        filters.Chat(chat_id=ADMIN_IDS) & filters.REPLY,
        handle_admin_reply
    ))

    app.add_handler(MessageHandler(
        filters.ChatType.PRIVATE,
        handle_user_message
    ))

    app.add_handler(ChatMemberHandler(new_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))

    print("🤖 Бот запущено...")
    app.run_polling()

if __name__ == '__main__':
    main()
