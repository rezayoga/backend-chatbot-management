from typing import List, Union, Any

from faker import Faker
from passlib.handlers.bcrypt import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Active_Template, Template
# from .models import Template_Content
from .schemas import User as UserSchema, Active_Template_Update as Create_Update_Active_TemplateSchema, \
	Template as TemplateSchema, TemplateUpdate as TemplateUpdateSchema


###
# Data Access Layer (DAL) for all service endpoints
###

### Authentication & User services ###

def get_password_hash(password: str):
	return bcrypt.hash(password)


def verify_password(plain_password, hashed_password):
	return bcrypt.verify(plain_password, hashed_password)


class User_DAL:
	@classmethod
	async def auth_user(cls, username: str, password: str, session: AsyncSession) -> Union[bool, User]:
		u = await session.execute(select(User).where(User.username == username).where(User.is_active == True))
		user = u.scalars().first()
		if not user:
			return False
		if not verify_password(password, user.hashed_password):
			return False
		return user

	@classmethod
	async def auth_user_by_user_id(cls, user_id: int, session: AsyncSession) -> Union[bool, User]:
		u = await session.execute(select(User).where(User.id == user_id).where(User.is_active == True))
		user = u.scalars().first()
		if not user:
			return False
		return user

	@classmethod
	async def get_users(cls, session: AsyncSession) -> Union[bool, List[User]]:
		users = await session.execute(select(User))
		u = users.scalars().all()
		if not u:
			return False
		return u

	@classmethod
	def create_user(cls, created_user: UserSchema, session: AsyncSession) -> User:
		user = User()
		user.username = created_user.username
		user.email = created_user.email
		user.name = created_user.name
		user.hashed_password = get_password_hash(created_user.password)
		user.is_active = True
		session.add(user)
		return user


### Template configs ###

class Active_Template_DAL:
	@classmethod
	async def create_active_template(cls, create_active_template: Create_Update_Active_TemplateSchema,
	                                 session: AsyncSession) -> Active_Template:

		template = await session.execute(
			select(Template).where(Template.id == create_active_template.template_id).where(
				Template.is_deleted == False))
		t = template.scalars().first()
		if not t:
			return False

		at = Active_Template()
		at.template_id = create_active_template.template_id
		at.user_id = create_active_template.user_id
		at.client_id = t.client_id
		at.channel_id = t.channel_id
		at.account_id = t.account_id
		at.account_alias = t.account_alias
		session.add(at)
		return at

	@classmethod
	async def update_active_template(cls, active_template_id: str,
	                                 updated_active_template: Create_Update_Active_TemplateSchema,
	                                 session: AsyncSession) -> Active_Template:

		template = await session.execute(
			select(Template).where(Template.id == updated_active_template.template_id).where(
				Template.is_deleted == False))
		t = template.scalars().first()
		if not t:
			return False

		at = await session.execute(
			select(Active_Template)
			.where(Active_Template.id == active_template_id))
		active_template = at.scalars().first()

		if not active_template:
			return False

		active_template.template_id = updated_active_template.template_id
		active_template.client_id = t.client_id
		active_template.channel_id = t.channel_id
		active_template.account_id = t.account_id
		active_template.account_alias = t.account_alias
		return active_template

	@classmethod
	async def get_active_template(cls, session: AsyncSession) -> Union[bool, Active_Template]:
		at = await session.execute(select(Active_Template))
		active_template = at.scalars().all()
		if not active_template:
			return False
		return active_template

	@classmethod
	def get_active_templates(cls) -> Any:
		return select(Active_Template)

	@classmethod
	async def delete_active_template(cls, active_template_id: str, session: AsyncSession) -> Union[
		bool, Active_Template]:
		at = await session.execute(
			select(Active_Template)
			.where(Active_Template.id == active_template_id))
		active_template = at.scalars().first()

		if not active_template:
			return False

		await session.delete(active_template)
		return True


class Template_DAL:
	@classmethod
	def get_templates(cls) -> Any:
		return select(Template).where(
			Template.is_deleted == False)

	@classmethod
	async def get_template_by_template_id(cls, template_id: str, session: AsyncSession) -> Union[
		bool, Template]:
		template = await session.execute(
			select(Template).where(Template.id == template_id).where(
				Template.is_deleted == False))
		t = template.scalars().first()
		if not t:
			return False
		return t

	@classmethod
	def create_template(cls, created_template: TemplateSchema, session: AsyncSession) -> Template:
		template = Template()
		template.client_id = created_template.client_id
		template.template_name = created_template.template_name
		template.template_description = created_template.template_description
		template.is_deleted = False
		template.channel_id = created_template.channel_id
		template.account_id = created_template.account_id
		template.account_alias = created_template.account_alias
		template.division_id = created_template.division_id

		session.add(template)
		return template

	@classmethod
	async def update_template(cls, template_id: str, updated_template: TemplateUpdateSchema,
	                          session: AsyncSession) -> Union[bool, Template]:
		template = await session.execute(select(Template).where(Template.id == template_id)
		                                 .where(Template.is_deleted == False))
		t = template.scalars().first()

		if not t:
			return False

		if updated_template.client_id:
			t.client_id = updated_template.client_id
		if updated_template.template_name:
			t.template_name = updated_template.template_name
		if updated_template.template_description:
			t.template_description = updated_template.template_description
		if updated_template.channel_id:
			t.channel_id = updated_template.channel_id
		if updated_template.account_id:
			t.account_id = updated_template.account_id
		if updated_template.account_alias:
			t.account_alias = updated_template.account_alias
		if updated_template.division_id:
			t.division_id = updated_template.division_id

		return t

	@classmethod
	async def delete_template(cls, template_id: str, session: AsyncSession) -> Union[bool, Template]:
		template = await session.execute(
			select(Template).where(Template.id == template_id)
			.where(Template.is_deleted == False))
		t = template.scalars().first()

		if not t:
			return False

		await session.delete(t)
		return t

	@classmethod
	def populate_templates(cls, count: int, session):

		fake = Faker(['it_IT', 'en_US', 'ja_JP', 'id_ID'])
		for i in range(count):
			template = Template()
			template.client_id = fake.name()
			template.template_name = fake.name()
			template.template_description = fake.text()
			template.is_deleted = False
			template.channel_id = fake.name()
			template.account_id = fake.name()
			template.account_alias = fake.name()
			template.division_id = fake.name()
			session.add(template)
