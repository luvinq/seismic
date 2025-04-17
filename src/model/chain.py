from dataclasses import dataclass


@dataclass(frozen=True)
class Chain:
    name: str
    rpc: str
    chain_id: int
    symbol: str
    explorer: str


SeismicChain = Chain(
    name="Seismic Testnet",
    rpc="https://node-2.seismicdev.net/rpc",
    chain_id=5124,
    symbol="ETH",
    explorer="https://explorer-2.seismicdev.net"
)
