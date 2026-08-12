import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

TOKEN = os.getenv("TOKEN")
jobs = {}

async def send_result(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    resultado = random.choice(["🟢 WIN", "🔴 LOSS", "🟢 WIN", "🟢 WIN"])
    await context.bot.send_message(chat_id=chat_id, text=f"SINAL: {resultado}")

async def send_signal(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    entrada1 = f"{random.randint(1,12)}:{random.randint(0,59):02d}"
    entrada2 = f"{random.randint(1,12)}:{random.randint(0,59):02d}"
    entrada3 = f"{random.randint(1,12)}:{random.randint(0,59):02d}"
    mensagem = f"""
🤖 SINAL DOMINADO
🎯 Entrada 1: {entrada1}
🎯 Entrada 2: {entrada2} 
🎯 Entrada 3: {entrada3}
⏰ Validade: 2 minutos
Boa sorte! 🍀
"""
    await context.bot.send_message(chat_id=chat_id, text=mensagem)
    context.job_queue.run_once(send_result, 120, data=chat_id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in jobs:
        jobs[chat_id].schedule_removal()
    
    # manda 1º sinal em 3 segundos
    context.job_queue.run_once(send_signal, 3, data=chat_id)
    # depois repete a cada 2 minutos
    job = context.job_queue.run_repeating(send_signal, interval=120, first=123, data=chat_id)
    jobs[chat_id] = job
    
      keyboard = [[InlineKeyboardButton("🛑 PARAR SINAIS", callback_data="stop")]]
    await update.message.reply_text(
        "🤖 ROBÔ DOMINADO ONLINE 24H\nSinais a cada 2 minutos!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

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
