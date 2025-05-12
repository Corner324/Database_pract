from sqlalchemy import Column, Date, DateTime, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Создаем базовый класс для моделей
BaseModel = declarative_base()


class SpimexTradingResult(BaseModel):
    __tablename__ = "spimex_trading_results"

    id = Column(Integer, primary_key=True)
    exchange_product_id = Column(String, nullable=False)
    exchange_product_name = Column(String, nullable=False)
    oil_id = Column(String, nullable=False)
    delivery_basis_id = Column(String, nullable=False)
    delivery_basis_name = Column(String, nullable=False)
    delivery_type_id = Column(String, nullable=False)
    volume = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    count = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    created_on = Column(DateTime, nullable=False)
    updated_on = Column(DateTime, nullable=False)
