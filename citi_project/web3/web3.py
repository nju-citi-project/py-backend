from web3 import Web3
from eth_account.signers.local import LocalAccount
from web3.contract import Contract
import functools
from typing import ParamSpec, TypeVar, Callable

w3: Web3 | None = None
py_account: LocalAccount | None = None

require_w3_P = ParamSpec("require_w3_P")
require_w3_R = TypeVar("require_w3_R")


def require_w3(
    func: Callable[require_w3_P, require_w3_R]
) -> Callable[require_w3_P, require_w3_R]:
    @functools.wraps(func)
    def wrapper(*args: require_w3_P.args, **kwargs: require_w3_P.kwargs):
        assert w3 is not None, "web3对象未初始化"
        return func(*args, **kwargs)

    return wrapper


def connect():
    global w3
    w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
    if w3.is_connected():
        print("测试网连接成功")
    else:
        raise ConnectionError("以太坊连接错误!")
    init_account()


MSG_CONTRACT_ADDR = "0x254dffcd3277C0b1660F6d42EFbB754edaBAbC2B"

PRIKEY = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"


@require_w3
def init_account():
    global py_account
    py_account = w3.eth.account.from_key(PRIKEY)
    print("连接账户")


@require_w3
def get_msg_collection_contract() -> type[Contract]:
    return w3.eth.contract(
        address=MSG_CONTRACT_ADDR,
        abi=[
            {
                "inputs": [
                    {"internalType": "address", "name": "account", "type": "address"}
                ],
                "name": "addAddress",
                "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
            {
                "inputs": [
                    {"internalType": "address", "name": "account", "type": "address"}
                ],
                "name": "getMsgBox",
                "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                "stateMutability": "view",
                "type": "function",
            },
        ],
    )


@require_w3
def create_msg_box(address: str):
    global py_account
    msg_coll_contract = get_msg_collection_contract()
    tx = msg_coll_contract.functions.addAddress(py_account.address).build_transaction(
        {
            "from": py_account.address,
            "nonce": w3.eth.get_transaction_count(py_account.address),
            "gas": 3000000,
            "gasPrice": w3.to_wei("10", "gwei"),
        }
    )

    tx_hash = w3.eth.send_transaction(tx)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("交易成功，Tx Hash:", tx_hash.hex())
    new_msgbox_address = msg_coll_contract.functions.getMsgBox(py_account.address).call(
        {"from": py_account.address}
    )
    print("新的 MsgBox 地址:", new_msgbox_address)
