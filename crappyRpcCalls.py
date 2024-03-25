# First thing, If you're not a pleb, run:  pip install --upgrade -r requirements.txt

import asyncio
from web3 import Web3
import requests
from loguru import logger


# Your RPC endpoint URL
rpc_endpoint = (
    "https://eth1.lava.build/lava-referer-28945481-f08d-4c9e-a41c-1ce9e9765da1/"
)

# Your Wallet address
wallet_address = "0xb03F14fF6151686825c4d70A1Fd57822E1EeDbf5"

# Contract address and ABI - use any contract address. This one is for DAI
contract_address = "0xDe30da39c46104798bB5aA3fe8B9e0e1F348163F"
contract_abi = [
    {
        "constant": True,
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]

# JSON-RPC payloads for different methods - more will be added later
payloads = [
    {"method": "eth_chainId", "params": [], "id": 1},
    {"method": "eth_protocolVersion", "params": [], "id": 2},
    {"method": "net_version", "params": [], "id": 3},
    {"method": "eth_getBlockByNumber", "params": ["latest", True], "id": 4},
    {
        "method": "eth_getLogs",
        "params": [
            {"fromBlock": "latest", "toBlock": "latest", "address": wallet_address}
        ],
        "id": 5,
    },
    # In case you are wondering - this is Cream hack transaction hash
    {
        "method": "eth_getTransactionReceipt",
        "params": [
            "0x0fe2542079644e107cbf13690eb9c2c65963ccb79089ff96bfaf8dced2331c92"
        ],
        "id": 6,
    },
]


async def main():
    web3 = Web3(Web3.HTTPProvider(rpc_endpoint))
    token_contract = web3.eth.contract(address=contract_address, abi=contract_abi)

    try:
        (
            eth_balance,
            transaction_count,
            gas_price,
            block_number,
            chain_id,
            syncing_status,
        ) = await asyncio.gather(
            get_eth_balance(web3, wallet_address),
            get_transaction_count(web3, wallet_address, "latest"),
            get_gas_price(web3),
            get_block_number(web3),
            get_chain_id(web3),
            get_syncing_status(web3),
        )

        logger.info(f"Eth Balance: {eth_balance}")
        logger.info(f"Transaction Count: {transaction_count}")
        logger.info(f"Gas Price: {gas_price}")
        logger.info(f"Block Number: {block_number}")
        logger.info(f"Chain ID: {chain_id}")
        logger.info(f"Syncing Status: {syncing_status}")

        token_name = await get_token_name(token_contract)
        token_balance = await get_token_balance(token_contract, wallet_address)
        logger.info(
            f"The Token balance of {wallet_address} is {token_balance} {token_name}"
        )

    except Exception as e:
        logger.error("Error:", e)


async def initialize_connection():
    try:
        # Send HTTP POST requests for each payload concurrently
        responses = await asyncio.gather(
            *[post_payload(payload) for payload in payloads]
        )

        for response, payload in zip(responses, payloads):
            method = payload["method"]
            logger.info(f"Response from {method}:")

            if response.get("result"):
                logger.info(response["result"])
            else:
                logger.info("No data found in the response.")

    except Exception as e:
        logger.error("Error initializing connection:", e)


async def post_payload(payload):
    response = requests.post(rpc_endpoint, json=payload)
    return response.json()


async def get_token_name(contract):
    name = contract.functions.name().call()
    return name


async def get_token_balance(contract, address):
    balance = contract.functions.balanceOf(address).call()
    return balance


async def get_eth_balance(web3, address):
    balance = web3.eth.get_balance(address)
    return web3.from_wei(balance, "ether")


async def get_transaction_count(web3, address, block_number):
    count = web3.eth.get_transaction_count(address, block_number)
    return count


async def get_gas_price(web3):
    gas_price = web3.eth.gas_price
    return web3.from_wei(gas_price, "gwei")


async def get_block_number(web3):
    return web3.eth.get_block_number()


async def get_chain_id(web3):
    return web3.eth.chain_id


async def get_syncing_status(web3):
    current_block_number = web3.eth.block_number
    latest_block_number = web3.eth.get_block("latest")["number"]
    is_syncing = current_block_number != latest_block_number
    return is_syncing


async def main_and_connection():
    while True:
        await main()
        await initialize_connection()
        await asyncio.sleep(5)  # 5 seconds - Change it to whatever you like. Na you sabi


if __name__ == "__main__":
    asyncio.run(main_and_connection())
