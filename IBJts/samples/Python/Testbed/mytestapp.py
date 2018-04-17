from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.common import *
import sys
from ContractSamples import ContractSamples
import time
from datetime import datetime, timedelta
import math
import pandas as pd
import logging
import os
import queue

from ibapi import comm

def printWhenExecuting(fn):
    def fn2(self):
        print("   doing", fn.__name__)
        fn(self)
        print("   done w/", fn.__name__)

    return fn2

def SetupLogger():
    if not os.path.exists("log"):
        os.makedirs("log")

    time.strftime("pyibapi.%Y%m%d_%H%M%S.log")

    recfmt = '(%(threadName)s) %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s'

    timefmt = '%y%m%d_%H:%M:%S'

    logging.basicConfig(level=logging.DEBUG,
                       format=recfmt, datefmt=timefmt)
    #logging.basicConfig(filename=time.strftime("log/pyibapi.%y%m%d_%H%M%S.log"),
    #                    filemode="w",
    #                   level=logging.INFO,
    #                    format=recfmt, datefmt=timefmt)
    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    logger.addHandler(console)


class TestWrapper(EWrapper):
    def __init__(self):
        EWrapper.__init__(self)
        self.historical_data = []
        self.historicalDataRequestIds = []
        self.historicalDataReceivedIds = []
        self.earliestTradeDate = ''
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        print("Error: ", reqId, " Code: ", errorCode, " Msg: ", errorString+'\n')
        if errorCode == 502:
            sys.exit()

    def headTimestamp(self, reqId: int, headTimestamp: str):
        print("HeadTimestamp: ", reqId, " ", headTimestamp)
        self.earliestTradeDate = headTimestamp

    # ! [historicaldata]
    def historicalData(self, reqId:int, bar: BarData):
        print("HistoricalData. ", reqId, " Date:", bar.date, "Open:", bar.open,
              "High:", bar.high, "Low:", bar.low, "Close:", bar.close, "Volume:", bar.volume,
              "Count:", bar.barCount, "WAP:", bar.average)
        self.historical_data.append([reqId, bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume, bar.barCount, bar.average])
        #if not self.historicalDataReceivedIds.count(reqId): self.historicalDataReceivedIds.append(reqId)
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
        TestClient.__init__(self, wrapper=self)
        self.nKeybInt = 0
        self.started = False
        self.nextValidOrderId = None
        self.nextHistoricalDataRequestId = 5000
        self.historicalDataFrame = pd.DataFrame(columns=["reqID", "Date", "Open", "High", "Low",
                                                         "Close", "Volume", "Count", "WAP"])
        self.permId2ord = {}
        #self.reqId2nErr = collections.defaultdict(int)
        self.globalCancelOnly = False
        self.simplePlaceOid = None
        self.sampleStock = ContractSamples.USStockAtSmart()

    @printWhenExecuting
    def earliestTradeDate_req(self):
        # ! [reqHeadTimeStamp]
        self.reqHeadTimeStamp(4100, self.sampleStock, "TRADES", 0, 1)
        # ! [reqHeadTimeStamp]
        time.sleep(1)
        # check the queue iif it is here
        while self.earliestTradeDate == '':
            try:
                text = self.msg_queue.get(block=True, timeout=0.2)
            except queue.Empty:
                logging.debug("queue.get: empty")
            else:
                fields = comm.read_fields(text)
                logging.debug("fields %s", fields)
                print(datetime.now(), 'CALLING INTERPRETER TOO')
                self.decoder.interpret(fields)


        # ! [cancelHeadTimestamp]
        self.cancelHeadTimeStamp(4100)
        # ! [cancelHeadTimestamp]

    @printWhenExecuting
    def historicalDataRequests_req(self):
        # ! [reqhistoricaldata]
        #queryTime = (datetime.datetime.today() - datetime.timedelta(days=180)).strftime("%Y%m%d %H:%M:%S")
        dateFormatStr = "%Y%m%d %H:%M:%S"
        #queryTime = datetime.today().strftime(dateFormatStr)
        queryTime =  '20040102  14:30:00'
        print("queryTime = ", queryTime)
        print("earliest trades date = ", self.earliestTradeDate)
        print("earliest trades date = ", self.sampleStock.earliestTradeDate)
        timeRange = datetime.strptime(queryTime, dateFormatStr) - datetime.strptime(self.earliestTradeDate, dateFormatStr)
        requestPeriod = timedelta(weeks=2)
        print("Steps:", math.ceil(timeRange/requestPeriod))
        for i in range(int(math.ceil(timeRange/requestPeriod))):
            print("step:", i)
            #requestID = 5000
            self.reqHistoricalData(self.nextHistoricalDataRequestId, self.sampleStock, queryTime,
                               "2 W", "5 mins", "TRADES", 1, 1, False, [])
            queryTime = (datetime.strptime(queryTime, dateFormatStr) - timedelta(weeks=2)).strftime(dateFormatStr)
            print("new query time:", queryTime)
            self.historicalDataRequestIds.append(self.nextHistoricalDataRequestId)
            self.nextHistoricalDataRequestId += 1
            if i == 1: break
            if i % 5 == 0 and i != 0: time.sleep(2)
            if i % 60 == 0 and i != 0: time.sleep(60*10)
            #self.reqHistoricalData(4102, ContractSamples.ETF(), queryTime, "1 Y", "1 day", "MIDPOINT", 1, 1, False, [])
        #self.reqHistoricalData(4104, ContractSamples.ETFOption(), queryTime, "2 W", "5 mins", "MIDPOINT", 1, 1, False, [])

        # ! [reqhistoricaldata]
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        self.historicalDataReceivedIds.append(reqId)
        if len(self.historicalDataReceivedIds) == len(self.historicalDataRequestIds):
            self.historicalDataStore()
            print("Data Stored")

    @printWhenExecuting
    def historicalDataStore(self):
        self.historicalDataFrame = self.historicalDataFrame.append(pd.DataFrame(self.historical_data,
                                                                                columns=["reqID", "Date", "Open",
                                                                                         "High", "Low", "Close",
                                                                                         "Volume", "Count", "WAP"]))
        self.historicalDataFrame.Date = pd.to_datetime(self.historicalDataFrame.Date)
        self.historicalDataFrame.set_index("Date", inplace=True)
        self.historicalDataFrame.to_hdf("Bstock.h5", 'df', mode='w')



    def historicalDataRequests_cancel(self):
        # Canceling historical data requests
        pass
        #self.cancelHistoricalData(4101)
        #self.cancelHistoricalData(4102)
        #self.cancelHistoricalData(4104)

    # ! [nextvalidid]
    #@printWhenExecuting
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)

        #self.nextValidOrderId = orderId
        # ! [nextvalidid]
        print("orderId = ", orderId)
        # we can start now
        self.start()

    #@printWhenExecuting
    def start(self):
        SetupLogger()
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
            #self.reqSecDefOptParams(5001, "SPY", "", "STK", 756733)
            self.earliestTradeDate_req()
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
    app.connect("127.0.0.1", 4002, 0)
    print("really no errors?")
    app.run()
    print("this is the last line in the code")
