from random import randint
from time import sleep
from time import time

import tls_client
import tls_client.sessions

from core import playbux_auth_start
from utils import logger


class WatchToEarn:
    def __init__(self,
                 account_email: str,
                 account_password: str,
                 account_proxy: str | None,
                 session: tls_client.sessions.Session):
        self.account_email: str = account_email
        self.account_password: str = account_password
        self.account_proxy: str | None = account_proxy
        self.session: tls_client.sessions.Session = session

    def get_fingerprint(self) -> str:
        try:
            r = self.session.get(url='https://www.playbux.co/api/v2/watch-to-earn/session')

            if r.json().get('msg') and r.json()['msg'] == 'success' and not r.json()['data']:
                r = self.session.get(url='https://kawayiyi.com/tls')

                return r.json()['tlsHashMd5']

            return r.json()['data']['fingerprint']

        except Exception as error:
            logger.error(f'{self.account_email} | Ошибка при получении FingerPrint: {error}')

            return self.get_fingerprint()

    def send_watch_video_request(self,
                                 current_vt: str) -> str:
        try:
            r = self.session.post(url='https://www.playbux.co/api/v2/watch-to-earn/session',
                                  json={
                                      'fingerprint': self.session.headers['fingerprint'],
                                      'timestamp': int(str(int(time())) + str("{:03d}".format(randint(0, 999))))
                                  })

            if r.json()['msg'] == 'success':
                return r.json()['data']

        except Exception as error:
            logger.error(f'{self.account_email} | Ошибка при отправке запроса на просмотр видео: {error}')

            return self.send_watch_video_request(current_vt=current_vt)

    def check_progress(self) -> bool:
        r = self.session.get(url='https://www.playbux.co/api/v2/watch-to-earn/rewards')

        return False if r.json()['latest']['progress'] < 100 else True

    def main(self) -> None:
        received_vt: str = 'first'
        fingerprint: str = self.get_fingerprint()

        self.session.headers.update({
            'accept-language': 'ru,en;q=0.9,vi;q=0.8,es;q=0.7,cy;q=0.6',
            'content-type': 'application/json',
            'fingerprint': fingerprint
        })

        logger.info(f'{self.account_email} | Начинаю просмотр видео')

        while not self.check_progress():
            self.session.headers.update({
                'vt': received_vt
            })

            received_vt: str = self.send_watch_video_request(current_vt=received_vt)

            sleep(5)

        logger.success(f'{self.account_email} | Успешно просмотрено видео до получения награды')


def watch_to_earn_start(account_data: dict) -> None:
    account_email: str = account_data['email']
    account_password: str = account_data['password']
    account_proxy: str = account_data['proxy']

    if not account_proxy: account_proxy = None

    session: bool | tls_client.sessions.Session = playbux_auth_start(account_data=account_data)

    if not session:
        return

    WatchToEarn(account_email=account_email,
                account_password=account_password,
                account_proxy=account_proxy,
                session=session).main()
