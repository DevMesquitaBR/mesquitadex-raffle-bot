
import logging
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")

# Configura o log
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

participants = {}
message_id_store = {"chat_id": None, "message_id": None}

# Configurações avançadas
settings = {
    "subscribe_channels": [],
    "raffle_message": None,
    "winner_message": None,
    "delete_original": True
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raffle_text = settings["raffle_message"] or (
        "🎉 Sorteio Aberto! 🎉\n"
        "Já temos 0 participantes!\n"
        "Clique no botão para participar! 🚀\n"
        "Boa sorte! 🍀"
    )
    keyboard = [[InlineKeyboardButton("🎉 Participar", callback_data="join_raffle")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_message = await update.message.reply_text(raffle_text, reply_markup=reply_markup)
    message_id_store["chat_id"] = sent_message.chat.id
    message_id_store["message_id"] = sent_message.message_id

async def randy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "join_raffle":
        user = query.from_user
        participants[user.id] = (user.username, user.first_name)

        try:
            raffle_text = settings["raffle_message"] or (
                f"🎉 Sorteio Aberto! 🎉\n"
                f"Já temos {len(participants)} participantes!\n"
                f"Clique no botão para participar! 🚀\n"
                f"Boa sorte! 🍀"
            )
            await context.bot.edit_message_text(
                chat_id=message_id_store["chat_id"],
                message_id=message_id_store["message_id"],
                text=raffle_text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🎉 Participar", callback_data="join_raffle")]]
                )
            )
        except Exception as e:
            logging.error(f"Erro ao editar mensagem: {e}")

async def participants_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not participants:
        await update.message.reply_text("Nenhum participante ainda. 🚫")
        return

    participant_lines = []
    for user_id, (username, first_name) in participants.items():
        if username:
            participant_lines.append(f"@{username}")
        else:
            participant_lines.append(f"{first_name}")

    participants_text = "👥 Participantes Atuais:\n" + "\n".join(participant_lines)
    await update.message.reply_text(participants_text)

async def raffle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not participants:
        await update.message.reply_text("Nenhum participante registrado ainda. 🚫")
        return

    try:
        winners_count = int(context.args[0]) if context.args else 5
    except:
        winners_count = 5

    eligible = []
    for user_id, (username, first_name) in participants.items():
        if settings["subscribe_channels"]:
            try:
                member_status = await context.bot.get_chat_member(settings["subscribe_channels"][0], user_id)
                if member_status.status not in ["member", "administrator", "creator"]:
                    continue
            except:
                continue
        eligible.append(user_id)

    if not eligible:
        await update.message.reply_text("Nenhum participante elegível para o sorteio. 🚫")
        return

    winners = random.sample(eligible, min(winners_count, len(eligible)))

    winners_text = settings["winner_message"] or '🏆 GANHADORES 🏆\n\n'

    for winner_id in winners:
        username, first_name = participants[winner_id]
        if username:
            winners_text += f"@{username}, "
        else:
            winners_text += f"[{first_name}](tg://user?id={winner_id}), "

    winners_text = winners_text.rstrip(", ")
    winners_text += f"\n\nNúmero total de participantes: {len(participants)} 🌎"

    await update.message.reply_text(winners_text, parse_mode='Markdown')

    if settings["delete_original"] and message_id_store["message_id"]:
        try:
            await context.bot.delete_message(chat_id=message_id_store["chat_id"], message_id=message_id_store["message_id"])
        except:
            pass

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    participants.clear()
    await update.message.reply_text("✅ Lista de participantes resetada com sucesso!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📋 *Comandos Disponíveis:*

"
        "/start ou /randy - Iniciar um sorteio
"
        "/participants - Ver participantes
"
        "/raffle [quantidade] - Sortear participantes
"
        "/subscribe @canal1 - Definir canal obrigatório
"
        "/nosubscribe - Liberar inscrição
"
        "/raffleMessage [texto] - Customizar mensagem do sorteio
"
        "/noRaffleMessage - Usar mensagem padrão
"
        "/winnerMessage [texto] - Customizar mensagem dos ganhadores
"
        "/noWinnerMessage - Usar mensagem padrão de ganhadores
"
        "/nodelete - Não apagar mensagem após sorteio
"
        "/reset - Resetar participantes
"
        "/help - Mostrar ajuda
"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Você precisa mencionar o canal. Exemplo: /subscribe @canal")
        return
    settings["subscribe_channels"] = context.args
    await update.message.reply_text(f"✅ Participantes precisarão estar inscritos em: {' '.join(context.args)}")

async def nosubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings["subscribe_channels"] = []
    await update.message.reply_text("✅ Liberado! Não é mais necessário inscrição para participar.")

async def raffleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings["raffle_message"] = " ".join(context.args)
    await update.message.reply_text("✅ Mensagem do sorteio personalizada!")

async def noRaffleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings["raffle_message"] = None
    await update.message.reply_text("✅ Mensagem do sorteio voltou ao padrão.")

async def winnerMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings["winner_message"] = " ".join(context.args)
    await update.message.reply_text("✅ Mensagem dos ganhadores personalizada!")

async def noWinnerMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings["winner_message"] = None
    await update.message.reply_text("✅ Mensagem dos ganhadores voltou ao padrão.")

async def nodelete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings["delete_original"] = False
    await update.message.reply_text("✅ Agora o bot não apagará a mensagem original após o sorteio.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("randy", randy))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("participants", participants_list))
    app.add_handler(CommandHandler("raffle", raffle))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("nosubscribe", nosubscribe))
    app.add_handler(CommandHandler("raffleMessage", raffleMessage))
    app.add_handler(CommandHandler("noRaffleMessage", noRaffleMessage))
    app.add_handler(CommandHandler("winnerMessage", winnerMessage))
    app.add_handler(CommandHandler("noWinnerMessage", noWinnerMessage))
    app.add_handler(CommandHandler("nodelete", nodelete))

    app.run_polling()

if __name__ == '__main__':
    main()
