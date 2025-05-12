import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

mapper_registry = registry()
BaseModel = mapper_registry.generate_base()


@mapper_registry.mapped
class Genre:
    __tablename__ = "genre"

    genre_id: Mapped[int] = mapped_column(primary_key=True)
    name_genre: Mapped[str] = mapped_column(nullable=False)

    books: Mapped[List["Book"]] = relationship(back_populates="genre")


@mapper_registry.mapped
class Author:
    __tablename__ = "author"

    author_id: Mapped[int] = mapped_column(primary_key=True)
    name_author: Mapped[str] = mapped_column(nullable=False)

    books: Mapped[List["Book"]] = relationship(back_populates="author")


@mapper_registry.mapped
class City:
    __tablename__ = "city"

    city_id: Mapped[int] = mapped_column(primary_key=True)
    name_city: Mapped[str] = mapped_column(nullable=False)
    days_delivery: Mapped[int] = mapped_column(nullable=False)

    clients: Mapped[List["Client"]] = relationship(back_populates="city")


@mapper_registry.mapped
class Client:
    __tablename__ = "client"

    client_id: Mapped[int] = mapped_column(primary_key=True)
    name_client: Mapped[str] = mapped_column(nullable=False)
    city_id: Mapped[int] = mapped_column(ForeignKey("city.city_id"), nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)

    city: Mapped["City"] = relationship(back_populates="clients")
    buys: Mapped[List["Buy"]] = relationship(back_populates="client")


@mapper_registry.mapped
class Book:
    __tablename__ = "book"

    book_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("author.author_id"), nullable=False)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genre.genre_id"), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)

    author: Mapped["Author"] = relationship(back_populates="books")
    genre: Mapped["Genre"] = relationship(back_populates="books")
    buy_books: Mapped[List["BuyBook"]] = relationship(back_populates="book")


@mapper_registry.mapped
class Buy:
    __tablename__ = "buy"

    buy_id: Mapped[int] = mapped_column(primary_key=True)
    buy_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.client_id"), nullable=False)

    client: Mapped["Client"] = relationship(back_populates="buys")
    buy_books: Mapped[List["BuyBook"]] = relationship(back_populates="buy")
    buy_steps: Mapped[List["BuyStep"]] = relationship(back_populates="buy")


@mapper_registry.mapped
class BuyBook:
    __tablename__ = "buy_book"

    buy_book_id: Mapped[int] = mapped_column(primary_key=True)
    buy_id: Mapped[int] = mapped_column(ForeignKey("buy.buy_id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.book_id"), nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)

    buy: Mapped["Buy"] = relationship(back_populates="buy_books")
    book: Mapped["Book"] = relationship(back_populates="buy_books")


@mapper_registry.mapped
class Step:
    __tablename__ = "step"

    step_id: Mapped[int] = mapped_column(primary_key=True)
    name_step: Mapped[str] = mapped_column(nullable=False)

    buy_steps: Mapped[List["BuyStep"]] = relationship(back_populates="step")


@mapper_registry.mapped
class BuyStep:
    __tablename__ = "buy_step"

    buy_step_id: Mapped[int] = mapped_column(primary_key=True)
    buy_id: Mapped[int] = mapped_column(ForeignKey("buy.buy_id"), nullable=False)
    step_id: Mapped[int] = mapped_column(ForeignKey("step.step_id"), nullable=False)
    date_step_beg: Mapped[Optional[datetime.date]] = mapped_column(nullable=False)
    date_step_end: Mapped[Optional[datetime.date]] = mapped_column(nullable=True)

    buy: Mapped["Buy"] = relationship(back_populates="buy_steps")
    step: Mapped["Step"] = relationship(back_populates="buy_steps")
