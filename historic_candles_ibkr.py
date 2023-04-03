from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import json
from historic_config_ibkr import CONFIG_CONTRACTS, CONFIG_TIMES
import csv
import time

from datetime import datetime
import pytz
import h5py
import numpy as np

# Existing solution, should this be used instead?
# download_bars.py
# https://gist.github.com/wrighter/dd201adb09518b3c1d862255238d2534

from ibapi import get_version_string
print(f'\n- Python IB API{get_version_string()}')

CSV_HEADER = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'barCount', 'wap']


def datetimeStringToUnix(datetime_str):
    # Define the concatenated string datetime and the timezone
    # datetime_str = '20230102 10:00:00 Japan'

    # Parse the string datetime into a datetime object
    date = datetime.strptime(datetime_str[:17], '%Y%m%d %H:%M:%S')

    # Get the timezone from the string and create a timezone object
    timezone_str = datetime_str[18:]
    timezone = pytz.timezone(timezone_str)

    # Adjust the datetime object for the given timezone
    date_timezone = timezone.localize(date)
    unix_timestamp = int(date_timezone.timestamp())

    #print(unix_timestamp)
    return unix_timestamp

class App(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, wrapper = self)
        self.writer = None
        print('init!!')
        
    def error(self, reqId, errorCode, errorString, json):
        print("Error {} {} {}".format(reqId,errorCode,errorString))

    count = 0

    def setWriter(self, writer):
        print('set writer!!')
        self.writer = writer

    def historicalData(self, reqId, bar):
        print('ugh!!!!!!!!!!!')
        self.count = self.count + 1

        if not self.writer:
            print(bar.open)
            print('%s %s' % (reqId, str(bar)))
        else:
            print(bar.open)
            # self.writer.writerow([datetimeStringToUnix(bar.date), bar.open, bar.high, bar.low, bar.close, bar.volume, bar.barCount, bar.wap])

            print(bar.date)

            new_ohlc_data = (datetimeStringToUnix(bar.date), float(bar.open), float(bar.high), float(bar.low), float(bar.close), int(bar.volume), int(bar.barCount), float(bar.wap))
            # self.writer.resize(self.writer.shape[0] + 1, axis=0)
            # self.writer[-1] = np.array(new_ohlc_data, dtype=self.writer.dtype)


            if len(self.writer) == 0:
                self.writer.resize(1, axis=0)
                self.writer[0] = np.array(new_ohlc_data, dtype=self.writer.dtype)
            else:
                self.writer.resize(len(self.writer) + len(new_ohlc_data), axis=0)
                self.writer[-len(new_ohlc_data):] = np.array(new_ohlc_data, dtype=self.writer.dtype)



def downloadHistoric(app, config_contract, config_time):

    contract = Contract()
    contract.symbol = config_contract['symbol']  # "ES"
    contract.secType = config_contract['secType'] # "FUT"
    contract.exchange = config_contract['exchange'] # "CME"
    contract.currency = config_contract['currency'] # "USD"
    contract.lastTradeDateOrContractMonth = config_time['lastTradeDateOrContractMonth'] #"202306"

    endDateTime = config_time['endDateTime'] # '20230401-00:00:00'

    # change durationStr='1 D', to 6 M for prod run
    #app.reqHistoricalData(reqId=1, contract=contract, endDateTime=endDateTime, durationStr='5 D',
    #        barSizeSetting='1 min', whatToShow='TRADES', useRTH=True, formatDate=1, keepUpToDate=False, 
    #        chartOptions=[])
    app.reqHistoricalData(reqId=1, contract=contract, endDateTime=endDateTime, durationStr='10 D',
            barSizeSetting='1 hour', whatToShow='TRADES', useRTH=True, formatDate=1, keepUpToDate=False, 
            chartOptions=[])


    import time
    time.sleep(10)




def main():
    ## Init
    LIVE_PORTS = [7496, 4001]
    SIMULATED_PORTS = [7497, 4002]

    host = '127.0.0.1'
    port = 7496

    print(f'\n- Connect {host}:{str(port)}')

    app = App()
    app.connect(host, port, clientId = 1)

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    ##


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
    CONFIG_TIME = CONFIG_TIMES[1]

    filename = '%s_%s_%s_%s_%s' % (CONFIG_TIME['lastTradeDateOrContractMonth'], CONFIG_CONTRACT['exchange'], CONFIG_CONTRACT['symbol'], CONFIG_CONTRACT['secType'], CONFIG_CONTRACT['currency'])

    with h5py.File('data/%s.h5' % filename, 'a') as f:
        # Get a reference to the OHLC dataset, creating it if necessary
        if 'ohlc' in f:
            ohlc_dataset = f['ohlc']
        else:
            ohlc_dataset = f.create_dataset('ohlc', shape=(0,), maxshape=(None,), chunks=True, data=np.array([], dtype=[
                ('timestamp', 'i8'),
                ('open', 'f8'),
                ('high', 'f8'),
                ('low', 'f8'),
                ('close', 'f8'),
                ('volume', 'i8'),
                ('barCount', 'i8'),
                ('wap', 'f8')
            ]))
        app.setWriter(ohlc_dataset)
        downloadHistoric(app, CONFIG_CONTRACT, CONFIG_TIME)

    #with open('data/%s.csv' % filename, 'w') as fout:
    #    csvout = csv.writer(fout)
    #    csvout.writerow(CSV_HEADER)#
    #
    #    app.setWriter(csvout)
    #    downloadHistoric(app, CONFIG_CONTRACT, CONFIG_TIME)

    import time
    time.sleep(5)



if __name__ == '__main__':
    main()