from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    message: str
    payload: Optional[T] = None
    status_code: int
