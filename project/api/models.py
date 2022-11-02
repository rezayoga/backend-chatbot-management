# coding: utf-8
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from project.database import Base

metadata = Base.metadata


class User(Base):
	__tablename__ = "users"
	__table_args__ = {"schema": "bot"}
	id = Column(Integer, primary_key=True, autoincrement=True)
	email = Column(String, unique=True, index=True)
	username = Column(String, unique=True, index=True)
	name = Column(String, nullable=True)
	hashed_password = Column(String, nullable=True)
	client_id = Column(String, nullable=True)
	is_active = Column(Boolean, default=True)
	created_at = Column(DateTime(timezone=True),
	                    nullable=False, default=func.now())
	updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
	templates = relationship("Template", backref="template_owner", cascade="all, delete-orphan")

	def __repr__(self):
		return f"{self.name} <{self.email}>"


class Inbound(Base):
	__tablename__ = "inbounds"
	__table_args__ = {"schema": "bot"}

	id = Column(String(128), primary_key=True, default=func.uuid_generate_v4())
	captured_id = Column(String, nullable=True)
	mid = Column(Text, nullable=True)
	client_id = Column(String, nullable=True)
	channel_id = Column(String, nullable=True)
	account_id = Column(String, nullable=True)
	account_alias = Column(String, nullable=True)
	application_id = Column(String, nullable=True)
	queue = Column(Text, nullable=True)
	data = Column(JSONB, nullable=True)
	type = Column(String(128), nullable=True)
	created_at = Column(DateTime(timezone=True),
	                    nullable=False, default=func.now())

	def __repr__(self) -> str:
		return f"<Inbound: {self.message_id} - {self.queue} - {self.data}>"


class Session(Base):
	__tablename__ = "sessions"
	__table_args__ = {"schema": "bot"}

	id = Column(String(128), primary_key=True, default=func.uuid_generate_v4())
	conversation_id = Column(String(128), nullable=True)
	client_id = Column(String, nullable=True)
	channel_id = Column(String, nullable=True)
	account_id = Column(String, nullable=True)
	account_alias = Column(String, nullable=True)
	application_id = Column(String, nullable=True)
	inbound_id = Column(String(128), ForeignKey("bot.inbounds.id"))
	outbound_id = Column(String(128), ForeignKey("bot.outbounds.xid"))
	from_number = Column(String(36), nullable=True)
	from_name = Column(String, nullable=True)
	expired_at = Column(DateTime(timezone=True), nullable=True)
	created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())

	def __repr__(self) -> str:
		return f"<Session: {self.id} -  {self.conversation_id} - {self.inbound_id} - {self.outbound_id} - " \
		       f"{self.from_number} - {self.from_name} - {self.expired_at}>"


class Template_Content(Base):
	__tablename__ = "template_contents"
	__table_args__ = {"schema": "bot"}

	id = Column(String(128), primary_key=True, default=func.uuid_generate_v4())
	parent_ids = Column(JSONB, nullable=True)
	payload = Column(JSONB, nullable=True)
	label = Column(Text, nullable=True)
	position = Column(JSONB, nullable=True)
	is_deleted = Column(Boolean, default=False)
	created_at = Column(DateTime(timezone=True),
	                    nullable=False, default=func.now())

	updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
	template_id = Column(String, ForeignKey("bot.templates.id"))

	def __repr__(self) -> str:
		return f"<Template Content: {self.id} -  {self.payload} - {self.label} - {self.parent_ids}>"


class Template(Base):
	__tablename__ = "templates"
	__table_args__ = (
		UniqueConstraint('template_name', 'client_id', 'channel_id', 'account_id', 'account_alias',
		                 name='unique_template_name'),
		{"schema": "bot"}
	)

	id = Column(String(128), primary_key=True, default=func.uuid_generate_v4())
	client_id = Column(String, nullable=True)
	channel_id = Column(String, nullable=True)
	account_id = Column(String, nullable=True)
	account_alias = Column(String, nullable=True)
	created_at = Column(DateTime(timezone=True),
	                    nullable=False, default=func.now())
	template_name = Column(Text, nullable=False)
	template_description = Column(Text, nullable=True)
	division_id = Column(String(128), nullable=True)
	is_deleted = Column(Boolean, default=False)
	owner_id = Column(Integer, ForeignKey("bot.users.id"))
	updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
	template_contents = relationship(
		"Template_Content", backref="template_content", cascade="all, delete-orphan")

	def __repr__(self) -> str:
		return f"<Template: {self.id} - {self.template_name} -  {self.template_description}>"


class Status(Base):
	__tablename__ = "statuses"
	__table_args__ = {"schema": "bot"}

	id = Column(String(128), primary_key=True, default=func.uuid_generate_v4())
	oid = Column(String, nullable=False)
	xid = Column(String, ForeignKey("bot.outbounds.xid"), nullable=False)
	mid = Column(Text, nullable=True)
	client_id = Column(String(128), nullable=True)
	channel_id = Column(String(128), nullable=True)
	account_alias = Column(String(128), nullable=True)
	application_id = Column(String(128), nullable=True)
	queue = Column(Text, nullable=True)
	type = Column(String(128), nullable=True)
	error = Column(String(128), nullable=True)
	data = Column(JSONB, nullable=True)
	created_at = Column(DateTime(timezone=True),
	                    nullable=False, default=func.now())

	def __repr__(self) -> str:
		return f"<Status: {self.mid} -  {self.data}>"


class Outbound(Base):
	__tablename__ = "outbounds"
	__table_args__ = {"schema": "bot"}

	xid = Column(String(128), primary_key=True, default=func.uuid_generate_v4())
	client_id = Column(String, nullable=True)
	channel_id = Column(String, nullable=True)
	account_id = Column(String, nullable=True)
	account_alias = Column(String, nullable=True)
	application_id = Column(String, nullable=True)
	queue = Column(Text, nullable=True)
	data = Column(JSONB, nullable=True)
	type = Column(String(128), nullable=True)
	template_id = Column(String, ForeignKey("bot.templates.id"))
	template_content_id = Column(String, ForeignKey("bot.template_contents.id"))
	created_at = Column(DateTime(timezone=True),
	                    nullable=False, default=func.now())
	division_id = Column(String, nullable=True)

	def __repr__(self) -> str:
		return f"<Outbound: {self.queue} - {self.data} - {self.template_id} - {self.template_content_id}>"


class Template_Config(Base):
	__tablename__ = "template_configs"
	__table_args__ = {"schema": "bot"}

	id = Column(String(128), primary_key=True, default=func.uuid_generate_v4())
	template_config = Column(JSONB, unique=True, nullable=False)
	created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
	updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

	def __repr__(self) -> str:
		return f"<Template Config: {self.id} -  {self.template_config}>"


class Active_Template(Base):
	__tablename__ = "active_templates"
	__table_args__ = (
		UniqueConstraint('user_id', 'template_id',
		                 name='unique_active_template'),
		{"schema": "bot"}
	)

	id = Column(String(128), primary_key=True, default=func.uuid_generate_v4())
	user_id = Column(Integer, ForeignKey("bot.users.id"))
	template_id = Column(String, ForeignKey("bot.templates.id"))
	created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
	updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

	def __repr__(self) -> str:
		return f"<Active Template: {self.id} -  {self.template_id}>"
