from typing import Generic, Optional, TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")


class StandardResponse(GenericModel, Generic[T]):
    message: str
    payload: Optional[T] = None
    status_code: int
