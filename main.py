from citi_project.backend import app
from citi_project.web3 import connect, create_msg_box

if __name__ == "__main__":
    import uvicorn

    # 以太坊连接成功
    connect()
    create_msg_box("0x0230A49a8E2FDFDDfADE030A2AE43967E3814Dda")
    uvicorn.run(app, port=3030)
