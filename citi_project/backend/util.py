def result_wrapper(
    data: dict[str, str | dict], code: int = 200
) -> dict[str, int | str | dict]:
    return {"code": code, "data": data}
