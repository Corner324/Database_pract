import logging

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from models import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("database.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Проверяем наличие всех переменных окружения
required_vars = {"DB_NAME": DB_NAME, "DB_HOST": DB_HOST, "DB_PORT": DB_PORT, "DB_USER": DB_USER, "DB_PASS": DB_PASS}
missing_vars = [key for key, value in required_vars.items() if not value]
if missing_vars:
    logger.error(f"Отсутствуют переменные окружения: {missing_vars}")
    raise ValueError(f"Отсутствуют переменные окружения: {missing_vars}")

# Формируем строку подключения
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
logger.info(f"Строка подключения: postgresql://{DB_USER}:[HIDDEN]@{DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    # Создаем движок
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    # Проверяем подключение
    with engine.connect() as connection:
        logger.info("Успешно подключено к базе данных")
        result = connection.execute(text("SELECT 1"))
        logger.info(f"Тестовый запрос выполнен: {result.fetchone()}")

    # Создаем таблицы
    BaseModel.metadata.create_all(engine, checkfirst=True)
    logger.info("Таблицы созданы или уже существуют")

    # Создаем фабрику сессий
    Session = sessionmaker(bind=engine)

    # Проверяем, что сессия привязана
    if not Session.kw.get("bind"):
        logger.error("Сессия не привязана к движку")
        raise ValueError("Сессия не привязана к движку")

except Exception as e:
    logger.error(f"Ошибка подключения к базе данных: {e}")
    raise
