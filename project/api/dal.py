from typing import List, Union

from passlib.handlers.bcrypt import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Active_Template
# from .models import Template_Content
from .schemas import User as UserSchema, Create_Update_Active_Template as Create_Update_Active_TemplateSchema


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
	def create_active_template(cls, user_id: int, create_active_template: Create_Update_Active_TemplateSchema,
	                           session: AsyncSession) -> Active_Template:
		at = Active_Template()
		at.template_id = create_active_template.template_id
		at.user_id = user_id
		session.add(at)
		return at

	@classmethod
	async def update_active_template(cls, user_id: int, active_template_id: str,
	                                 updated_active_template: Create_Update_Active_TemplateSchema,
	                                 session: AsyncSession) -> Active_Template:
		at = await session.execute(
			select(Active_Template).where(Active_Template.user_id == user_id)
			.where(Active_Template.id == active_template_id))
		active_template = at.scalars().first()

		if not active_template:
			return False

		active_template.template_id = updated_active_template.template_id
		return active_template

	@classmethod
	async def get_active_template(cls, user_id: int, session: AsyncSession) -> Union[bool, Active_Template]:
		at = await session.execute(select(Active_Template).where(Active_Template.user_id == user_id))
		active_template = at.scalars().first()
		if not active_template:
			return False
		return active_template

	@classmethod
	async def delete_active_template(cls, user_id: int, active_template_id: str, session: AsyncSession) -> Union[
		bool, Active_Template]:
		at = await session.execute(
			select(Active_Template).where(Active_Template.user_id == user_id)
			.where(Active_Template.id == active_template_id))
		active_template = at.scalars().first()

		if not active_template:
			return False

		await session.delete(active_template)
		return True
