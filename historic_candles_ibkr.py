from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import json
from historic_config_ibkr import CONFIG_CONTRACTS, CONFIG_TIMES
import csv
import time

# Existing solution, should this be used instead?
# download_bars.py
# https://gist.github.com/wrighter/dd201adb09518b3c1d862255238d2534

from ibapi import get_version_string
print(f'\n- Python IB API{get_version_string()}')

CSV_HEADER = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'barCount', 'wap']

class App(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, wrapper = self)
        self.writer = None
        
    def error(self, reqId, errorCode, errorString, json):
        print("Error {} {} {}".format(reqId,errorCode,errorString))

    count = 0
    def historicalData(self, reqId, bar):
        self.count = self.count + 1

        if not self.writer:
            print(bar.open)
            print('%s %s' % (reqId, str(bar)))
        else:
            print(bar.open)
            self.writer.writerow([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume, bar.barCount, bar.wap])


def downloadHistoric(config_contract, config_time, writer = None):
    LIVE_PORTS = [7496, 4001]
    SIMULATED_PORTS = [7497, 4002]

    host = '127.0.0.1'
    port = 7496

    print(f'\n- Connect {host}:{str(port)}')

    app = App()
    app.writer = writer
    app.connect(host, port, clientId = 1)

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()


    contract = Contract()
    contract.symbol = config_contract['symbol']  # "ES"
    contract.secType = config_contract['secType'] # "FUT"
    contract.exchange = config_contract['exchange'] # "CME"
    contract.currency = config_contract['currency'] # "USD"
    contract.lastTradeDateOrContractMonth = config_time['lastTradeDateOrContractMonth'] #"202306"

    endDateTime = config_time['endDateTime'] # '20230401-00:00:00'

    # change durationStr='1 D', to 6 M for prod run
    app.reqHistoricalData(reqId=1, contract=contract, endDateTime=endDateTime, durationStr='3 M',
            barSizeSetting='1 min', whatToShow='TRADES', useRTH=True, formatDate=1, keepUpToDate=False, 
            chartOptions=[])





def main():
    print(str(CONFIG_CONTRACTS))
    print(str(CONFIG_TIMES))

    #for CONFIG_TIME in CONFIG_TIMES:
    #    for CONFIG_CONTRACT in CONFIG_CONTRACTS:

    #        filename = '%s_%s_%s_%s_%s' % (CONFIG_TIME['lastTradeDateOrContractMonth'], CONFIG_CONTRACT['exchange'], CONFIG_CONTRACT['symbol'], CONFIG_CONTRACT['secType'], CONFIG_CONTRACT['currency'])
    #        with open('data/%s.csv' % filename, 'w') as fout:
    #            csvout = csv.writer(fout)
    #            csvout.writerow(CSV_HEADER)
    #            downloadHistoric(CONFIG_CONTRACT, CONFIG_TIME, csvout)
    #            time.sleep(1)

    CONFIG_CONTRACT = CONFIG_CONTRACTS[0]
    CONFIG_TIME = CONFIG_TIMES[0]

    filename = '%s_%s_%s_%s_%s' % (CONFIG_TIME['lastTradeDateOrContractMonth'], CONFIG_CONTRACT['exchange'], CONFIG_CONTRACT['symbol'], CONFIG_CONTRACT['secType'], CONFIG_CONTRACT['currency'])
    with open('data/__%s.csv' % filename, 'w') as fout:
        csvout = csv.writer(fout)
        csvout.writerow(CSV_HEADER)
        downloadHistoric(CONFIG_CONTRACT, CONFIG_TIME, csvout)

    import time
    time.sleep(20)


if __name__ == '__main__':
    main()