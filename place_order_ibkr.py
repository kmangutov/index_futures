from ibapi import wrapper
from ibapi.client import EClient
from ibapi.common import *
from ibapi.contract import *
from ibapi.order import *
from time import sleep

from ibapi.client import *
from ibapi.wrapper import *

# https://ibkrcampus.com/trading-lessons/python-placing-orders/

# alternative api ib_insync, supposedly easier
# https://algotrading101.com/learn/ib_insync-interactive-brokers-api-guide/

class IBKROrderPlacer(EClient, wrapper.EWrapper):
    def __init__(self, client_id):
        EClient.__init__(self, self)
        self.client_id = client_id
        self.order_id = None
        self.confirmation_received = False

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.order_id = orderId

    def orderStatus(self, orderId:OrderId , status:str, filled:float, remaining:float, avgFillPrice:float, permId:int, parentId:int, lastFillPrice:float, clientId:int, whyHeld:str, mktCapPrice: float):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
        print('orderStatus %s %s', ((str(orderId), status)))
        if orderId == self.order_id and status == "Filled":
            print("Order filled.")
            self.confirmation_received = True


    def openOrder(self, orderId: OrderId, contract: Contract, order: Order, orderState: OrderState):
        print(f"openOrder. orderId: {orderId}, contract: {contract}, order: {order}")
    #def orderStatus(self, orderId: OrderId, status: str, filled: Decimal, remaining: Decimal, avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float):
    #    print(f"orderId: {orderId}, status: {status}, filled: {filled}, remaining: {remaining}, avgFillPrice: {avgFillPrice}, permId: {permId}, parentId: {parentId}, lastFillPrice: {lastFillPrice}, clientId: {clientId}, whyHeld: {whyHeld}, mktCapPrice: {mktCapPrice}")


    def error(self, reqId, errorCode, errorString):
        print("Error {} {} {}".format(reqId,errorCode,errorString))

    def place_order(self, symbol, quantity, limit_price, action):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "FUT"
        contract.exchange = "GLOBEX"
        contract.currency = "USD"
        contract.lastTradeDateOrContractMonth = "202306"

        order = Order()
        order.action = action
        order.orderType = "LMT"
        order.totalQuantity = quantity
        order.lmtPrice = limit_price

        self.nextValidId(1)
        while self.order_id is None:
            sleep(0.1)

        print('placeORder')

        self.placeOrder(self.order_id, contract, order)

        if False:
            while not self.confirmation_received:
                sleep(0.1)

            self.cancelOrder(self.order_id)
            print("Order canceled.")


from ibapi import get_version_string
print(f'\n- Python IB API{get_version_string()}')


if __name__ == '__main__':
    ib_order_placer = IBKROrderPlacer(client_id=999)
    ib_order_placer.connect("127.0.0.1", 7497, clientId=999)

    ib_order_placer.place_order(symbol="ES", quantity=1, limit_price=4000, action="BUY")

    ib_order_placer.reqAllOpenOrders()
    sleep(5)

    ib_order_placer.reqAllOpenOrders()
    sleep(5)

    ib_order_placer.disconnect()
