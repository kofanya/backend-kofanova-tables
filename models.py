from datetime import datetime
from typing import List
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
 
class Base(DeclarativeBase):
    pass

class Table(Base):
    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String, index=True) 
    capacity: Mapped[int] = mapped_column(Integer)
    zone: Mapped[str] = mapped_column(String)

    reservations: Mapped[List["Reservation"]] = relationship(
        back_populates="table", 
        cascade="all, delete-orphan"
    )

class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True)
    table_id: Mapped[int] = mapped_column(ForeignKey("tables.id"))
    guest_name: Mapped[str] = mapped_column(String)
    date_time: Mapped[datetime] = mapped_column(DateTime)
    guests_count: Mapped[int] = mapped_column(Integer)

    table: Mapped["Table"] = relationship(back_populates="reservations")