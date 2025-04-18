import random
import string
from asyncio import Semaphore

from loguru import logger

from src import utils, config
from src.model import Account, SeismicChain
from src.service import Service

TIMER_CONTRACT_BYTECODE = "0x6080604052348015600f57600080fd5b5061018d8061001f6000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c8063557ed1ba1461003b578063d09de08a14610059575b600080fd5b610043610063565b60405161005091906100d9565b60405180910390f35b61006161006c565b005b60008054905090565b600160008082825461007e9190610123565b925050819055507f3912982a97a34e42bab8ea0e99df061a563ce1fe3333c5e14386fd4c940ef6bc6000546040516100b691906100d9565b60405180910390a1565b6000819050919050565b6100d3816100c0565b82525050565b60006020820190506100ee60008301846100ca565b92915050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052601160045260246000fd5b600061012e826100c0565b9150610139836100c0565b9250828201905080821115610151576101506100f4565b5b9291505056fea2646970667358221220801aef4e99d827a7630c9f3ce9c8c00d708b58053b756fed98cd9f2f5928d10f64736f6c634300081c0033"

ERC20_CONTRACT_BASE_BYTECODE = "0x608060405234801561001057600080fd5b50604051611972380380611972833981810160405281019061003291906104c2565b81818160039081610043919061075b565b508060049081610053919061075b565b5050506100903361006861009760201b60201c565b60ff16600a610077919061098f565b620f424061008591906109da565b6100a060201b60201c565b5050610b0d565b60006012905090565b600073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff16036101125760006040517fec442f050000000000000000000000000000000000000000000000000000000081526004016101099190610a5d565b60405180910390fd5b6101246000838361012860201b60201c565b5050565b600073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff160361017a57806002600082825461016e9190610a78565b9250508190555061024d565b60008060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054905081811015610206578381836040517fe450d38c0000000000000000000000000000000000000000000000000000000081526004016101fd93929190610abb565b60405180910390fd5b8181036000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550505b600073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff160361029657806002600082825403925050819055506102e3565b806000808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825401925050819055505b8173ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef836040516103409190610af2565b60405180910390a3505050565b6000604051905090565b600080fd5b600080fd5b600080fd5b600080fd5b6000601f19601f8301169050919050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052604160045260246000fd5b6103b48261036b565b810181811067ffffffffffffffff821117156103d3576103d261037c565b5b80604052505050565b60006103e661034d565b90506103f282826103ab565b919050565b600067ffffffffffffffff8211156104125761041161037c565b5b61041b8261036b565b9050602081019050919050565b60005b8381101561044657808201518184015260208101905061042b565b60008484015250505050565b6000610465610460846103f7565b6103dc565b90508281526020810184848401111561048157610480610366565b5b61048c848285610428565b509392505050565b600082601f8301126104a9576104a8610361565b5b81516104b9848260208601610452565b91505092915050565b600080604083850312156104d9576104d8610357565b5b600083015167ffffffffffffffff8111156104f7576104f661035c565b5b61050385828601610494565b925050602083015167ffffffffffffffff8111156105245761052361035c565b5b61053085828601610494565b9150509250929050565b600081519050919050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b6000600282049050600182168061058c57607f821691505b60208210810361059f5761059e610545565b5b50919050565b60008190508160005260206000209050919050565b60006020601f8301049050919050565b600082821b905092915050565b6000600883026106077fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff826105ca565b61061186836105ca565b95508019841693508086168417925050509392505050565b6000819050919050565b6000819050919050565b600061065861065361064e84610629565b610633565b610629565b9050919050565b6000819050919050565b6106728361063d565b61068661067e8261065f565b8484546105d7565b825550505050565b600090565b61069b61068e565b6106a6818484610669565b505050565b5b818110156106ca576106bf600082610693565b6001810190506106ac565b5050565b601f82111561070f576106e0816105a5565b6106e9846105ba565b810160208510156106f8578190505b61070c610704856105ba565b8301826106ab565b50505b505050565b600082821c905092915050565b600061073260001984600802610714565b1980831691505092915050565b600061074b8383610721565b9150826002028217905092915050565b6107648261053a565b67ffffffffffffffff81111561077d5761077c61037c565b5b6107878254610574565b6107928282856106ce565b600060209050601f8311600181146107c557600084156107b3578287015190505b6107bd858261073f565b865550610825565b601f1984166107d3866105a5565b60005b828110156107fb578489015182556001820191506020850194506020810190506107d6565b868310156108185784890151610814601f891682610721565b8355505b6001600288020188555050505b505050505050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052601160045260246000fd5b60008160011c9050919050565b6000808291508390505b60018511156108b35780860481111561088f5761088e61082d565b5b600185161561089e5780820291505b80810290506108ac8561085c565b9450610873565b94509492505050565b6000826108cc5760019050610988565b816108da5760009050610988565b81600181146108f057600281146108fa57610929565b6001915050610988565b60ff84111561090c5761090b61082d565b5b8360020a9150848211156109235761092261082d565b5b50610988565b5060208310610133831016604e8410600b841016171561095e5782820a9050838111156109595761095861082d565b5b610988565b61096b8484846001610869565b925090508184048111156109825761098161082d565b5b81810290505b9392505050565b600061099a82610629565b91506109a583610629565b92506109d27fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff84846108bc565b905092915050565b60006109e582610629565b91506109f083610629565b92508282026109fe81610629565b91508282048414831517610a1557610a1461082d565b5b5092915050565b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b6000610a4782610a1c565b9050919050565b610a5781610a3c565b82525050565b6000602082019050610a726000830184610a4e565b92915050565b6000610a8382610629565b9150610a8e83610629565b9250828201905080821115610aa657610aa561082d565b5b92915050565b610ab581610629565b82525050565b6000606082019050610ad06000830186610a4e565b610add6020830185610aac565b610aea6040830184610aac565b949350505050565b6000602082019050610b076000830184610aac565b92915050565b610e5680610b1c6000396000f3fe608060405234801561001057600080fd5b50600436106100935760003560e01c8063313ce56711610066578063313ce5671461013457806370a082311461015257806395d89b4114610182578063a9059cbb146101a0578063dd62ed3e146101d057610093565b806306fdde0314610098578063095ea7b3146100b657806318160ddd146100e657806323b872dd14610104575b600080fd5b6100a0610200565b6040516100ad9190610aaa565b60405180910390f35b6100d060048036038101906100cb9190610b65565b610292565b6040516100dd9190610bc0565b60405180910390f35b6100ee6102b5565b6040516100fb9190610bea565b60405180910390f35b61011e60048036038101906101199190610c05565b6102bf565b60405161012b9190610bc0565b60405180910390f35b61013c6102ee565b6040516101499190610c74565b60405180910390f35b61016c60048036038101906101679190610c8f565b6102f7565b6040516101799190610bea565b60405180910390f35b61018a61033f565b6040516101979190610aaa565b60405180910390f35b6101ba60048036038101906101b59190610b65565b6103d1565b6040516101c79190610bc0565b60405180910390f35b6101ea60048036038101906101e59190610cbc565b6103f4565b6040516101f79190610bea565b60405180910390f35b60606003805461020f90610d2b565b80601f016020809104026020016040519081016040528092919081815260200182805461023b90610d2b565b80156102885780601f1061025d57610100808354040283529160200191610288565b820191906000526020600020905b81548152906001019060200180831161026b57829003601f168201915b5050505050905090565b60008061029d61047b565b90506102aa818585610483565b600191505092915050565b6000600254905090565b6000806102ca61047b565b90506102d7858285610495565b6102e285858561052a565b60019150509392505050565b60006012905090565b60008060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050919050565b60606004805461034e90610d2b565b80601f016020809104026020016040519081016040528092919081815260200182805461037a90610d2b565b80156103c75780601f1061039c576101008083540402835291602001916103c7565b820191906000526020600020905b8154815290600101906020018083116103aa57829003601f168201915b5050505050905090565b6000806103dc61047b565b90506103e981858561052a565b600191505092915050565b6000600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054905092915050565b600033905090565b610490838383600161061e565b505050565b60006104a184846103f4565b90507fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff8110156105245781811015610514578281836040517ffb8f41b200000000000000000000000000000000000000000000000000000000815260040161050b93929190610d6b565b60405180910390fd5b6105238484848403600061061e565b5b50505050565b600073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff160361059c5760006040517f96c6fd1e0000000000000000000000000000000000000000000000000000000081526004016105939190610da2565b60405180910390fd5b600073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff160361060e5760006040517fec442f050000000000000000000000000000000000000000000000000000000081526004016106059190610da2565b60405180910390fd5b6106198383836107f5565b505050565b600073ffffffffffffffffffffffffffffffffffffffff168473ffffffffffffffffffffffffffffffffffffffff16036106905760006040517fe602df050000000000000000000000000000000000000000000000000000000081526004016106879190610da2565b60405180910390fd5b600073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff16036107025760006040517f94280d620000000000000000000000000000000000000000000000000000000081526004016106f99190610da2565b60405180910390fd5b81600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000208190555080156107ef578273ffffffffffffffffffffffffffffffffffffffff168473ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925846040516107e69190610bea565b60405180910390a35b50505050565b600073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff160361084757806002600082825461083b9190610dec565b9250508190555061091a565b60008060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050818110156108d3578381836040517fe450d38c0000000000000000000000000000000000000000000000000000000081526004016108ca93929190610d6b565b60405180910390fd5b8181036000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550505b600073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff160361096357806002600082825403925050819055506109b0565b806000808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825401925050819055505b8173ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef83604051610a0d9190610bea565b60405180910390a3505050565b600081519050919050565b600082825260208201905092915050565b60005b83811015610a54578082015181840152602081019050610a39565b60008484015250505050565b6000601f19601f8301169050919050565b6000610a7c82610a1a565b610a868185610a25565b9350610a96818560208601610a36565b610a9f81610a60565b840191505092915050565b60006020820190508181036000830152610ac48184610a71565b905092915050565b600080fd5b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b6000610afc82610ad1565b9050919050565b610b0c81610af1565b8114610b1757600080fd5b50565b600081359050610b2981610b03565b92915050565b6000819050919050565b610b4281610b2f565b8114610b4d57600080fd5b50565b600081359050610b5f81610b39565b92915050565b60008060408385031215610b7c57610b7b610acc565b5b6000610b8a85828601610b1a565b9250506020610b9b85828601610b50565b9150509250929050565b60008115159050919050565b610bba81610ba5565b82525050565b6000602082019050610bd56000830184610bb1565b92915050565b610be481610b2f565b82525050565b6000602082019050610bff6000830184610bdb565b92915050565b600080600060608486031215610c1e57610c1d610acc565b5b6000610c2c86828701610b1a565b9350506020610c3d86828701610b1a565b9250506040610c4e86828701610b50565b9150509250925092565b600060ff82169050919050565b610c6e81610c58565b82525050565b6000602082019050610c896000830184610c65565b92915050565b600060208284031215610ca557610ca4610acc565b5b6000610cb384828501610b1a565b91505092915050565b60008060408385031215610cd357610cd2610acc565b5b6000610ce185828601610b1a565b9250506020610cf285828601610b1a565b9150509250929050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b60006002820490506001821680610d4357607f821691505b602082108103610d5657610d55610cfc565b5b50919050565b610d6581610af1565b82525050565b6000606082019050610d806000830186610d5c565b610d8d6020830185610bdb565b610d9a6040830184610bdb565b949350505050565b6000602082019050610db76000830184610d5c565b92915050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052601160045260246000fd5b6000610df782610b2f565b9150610e0283610b2f565b9250828201905080821115610e1a57610e19610dbd565b5b9291505056fea2646970667358221220523b33a3e8f4890612d89b0b11841024f242e6b916323bfdffabb0be5f1c822f64736f6c634300081c0033"


class Mintair(Service):

    def __init__(self):
        Service.__init__(self)

        self.msg = {
            "en": {
                "deploy": "Deploy",
                "deploying": "Deploying",
                "name": "Name",
                "symbol": "Symbol"
            },
            "ru": {
                "deploy": "Деплой",
                "deploying": "Деплой",
                "name": "Название",
                "symbol": "Символ"
            }
        }[config.LOGS_LANGUAGE]

    async def deploy_timer_contract(self, semaphore: Semaphore, account: Account):
        tag = f"{account} > Mintair > {self.msg['deploy']}"
        await utils.delay(self._random_delay, tag)

        async with utils.web3_session(semaphore, account.proxy, tag) as web3:
            logger.bind(tag=tag).info(f"{self.msg['deploying']} Timer Contract")

            address = web3.eth.account.from_key(account.private_key).address

            tx = {
                'chainId': SeismicChain.chain_id,
                'from': address,
                'data': TIMER_CONTRACT_BYTECODE,
            }

            await utils.perform_transaction(web3, tx, account.private_key, tag)

    async def deploy_erc20_contract(self, semaphore: Semaphore, account: Account):
        tag = f"{account} > Mintair > {self.msg['deploy']}"
        await utils.delay(self._random_delay, tag)

        async with utils.web3_session(semaphore, account.proxy, tag) as web3:
            contract_name = self._generate_random_contract_name()
            contract_symbol = contract_name.upper()

            logger.bind(tag=tag).info(f"{self.msg['deploying']} ERC20 Contract")
            logger.bind(tag=tag).info(f"{self.msg['name']}: {contract_name}")
            logger.bind(tag=tag).info(f"{self.msg['symbol']}: {contract_symbol}")

            address = web3.eth.account.from_key(account.private_key).address
            data = self._generate_erc20_contract_bytecode(contract_name, contract_symbol)

            tx = {
                'chainId': SeismicChain.chain_id,
                'from': address,
                'data': data,
            }

            await utils.perform_transaction(web3, tx, account.private_key, tag)

    def _generate_random_contract_name(self) -> str:
        length = random.choice([4, 6])
        random_string = ''.join(random.choices(string.ascii_lowercase, k=length))
        return random_string

    def _string_to_hex_padded(self, s):
        hex_str = s.encode('utf-8').hex()
        padded_hex = hex_str.ljust(64, '0')
        return padded_hex

    def _generate_erc20_contract_bytecode(self, name: str, symbol: str):
        name_len_hex = "{:064x}".format(len(name))
        name_hex = self._string_to_hex_padded(name)

        symbol_len_hex = "{:064x}".format(len(symbol))
        symbol_hex = self._string_to_hex_padded(symbol)

        bytecode = (
                "0000000000000000000000000000000000000000000000000000000000000040"  # name offset
                "0000000000000000000000000000000000000000000000000000000000000080"  # symbol offset
                + name_len_hex
                + name_hex
                + symbol_len_hex
                + symbol_hex
        )

        return ERC20_CONTRACT_BASE_BYTECODE + bytecode
