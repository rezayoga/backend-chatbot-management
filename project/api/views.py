import logging

from fastapi import HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_pagination.ext.async_sqlalchemy import paginate
from rich.console import Console
from starlette.responses import JSONResponse

from project.api.dal import *
from . import api_router
from .pagination import JsonApiPage
from .schemas import Template as TemplateSchema, Active_Template_Create as Active_Template_CreateSchema, \
	Active_Template_Update as Active_Template_UpdateSchema, Active_Template_Paginated as Active_Template_PaginatedSchema
from ..database import get_session

logger = logging.getLogger(__name__)
# session = SessionLocal()
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


""" active_template """


@api_router.post("/active_templates/", tags=["active_templates"])
async def create_active_template(created_active_template: Active_Template_CreateSchema,

                                 session: AsyncSession = Depends(get_session)):
	template = await Active_Template_DAL.create_active_template(created_active_template, session)
	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Active template created successfully",
		                                              "body": jsonable_encoder(template)})
	except Exception as ex:
		await session.rollback()
		raise incorrect_request_exception(jsonable_encoder(ex))


@api_router.get("/active_templates/", tags=["active_templates"])
async def get_active_templates(session: AsyncSession = Depends(get_session)):
	active_template = await Active_Template_DAL.get_active_template(session)

	if active_template is None or active_template == False:
		raise not_found_exception("Active Template not found")

	return active_template


@api_router.get("/active_templates/{active_template_id}/", tags=["active_templates"])
async def get_active_template(active_template_id: str, session: AsyncSession = Depends(get_session)):
	active_template = await Active_Template_DAL.get_active_template_by_id(active_template_id, session)

	if active_template is None or active_template == False:
		raise not_found_exception("Active Template not found")

	return active_template


@api_router.get("/active_templates/display/all/", tags=["active_templates"],
                response_model=JsonApiPage[Active_Template_PaginatedSchema])
async def get_active_template(session: AsyncSession = Depends(get_session)):
	return await paginate(session, Active_Template_DAL.get_active_templates())


@api_router.put("/active_templates/{active_template_id}/", tags=["active_templates"])
async def update_active_template(active_template_id: str, updated_active_template: Active_Template_UpdateSchema,
                                 session: AsyncSession = Depends(get_session)):
	active_template = await Active_Template_DAL.update_active_template(active_template_id,
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


@api_router.delete("/active_templates/{active_template_id}/", tags=["active_templates"])
async def delete_active_template(active_template_id: str,
                                 session: AsyncSession = Depends(get_session)):
	active_template = await Active_Template_DAL.delete_active_template(active_template_id, session)

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
async def create_template(created_template: TemplateSchema,
                          session: AsyncSession = Depends(get_session)):
	template = Template_DAL.create_template(created_template, session)
	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Template created successfully",
		                                              "body": jsonable_encoder(template)})
	except Exception as ex:
		await session.rollback()
		raise incorrect_request_exception(jsonable_encoder(ex))


@api_router.get("/templates/populate/", tags=["templates"], include_in_schema=False)
async def populate_templates(session: AsyncSession = Depends(get_session)):
	template = Template_DAL.populate_templates(25, session)
	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Templates populated successfully",
		                                              "body": jsonable_encoder(template)})
	except Exception as ex:
		await session.rollback()
		raise incorrect_request_exception(jsonable_encoder(ex))


@api_router.get("/templates/{template_id}/", tags=["templates"])
async def get_template_by_template_id(template_id: str,
                                      session: AsyncSession = Depends(get_session)):
	template = await Template_DAL.get_template_by_template_id(template_id, session)

	if template is None or template == False:
		raise not_found_exception("Template not found")

	return template


@api_router.get("/templates/display/all/", tags=["templates"], response_model=JsonApiPage[TemplateSchema])
async def get_templates(session: AsyncSession = Depends(get_session)):
	return await paginate(session, Template_DAL.get_templates())


@api_router.put("/templates/{template_id}/", tags=["templates"])
async def update_template(template_id: str, updated_template: TemplateSchema,
                          session: AsyncSession = Depends(get_session)):
	template = await Template_DAL.update_template(template_id, updated_template, session)

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
async def delete_template(template_id: str,
                          session: AsyncSession = Depends(get_session)):
	template = await Template_DAL.delete_template(template_id, session)

	if template is None or template == False:
		raise not_found_exception("Template not found")

	try:
		await session.commit()
		return JSONResponse(status_code=200, content={"message": "Template deleted successfully",
		                                              "body": jsonable_encoder(template)})
	except Exception as ex:
		await session.rollback()
		raise incorrect_request_exception(jsonable_encoder(ex))
