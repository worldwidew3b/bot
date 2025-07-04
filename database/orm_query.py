from sqlalchemy import select, insert, update, delete
from database.models import User, BroadcastSettings, Booking
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


async def get_or_create_user(session: AsyncSession, user_tg_id: int, user_name: str) -> User:
    """Получает пользователя из БД или создает нового. Возвращает объект пользователя."""
    current_user = await session.get(User, user_tg_id)
    if current_user is None:
        # Создаем нового пользователя
        current_user = User(tg_id=user_tg_id, name=user_name)
        session.add(current_user)
        await session.commit()
        return current_user
    else:
        # Обновляем имя если изменилось и активируем пользователя
        if current_user.name != user_name:
            current_user.name = user_name
        if not current_user.is_active:
            current_user.is_active = True
        await session.commit()
        return current_user

async def deactivate_user(session: AsyncSession, user_tg_id: int):
    """Деактивирует пользователя (при блокировке бота)"""
    current_user = await session.get(User, user_tg_id)
    if current_user and current_user.is_active:
        current_user.is_active = False
        await session.commit()

async def get_active_users(session: AsyncSession):
    """Получает всех активных пользователей для рассылки"""
    users = await session.scalars(select(User).where(User.is_active == True))
    return list(users)

async def get_or_create_broadcast_settings(session: AsyncSession) -> BroadcastSettings:
    """Получает настройки рассылки админа или создает новые"""
    settings = await session.scalars(select(BroadcastSettings))
    settings = settings.first()
    if settings is None:
        settings = BroadcastSettings()
        session.add(settings)
        await session.commit()
    return settings

async def update_default_broadcast_text(session: AsyncSession, new_text: str):
    """Обновляет стандартный текст рассылки для админа"""
    settings = await get_or_create_broadcast_settings(session)
    settings.default_text = new_text
    await session.commit()
    return settings


async def create_booking(
    session: AsyncSession,
    user_tg_id: int,
    service_id: int,
    client_name: str,
    phone: str,
    preferred_date: str,
    preferred_time: str,
) -> Booking:
    """Создает новую запись"""
    booking = Booking(
        user_tg_id=user_tg_id,
        service_id=service_id,
        client_name=client_name,
        phone=phone,
        preferred_date=preferred_date,
        preferred_time=preferred_time
    )
    session.add(booking)
    await session.commit()
    return booking

async def get_all_bookings(session: AsyncSession):
    """Получает все записи (for admin)"""
    query = select(Booking).options(selectinload(Booking.service)).order_by(Booking.created_at.desc())
    bookings = await session.scalars(query)
    return list(bookings)

async def get_user_bookings(session: AsyncSession, user_id: int):
    """Получает записи пользователя по его id"""
    user_bookings = await session.scalars(select(Booking).where(Booking.user_tg_id == user_id))
    return len(list(user_bookings))


async def delete_booking(session: AsyncSession, booking_id: int):
    """Удаляет запись (for admin)"""
    booking = await session.get(Booking, booking_id)
    if booking:
        await session.execute(delete(Booking).where(Booking.id == booking_id))
        await session.commit()
        return booking.user_tg_id
    return None