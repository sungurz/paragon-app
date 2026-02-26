from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # Admin, Staff, Manager


class Apartment(Base):
    __tablename__ = "apartments"

    id = Column(Integer, primary_key=True)
    city = Column(String(50))
    address = Column(String(100))
    status = Column(String(20))  # Available, Occupied


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))