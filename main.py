
import logging
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Pegando o token do ambiente Railway
TOKEN = os.getenv("BOT_TOKEN")

# Mudança: Agora um dicionário para armazenar {user_id: (username, first_name)}
participants = {}

message_id_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🎉 Participar", callback_data="join_raffle")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Clique no botão para participar do sorteio! 🎲", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "join_raffle":
        user = query.from_user
        participants[user.id] = (user.username, user.first_name)
        await query.edit_message_text(text="Você entrou no sorteio! Boa sorte! 🍀")

async def raffle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not participants:
        await update.message.reply_text("Nenhum participante registrado ainda.")
        return

    winners_count = 5  # Número de ganhadores
    winners = random.sample(list(participants.keys()), min(winners_count, len(participants)))

    winners_text = "OS GANHADORES DAS BANCAS SÃO 🎉🔥:

"
    for winner_id in winners:
        username, first_name = participants[winner_id]
        if username:
            winners_text += f"@{username}, "
        else:
            winners_text += f"[{first_name}](tg://user?id={winner_id}), "

    winners_text = winners_text.rstrip(", ")  # Remove a última vírgula
    winners_text += f"

O número de participantes neste sorteio foi {len(participants)} pessoas 🌎"

    await update.message.reply_text(winners_text, parse_mode='Markdown')

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("raffle", raffle))

    app.run_polling()

if __name__ == '__main__':
    main()
