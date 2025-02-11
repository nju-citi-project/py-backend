from fastapi import FastAPI

from .util import result_wrapper
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


contract_api_path = "/api"


@app.get(f"{contract_api_path}/test")
def read_root():
    return result_wrapper({"test": "ok!"})
