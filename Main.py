from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import sys
import os
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), 'handlers'))

from handlers.schedule_report import ScheduleReportHandler
from handlers.lesson_topics import LessonTopicsHandler
from handlers.students_report import StudentsReportHandler
from handlers.attendance_report import AttendanceReportHandler
from handlers.checked_hw_report import CheckedHWReportHandler
from handlers.submitted_hw_report import SubmittedHWReportHandler

TOKEN = "8467009043:AAF4h0kFcfH_QLisNWru6Cz4d_ZPq-VzRnc"

SELECTING_OPTION, WAITING_FILE = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["1. Отчет по расписанию", "2. Отчет по темам", "3. Отчет по студентам"],
        ["4. Отчет по посещаемости", "5. Отчет по проверке ДЗ", "6. Отчет по сдаче ДЗ"]
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите тип отчета:", reply_markup=reply_markup)
    return SELECTING_OPTION

async def handle_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    options = {
        "1.": (1, "Отчет по расписанию", "расписанием"),
        "2.": (2, "Отчет по темам занятия", "темами занятий"),
        "3.": (3, "Отчет по студентам", "данными студентов"),
        "4.": (4, "Отчет по посещаемости", "посещаемостью"),
        "5.": (5, "Отчет по проверенным ДЗ", "проверкой ДЗ"),
        "6.": (6, "Отчет по сданным ДЗ", "сдачей ДЗ")
    }
    
    for prefix, (num, name, desc) in options.items():
        if prefix in user_text:
            context.user_data['selected_option'] = num
            context.user_data['report_name'] = name
            context.user_data['report_desc'] = desc
            
            await update.message.reply_text(f"Вы выбрали: {name}\n\nЗагрузите Excel файл с {desc}.")
            return WAITING_FILE
    
    await update.message.reply_text("Выберите опцию из меню.")
    return SELECTING_OPTION

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'selected_option' not in context.user_data:
        await update.message.reply_text("Сначала выберите тип отчета из меню.")
        return SELECTING_OPTION
    
    document = update.message.document
    file_name = document.file_name
    
    if not (file_name.endswith('.xls') or file_name.endswith('.xlsx')):
        await update.message.reply_text("Загрузите файл .xls или .xlsx")
        return WAITING_FILE
    
    try:
        await update.message.reply_text("Обрабатываю файл...")
        file = await document.get_file()
        file_bytes = await file.download_as_bytearray()
        
        option = context.user_data['selected_option']
        
        handlers = {
            1: (ScheduleReportHandler, "расписанию"),
            2: (LessonTopicsHandler, "темам занятий"),
            3: (StudentsReportHandler, "студентам"),
            4: (AttendanceReportHandler, "посещаемости"),
            5: (CheckedHWReportHandler, "проверенным ДЗ"),
            6: (SubmittedHWReportHandler, "сданным ДЗ")
        }
        
        HandlerClass, report_name = handlers[option]
        handler = HandlerClass(file_bytes, file_name)
        result = handler.get_result()
        
        header = f"ОТЧЕТ ПО {report_name.upper()} ГОТОВ!\n📄 Файл: {file_name}\n\n"
        
        if isinstance(result, list):
            first_part = header + result[0]
            await _send_message(update, first_part)
            
            for i, part in enumerate(result[1:], 2):
                await asyncio.sleep(0.3)
                part_header = f"\nЧасть {i} из {len(result)}:\n"
                await _send_message(update, part_header + part)
            
            await update.message.reply_text(f"Отчет полностью сформирован!\nВсего частей: {len(result)}")
        else:
            full_response = header + str(result)
            await _send_message(update, full_response)
        
        await update.message.reply_text("Загрузите новый файл или выберите другой отчет.")
        return WAITING_FILE
        
    except Exception as e:
        error_msg = f"Ошибка: {str(e)}\n\nПроверьте формат и структуру файла."
        await update.message.reply_text(error_msg)
        return WAITING_FILE

async def _send_message(update: Update, text: str):
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            await update.message.reply_text(part)
            await asyncio.sleep(0.1)
    else:
        await update.message.reply_text(text)

def main():
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_option)],
            WAITING_FILE: [
                MessageHandler(filters.Document.ALL, handle_file),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_option)
            ]
        },
        fallbacks=[]
    )
    
    app.add_handler(conv_handler)
    
    print("Бот запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()