from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.common import *
import sys
from ContractSamples import ContractSamples
import time
import datetime

class TestWrapper(EWrapper):
    def __init__(self):
        EWrapper.__init__(self)

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        print("Error: ", reqId, " Code: ", errorCode, " Msg: ", errorString+'\n')
        if errorCode == 502:
            sys.exit()

    def headTimestamp(self, reqId: int, headTimestamp: str):
        print("HeadTimestamp: ", reqId, " ", headTimestamp)
        self.earliestDate = headTimestamp

    # ! [historicaldata]
    def historicalData(self, reqId:int, bar: BarData):
        print("HistoricalData. ", reqId, " Date:", bar.date, "Open:", bar.open,
              "High:", bar.high, "Low:", bar.low, "Close:", bar.close, "Volume:", bar.volume,
              "Count:", bar.barCount, "WAP:", bar.average)
    # ! [historicaldata]

    # ! [historicaldataend]
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd ", reqId, "from", start, "to", end)
    # ! [historicaldataend]

    # ! [historicalDataUpdate]
    def historicalDataUpdate(self, reqId: int, bar: BarData):
        print("HistoricalDataUpdate. ", reqId, " Date:", bar.date, "Open:", bar.open,
              "High:", bar.high, "Low:", bar.low, "Close:", bar.close, "Volume:", bar.volume,
              "Count:", bar.barCount, "WAP:", bar.average)
    # ! [historicalDataUpdate]

    # ! [securityDefinitionOptionParameter]
    def securityDefinitionOptionParameter(self, reqId: int, exchange: str,
                                          underlyingConId: int, tradingClass: str, multiplier: str,
                                          expirations: SetOfString, strikes: SetOfFloat):
        super().securityDefinitionOptionParameter(reqId, exchange,
                                                  underlyingConId, tradingClass, multiplier, expirations, strikes)
        print("Security Definition Option Parameter. ReqId:", reqId, "Exchange:", exchange, "Underlying conId:", underlyingConId)
        #print("Security Definition Option Parameter. ReqId:%d Exchange:%s Underlying conId: %d " % reqId, exchange, underlyingConId)
        #print("TradingClass:%s Multiplier:%s Exp:%s Strikes:%s" % tradingClass, multiplier, ",".join(expirations), ",".join(str(strikes)))
        print("TradingClass:", tradingClass, "Multiplier:", multiplier, "Exp:", ",".join(expirations))
        print("Strikes:", strikes)
    # ! [securityDefinitionOptionParameter]




    # ! [securityDefinitionOptionParameterEnd]
    def securityDefinitionOptionParameterEnd(self, reqId: int):
        super().securityDefinitionOptionParameterEnd(reqId)
        print("Security Definition Option Parameter End. Request: ", reqId)
    # ! [securityDefinitionOptionParameterEnd]



class TestClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)




class TestApp(TestClient, TestWrapper):
    def __init__(self):
        TestWrapper.__init__(self)
        TestClient.__init__(self,wrapper=self)
        self.nKeybInt = 0
        self.started = False
        self.nextValidOrderId = None
        self.permId2ord = {}
        #self.reqId2nErr = collections.defaultdict(int)
        self.globalCancelOnly = False
        self.simplePlaceOid = None

    def historicalDataRequests_req(self):
        # ! [reqHeadTimeStamp]
        self.reqHeadTimeStamp(4103, ContractSamples.USStockAtSmart(), "TRADES", 0, 1)
        # ! [reqHeadTimeStamp]

        time.sleep(1)

        # ! [cancelHeadTimestamp]
        self.cancelHeadTimeStamp(4103)
        # ! [cancelHeadTimestamp]
        # ! [reqhistoricaldata]
        #queryTime = (datetime.datetime.today() - datetime.timedelta(days=180)).strftime("%Y%m%d %H:%M:%S")
        queryTime = datetime.datetime.today().strftime("%Y%m%d %H:%M:%S")
        print("queryTime = ", queryTime)
        self.reqHistoricalData(4101, ContractSamples.USStockAtSmart(), queryTime,
                               "1 M", "1 day", "MIDPOINT", 1, 1, False, [])
        #self.reqHistoricalData(4102, ContractSamples.ETF(), queryTime, "1 Y", "1 day", "MIDPOINT", 1, 1, False, [])
        self.reqHistoricalData(4104, ContractSamples.ETFOption(), queryTime, "1 M", "1 hour", "MIDPOINT", 1, 1, False, [])

        # ! [reqhistoricaldata]

    def historicalDataRequests_cancel(self):
        # Canceling historical data requests
        self.cancelHistoricalData(4101)
        self.cancelHistoricalData(4102)
        self.cancelHistoricalData(4104)

    # ! [nextvalidid]
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)

        #self.nextValidOrderId = orderId
        # ! [nextvalidid]
        print("orderId = ", orderId)
        # we can start now
        self.start()


    def start(self):
        if self.started:
            return

        self.started = True
        print("STARTING")

        if self.globalCancelOnly:
            print("Executing GlobalCancel only")
            self.reqGlobalCancel()
        else:
            print("Executing requests")
            #self.reqGlobalCancel()
            #self.marketDataType_req()
            #self.accountOperations_req()
            #self.tickDataOperations_req()
            #self.marketDepthOperations_req()
            #self.realTimeBars_req()
            self.reqSecDefOptParams(5001, "SPY", "", "STK", 756733)
            self.historicalDataRequests_req()
            #self.optionsOperations_req()
            #self.marketScanners_req()
            #self.reutersFundamentals_req()
            #self.bulletins_req()
            #self.contractOperations_req()
            #self.contractNewsFeed_req()
            #self.miscelaneous_req()
            #self.linkingOperations()
            #self.financialAdvisorOperations()
            #self.orderOperations_req()
            print("Executing requests ... finished")

    def keyboardInterrupt(self):
        self.nKeybInt += 1
        if self.nKeybInt == 1:
            self.stop()
        else:
            print("Finishing test")
            self.done = True

    def stop(self):
        print("Executing cancels")
        #self.orderOperations_cancel()
        #self.accountOperations_cancel()
        #self.tickDataOperations_cancel()
        #self.marketDepthOperations_cancel()
        #self.realTimeBars_cancel()
        self.historicalDataRequests_cancel()
        #self.optionsOperations_cancel()
        #self.marketScanners_cancel()
        #self.reutersFundamentals_cancel()
        #self.bulletins_cancel()
        print("Executing cancels ... finished")

    def nextOrderId(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid


if __name__ == '__main__':
    app = TestApp()
    app.connect("127.0.0.1", 7497, 0)
    print("really no errors?")
    app.run()
    print("this is the last line in the code")
