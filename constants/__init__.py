from json import load

with open('constants/playbux_quest_abi.json', 'r', encoding='utf-8-sig') as file:
    playbux_quest_abi: list = load(file)

with open('settings.json', 'r', encoding='utf-8-sig') as file:
    settings_json: dict = load(file)

PLAYBUX_QUEST_CONTRACT_ADDRESS: str = '0x93C2260EE41b285C9Bbf98c6B9FFfbd3D62fcA36'
RPC_URL: str = settings_json['rpc_url']
WAIT_TRANSACTION_RESULT: bool = settings_json['wait_transaction_result']
