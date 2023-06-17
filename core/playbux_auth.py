from random import choice

import tls_client
import tls_client.sessions
from pypasser import reCaptchaV3
from pyuseragents import random as random_useragent

from utils import logger

headers = {
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://www.playbux.co',
    'referer': 'https://www.playbux.co/',
    'user-agent': random_useragent()
}


class PlayBuxAuth:
    def __init__(self,
                 account_email: str,
                 account_password: str,
                 account_proxy: str | None):
        self.account_email: str = account_email
        self.account_password: str = account_password
        self.account_proxy: str | None = account_proxy

    def solve_captcha(self) -> str:
        try:
            captcha_response: str = reCaptchaV3(anchor_url='https://www.google.com/recaptcha/api2/anchor?ar=1&'
                                                           'k=6LfBM9AgAAAAAMjPaQDEfiGRhGnFIkBd8BwWsJ6c&'
                                                           'co=aHR0cHM6Ly93d3cucGxheWJ1eC5jbzo0NDM.&hl=en&'
                                                           'v=SglpK98hSCn2CroR0bKRSJl5&size=invisible&cb=v02i16n2qhp8')

            return captcha_response

        except Exception as error:
            logger.error(f'{self.account_email} | Ошибка при решении капчи: {error}')

            return self.solve_captcha()

    def get_csrf_token(self,
                       session: tls_client.sessions.Session) -> str:
        try:
            r = session.get('https://www.playbux.co/api/auth/csrf')

            return r.json()['csrfToken']

        except Exception as error:
            logger.error(f'{self.account_email} | Ошибка при получении CSRF-токена: {error}')

            return self.get_csrf_token(session=session)

    def make_auth(self,
                  session: tls_client.sessions.Session,
                  captcha_response: str,
                  csrf_token: str) -> bool:
        try:
            r = session.post(url='https://www.playbux.co/api/auth/callback/credentials',
                             params={
                                 'recaptchaToken': captcha_response
                             },
                             data={
                                 'redirect': 'false',
                                 'email': self.account_email,
                                 'password': self.account_password,
                                 'callbackUrl': 'https://www.playbux.co/pre-alpha',
                                 'csrfToken': csrf_token,
                                 'json': 'true'
                             })

            if r.json()['url'] == 'https://www.playbux.co/pre-alpha':
                return True

            logger.error(f'{self.account_email} | Ошибка при авторизации, ответ: {r.text}')

            return False

        except Exception as error:
            logger.error(f'{self.account_email} | Неизвестная ошибка при авторизации: {error}')

            return self.make_auth(session=session,
                                  captcha_response=captcha_response,
                                  csrf_token=csrf_token)

    def main(self) -> bool | tls_client.sessions.Session:
        session = tls_client.Session(client_identifier=choice(['chrome_103',
                                                               'chrome_104',
                                                               'chrome_105',
                                                               'chrome_106',
                                                               'chrome_107',
                                                               'chrome_108',
                                                               'chrome109',
                                                               'Chrome110',
                                                               'chrome111',
                                                               'chrome112',
                                                               'firefox_102',
                                                               'firefox_104',
                                                               'firefox108',
                                                               'Firefox110',
                                                               'opera_89',
                                                               'opera_90']),
                                     random_tls_extension_order=True)
        session.headers.update(headers)

        if self.account_proxy: session.proxies.update({
            'http': self.account_proxy,
            'https': self.account_proxy
        })

        captcha_response: str = self.solve_captcha()
        csrf_token: str = self.get_csrf_token(session=session)

        make_auth_response: bool = self.make_auth(session=session,
                                                  captcha_response=captcha_response,
                                                  csrf_token=csrf_token)

        if make_auth_response:
            return session

        return False


def playbux_auth_start(account_data: dict) -> bool | tls_client.sessions.Session:
    account_email: str = account_data['email']
    account_password: str = account_data['password']
    account_proxy: str = account_data['proxy']

    if not account_proxy: account_proxy = None

    return PlayBuxAuth(account_email=account_email,
                       account_password=account_password,
                       account_proxy=account_proxy).main()
