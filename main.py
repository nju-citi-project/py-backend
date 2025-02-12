from citi_project.backend import app
from citi_project.backend.model import MsgModel
from citi_project.w3 import connect, get_msg_list, create_msg_box, add_msg

if __name__ == "__main__":
    import uvicorn

    # 以太坊连接成功
    connect()
    # create_msg_box("0xf02E506d12202E4ACccD837ffbA020cf8Cf1AE0b")
    # add_msg(
    #     "0xf02E506d12202E4ACccD837ffbA020cf8Cf1AE0b",
    #     msg=MsgModel(type=1, info="0xaabbccddeeff"),
    # )
    # print(get_msg_list(account_address="0xf02E506d12202E4ACccD837ffbA020cf8Cf1AE0b"))
    uvicorn.run(app, port=3030)
