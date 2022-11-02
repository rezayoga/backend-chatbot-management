import logging.config
import os

import bugsnag
from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from project.celery_utils import create_celery  # new

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__)  # __name__ = "project"

bugsnag.configure(
	api_key="eeaa7bece3b5c4658b714847d69d7f19",
	project_root=os.getcwd(),
)


def create_app() -> FastAPI:
	app = FastAPI(title="Chatbot Management API",
	              version="1.0.0",
	              description="API docs for Jatis Mobile Chatbot Management",
	              contact={
		              "name": "Reza Yogaswara",
		              "url": "https://me.rezayogaswara.dev/",
		              "email": "reza.yoga@gmail.com",
	              },
	              servers=[{"url": "https://chatbotstudio.rezayogaswara.dev/", "description": "Development"}]
	              )

	# Salt to your taste
	ALLOWED_ORIGINS = 'https://localhost:5173'  # or 'foo.com', etc.

	# handle CORS preflight requests
	@app.options('/{rest_of_path:path}')
	async def preflight_handler(request: Request, rest_of_path: str) -> Response:
		response = Response()
		response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS
		response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE, OPTIONS, PUT'
		response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
		response.headers['Access-Control-Allow-Headers'] = 'x-requested-with, x-requested-by'
		response.headers['Access-Control-Allow-Credentials'] = 'true'
		return response

	# set CORS headers
	@app.middleware('http')
	async def add_CORS_header(request: Request, call_next):
		response = await call_next(request)
		response.headers['Access-Control-Allow-Origin'] = ALLOWED_ORIGINS
		response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE, OPTIONS, PUT'
		response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
		response.headers['Access-Control-Allow-Headers'] = 'x-requested-with, x-requested-by'
		response.headers['Access-Control-Allow-Credentials'] = 'true'

		# Buat login disini

		return response

	# origins = [
	# 	"https://localhost:5173",
	# 	"https://127.0.0.1:5173"
	# ]
	#
	# app.add_middleware(
	# 	CORSMiddleware,
	# 	allow_origins=origins,
	# 	allow_credentials=True,
	# 	allow_methods=["*"],
	# 	allow_headers=["*"],
	# )

	# do this before loading routes
	app.celery_app = create_celery()

	from fastapi.exceptions import RequestValidationError
	@app.exception_handler(RequestValidationError)
	async def validation_exception_handler(request: Request, exc: RequestValidationError):
		return JSONResponse(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
		)

	from fastapi_jwt_auth.exceptions import AuthJWTException
	@app.exception_handler(AuthJWTException)
	def authjwt_exception_handler(request: Request, exc: AuthJWTException):
		return JSONResponse(
			status_code=exc.status_code,
			content={"detail": exc.message}
		)

	from project.api import api_router  # new
	app.include_router(api_router)  # new

	@app.get("/")
	async def root():
		return {"message": "App started successfully"}

	return app
