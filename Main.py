from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sys
import pandas as pd
import io

TOKEN = "8467009043:AAF4h0kFcfH_QLisNWru6Cz4d_ZPq-VzRnc"
awaiting_excel = True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет')
    keyboard = [
        ["1.Отчет по выставленному расписанию", "2.Отчет по темам занятия","3.Отчет по студентам"],
        ["4.Отчет по посещаемости студентов", "5.Отчет по проверенным домашним заданиям", "6.Отчет по сданным домашним заданиям"]
        ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)
    await update.message.reply_text("Пожалуйста, загрузите XLS/XLSX файл")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text(f'Ты: "{user_text}"')

async def reader_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global awaiting_excel
    if not awaiting_excel:
        return
    document = update.message.document
    file_name = document.file_name
    if not (file_name.endswith('.xls') or file_name.endswith('.xlsx')):
        await update.message.reply_text("Пожалуйста, загрузите файл с расширением .xls или .xlsx")
        return
    try:
        file = await document.get_file()
        file_bytes = await file.download_as_bytearray()
        
        df = pd.read_excel(io.BytesIO(file_bytes))

        response = f" Файл '{file_name}' успешно получен\n\n"
        response += f"Информация о файле:\n"
        response += f"• Столбцы: {', '.join(df.columns)}\n\n"
        await update.message.reply_text(response)
        awaiting_excel = False

    except Exception as e:
        await update.message.reply_text(f"Ошибка при чтении файла")
        awaiting_excel = False

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, echo))
    app.add_handler(MessageHandler(filters.Document.ALL, reader_text))

    print("Бот запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()