from pydantic import BaseModel, Field


class AddressModel(BaseModel):
    address: str = Field(default=..., pattern=r"^0x[0-9a-fA-F]{40}$")


class MsgModel(BaseModel):
    info: str
    type: int
    deleted: bool = Field(default=False)
