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

# https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html
# https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html
class App(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, wrapper = self)
        self.writer = None
        
    def error(self, reqId, errorCode, errorString, json):
        print("Error {} {} {}".format(reqId,errorCode,errorString))

    count = 0

    def setWriter(self, writer):
        self.writer = writer
        # print('dtpye: ' + str(self.writer.dtype))


    def historicalData(self, reqId, bar):
        self.count = self.count + 1
        print('a')
        new_ohlc_data = (datetimeStringToUnix(bar.date), float(bar.open), float(bar.high), float(bar.low), float(bar.close), int(bar.volume), int(bar.barCount), float(bar.wap))

        if not self.writer:
            print('historicalData: ' + str(new_ohlc_data))
            return

        #if False:
        #    if len(self.writer) == 0:
        #        self.writer.resize(1, axis=0)
        #        self.writer[0] = np.array(new_ohlc_data, dtype=self.writer.dtype)
        #    else:
        #        self.writer.resize(len(self.writer) + len(new_ohlc_data), axis=0)
        #        self.writer[-len(new_ohlc_data):] = np.array(new_ohlc_data, dtype=self.writer.dtype)
        #else:
        
        #if len(self.writer) == 0:
        #    self.writer.resize(1, axis=0)
        #    self.writer[0] = np.array([new_ohlc_data], dtype=self.writer.dtype)
        #else:
        #    self.writer.resize(len(self.writer) + len(new_ohlc_data), axis=0)
        #    self.writer[-len(new_ohlc_data):] = np.array([new_ohlc_data], dtype=self.writer.dtype)

        self.writer.resize(len(self.writer) + 1, axis=0)
        self.writer[-1] = new_ohlc_data
        self.writer.flush()

    def historicalDataEnd(self, reqId, start, end):
        print('end')


def downloadHistoric(app, config_contract, config_time):

    contract = Contract()
    contract.symbol = config_contract['symbol']  # "ES"
    contract.secType = config_contract['secType'] # "FUT"
    contract.exchange = config_contract['exchange'] # "CME"
    contract.currency = config_contract['currency'] # "USD"
    
    if config_contract['secType'] != 'CASH':
        contract.lastTradeDateOrContractMonth = config_time['lastTradeDateOrContractMonth'] #"202306"

    endDateTime = config_time['endDateTime'] # '20230401-00:00:00'

    # change durationStr='1  D', to 6 M for prod run
    
    whatToShow = 'TRADES'
    if config_contract['secType'] == 'CASH':
        whatToShow = 'MIDPOINT'

    print(str(contract))
    app.reqHistoricalData(reqId=1, contract=contract, endDateTime=endDateTime, durationStr='1 W',
            barSizeSetting='1 hour', whatToShow=whatToShow, useRTH=True, formatDate=1, keepUpToDate=False, 
            chartOptions=[])

    # Needed because downloading happen in separate thread
    # TODO: In App override historicalEnd and use that to communicate finish
    time.sleep(30)

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

    time.sleep(1)

    print(str(CONFIG_CONTRACTS))
    print(str(CONFIG_TIMES))

    #for CONFIG_TIME in CONFIG_TIMES:
    #    for CONFIG_CONTRACT in CONFIG_CONTRACTS:

    # Hardcoaded 1 by 1 for now
    CONFIG_CONTRACT = CONFIG_CONTRACTS[4]
    CONFIG_TIME = CONFIG_TIMES[0]

    filename = '%s_%s_%s_%s_%s' % (CONFIG_TIME['lastTradeDateOrContractMonth'], CONFIG_CONTRACT['exchange'], CONFIG_CONTRACT['symbol'], CONFIG_CONTRACT['secType'], CONFIG_CONTRACT['currency'])

    f =  h5py.File('data_hdf5/%s.h5' % filename, 'a')
    ohlc_dataset = f.create_dataset('bars', shape=(0,), maxshape=(None,), chunks=True, dtype=[
        ('timestamp', 'i8'),
        ('open', 'f8'),
        ('high', 'f8'),
        ('low', 'f8'),
        ('close', 'f8'),
        ('volume', 'i8'),
        ('barCount', 'i8'),
        ('wap', 'f8')
    ])
    app.setWriter(ohlc_dataset)
    
    # app.setWriter(None)
    downloadHistoric(app, CONFIG_CONTRACT, CONFIG_TIME)

    time.sleep(5)



if __name__ == '__main__':
    main()