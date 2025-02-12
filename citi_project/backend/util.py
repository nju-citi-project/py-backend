from fastapi.responses import JSONResponse


def result_wrapper(
    data: dict[str, str | dict], code: int = 200
) -> dict[str, int | str | dict]:
    return JSONResponse(status_code=code, content={"code": code, "data": data})


def ok_wrapper(data: dict[str, str | dict] = {"msg": "ok"}):
    return result_wrapper(data=data, code=200)


def err_wrapper(msg: str):
    return result_wrapper(data={"msg": msg}, code=500)
