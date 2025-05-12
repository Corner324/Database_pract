import logging

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from models import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("database.log", encoding="utf-8"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    BaseModel.metadata.create_all(engine, checkfirst=True)
    logger.info("Таблицы созданы или уже существуют")

    Session = sessionmaker(bind=engine)

    if not Session.kw.get("bind"):
        logger.error("Сессия не привязана к движку")
        raise ValueError("Сессия не привязана к движку")

except Exception as e:
    logger.error(f"Ошибка подключения к базе данных: {e}")
    raise
