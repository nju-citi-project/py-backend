from fastapi import Request
from fastapi.exceptions import RequestValidationError
from citi_project.backend.util import err_wrapper
from .app import app

from web3.exceptions import InvalidAddress, ContractLogicError


@app.exception_handler(RequestValidationError)
def request_validation_handler(_: Request, exc: RequestValidationError):
    return err_wrapper(f"{exc}")


@app.exception_handler(InvalidAddress)
def invalid_addr_handler(req: Request, _):
    return err_wrapper("Invalid Address")


@app.exception_handler(ContractLogicError)
def contract_logic_handler(_, exc: ContractLogicError):
    return err_wrapper(msg=f"Contract Logic Err: {exc.data["reason"]}")
