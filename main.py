from json import load
from multiprocessing.dummy import Pool

from core import watch_to_earn_start, daily_check_in_start
from utils import logger

if __name__ == '__main__':
    print('Donate (any EVM chain) - 0xDEADf12DE9A24b47Da0a43E1bA70B8972F5296F2\n')

    with open('accounts.json', 'r', encoding='utf-8-sig') as file:
        accounts_dict: list = load(file)

    logger.info(f'Загружено {len(accounts_dict)} аккаунтов')

    user_action: int = int(input('\n1. Watch To Earn'
                                 '\n2. Daily Check-in'
                                 '\nВыберите ваше действие: '))
    threads: int = int(input('Threads: '))
    print('')

    match user_action:
        case 1:
            with Pool(processes=threads) as executor:
                executor.map(watch_to_earn_start, accounts_dict)

        case 2:
            with Pool(processes=threads) as executor:
                executor.map(daily_check_in_start, accounts_dict)

        case _:
            pass

    logger.info('Работа успешно завершена')
    input('\nPress Enter To Exit..')
