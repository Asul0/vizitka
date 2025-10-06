import telebot
import logging
import base64
import io
from config import TELEGRAM_BOT_TOKEN, setup_logging_globally, FUSIONBRAIN_URL, FUSIONBRAIN_API_KEY, FUSIONBRAIN_SECRET_KEY
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

participants = {
    "надежда": {
        "name": "Сорванова Надежда Александровна",
        "role": "Специалист по адаптации и анализу",
        "raw_data": "Гибкость, адаптивность, эмпатия, аналитические способности",
        "aliases": ["надежда", "надя", "сорванова", "наденька"],
        "gender": "женщина",
        "age": "27-30"
    },
    "юлия": {
        "name": "Жданова Юлия Борисовна",
        "role": "Инициатор идей и командный игрок",
        "raw_data": "Адаптивность, обучаемость, поиск идей, командная работа. Хочется заниматься внедрением инициатив",
        "aliases": ["юлия", "юля", "жданова", "юлечка"],
        "gender": "женщина",
        "age": "30-35"
    },
    "иван": {
        "name": "Жадан Иван Валерьевич",
        "role": "Идеолог и коммуникатор",
        "raw_data": "Отлично развиваю сырые идеи, большая насмотренность, недовольство окружающими сервисами/организацией быта как потребителя с идеями по развитию. Могу найти общий язык и темы для разговора с любым человеком",
        "aliases": ["иван", "ваня", "жадан", "иваныч"],
        "gender": "мужчина",
        "age": "22-25"
    },
    "евгений": {
        "name": "Сердюков Евгений Александрович",
        "role": "Лидер и визуализатор идей",
        "raw_data": "Готовность формировать здравые идеи и идти к их реализации... Успевает всё, кроме сна...",
        "aliases": ["евгений", "женя", "сердюков", "жека"],
        "gender": "мужчина",
        "age": "28-35"
    },
    "володя": {
        "name": "Атоян Володя Араратович",
        "role": "Разработчик и оптимизатор",
        "raw_data": "Нестандартное мышление, умение оптимизировать процессы, получения результата любыми путями, с нейросетями на ты, практика создании агентов, написания непростых кодов путем вайб кодинга. Легок в общении, командный",
        "aliases": ["Володю", "вова", "атоян", "володик"],
        "gender": "мужчина",
        "age": "23"
    },
    "андрей": {
        "name": "Панин Андрей Александрович",
        "role": "Координатор и идейный вдохновитель",
        "raw_data": "Позитивный и Энергичный... Стрессоустойчив, гибок и легко воспринимаю новую информацию",
        "aliases": ["андрей", "андрюха", "панин", "андрейка"],
        "gender": "мужчина",
        "age": "22-23"
    }
}


summary_system_prompt = """
Ты - ассистент, создающий привлекательные визитки для представления участников команды жюри. 
На основе предоставленных данных о человеке, создай краткое, профессиональное саммари: 
- Начни с имени и роли.
- Опиши ключевые личные качества и сильные стороны.
- Добавь интересные факты или опыт.
- Сделай текст позитивным, вдохновляющим, не более 150 слов.
- Формат: как визитка, с заголовком "Визитка: [Имя]".
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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "Привет! Я - виртуальный гид по команде 'ОгнИИ', где огонь встречается с интеллектом. 😎 Я могу рассказать о наших крутых участниках. Просто скажи: 'расскажи про [имя]' или 'давай про [имя]'. Например, 'расскажи про Надежду'. С кого начнём?"
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()
    found_participant = None
    
    # Проверяем фразы вроде "расскажи про ..." или "давай про ..."
    if "расскажи про " in text or "давай про " in text:
        # Извлекаем имя после фразы
        for data in participants.values():
            for alias in data["aliases"]:
                if f"расскажи про {alias}" in text or f"давай про {alias}" in text:
                    found_participant = data
                    break
            if found_participant:
                break
    else:
        # Проверяем просто имя как отдельное слово
        for data in participants.values():
            if any(alias in text for alias in data["aliases"]):
                found_participant = data
                break
    
    if found_participant:
        raw_data = found_participant['raw_data']
        name = found_participant['name']
        
        summary_user_prompt = f"Создай визитку на основе этих данных: Имя: {found_participant['name']}, Роль: {found_participant['role']}, Данные: {raw_data}"
        summary = gigachat_manager.get_analysis(summary_system_prompt, summary_user_prompt)
        bot.reply_to(message, summary)
        
        image_prompt_user = f"Создай промпт для Kandinsky: {raw_data} (пол: {found_participant['gender']}, возраст: {found_participant['age']})"
        image_prompt = gigachat_manager.get_analysis(image_prompt_system, image_prompt_user)
        logger.info(f"Генерируем изображение с промптом: {image_prompt}")
        
        if fusionbrain_api and pipeline_id:
            logger.info(f"Проверяем доступность для {name}")
            uuid = fusionbrain_api.generate(image_prompt, pipeline_id)
            files = fusionbrain_api.check_generation(uuid)
            try:
                uuid = fusionbrain_api.generate(image_prompt, pipeline_id)
                files = fusionbrain_api.check_generation(uuid)
                if files and len(files) > 0:
                    img_base64 = files[0]
                    img_data = base64.b64decode(img_base64)
                    bio = io.BytesIO(img_data)
                    bio.name = 'generated_image.jpg'
                    bot.send_photo(message.chat.id, bio, caption=f"Портрет {name} от Kandinsky 🎨")
                else:
                    bot.reply_to(message, "Не удалось сгенерировать изображение (возможно, модерация или ошибка).")
            except Exception as e:
                logger.error(f"Ошибка генерации изображения: {e}")
                bot.reply_to(message, f"Текст готов, но изображение не сгенерировалось: {str(e)}")
        else:
            bot.reply_to(message, "Текст готов! Генерация изображений временно недоступна.")
    else:
        participant_names = ", ".join([data['name'] for data in participants.values()])
        bot.reply_to(message, f"Не понял, про кого ты спрашиваешь. Вот список участников: {participant_names}. Попробуй сказать 'расскажи про [имя]' или 'давай про [имя]'.")

if __name__ == "__main__":
    logger.info("Запуск Telegram-бота...")
    bot.polling(none_stop=True)