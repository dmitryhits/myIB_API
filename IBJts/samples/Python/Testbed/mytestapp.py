from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.common import *
import sys
from ContractSamples import ContractSamples
import time

class TestWrapper(EWrapper):
    def __init__(self):
        EWrapper.__init__(self)

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        print("Error: ", reqId, " Code: ", errorCode, " Msg: ", errorString+'\n')
        if errorCode == 502:
            sys.exit()

    def headTimestamp(self, reqId: int, headTimestamp: str):
        print("HeadTimestamp: ", reqId, " ", headTimestamp)


class TestClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)




class TestApp(TestClient, TestWrapper):
    def __init__(self):
        TestWrapper.__init__(self)
        TestClient.__init__(self,wrapper=self)

    # ! [nextvalidid]
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)

        #self.nextValidOrderId = orderId
        # ! [nextvalidid]

        # we can start now
        self.historicalDataRequests_req()

    def historicalDataRequests_req(self):
        # ! [reqHeadTimeStamp]
        self.reqHeadTimeStamp(4103, ContractSamples.USStockAtSmart(), "TRADES", 0, 1)
        # ! [reqHeadTimeStamp]

        time.sleep(1)

        # ! [cancelHeadTimestamp]
        self.cancelHeadTimeStamp(4103)
        # ! [cancelHeadTimestamp]

if __name__ == '__main__':
    app = TestApp()
    app.connect("127.0.0.1", 7497, 0)
    print("really no errors?")
    app.run()
    print("this is the last line in the code")
