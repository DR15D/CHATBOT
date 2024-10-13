from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from transformers import pipeline
import ollama

gpt2_pipeline = pipeline('text-generation', model='gpt2')

user_model_selection = {}

def gpt2_response(prompt):
    return gpt2_pipeline(prompt, max_length=100, num_return_sequences=1)[0]['generated_text']

def llama_response(prompt):
    return ollama.generate(model="llama3.2", prompt=prompt)['response']

async def start(update: Update, context):
    keyboard = [
        [
            InlineKeyboardButton("GPT-2", callback_data='gpt2'),
            InlineKeyboardButton("LLaMA 3.2", callback_data='llama')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Привет! Выберите модель для ответа:",
        reply_markup=reply_markup
    )
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - Перезапустить бота и выбрать модель\n"
        "/current_model - Показать текущую выбранную модель\n"
        "/help - Показать доступные команды"
    )

async def help_command(update: Update, context):
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - Перезапустить бота и выбрать модель\n"
        "/current_model - Показать текущую выбранную модель\n"
        "/help - Показать доступные команды"
    )

async def button(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_model_selection[user_id] = query.data
    await query.edit_message_text(f"Вы выбрали модель: {query.data.upper()}")

async def current_model(update: Update, context):
    user_id = update.message.from_user.id
    model = user_model_selection.get(user_id, 'gpt2')
    await update.message.reply_text(f"Текущая выбранная модель: {model.upper()}")

async def handle_message(update: Update, context):
    user_input = update.message.text
    user_id = update.message.from_user.id
    model = user_model_selection.get(user_id, 'gpt2')  # GPT-2 по умолчанию

    if model == 'gpt2':
        response = gpt2_response(user_input)
    else:
        response = llama_response(user_input)

    await update.message.reply_text(response)

if __name__ == '__main__':
    TOKEN = '7755360720:AAFl5JHFZ_Ek0c7BQRt3eFYwp10tJ76tid0'

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("current_model", current_model))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен!")
    app.run_polling()
