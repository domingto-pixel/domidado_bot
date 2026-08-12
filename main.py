import os
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TOKEN")

jobs = {}
pendentes = {}

async def send_result(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    if chat_id not in pendentes:
        return
    sinal = pendentes[chat_id]
    deu_win = random.random() < 0.65
    resultado = "✅ VITÓRIA" if deu_win else "❌ DERROTA"
    mensagem = f"📊\n RESULTADO DO SINAL\n🎮 Jogo: BAC BO\n🎯 Entrada: {sinal['hora']}\n{resultado}"
    await context.bot.send_message(chat_id=chat_id, text=mensagem)
    del pendentes[chat_id]

async def send_signal(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    aposta = random.choice(["BANQUEIRO", "JOGADOR"])
    hora_entrada = datetime.now().strftime("%H:%M")
    pendentes[chat_id] = {"aposta": aposta, "hora": hora_entrada}
    mensagem = f"🚨 NOVO SINAL 🚨\n🎮 Jogo: BAC BO\n🎯 Entrada: {hora_entrada}\n APÓS 1 VELA: {aposta}"
    await context.bot.send_message(chat_id=chat_id, text=mensagem)
    context.job_queue.run_once(send_result, 30, data=chat_id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in jobs:
        jobs[chat_id].schedule_removal()
    context.job_queue.run_once(send_signal, 3, data=chat_id)
    job = context.job_queue.run_repeating(send_signal, interval=120, first=123, data=chat_id)
    jobs[chat_id] = job
    keyboard = [[InlineKeyboardButton("🛑 PARAR SINAIS", callback_data="stop")]]
    await update.message.reply_text("🤖 ROBÔ DOMINADO ONLINE 24H\nSinais a cada 2 minutos!", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    if query.data == "stop":
        if chat_id in jobs:
            jobs[chat_id].schedule_removal()
            del jobs[chat_id]
        await query.edit_message_text("🛑 Sinais pausados!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("bot rodando 24h no Render 🚀")
    app.run_polling()

if __name__ == '__main__':
    main()
