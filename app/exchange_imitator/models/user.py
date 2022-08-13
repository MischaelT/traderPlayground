from utils.config import TRADING_LIST


class User():

    def __init__(self, user_balance, trading_list) -> None:

        self.account_balance = user_balance
        self.trading_list = trading_list
        self.asset_balance = {i: 0 for i in TRADING_LIST}
