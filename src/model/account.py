from dataclasses import dataclass
from typing import Optional

from src import config


@dataclass(frozen=True)
class Account:
    id: int
    private_key: str
    proxy: Optional[str]

    def __str__(self) -> str:
        msg = {
            "en": {
                "account": "Account"
            },
            "ru": {
                "account": "Аккаунт"
            }
        }[config.LOGS_LANGUAGE]

        return f"{msg['account']} {self.id}"
