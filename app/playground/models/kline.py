class Kline:

    def __init__(self, tick, open_price, high_price, low_price, close_price, timeframe) -> None:

        self.timeframe = timeframe

        self.tick = tick
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price

    def get_average_price(self):
        # return (self.open_price+self.close_price)/2
        return (self.close_price)
