from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

BaseModel = declarative_base()


class Genre(BaseModel):
    __tablename__ = "genre"

    genre_id = Column(Integer, primary_key=True)
    name_genre = Column(String, nullable=False)

    books = relationship("Book", back_populates="genre")


class Author(BaseModel):
    __tablename__ = "author"

    author_id = Column(Integer, primary_key=True)
    name_author = Column(String, nullable=False)

    books = relationship("Book", back_populates="author")


class City(BaseModel):
    __tablename__ = "city"

    city_id = Column(Integer, primary_key=True)
    name_city = Column(String, nullable=False)
    days_delivery = Column(Integer, nullable=False)

    clients = relationship("Client", back_populates="city")


class Client(BaseModel):
    __tablename__ = "client"

    client_id = Column(Integer, primary_key=True)
    name_client = Column(String, nullable=False)
    city_id = Column(Integer, ForeignKey("city.city_id"), nullable=False)
    email = Column(String, nullable=False)

    city = relationship("City", back_populates="clients")
    buys = relationship("Buy", back_populates="client")


class Book(BaseModel):
    __tablename__ = "book"

    book_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("author.author_id"), nullable=False)
    genre_id = Column(Integer, ForeignKey("genre.genre_id"), nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Integer, nullable=False)

    author = relationship("Author", back_populates="books")
    genre = relationship("Genre", back_populates="books")
    buy_books = relationship("BuyBook", back_populates="book")


class Buy(BaseModel):
    __tablename__ = "buy"

    buy_id = Column(Integer, primary_key=True)
    buy_description = Column(Text, nullable=True)
    client_id = Column(Integer, ForeignKey("client.client_id"), nullable=False)

    client = relationship("Client", back_populates="buys")
    buy_books = relationship("BuyBook", back_populates="buy")
    buy_steps = relationship("BuyStep", back_populates="buy")


class BuyBook(BaseModel):
    __tablename__ = "buy_book"

    buy_book_id = Column(Integer, primary_key=True)
    buy_id = Column(Integer, ForeignKey("buy.buy_id"), nullable=False)
    book_id = Column(Integer, ForeignKey("book.book_id"), nullable=False)
    amount = Column(Integer, nullable=False)

    buy = relationship("Buy", back_populates="buy_books")
    book = relationship("Book", back_populates="buy_books")


class Step(BaseModel):
    __tablename__ = "step"

    step_id = Column(Integer, primary_key=True)
    name_step = Column(String, nullable=False)

    buy_steps = relationship("BuyStep", back_populates="step")


class BuyStep(BaseModel):
    __tablename__ = "buy_step"

    buy_step_id = Column(Integer, primary_key=True)
    buy_id = Column(Integer, ForeignKey("buy.buy_id"), nullable=False)
    step_id = Column(Integer, ForeignKey("step.step_id"), nullable=False)
    date_step_beg = Column(Date, nullable=False)
    date_step_end = Column(Date, nullable=True)

    buy = relationship("Buy", back_populates="buy_steps")
    step = relationship("Step", back_populates="buy_steps")
