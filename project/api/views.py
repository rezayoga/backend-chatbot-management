import logging

from fastapi import HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from redis import Redis
from rich.console import Console
from sqlalchemy.exc import IntegrityError
from starlette.responses import JSONResponse

# from project.database import SessionLocal
from project.api.dal import *
from . import api_router
from .schemas import JWT_Settings as JWT_SettingsSchema
from .schemas import User as UserSchema
from .schemas import User_Login as User_LoginSchema, Template as TemplateSchema
from ..database import get_session

logger = logging.getLogger(__name__)
# session = SessionLocal()
settings = JWT_SettingsSchema()
console = Console()

""" Exception Handler """


# Dependency


def not_found_exception(message: str):
	not_found_exception_response = HTTPException(
		status_code=200,
		detail=jsonable_encoder({"message": message, "data": {}}),
	)
	return not_found_exception_response


def incorrect_request_exception(message: str):
	incorrect_request_exception_response = HTTPException(
		status_code=400,
		detail=message,
	)
	return incorrect_request_exception_response


def get_user_exception():
	credentials_exception = HTTPException(
		status_code=401,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	return credentials_exception


""" auth """


@AuthJWT.load_config
def get_config():
	return settings


redis_connection = Redis(host='rezayogaswara.com', username='reza', password='reza1985', port=6379, db=0,
                         decode_responses=True)


# A storage engine to save revoked tokens. in production,
# you can use Redis for storage system
# denylist = set()


# For this example, we are just checking if the tokens jti
# (unique identifier) is in the denylist set. This could
# be made more complex, for example storing the token in Redis
# with the value true if revoked and false if not revoked
@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
	jti = decrypted_token['jti']
	entry = redis_connection.get(jti)
	return entry and entry == 'true'


@api_router.post("/token/refresh/", tags=["auth"])
async def refresh_access_token(auth: AuthJWT = Depends()):
	auth.jwt_refresh_token_required()
	current_user = auth.get_jwt_subject()
	new_access_token = auth.create_access_token(subject=current_user)
	return {"access_token": new_access_token}


@api_router.delete("/access/revoke/", tags=["auth"])
async def access_revoke(auth: AuthJWT = Depends()):
	auth.jwt_required()
	jti = auth.get_raw_jwt()['jti']
	# denylist.add(jti)
	redis_connection.setex(jti, settings.access_token_expires, 'true')
	return {"message": "Access token revoked"}


@api_router.delete("/refresh/revoke/", tags=["auth"])
async def refresh_revoke(auth: AuthJWT = Depends()):
	auth.jwt_refresh_token_required()
	jti = auth.get_raw_jwt()['jti']
	# denylist.add(jti)
	redis_connection.setex(jti, settings.refresh_token_expires, 'true')
	return {"message": "Refresh token revoked"}


@api_router.post("/token/", tags=["auth"])
async def login(user: User_LoginSchema, auth: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)):
	# Check if username and password match
	user = await User_DAL.auth_user(user.username, user.password, session)
	if not user:
		raise incorrect_request_exception("Incorrect username or password")

	access_token = auth.create_access_token(subject=user.id)
	refresh_token = auth.create_refresh_token(subject=user.id)
	return {
		"access_token": access_token,
		"refresh_token": refresh_token,
		"token_type": "bearer",
		"expires_in": settings.access_token_expires
	}


""" users """


@api_router.get("/users/", tags=["users"])
async def get_users(session: AsyncSession = Depends(get_session)):
	users = await User_DAL.get_users(session)
	return users


@api_router.post("/users/", tags=["users"])
async def create_user(created_user: UserSchema, session: AsyncSession = Depends(get_session)):
	user = User_DAL.create_user(created_user, session)
	try:
		await session.commit()
		return user
	except IntegrityError as ex:
		await session.rollback()
		raise incorrect_request_exception("Username already exists")


""" active_template """


@api_router.post("/active_template/", tags=["active_template"])
async def create_active_template(created_active_template: Create_Update_Active_TemplateSchema,
                                 auth: AuthJWT = Depends(),
                                 session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	# console.print(user, style="bold red")
	# inspect(user, methods=False)

	if user is None:
		raise get_user_exception()

	template = Active_Template_DAL.create_active_template(user.id, created_active_template, session)
	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Active template created successfully",
		                                              "body": jsonable_encoder(template)})
	except Exception as ex:
		await session.rollback()
		raise incorrect_request_exception(jsonable_encoder(ex))


@api_router.get("/active_template/", tags=["active_template"])
async def get_active_template(auth: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	active_template = await Active_Template_DAL.get_active_template(user.id, session)

	if active_template is None or active_template == False:
		raise not_found_exception("Active Template not found")

	return active_template


@api_router.put("/active_template/{active_template_id}/", tags=["active_template"])
async def update_active_template(active_template_id: str, updated_active_template: Create_Update_Active_TemplateSchema,
                                 auth: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	active_template = await Active_Template_DAL.update_active_template(user.id, active_template_id,
	                                                                   updated_active_template, session)

	if active_template is None or active_template == False:
		raise not_found_exception("Active Template not found")

	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Template updated successfully",
		                                              "body": jsonable_encoder(active_template)})
	except Exception as ex:
		await session.rollback()
		raise incorrect_request_exception(jsonable_encoder(ex))


@api_router.delete("/active_template/{active_template_id}/", tags=["active_template"])
async def delete_active_template(active_template_id: str, auth: AuthJWT = Depends(),
                                 session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	active_template = await Active_Template_DAL.delete_active_template(user.id, active_template_id, session)

	if active_template is None or active_template == False:
		raise not_found_exception("Active Template not found")

	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Template deleted successfully",
		                                              "body": jsonable_encoder(active_template)})
	except Exception as ex:
		await session.rollback()
		raise incorrect_request_exception(jsonable_encoder(ex))


""" templates """


@api_router.post("/templates/", tags=["templates"])
async def create_template(created_template: TemplateSchema, auth: AuthJWT = Depends(),
                          session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	template = Template_DAL.create_template(user.id, created_template, session)
	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Template created successfully",
		                                              "body": jsonable_encoder(template)})
	except Exception as ex:
		await session.rollback()
		raise incorrect_request_exception(jsonable_encoder(ex))


@api_router.get("/templates/{template_id}/", tags=["templates"])
async def get_template_by_template_id(template_id: str, auth: AuthJWT = Depends(),
                                      session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	template = await Template_DAL.get_template_by_template_id(auth.get_jwt_subject(), template_id, session)

	if template is None or template == False:
		raise not_found_exception("Template not found")

	return template


@api_router.get("/templates/", tags=["templates"], response_model=List[TemplateSchema])
async def get_templates(session: AsyncSession = Depends(get_session)):
	templates = await Template_DAL.get_templates(session)

	# if templates is None or templates == False:
	# 	raise not_found_exception("Templates not found")

	return templates


@api_router.get("/user/templates/", tags=["templates"])
async def get_templates_by_user_id(auth: AuthJWT = Depends(),
                                   session: AsyncSession = Depends(get_session)):
	auth.jwt_required()

	templates = await Template_DAL.get_template_by_user_id(auth.get_jwt_subject(), session)

	if templates is None or templates == False:
		raise not_found_exception("Templates not found")

	return templates


@api_router.put("/templates/{template_id}/", tags=["templates"])
async def update_template(template_id: str, updated_template: TemplateSchema, auth: AuthJWT = Depends(),
                          session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	template = await Template_DAL.update_template(user.id, template_id, updated_template, session)

	if template is None or template == False:
		raise not_found_exception("Template not found")

	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Template updated successfully",
		                                              "body": jsonable_encoder(template)})
	except Exception as ex:
		await session.rollback()
		raise incorrect_request_exception(jsonable_encoder(ex))


@api_router.delete("/templates/{template_id}/", tags=["templates"])
async def delete_template(template_id: str, auth: AuthJWT = Depends(),
                          session: AsyncSession = Depends(get_session)):
	auth.jwt_required()
	user = await User_DAL.auth_user_by_user_id(auth.get_jwt_subject(), session)

	if user is None:
		raise get_user_exception()

	template = await Template_DAL.delete_template(user.id, template_id, session)

	if template is None or template == False:
		raise not_found_exception("Template not found")

	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Template deleted successfully",
		                                              "body": jsonable_encoder(template)})
	except Exception as ex:
		await session.rollback()
		raise incorrect_request_exception(jsonable_encoder(ex))
