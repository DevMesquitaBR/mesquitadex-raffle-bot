import logging
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Pegando o token do ambiente Railway
TOKEN = os.getenv("BOT_TOKEN")
participants = set()
message_id_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎉 Participar", callback_data="join_raffle")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await update.message.reply_text(
        f"""🎉 Sorteio Aberto! 🎉
Já temos {len(participants)} participando!
Clique no botão Participar para entrar! 🚀
🔗 Cadastre-se também aqui: https://bit.ly/42puLF6
Boa sorte! 🍀""",
        reply_markup=reply_markup
    )
    message_id_store[update.effective_chat.id] = message.message_id

async def join_raffle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user.username or query.from_user.first_name
    participants.add(user)

    chat_id = query.message.chat_id
    msg_id = message_id_store.get(chat_id)

    if msg_id:
        keyboard = [[InlineKeyboardButton("🎉 Participar", callback_data="join_raffle")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=f"""🎉 Sorteio Aberto! 🎉
Já temos {len(participants)} participando!
Clique no botão Participar para entrar! 🚀
🔗 Cadastre-se também aqui: https://bit.ly/42puLF6
Boa sorte! 🍀""",
                reply_markup=reply_markup
            )
        except:
            pass

    await query.answer(
        text=f"""🎉 Você entrou no sorteio!
Já temos {len(participants)} participantes.""",
        show_alert=True
    )

async def sortear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not participants:
        await update.message.reply_text("❌ Nenhum participante no sorteio.")
        return

    count = int(context.args[0]) if context.args else 1
    selected = random.sample(list(participants), min(count, len(participants)))
    winners_formatted = ', '.join(selected)
    await update.message.reply_text(
        f"""🏆 Parabéns, {winners_formatted}!
Você foi o grande vencedor entre {len(participants)} participantes! 🎉
Entre em contato com a equipe para resgatar seu prêmio.
🔗 Ainda não participou? Cadastre-se aqui: https://bit.ly/42puLF6
Fique ligado nos próximos sorteios! 🍀"""
    )
    participants.clear()
    message_id_store.pop(update.effective_chat.id, None)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(join_raffle_callback, pattern="join_raffle"))
    app.add_handler(CommandHandler("sortear", sortear))
    app.run_polling()