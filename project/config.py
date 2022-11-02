from functools import lru_cache


class BaseConfig:
	DATABASE_URL: str = "postgresql+asyncpg://costervxpostgres:32zwXBKZpXsVQ5nn@103.145.194.80/costerv3"
	DATABASE_CONNECT_DICT: dict = {}

	CELERY_BROKER_URL: str = "redis://reza:reza1985@rezayogaswara.com:6379/0"
	CELERY_RESULT_BACKEND: str = "redis://reza:reza1985@rezayogaswara.com:6379/0"


class DevelopmentConfig(BaseConfig):
	pass


class ProductionConfig(BaseConfig):
	pass


class TestingConfig(BaseConfig):
	pass


@lru_cache()
def get_settings():
	config_cls_dict = {
		"development": DevelopmentConfig,
		"production": ProductionConfig,
		"testing": TestingConfig
	}

	config_name = "development"
	config_cls = config_cls_dict[config_name]
	return config_cls()


settings = get_settings()
