# ⚡ Seismic Testnet Script

![](https://docs.seismic.systems/~gitbook/image?url=https%3A%2F%2F1676143925-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Forganizations%252FwsvtQCKyhniEkSm6fIzR%252Fsites%252Fsite_eI6TX%252Fsocialpreview%252FKmVxIslEccslZruTmvwx%252FFrame%25203337.png%3Falt%3Dmedia%26token%3Da32be09a-ddb9-46d6-b052-db5d1300e8cf&width=1200&height=630&sign=5e3cc800&sv=2)

## ⭐ Features

- **Transfers:** Send ETH to yourself
- **Mintair:** Deploy Smart Contracts
  - Timer Contract
  - ERC20 Contract with random name and symbol
- **...**

<br>

- **Multi-account Support:** Use many accounts with proxies
- **Easy Setup:** Add, remove, and view accounts through a user-friendly CLI

## 📦 Installation

1. Clone the repository

```shell
git clone https://github.com/luvinq/seismic.git
cd seismic
```

2. Install dependencies

```shell
pip install -r requirements.txt
```

## 📝 Configuration

1. Configure your accounts

```shell
python accounts.py
```

2. (Optional) Configure script settings in `src/config.py`

```python
AMOUNT_MIN = 0.000001     # Minimal amount for one action
AMOUNT_MAX = 0.00001      # Maximal amount for one action

DELAY_MAX = 30            # Maximal delay for one action (in minutes!)

RUN_TIMES_MAX = 3         # Maximal action run times
```

## ❓ What the script does

- For `each account`
- The script will run `every action`
- Random times from `1` to `RUN_TIMES_MAX`
- With random delay from `0` to `DELAY_MAX`
- Using from `AMOUNT_MIN` to `AMOUNT_MAX` tokens

## 🚀 Usage

⚠️ Before running the script make sure your accounts have positive ETH
balance

```shell
python -m src.main
```

ETH is available at https://faucet-2.seismicdev.net/

## 😢 Problems

If you have any problems, contact me via https://t.me/iamluvin
and I will try to help you ❤️
