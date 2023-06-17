import requests.exceptions
import web3.auto


def get_chain_id(provider: web3.auto.Web3) -> int:
    try:
        return provider.eth.chain_id

    except (requests.exceptions.Timeout, TimeoutError, requests.exceptions.ConnectionError):
        return get_chain_id(provider=provider)

    except requests.exceptions.HTTPError as error:
        if '[429]' in str(error.response) or '[502]' in str(error.response):
            return get_chain_id(provider=provider)

        raise error

    except Exception as error:
        if not str(error):
            return get_chain_id(provider=provider)

        raise error


def get_nonce(provider: web3.auto.Web3,
              address: str) -> int:
    try:
        return provider.eth.get_transaction_count(address)


    except (requests.exceptions.Timeout, TimeoutError, requests.exceptions.ConnectionError):
        return get_nonce(provider=provider,
                         address=address)

    except requests.exceptions.HTTPError as error:
        if '[429]' in str(error.response) or '[502]' in str(error.response):
            return get_nonce(provider=provider,
                             address=address)

        raise error

    except Exception as error:
        if not str(error):
            return get_nonce(provider=provider,
                             address=address)

        raise error


def get_gwei(provider: web3.auto.Web3) -> int:
    try:
        return provider.eth.gas_price

    except (requests.exceptions.Timeout, TimeoutError, requests.exceptions.ConnectionError):
        return get_gwei(provider=provider)

    except requests.exceptions.HTTPError as error:
        if '[429]' in str(error.response) or '[502]' in str(error.response):
            return get_gwei(provider=provider)

        raise error

    except Exception as error:
        if not str(error):
            return get_gwei(provider=provider)

        raise error
