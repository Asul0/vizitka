import telebot
import logging
import base64
import io
from config import (
    TELEGRAM_BOT_TOKEN,
    setup_logging_globally,
    FUSIONBRAIN_URL,
    FUSIONBRAIN_API_KEY,
    FUSIONBRAIN_SECRET_KEY,
)
from llm_agent import GigaChatManagerAssistant
from image_generator import FusionBrainAPI

setup_logging_globally()
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
gigachat_manager = GigaChatManagerAssistant()

try:
    fusionbrain_api = FusionBrainAPI(
        FUSIONBRAIN_URL, FUSIONBRAIN_API_KEY, FUSIONBRAIN_SECRET_KEY
    )
    pipeline_id = fusionbrain_api.get_pipeline()
    logger.info(f"FusionBrain pipeline ID: {pipeline_id}")
except Exception as e:
    logger.error(f"Ошибка инициализации FusionBrain: {e}")
    fusionbrain_api = None
    pipeline_id = None

# Файл: bot.py

participants = {
    "надежда": {
        "name": "Сорванова Надежда Александровна",
        "role": "Специалист по адаптации и анализу",
        "raw_data": "Гибкость, адаптивность, эмпатия, аналитические способности",
        "aliases": ["надежда", "надя", "сорванова", "наденька"],
        "gender": "женщина",
        "age": "27-30",
        "interesting_facts": [
            "Впервые встав на коньки в подростковом возрасте, сразу начала уверенно кататься.",
            "Каждый день начинает с 5 минут тишины, чтобы настроиться на продуктивный день.",
            "Любит проводить свободное время с детьми за просмотром мультфильмов.",
        ],
    },
    "юлия": {
        "name": "Жданова Юлия Борисовна",
        "role": "Инициатор идей и командный игрок",
        "raw_data": "Адаптивность, обучаемость, поиск идей, командная работа. Хочется заниматься внедрением инициатив",
        "aliases": ["юлия", "юля", "жданова", "юлечка"],
        "gender": "женщина",
        "age": "30-35",
        "interesting_facts": [
            "Счастливая мама ребенка 4.5 лет.",
            "В 33 года встала на сноуборд и спустилась с Эльбруса.",
            "В 34 года освоила вейкборд.",
            "Любит читать, ходить в театры и изучать новое.",
        ],
    },
    "иван": {
        "name": "Жадан Иван Валерьевич",
        "role": "Идеолог и коммуникатор",
        "raw_data": "Отлично развиваю сырые идеи, большая насмотренность, недовольство окружающими сервисами/организацией быта как потребителя с идеями по развитию. Могу найти общий язык и темы для разговора с любым человеком",
        "aliases": ["иван", "ваня", "жадан", "иваныч"],
        "gender": "мужчина",
        "age": "22-25",
        "interesting_facts": [
            "Родился на Камчатке, а сейчас работает в Сбере в Воронеже.",
            "За полтора года работы получил свидетельство о признании от председателя ЦЧБ.",
            "Покорил 3 вулкана на Камчатке.",
            "Мечтает исполнить песню в жанре поп-рок в качестве уличного музыканта.",
            "Очень боится глубины и любит рисовать.",
        ],  # Пока пусто, можно будет добавить
    },
    "евгений": {
        "name": "Сердюков Евгений Александрович",
        "role": "Лидер и визуализатор идей",
        "raw_data": "Готовность формировать здравые идеи и идти к их реализации... Успевает всё, кроме сна...",
        "aliases": ["евгений", "женя", "сердюков", "жека"],
        "gender": "мужчина",
        "age": "28-35",
        "interesting_facts": ["Люблю рисовать"],
    },
    "володя": {
        "name": "Атоян Володя Араратович",
        "role": "Разработчик и оптимизатор",
        "raw_data": "Нестандартное мышление, умение оптимизировать процессы, получения результата любыми путями, с нейросетями на ты, практика создании агентов, написания непростых кодов путем вайб кодинга. Легок в общении, командный",
        "aliases": ["Володю", "вова", "атоян", "володик"],
        "gender": "мужчина",
        "age": "23",
        "interesting_facts": [
            "В детстве мечтал стать профессиональным футболистом.",
            "Глубоко интересуется нейросетями: умеет создавать как простых ботов, так и полноценных ИИ-агентов.",
        ],
    },
    "андрей": {
        "name": "Панин Андрей Александрович",
        "role": "Координатор и идейный вдохновитель",
        "raw_data": "Позитивный и Энергичный... Стрессоустойчив, гибок и легко воспринимаю новую информацию",
        "aliases": ["андрей", "андрюха", "панин", "андрейка"],
        "gender": "мужчина",
        "age": "22-23",
        "interesting_facts": [
            "10 лет занимался легкой атлетикой (1-й взрослый разряд).",
            "Окончил университет с красным дипломом.",
            "Иногда играет на укулеле.",
            "Свой первый сериал посмотрел только год назад.",
            "Владелец двух улиток и котенка.",
        ],
    },
}

summary_system_prompt = """
Ты — ассистент, который пишет профессиональные саммари для визиток.
Твоя задача — на основе предоставленных данных составить сдержанный и объективный текст.

Правила:
1.  Начни с имени и роли.
2.  Опиши ключевые качества, строго придерживаясь исходного текста.
3.  **Не преувеличивай и не добавляй от себя громких эпитетов** (избегай слов вроде "гениальный", "мастерски", "вдохновляет", "невероятно").
4.  Сохраняй профессиональный, но позитивный тон.
5.  Объем — не более 150 слов.
6.  Формат: заголовок "**Визитка: [Имя]**".

Пример того, как нужно делать:
---
Входные данные: "Нестандартное мышление, умение оптимизировать процессы, получения результата любыми путями, с нейросетями на ты, практика создании агентов, написания непростых кодов путем вайб кодинга. Легок в общении, командный"

Хороший результат:
"**Визитка: Атоян Володя Араратович**

Разработчик и оптимизатор

Обладает нестандартным мышлением и умением оптимизировать рабочие процессы для достижения результата. Имеет практический опыт в работе с нейросетями и создании ИИ-агентов. Легко находит общий язык с коллегами и эффективно работает в команде."
---
"""

image_prompt_system = """
На основе данных о человеке, создай простой, позитивный промпт для портрета в Kandinsky. 
Промпт на русском, до 200 символов, без слов: нейросети, код, серверы, технологии. Включи:
- Портрет [Имя] ([пол: мужчина/женщина]) в роли [role], возраст [age].
- Внешность по качествам (улыбка для дружелюбности, уверенность для лидера).
- Фон: офис, природа или нейтральная комната.
- Стиль: PIXAR.
Пример: 'Реалистичный портрет женщины-аналитика 30-35 лет в офисе, улыбка, светлое освещение'.
"""


@bot.message_handler(commands=["start"])
def send_welcome(message):
    welcome_text = "Привет! Я - виртуальный гид по команде 'ОгнИИ', где огонь встречается с интеллектом. 😎 Я могу рассказать о наших крутых участниках. Просто скажи: 'расскажи про [имя]' или 'давай про [имя]'. Например, 'расскажи про Надежду'. С кого начнём?"
    bot.reply_to(message, welcome_text)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()
    found_participant = None

    # Сначала ищем по ключевым фразам "расскажи про"
    trigger_phrases = ["расскажи про ", "давай про "]
    for phrase in trigger_phrases:
        if phrase in text:
            search_query = text.split(phrase)[1].strip()
            for key, data in participants.items():
                if search_query in data["aliases"]:
                    found_participant = data
                    break
            if found_participant:
                break

    # Если не нашли, ищем по простому упоминанию имени
    if not found_participant:
        for data in participants.values():
            if any(
                f" {alias} " in f" {text} " or text == alias
                for alias in data["aliases"]
            ):
                found_participant = data
                break

    if found_participant:
        name = found_participant["name"]

        # --- БЛОК ГЕНЕРАЦИИ ТЕКСТОВОЙ ВИЗИТКИ ---

        summary_user_prompt = f"Создай визитку на основе этих данных: Имя: {found_participant['name']}, Роль: {found_participant['role']}, Данные: {found_participant['raw_data']}"
        summary = gigachat_manager.get_analysis(
            summary_system_prompt, summary_user_prompt
        )

        final_message = summary
        facts = found_participant.get("interesting_facts", [])

        if facts:
            facts_text = "\n\n**Интересные факты:**\n"
            for fact in facts:
                facts_text += f"• {fact}\n"
            final_message += facts_text

        # ИЗМЕНЕНИЕ ЗДЕСЬ: bot.reply_to -> bot.send_message
        bot.send_message(message.chat.id, final_message, parse_mode="Markdown")

        # --- БЛОК ГЕНЕРАЦИИ ИЗОБРАЖЕНИЯ ---

        image_prompt_user = f"Создай промпт для Kandinsky: {found_participant['raw_data']} (пол: {found_participant['gender']}, возраст: {found_participant['age']})"
        image_prompt = gigachat_manager.get_analysis(
            image_prompt_system, image_prompt_user
        )
        logger.info(f"Генерируем изображение для '{name}' с промптом: {image_prompt}")

        if fusionbrain_api and pipeline_id:
            try:
                uuid = fusionbrain_api.generate(image_prompt, pipeline_id)
                files = fusionbrain_api.check_generation(uuid)

                if files and len(files) > 0:
                    img_base64 = files[0]
                    img_data = base64.b64decode(img_base64)
                    bio = io.BytesIO(img_data)
                    bio.name = "generated_image.jpg"
                    bot.send_photo(
                        message.chat.id, bio, caption=f"Портрет {name} от Kandinsky 🎨"
                    )
                else:
                    logger.warning(
                        f"Не удалось сгенерировать изображение для '{name}'. Ответ от API пустой."
                    )
                    # ИЗМЕНЕНИЕ ЗДЕСЬ: bot.reply_to -> bot.send_message
                    bot.send_message(
                        message.chat.id,
                        "Не удалось сгенерировать изображение (возможно, сработала модерация или произошла ошибка).",
                    )

            except Exception as e:
                logger.error(
                    f"Критическая ошибка при генерации изображения для '{name}': {e}"
                )
                # ИЗМЕНЕНИЕ ЗДЕСЬ: bot.reply_to -> bot.send_message
                bot.send_message(
                    message.chat.id,
                    f"Текст готов, но при создании изображения произошла ошибка: {str(e)}",
                )
        else:
            # ИЗМЕНЕНИЕ ЗДЕСЬ: bot.reply_to -> bot.send_message
            bot.send_message(
                message.chat.id,
                "Текст готов! Генерация изображений временно недоступна.",
            )

    else:
        # Если участник не найден, отправляем сообщение с перечислением доступных
        participant_names = ", ".join(
            [data["aliases"][0].capitalize() for data in participants.values()]
        )
        # ИЗМЕНЕНИЕ ЗДЕСЬ: bot.reply_to -> bot.send_message
        bot.send_message(
            message.chat.id,
            f"Не понял, о ком ты. Я могу рассказать про: {participant_names}. Попробуй, например, так: 'расскажи про Надю'.",
        )


if __name__ == "__main__":
    logger.info("Запуск Telegram-бота...")
    bot.polling(none_stop=True)
