
import random
import logging

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# ==================== SETTINGS ====================

TOKEN = "8792780296:AAEPiwjgsRA4wSBcu0FGRdnOv9a5fxnSkms"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Головне меню
MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["🎯 Вікторина", "🧩 Загадки"],
        ["🎲 Випадкове завдання", "🏆 Мої бали"],
        ["ℹ️ Допомога"],
    ],
    resize_keyboard=True,
)


# ==================== QUIZ QUESTIONS ====================

QUIZ = [
    {
        "question": "Яка мова використовується в цьому боті?",
        "answers": ["Java", "Python", "C++", "HTML"],
        "correct": 1,
    },
    {
        "question": "Скільки буде 7 × 8?",
        "answers": ["54", "48", "56", "64"],
        "correct": 2,
    },
    {
        "question": "Яка планета відома як Червона планета?",
        "answers": ["Марс", "Венера", "Сатурн", "Меркурій"],
        "correct": 0,
    },
    {
        "question": "Який тег HTML створює посилання?",
        "answers": ["<p>", "<img>", "<a>", "<h1>"],
        "correct": 2,
    },
    {
        "question": "Який тип даних у Python зберігає True або False?",
        "answers": ["str", "bool", "list", "int"],
        "correct": 1,
    },
]


# ==================== RIDDLES ====================

RIDDLES = [
    {
        "question": "Що має клавіші, але не відкриває дверей?",
        "answer": "клавіатура",
    },
    {
        "question": "Що можна зламати, навіть не торкаючись?",
        "answer": "обіцянку",
    },
    {
        "question": "Удень спить, а вночі світить. Що це?",
        "answer": "місяць",
    },
    {
        "question": "Що постійно йде, але нікуди не приходить?",
        "answer": "час",
    },
    {
        "question": "Що має стрілки, але не стріляє?",
        "answer": "годинник",
    },
]


# ==================== RANDOM TASKS ====================

TASKS = [
    "Назви три свої улюблені комп'ютерні ігри.",
    "Відгадай: що більше — 99 чи 100?",
    "Придумай назву для власної відеогри.",
    "Назви п'ять мов програмування.",
    "Придумай ідею для нового Telegram-бота.",
    "Розв'яжи: 12 × 12.",
    "Назви три планети Сонячної системи.",
    "Придумай загадку для інших гравців.",
]


# ==================== START COMMAND ====================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.setdefault("points", 0)

    user = update.effective_user
    name = user.first_name if user else "гравцю"

    await update.message.reply_text(
        f"Привіт, {name}!\n\n"
        "Я GameBot — твій ігровий помічник.\n"
        "Тут можна проходити вікторини, "
        "відгадувати загадки та заробляти бали.\n\n"
        "Обирай гру в меню нижче!",
        reply_markup=MAIN_MENU,
    )


# ==================== HELP COMMAND ====================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "📖 ДОПОМОГА\n\n"
        "/start — головне меню\n"
        "/help — ця довідка\n"
        "/quiz — почати вікторину\n"
        "/riddle — загадка\n"
        "/task — випадкове завдання\n"
        "/score — переглянути бали\n"
        "/cancel — зупинити поточну гру\n\n"
        "За правильні відповіді у вікторині "
        "ти отримуєш бали!"
    )


# ==================== QUIZ ====================

async def send_quiz_question(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    index = context.user_data["quiz_index"]

    if index >= len(QUIZ):
        points = context.user_data["quiz_points"]
        total = len(QUIZ)

        context.user_data["points"] = (
            context.user_data.get("points", 0) + points
        )

        context.user_data["mode"] = None

        await update.effective_message.reply_text(
            f"🏁 Вікторину завершено!\n\n"
            f"Твій результат: {points} із {total}\n"
            f"Зароблено балів: {points}\n\n"
            "Хочеш зіграти ще раз? Обирай меню!"
        )
        return

    item = QUIZ[index]

    buttons = []

    for answer_index, answer in enumerate(item["answers"]):
        buttons.append([
            InlineKeyboardButton(
                answer,
                callback_data=f"quiz:{index}:{answer_index}",
            )
        ])

    keyboard = InlineKeyboardMarkup(buttons)

    await update.effective_message.reply_text(
        f"🎯 Запитання {index + 1}/{len(QUIZ)}\n\n"
        f"{item['question']}",
        reply_markup=keyboard,
    )


async def start_quiz(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data["mode"] = "quiz"
    context.user_data["quiz_index"] = 0
    context.user_data["quiz_points"] = 0

    await update.effective_message.reply_text(
        "Починаємо вікторину!\n"
        "Обирай одну правильну відповідь."
    )

    await send_quiz_question(update, context)


async def quiz_answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    if context.user_data.get("mode") != "quiz":
        await query.edit_message_text(
            "Ця гра вже завершена. Запусти нову вікторину."
        )
        return

    _, question_text, answer_text = query.data.split(":")
    question_index = int(question_text)
    answer_index = int(answer_text)

    # Захист від повторного натискання старої кнопки
    if question_index != context.user_data["quiz_index"]:
        await query.answer(
            "Це запитання вже пройдено.",
            show_alert=True,
        )
        return

    item = QUIZ[question_index]

    if answer_index == item["correct"]:
        context.user_data["quiz_points"] += 1
        result = "Правильно! Ти отримуєш 1 бал."
    else:
        correct_answer = item["answers"][item["correct"]]
        result = f"Неправильно. Правильна відповідь: {correct_answer}."

    await query.edit_message_text(
        f"{item['question']}\n\n{result}"
    )

    context.user_data["quiz_index"] += 1

    await send_quiz_question(update, context)


# ==================== RIDDLES ====================

async def start_riddle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    riddle = random.choice(RIDDLES)

    context.user_data["mode"] = "riddle"
    context.user_data["riddle_answer"] = riddle["answer"]

    await update.effective_message.reply_text(
        "🧩 ЗАГАДКА\n\n"
        f"{riddle['question']}\n\n"
        "Напиши свою відповідь повідомленням.\n"
        "За правильну відповідь отримаєш 2 бали."
    )


async def check_riddle(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    answer = update.message.text.strip().lower()
    correct = context.user_data.get("riddle_answer", "")

    if answer == correct:
        context.user_data["points"] = (
            context.user_data.get("points", 0) + 2
        )
        context.user_data["mode"] = None

        await update.message.reply_text(
            "Правильно! Ти отримуєш 2 бали."
        )
    else:
        await update.message.reply_text(
            "Не зовсім! Спробуй ще раз.\n"
            "Або напиши /cancel, щоб завершити гру."
        )


# ==================== RANDOM TASK ====================

async def random_task(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    task = random.choice(TASKS)

    await update.effective_message.reply_text(
        "🎲 ТВОЄ ВИПАДКОВЕ ЗАВДАННЯ\n\n"
        f"{task}\n\n"
        "Виконуй завдання та розвивай свої навички!"
    )


# ==================== SCORE ====================

async def show_score(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    points = context.user_data.get("points", 0)

    await update.effective_message.reply_text(
        f"🏆 ТВОЇ РЕЗУЛЬТАТИ\n\n"
        f"Загальна кількість балів: {points}\n\n"
        "Вікторина: 1 бал за правильну відповідь.\n"
        "Загадки: 2 бали за правильну відповідь."
    )


# ==================== CANCEL GAME ====================

async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data["mode"] = None
    context.user_data.pop("riddle_answer", None)

    await update.effective_message.reply_text(
        "Поточну гру завершено.\n"
        "Можеш почати іншу гру в меню.",
        reply_markup=MAIN_MENU,
    )


# ==================== MENU HANDLER ====================

async def menu_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text

    if text == "🎯 Вікторина":
        await start_quiz(update, context)

    elif text == "🧩 Загадки":
        await start_riddle(update, context)

    elif text == "🎲 Випадкове завдання":
        await random_task(update, context)

    elif text == "🏆 Мої бали":
        await show_score(update, context)

    elif text == "ℹ️ Допомога":
        await help_command(update, context)

    elif context.user_data.get("mode") == "riddle":
        await check_riddle(update, context)

    else:
        await update.message.reply_text(
            "Обери дію за допомогою кнопок меню "
            "або напиши /help."
        )


# ==================== MAIN ====================

def main():
    if TOKEN == "ВСТАВ_СЮДИ_СВІЙ_ТОКЕН":
        print("Помилка: встав токен свого Telegram-бота в код.")
        return

    app = Application.builder().token(TOKEN).build()

    # Команди
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quiz", start_quiz))
    app.add_handler(CommandHandler("riddle", start_riddle))
    app.add_handler(CommandHandler("task", random_task))
    app.add_handler(CommandHandler("score", show_score))
    app.add_handler(CommandHandler("cancel", cancel))

    # Кнопки відповідей у вікторині
    app.add_handler(
        CallbackQueryHandler(quiz_answer, pattern=r"^quiz:")
    )

    # Текстові повідомлення та меню
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler)
    )

    print("GameBot запущено!")
    app.run_polling()


if __name__ == "__main__":
    main()
