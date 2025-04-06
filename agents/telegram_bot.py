import os
import subprocess
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from saci_orchestrator.orchestrator import SACIOrchestrator

logging.basicConfig(level=logging.INFO)


class TelegramBot:
    def __init__(self, token: str):
        self.orchestrator = SACIOrchestrator()
        self.application = Application.builder().token(token).build()

        # Обработчик команды /start
        self.application.add_handler(CommandHandler("start", self.start))
        # Обработчик текстовых сообщений
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Привет! Отправь описание технологии, которую хочешь разработать."
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_goal = update.message.text
        # Передаем цель в SACI-оркестратор
        self.orchestrator.set_goal(user_goal)
        tasks = self.orchestrator.plan_tasks()

        response = "Цель установлена. План задач:\n" + "\n".join(
            f"{i+1}. {task}" for i, task in enumerate(tasks)
        )
        await update.message.reply_text(response)

    def run(self):
        self.application.run_polling()


if __name__ == "__main__":
    # Замените на свой токен Telegram Bot
    TOKEN = "7207967791:AAE718TLFOyr71INFTu-qYa4dzcf8PDawPM"
    bot = TelegramBot(TOKEN)
    bot.run()
