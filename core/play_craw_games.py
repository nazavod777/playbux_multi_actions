from random import choice

import tls_client
import tls_client.sessions

from constants import AVAILABLE_CRAW_GAMES
from core import playbux_auth_start
from utils import logger


class PlayCrawGames:
    def __init__(self,
                 account_email: str,
                 account_password: str,
                 account_proxy: str | None,
                 casino_type: int,
                 session: tls_client.sessions.Session):
        self.account_email: str = account_email
        self.account_password: str = account_password
        self.account_proxy: str | None = account_proxy
        self.casino_type: int = casino_type
        self.session: tls_client.sessions.Session = session

    def get_balance(self) -> int:
        try:
            r = self.session.get(url='https://www.playbux.co/api/v2/me')

            return int(r.json()['user']['balance']['BRK'])

        except Exception as error:
            logger.error(f'{self.account_email} | Ошибка при получении BRK баланса: {error}')

            return self.get_balance()

    def play_craw_game(self,
                       current_casino_name: str) -> bool:
        r = self.session.post(url=f'https://www.playbux.co/api/v2/claw-machines/{current_casino_name}')

        if r.json().get('error') and r.json()['error'] == 'Not enough balance':
            return False

        logger.info(f'{self.account_email} | {r.text}')

        return True

    def main(self) -> None:
        brk_balance: int = self.get_balance()

        while brk_balance >= 1000000000000000000:
            if self.casino_type == 7:
                current_casino_name: str = choice(list(AVAILABLE_CRAW_GAMES.values()))

            else:
                current_casino_name: str = AVAILABLE_CRAW_GAMES[self.casino_type]

            play_craw_game_result: bool = self.play_craw_game(current_casino_name=current_casino_name)

            if not play_craw_game_result:
                break

            brk_balance: int = self.get_balance()

        logger.info(f'{self.account_email} | Закончились BRK для игры')


def play_craw_games_start(account_data: dict,
                          casino_type: int) -> None:
    account_email: str = account_data['email']
    account_password: str = account_data['password']
    account_proxy: str = account_data['proxy']

    if not account_proxy: account_proxy = None

    session: bool | tls_client.sessions.Session = playbux_auth_start(account_data=account_data)

    if not session:
        return

    PlayCrawGames(account_email=account_email,
                  account_password=account_password,
                  account_proxy=account_proxy,
                  casino_type=casino_type,
                  session=session).main()
