from asyncio import Semaphore

from loguru import logger

from src import utils, config
from src.model import Account, SeismicChain
from src.service import Service


class Native(Service):

    def __init__(self):
        Service.__init__(self)

        self.msg = {
            "en": {
                "send": "Send",
                "sending": "Sending {amount:.12f} ETH to myself"
            },
            "ru": {
                "send": "Отправить",
                "sending": "Отправка {amount:.12f} ETH самому себе"
            }
        }[config.LOGS_LANGUAGE]

    async def send_eth(self, semaphore: Semaphore, account: Account):
        tag = f"{account} > {self.msg['send']} ETH"
        await utils.delay(self._random_delay, tag)

        async with utils.web3_session(semaphore, account.proxy, tag) as web3:
            amount = self._random_amount
            logger.bind(tag=tag).info(self.msg["sending"].format(amount=amount))

            address = web3.eth.account.from_key(account.private_key).address

            tx = {
                'chainId': SeismicChain.chain_id,
                'from': address,
                'to': address,
                'value': web3.to_wei(amount, 'ether'),
            }

            await utils.perform_transaction(web3, tx, account.private_key, tag)
