import tls_client
import tls_client.sessions
import web3.main
from eth_account import Account
from eth_account.datastructures import SignedTransaction
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.auto import w3
from web3.exceptions import TimeExhausted
from web3.types import TxReceipt

from constants import RPC_URL, playbux_quest_abi, PLAYBUX_QUEST_CONTRACT_ADDRESS
from core import playbux_auth_start
from utils import get_gwei, get_nonce, get_chain_id
from utils import logger


class DailyCheckIn:
    def __init__(self,
                 account_email: str,
                 account_password: str,
                 account_private_key: str,
                 account_proxy: str | None,
                 session: tls_client.sessions.Session):
        self.account_email: str = account_email
        self.account_password: str = account_password
        self.account_private_key: str = account_private_key
        self.account_proxy: str | None = account_proxy
        self.session: tls_client.sessions.Session = session

    def check_available_check_in(self,
                                 address: str) -> tuple[bool, str]:
        try:
            r = self.session.get(url='https://www.playbux.co/api/v2/quests/check-in',
                                 params={
                                     'address': address
                                 })

            return r.json()['isCheckInToday'], r.json()['hashedUser']

        except Exception as error:
            logger.error(f'{self.account_email} | Ошибка при проверке на доступность Daily Check-in: {error}')

            return self.check_available_check_in(address=address)

    def complete_quest(self,
                       transaction_hash: str) -> bool:
        try:
            r = self.session.post('https://www.playbux.co/api/v2/quests/confirm-quests',
                                  json={
                                      'txId': transaction_hash
                                  })

            if r.json().get('error'):
                logger.error(f'{self.account_email} | Ошибка при подтверждении транзакции на '
                             f'Daily Check-in: {r.json()["error"]}')

                return self.complete_quest(transaction_hash=transaction_hash)

            return r.json()['success']

        except Exception as error:
            logger.error(f'{self.account_email} | Ошибка при подтверждении транзакции на Daily Check-in: {error}')

            return self.complete_quest(transaction_hash=transaction_hash)

    def main(self) -> None:
        account: LocalAccount = Account.from_key(private_key=self.account_private_key)

        is_available_check_in, hashed_user = self.check_available_check_in(address=account.address)

        if is_available_check_in:
            logger.info(f'{self.account_email} | Daily Check-in уже заклеймлен')
            return

        web3_provider: web3.main.Web3 = Web3(Web3.HTTPProvider(RPC_URL))
        contract = web3_provider.eth.contract(address=PLAYBUX_QUEST_CONTRACT_ADDRESS,
                                              abi=playbux_quest_abi)

        transaction_data: dict = contract.functions.doQuest(1,
                                                            f'DAILY_CHECK_IN-{hashed_user}').build_transaction({
            'gasPrice': get_gwei(provider=web3_provider),
            'from': account.address,
            'nonce': get_nonce(provider=web3_provider,
                               address=account.address),
            'chainId': get_chain_id(provider=web3_provider)
        })

        try:
            web3_provider.eth.estimate_gas(transaction=transaction_data)

        except ValueError as error:
            logger.error(
                f'{self.account_email} | Ошибка при симуляции транзакции на выполнение Daily Check-in: {error}')
            return

        signed_tx: SignedTransaction = web3_provider.eth.account.sign_transaction(transaction_dict=transaction_data,
                                                                                  private_key=self.account_private_key)
        transaction_hash: str = w3.to_hex(web3_provider.eth.send_raw_transaction(signed_tx.rawTransaction))

        logger.info(f'{self.account_email} | Транзакция на Daily Check-in отправлена, TX Hash: {transaction_hash}')

        try:
            transaction_response: TxReceipt = web3_provider.eth.wait_for_transaction_receipt(
                transaction_hash=transaction_hash)

        except TimeExhausted:
            logger.error(f'{self.account_email} | Не удалось дождаться завершения транзакции, '
                         f'TX Hash: {transaction_hash}')
            return

        if transaction_response.status == 1:
            self.session.headers.update({
                'content-type': 'application/json',
            })

            logger.success(f'{self.account_email} | {transaction_hash}')

            if self.complete_quest(transaction_hash=transaction_hash):
                logger.success(f'{self.account_email} | Успешно заклеймил Daily Check-in')

            return

        logger.error(f'{self.account_email} | {transaction_hash}')


def daily_check_in_start(account_data: dict) -> None:
    account_email: str = account_data['email']
    account_password: str = account_data['password']
    account_private_key: str = account_data['private_key']
    account_proxy: str = account_data['proxy']

    if not account_proxy: account_proxy = None

    session: bool | tls_client.sessions.Session = playbux_auth_start(account_data=account_data)

    if not session:
        return

    DailyCheckIn(account_email=account_email,
                 account_password=account_password,
                 account_private_key=account_private_key,
                 account_proxy=account_proxy,
                 session=session).main()
