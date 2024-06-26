from typing import TypeVar, Generic

from fastapi_pagination.links import Page

T = TypeVar("T")


class JsonApiPage(Page[T], Generic[T]):
	"""JSON:API 1.0 specification says that result key should be a `data`."""

	class Config:
		allow_population_by_field_name = True
		fields = {"items": {"alias": "data"}}
