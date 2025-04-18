import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from loguru import logger
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.eth import AsyncEth

from src import config
from src.model import SeismicChain


#
# Common
#

async def delay(delay_: float, tag: str):
    if delay_ <= 0:
        return

    lang = config.LOGS_LANGUAGE
    msg = {
        "en": {
            "hour": ("hour", "hours"),
            "minute": ("minute", "minutes"),
            "second": ("second", "seconds"),
            "before_launch": "{time_str} before launch"
        },
        "ru": {
            "hour": ("час", "часа", "часов"),
            "minute": ("минута", "минуты", "минут"),
            "second": ("секунда", "секунды", "секунд"),
            "before_launch": "{time_str} до запуска"
        }
    }[lang]

    hours = int(delay_ // 3600)
    remaining = delay_ % 3600
    minutes = int(remaining // 60)
    seconds = int(remaining % 60)

    def get_plural(num: int, words: tuple) -> str:
        if lang == "ru":
            if num % 10 == 1 and num % 100 != 11:
                return words[0]
            elif 2 <= num % 10 <= 4 and (num % 100 < 10 or num % 100 >= 20):
                return words[1]
            else:
                return words[2]
        else:  # english
            return words[0] if num == 1 else words[1]

    time_parts = []
    if hours > 0:
        time_parts.append(f"{hours} {get_plural(hours, msg['hour'])}")
    if minutes > 0:
        time_parts.append(f"{minutes} {get_plural(minutes, msg['minute'])}")
    if seconds > 0 or not time_parts:
        time_parts.append(f"{seconds} {get_plural(seconds, msg['second'])}")

    time_str = " ".join(time_parts)
    logger.bind(tag=tag).info(msg["before_launch"].format(time_str=time_str))
    await asyncio.sleep(delay_)


#
# Web3
#

@asynccontextmanager
async def web3_session(semaphore: asyncio.Semaphore, proxy: Optional[str], tag: str):
    msg = {
        "en": {
            "via_proxy": "via proxy: {proxy}",
            "without_proxy": "without proxy",
            "connecting_to": "Connecting to {rpc} {proxy_str}",
            "connection_failed": "Connection failed"
        },
        "ru": {
            "via_proxy": "через прокси: {proxy}",
            "without_proxy": "без прокси",
            "connecting_to": "Подключение к {rpc} {proxy_str}",
            "connection_failed": "Не удалось подключиться"
        }
    }[config.LOGS_LANGUAGE]

    await semaphore.acquire()

    rpc = SeismicChain.rpc
    web3 = AsyncWeb3(
        AsyncHTTPProvider(
            endpoint_uri=rpc,
            request_kwargs={'proxy': proxy},
        ),
        modules={'eth': AsyncEth},
    )

    try:
        proxy_str = msg["via_proxy"].format(proxy=proxy) if proxy else msg["without_proxy"]
        logger.bind(tag=tag).info(msg["connecting_to"].format(rpc=rpc, proxy_str=proxy_str))
        if not await web3.is_connected():
            logger.bind(tag=tag).error(msg["connection_failed"])
            raise ConnectionError

        yield web3
    except Exception as e:
        logger.bind(tag=tag).error(e)
    finally:
        await web3.provider.disconnect()
        await asyncio.sleep(10)
        semaphore.release()


async def perform_transaction(w3: AsyncWeb3, transaction, private_key: str, tag: str):
    msg = {
        "en": {
            "low_balance": "Low balance: {balance_eth:.12f} ETH. Tx cost: {tx_cost_eth:.12f} ETH",
            "perform_tx": "Performing transaction"
        },
        "ru": {
            "low_balance": "Низкий баланс: {balance_eth:.12f} ETH. Стоимость транзакции: {tx_cost_eth:.12f} ETH",
            "perform_tx": "Выполнение транзакции"
        }
    }[config.LOGS_LANGUAGE]

    address = w3.eth.account.from_key(private_key).address

    transaction["gas"] = await w3.eth.estimate_gas(transaction)
    gas_price = await w3.eth.gas_price
    transaction["maxFeePerGas"] = gas_price
    transaction["maxPriorityFeePerGas"] = gas_price

    transaction["nonce"] = await w3.eth.get_transaction_count(address)
    transaction["type"] = 2

    value = transaction.get("value", 0)
    tx_cost = value + transaction["gas"]

    balance = await w3.eth.get_balance(address)
    if balance < tx_cost:
        balance_eth = w3.from_wei(balance, "ether")
        tx_cost_eth = w3.from_wei(tx_cost, "ether")
        logger.bind(tag=tag).critical(msg["low_balance"].format(balance_eth=balance_eth, tx_cost_eth=tx_cost_eth))
        return

    logger.bind(tag=tag).info(msg["perform_tx"])

    signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = await w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_receipt = await w3.eth.wait_for_transaction_receipt(tx_hash)
    tx_hash_hex = w3.to_hex(tx_hash)

    message = f"{SeismicChain.explorer}/tx/{tx_hash_hex}"
    if tx_receipt["status"] == 1:
        logger.bind(tag=tag).success(message)
    else:
        logger.bind(tag=tag).error(message)

    return tx_receipt
