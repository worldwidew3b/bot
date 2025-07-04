from sqlalchemy import Boolean, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    tg_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    # Связь с записями
    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")

class Service(Base):
    __tablename__ = 'services'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # в минутах
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Связь с записями
    bookings: Mapped[list["Booking"]] = relationship(back_populates="service")

class BroadcastSettings(Base):
    __tablename__ = 'broadcast_settings'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    default_text: Mapped[str] = mapped_column(Text, nullable=False, default='Заходи на эфир')

class Booking(Base):
    __tablename__ = 'bookings'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_tg_id: Mapped[int] = mapped_column(ForeignKey('users.tg_id'), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey('services.id'), nullable=False)
    client_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    preferred_date: Mapped[str] = mapped_column(String(50), nullable=False)  # "15 января"
    preferred_time: Mapped[str] = mapped_column(String(10), nullable=False)  # "14:00"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False)
    
    # Связи
    user: Mapped["User"] = relationship(back_populates="bookings")
    service: Mapped["Service"] = relationship(back_populates="bookings")