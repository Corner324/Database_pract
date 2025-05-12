import logging
import os
import ssl
import urllib.request
from datetime import date, datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
from database import Session
from models import SpimexTradingResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("spimex_parser.log", encoding="utf-8"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

ssl._create_default_https_context = ssl._create_unverified_context


def get_bulletin_urls(start_date: date, end_date: date) -> list:
    """Парсит сайт SPIMEX и возвращает список URL бюллетеней за указанный период."""
    base_url = "https://spimex.com/markets/oil_products/trades/results/"
    bulletin_urls = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()

        logger.info(f"Успешно получен ответ от {base_url}, длина HTML: {len(response.text)}")

        soup = BeautifulSoup(response.text, "html.parser")

        links = soup.find_all("a", class_="accordeon-inner__item-title link xls")
        logger.info(f"Найдено {len(links)} ссылок с классом 'accordeon-inner__item-title link xls'")

        for link in links:
            href = link.get("href")  # type: ignore
            if not href:
                logger.debug("Пропущена ссылка без href")
                continue

            href = href.split("?")[0]  # type: ignore

            if "/upload/reports/oil_xls/oil_xls_" in href and href.endswith(".xls"):
                try:
                    file_date_str = href.split("oil_xls_")[1][:8]
                    file_date = datetime.strptime(file_date_str, "%Y%m%d").date()
                    if start_date <= file_date <= end_date:
                        full_url = href if href.startswith("http") else f"https://spimex.com{href}"
                        bulletin_urls.append((full_url, file_date))
                        logger.debug(f"Добавлена ссылка: {full_url}, дата: {file_date}")
                    else:
                        logger.debug(f"Ссылка {href} вне диапазона дат")
                except (IndexError, ValueError) as e:
                    logger.warning(f"Не удалось извлечь дату из ссылки {href}: {e}")
            else:
                logger.debug(f"Пропущена ссылка {href}: не соответствует шаблону oil_xls_")

        logger.info(f"Найдено {len(bulletin_urls)} подходящих бюллетеней")
        return bulletin_urls
    except Exception as e:
        logger.error(f"Ошибка при парсинге сайта {base_url}: {e}")
        return []


def download_bulletin(url: str, output_path: str) -> bool:
    """Загружает бюллетень по указанному URL."""
    try:
        if os.path.exists(output_path):
            logger.info(f"Файл {output_path} уже существует, пропускаем загрузку")
            return True
        urllib.request.urlretrieve(url, output_path)
        logger.info(f"Бюллетень загружен: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при загрузке бюллетеня {url}: {e}")
        return False


def parse_bulletin(file_path: str, trade_date: date) -> pd.DataFrame:
    """Парсит Excel-бюллетень и возвращает DataFrame."""
    try:
        df = pd.read_excel(file_path, sheet_name=0, header=None)

        header_row_index = 6
        if len(df) <= header_row_index:
            logger.error(f"Файл {file_path} слишком короткий, нет строки с заголовками")
            return None  # type: ignore

        headers = df.iloc[header_row_index].fillna("").tolist()

        headers_clean = [h.replace("\n", " ").strip() for h in headers[1:]]

        required_columns = {
            "Код Инструмента": "exchange_product_id",
            "Наименование Инструмента": "exchange_product_name",
            "Базис поставки": "delivery_basis_name",
            "Объем Договоров в единицах измерения": "volume",
            "Обьем Договоров, руб.": "total",
            "Количество Договоров, шт.": "count",
        }

        missing_cols = [col for col in required_columns if col not in headers_clean]
        if missing_cols:
            logger.error(f"Отсутствуют столбцы в {file_path}: {missing_cols}")
            return None  # type: ignore

        data_rows = []
        for i in range(8, len(df)):
            row = df.iloc[i].tolist()
            if pd.isna(row[1]) or row[1] == "" or row[1] == "Код Инструмента" or row[1].startswith("Код"):
                logger.debug(f"Пропущена строка {i + 1}: содержит пустое значение или заголовок")
                break
            data_rows.append(row[1:])

        if not data_rows:
            logger.warning(f"Нет данных в {file_path} после строки с заголовками")
            return None  # type: ignore

        data_df = pd.DataFrame(data_rows, columns=headers_clean)
        logger.debug(f"Первые 5 строк данных:\n{data_df.head(5).to_string()}")

        for col in ["Объем Договоров в единицах измерения", "Обьем Договоров, руб.", "Количество Договоров, шт."]:
            data_df[col] = data_df[col].replace("-", pd.NA)
            data_df[col] = pd.to_numeric(data_df[col], errors="coerce").fillna(0)

        data_df = data_df[data_df["Количество Договоров, шт."] > 0]

        data_df = data_df[list(required_columns.keys())].rename(columns=required_columns)

        data_df = data_df[~data_df["exchange_product_id"].str.contains("Итог", case=False, na=False)]

        data_df["exchange_product_id"] = data_df["exchange_product_id"].astype(str)
        data_df["exchange_product_name"] = data_df["exchange_product_name"].astype(str)
        data_df["delivery_basis_name"] = data_df["delivery_basis_name"].astype(str)
        data_df["oil_id"] = data_df["exchange_product_id"].str[:4].astype(str)
        data_df["delivery_basis_id"] = data_df["exchange_product_id"].str[4:7].astype(str)
        data_df["delivery_type_id"] = data_df["exchange_product_id"].str[-1].astype(str)
        data_df["volume"] = data_df["volume"].astype(float)
        data_df["total"] = data_df["total"].astype(float)
        data_df["count"] = data_df["count"].astype(int)
        data_df["date"] = trade_date
        data_df["created_on"] = pd.to_datetime(datetime.now())
        data_df["updated_on"] = pd.to_datetime(datetime.now())

        logger.debug(f"Значения столбца date: {data_df['date'].head(5).to_list()}")
        logger.debug(f"Тип значений столбца date: {type(data_df['date'].iloc[0])}")

        logger.debug(f"Столбцы DataFrame: {data_df.columns.tolist()}")
        logger.debug(f"Типы данных:\n{data_df.dtypes}")
        logger.debug(f"Первые 5 строк после обработки:\n{data_df.head(5).to_string()}")

        logger.info(f"Спарсено {len(data_df)} записей из {file_path}")
        return data_df
    except Exception as e:
        logger.error(f"Ошибка при парсинге {file_path}: {e}")
        return None  # type: ignore


def save_to_database(data_df: pd.DataFrame, session):
    """Сохраняет данные в PostgreSQL."""
    try:
        if data_df.empty:
            logger.info("Нет данных для сохранения")
            session.commit()
            logger.info("Данные успешно сохранены в базу данных (пустой DataFrame)")
            return

        logger.info(f"Сохранение {len(data_df)} записей в базу данных")

        if not hasattr(session, "bind") or session.bind is None:
            logger.error("Сессия не привязана к базе данных")
            raise ValueError("Сессия не привязана к базе данных")

        expected_dtypes = {
            "exchange_product_id": (str, "string", "object"),
            "exchange_product_name": (str, "string", "object"),
            "oil_id": (str, "string", "object"),
            "delivery_basis_id": (str, "string", "object"),
            "delivery_basis_name": (str, "string", "object"),
            "delivery_type_id": (str, "string", "object"),
            "volume": (float, "float64"),
            "total": (float, "float64"),
            "count": (int, "int64"),
            "date": (date, "object"),
            "created_on": (pd.Timestamp, "datetime64[ns]", "datetime64[us]"),
            "updated_on": (pd.Timestamp, "datetime64[ns]", "datetime64[us]"),
        }
        for col, dtypes in expected_dtypes.items():
            if col in data_df.columns:
                actual_dtype = str(data_df[col].dtype)
                if actual_dtype not in [str(d) for d in dtypes]:
                    logger.warning(f"Столбец {col} имеет тип {actual_dtype}, ожидается один из {dtypes}")

        for _, row in data_df.iterrows():
            trading_result = SpimexTradingResult(
                exchange_product_id=str(row["exchange_product_id"]),
                exchange_product_name=str(row["exchange_product_name"]),
                oil_id=str(row["oil_id"]),
                delivery_basis_id=str(row["delivery_basis_id"]),
                delivery_basis_name=str(row["delivery_basis_name"]),
                delivery_type_id=str(row["delivery_type_id"]),
                volume=float(row["volume"]),
                total=float(row["total"]),
                count=int(row["count"]),
                date=row["date"],
                created_on=row["created_on"],
                updated_on=row["updated_on"],
            )
            session.add(trading_result)

        session.commit()
        logger.info("Данные успешно сохранены в базу данных")
    except Exception as e:
        logger.error(f"Ошибка при сохранении в базу данных: {e}")
        session.rollback()


def process_bulletins(start_date: date, end_date: date, output_dir: str = "bulletins"):
    """Обрабатывает бюллетени за указанный период."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    bulletin_urls = get_bulletin_urls(start_date, end_date)
    logger.info("Создание сессии базы данных")
    session = Session()

    try:
        for url, trade_date in bulletin_urls:
            output_path = os.path.join(output_dir, f"oil_xls_{trade_date.strftime('%Y%m%d')}.xls")

            if download_bulletin(url, output_path):
                data_df = parse_bulletin(output_path, trade_date)
                if data_df is not None:
                    save_to_database(data_df, session)
    finally:
        session.close()
