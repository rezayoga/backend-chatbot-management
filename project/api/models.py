# coding: utf-8
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from project.database import Base

metadata = Base.metadata


class User(Base):
	__tablename__ = "users"
	id = Column(Integer, primary_key=True, autoincrement=True)
	email = Column(String, unique=True, index=True)
	username = Column(String, unique=True, index=True)
	name = Column(String, nullable=True)
	hashed_password = Column(String, nullable=True)
	is_active = Column(Boolean, default=True)
	created_at = Column(DateTime(timezone=True),
	                    nullable=False, default=func.now())
	updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
	templates = relationship("Template", backref="template_owner", cascade="all, delete-orphan")

	def __repr__(self):
		return f"{self.name} <{self.email}>"
