from web3 import Web3
from eth_account.signers.local import LocalAccount
from web3.contract import Contract
import functools
from typing import ParamSpec, TypeVar, Callable

from citi_project.backend.model import MsgModel

w3: Web3 | None = None
py_account: LocalAccount | None = None

require_w3_P = ParamSpec("require_w3_P")
require_w3_R = TypeVar("require_w3_R")


def require_init(
    func: Callable[require_w3_P, require_w3_R]
) -> Callable[require_w3_P, require_w3_R]:
    global w3, py_account

    @functools.wraps(func)
    def wrapper(*args: require_w3_P.args, **kwargs: require_w3_P.kwargs):
        assert w3 is not None and py_account is not None, "web3未初始化"
        return func(*args, **kwargs)

    return wrapper


def connect():
    global w3, py_account
    w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
    if w3.is_connected():
        print("测试网连接成功")
    else:
        raise ConnectionError("以太坊连接错误!")
    py_account = w3.eth.account.from_key(PRIKEY)
    print("连接账户")


MSG_CONTRACT_ADDR = "0xc34175A79ACca40392bECD22ff10fAeBFE780Ae7"

PRIKEY = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"


@require_init
def get_msg_collection_contract() -> type[Contract]:
    return w3.eth.contract(
        address=MSG_CONTRACT_ADDR,
        abi=[
            {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
            {
                "inputs": [
                    {"internalType": "address", "name": "account", "type": "address"}
                ],
                "name": "addAddress",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            },
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


@require_init
def get_msg_box_contract(contract_address: str) -> type[Contract]:
    return w3.eth.contract(
        address=contract_address,
        abi=[
            {
                "inputs": [
                    {"internalType": "address", "name": "msgAcco", "type": "address"}
                ],
                "stateMutability": "nonpayable",
                "type": "constructor",
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "msgType", "type": "uint256"},
                    {"internalType": "bytes", "name": "info", "type": "bytes"},
                ],
                "name": "addMsg",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "inputs": [],
                "name": "getActiveMsgs",
                "outputs": [
                    {"internalType": "uint256[]", "name": "", "type": "uint256[]"},
                    {"internalType": "bytes[]", "name": "", "type": "bytes[]"},
                ],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [],
                "name": "getAllMsgs",
                "outputs": [
                    {"internalType": "uint256[]", "name": "", "type": "uint256[]"},
                    {"internalType": "bytes[]", "name": "", "type": "bytes[]"},
                    {"internalType": "bool[]", "name": "", "type": "bool[]"},
                ],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "index", "type": "uint256"}
                ],
                "name": "getMsg",
                "outputs": [
                    {"internalType": "uint256", "name": "", "type": "uint256"},
                    {"internalType": "bytes", "name": "", "type": "bytes"},
                    {"internalType": "bool", "name": "", "type": "bool"},
                ],
                "stateMutability": "view",
                "type": "function",
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "index", "type": "uint256"}
                ],
                "name": "markMsgAsDeleted",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function",
            },
            {
                "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "name": "msgs",
                "outputs": [
                    {"internalType": "uint256", "name": "msgType", "type": "uint256"},
                    {"internalType": "bytes", "name": "info", "type": "bytes"},
                    {"internalType": "bool", "name": "deleted", "type": "bool"},
                ],
                "stateMutability": "view",
                "type": "function",
            },
        ],
    )


@require_init
def create_msg_box(account_address: str) -> str:
    """
    Returns:
        str: new msg box address
    """
    global py_account
    msg_coll_contract = get_msg_collection_contract()

    gas_estimate = msg_coll_contract.functions.addAddress(account_address).estimate_gas(
        {
            "from": py_account.address,
            "nonce": w3.eth.get_transaction_count(py_account.address),
            "gasPrice": w3.to_wei("10", "gwei"),
        }
    )
    tx = msg_coll_contract.functions.addAddress(account_address).build_transaction(
        {
            "from": py_account.address,
            "nonce": w3.eth.get_transaction_count(py_account.address),
            "gas": gas_estimate,
            "gasPrice": w3.to_wei("10", "gwei"),
        }
    )
    sign_tx = py_account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(sign_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print("create msg box成功: Tx Hash:", tx_hash.hex())

    return str(get_msg_box_address(account_address))


@require_init
def get_msg_box_address(account_address: str) -> str:
    global py_account
    return str(
        get_msg_collection_contract()
        .functions.getMsgBox(account_address)
        .call({"from": py_account.address})
    )


@require_init
def get_msg_list(account_address: str) -> list[MsgModel]:
    contract_addr = get_msg_box_address(account_address)
    msg_box_contract = get_msg_box_contract(contract_addr)
    msg_types: list[int]
    contents: list[bytes]
    msg_types, contents, deleted = msg_box_contract.functions.getAllMsgs().call()
    return [
        MsgModel(info=f"0x{contents[index].hex()}", type=type, deleted=deleted[index])
        for index, type in enumerate(msg_types)
    ]


@require_init
def add_msg(account_address: str, msg: MsgModel):
    content: bytes = b""
    if msg.info.startswith("0x") or msg.info.startswith("0x"):
        content = bytes.fromhex(msg.info[2:])
    else:
        content = bytes(msg.info, encoding="utf8")
    content: bytes
    msg_box_contract = get_msg_box_contract(get_msg_box_address(account_address))
    gas_estimate = msg_box_contract.functions.addMsg(msg.type, content).estimate_gas(
        {
            "from": py_account.address,
            "nonce": w3.eth.get_transaction_count(py_account.address),
            "gasPrice": w3.to_wei("10", "gwei"),
        }
    )
    tx = msg_box_contract.functions.addMsg(msg.type, content).build_transaction(
        {
            "from": py_account.address,
            "nonce": w3.eth.get_transaction_count(py_account.address),
            "gas": gas_estimate,
            "gasPrice": w3.to_wei("10", "gwei"),
        }
    )

    sign_tx = py_account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(sign_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print("addMsg成功: Tx Hash:", tx_hash.hex())
