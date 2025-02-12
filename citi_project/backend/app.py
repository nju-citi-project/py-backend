from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from citi_project.backend.model import AddressModel, MsgModel
from citi_project.w3.web3 import get_msg_list, add_msg as w3_add_msg

from .util import ok_wrapper

from .. import w3

app = FastAPI()

from . import err_handler

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


CONTRACT_API_PATH = "/api"


@app.get(f"{CONTRACT_API_PATH}/test")
async def api_test():
    return ok_wrapper({"test": "ok!"})


@app.post(f"{CONTRACT_API_PATH}/create-msg-box")
async def create_msg_box(data: AddressModel):
    address = data.address
    new_addr = w3.create_msg_box(address=address)
    return ok_wrapper({"new_address": address})


@app.post(f"{CONTRACT_API_PATH}/msg-list")
async def msg_list(data: AddressModel):
    return ok_wrapper(
        [msg.model_dump_json() for msg in get_msg_list(account_address=data.address)]
    )


@app.post(f"{CONTRACT_API_PATH}/add-msg")
async def add_msg(address: AddressModel, msg: MsgModel):
    w3_add_msg(address.address, msg=msg)
    return ok_wrapper({"msg": "ok"})
