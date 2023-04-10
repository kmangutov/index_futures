from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import json
from historic_config_ibkr import CONFIG_OILS, CONFIG_CURRENCIES, CONFIG_CONTRACTS, CONFIG_TIMES
import csv
import time

from datetime import datetime
import pytz
import h5py
import numpy as np

from queue import Queue

# Existing solution, should this be used instead?
# download_bars.py
# https://gist.github.com/wrighter/dd201adb09518b3c1d862255238d2534

from ibapi import get_version_string
print(f'\n- Python IB API{get_version_string()}')

CSV_HEADER = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'barCount', 'wap']


def datetimeStringToUnix(datetime_str):
    date = datetime.strptime(datetime_str[:17], '%Y%m%d %H:%M:%S')
    timezone_str = datetime_str[18:]
    timezone = pytz.timezone(timezone_str)

    date_timezone = timezone.localize(date)
    unix_timestamp = int(date_timezone.timestamp())

    return unix_timestamp


# https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html
# https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html
class App(EClient, EWrapper):
    def __init__(self, contracts, times):
        EClient.__init__(self, wrapper = self)
        self.writer = None

        self.queue = Queue()
        
    def error(self, reqId, errorCode, errorString, json):
        print("Error {} {} {}".format(reqId,errorCode,errorString))

    def setWriter(self, writer):
        self.writer = writer

    def send_done(self, code):
        print(f'Sending code {code}')
        self.queue.put(code)

    def wait_done(self):
        print('Waiting for thread to finish ...')
        code = self.queue.get()
        print(f'Received code {code}')
        self.queue.task_done()
        return code

    def historicalData(self, reqId, bar):
        new_ohlc_data = (datetimeStringToUnix(bar.date), float(bar.open), float(bar.high), float(bar.low), float(bar.close), int(bar.volume), int(bar.barCount), float(bar.wap))

        print('historicalData: ' + str(new_ohlc_data))

        self.writer.resize(len(self.writer) + 1, axis=0)
        self.writer[-1] = new_ohlc_data
        self.writer.flush()

    def historicalDataEnd(self, reqId, start, end):
        self.send_done(0)


def downloadHistoric(app, config_contract, config_time, debug=False):
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

    if debug:
        app.reqHistoricalData(reqId=1, contract=contract, endDateTime=endDateTime, durationStr='1 W',
                barSizeSetting='1 hour', whatToShow=whatToShow, useRTH=True, formatDate=1, keepUpToDate=False, 
                chartOptions=[])
    else:
        app.reqHistoricalData(reqId=1, contract=contract, endDateTime=endDateTime, durationStr='6 M',
                barSizeSetting='1 min', whatToShow=whatToShow, useRTH=True, formatDate=1, keepUpToDate=False, 
                chartOptions=[])



def main():
    LIVE_PORTS = [7496, 4001]
    SIMULATED_PORTS = [7497, 4002]

    host = '127.0.0.1'
    port = 7496

    print(f'\n- Connect {host}:{str(port)}')

    app = App(CONFIG_CONTRACTS, CONFIG_TIMES)
    app.connect(host, port, clientId = 1)

    def run_loop():
        app.run()

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    ##

    time.sleep(1)

    print(str(CONFIG_CONTRACTS))
    print(str(CONFIG_TIMES))

    # INDEX FUTURES
    if False:
        for CONFIG_TIME in CONFIG_TIMES:
            for CONFIG_CONTRACT in CONFIG_CONTRACTS:
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
                downloadHistoric(app, CONFIG_CONTRACT, CONFIG_TIME)
                code = app.wait_done()
                time.sleep(2)

    # CURRENCIES
    if False:
        for CONFIG_CONTRACT in CONFIG_CURRENCIES:
            filename = '%s_%s_%s_%s' % (CONFIG_CONTRACT['exchange'], CONFIG_CONTRACT['symbol'], CONFIG_CONTRACT['secType'], CONFIG_CONTRACT['currency'])

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

            # CONFIG_TIMES only used for end date
            downloadHistoric(app, CONFIG_CONTRACT, CONFIG_TIMES[0])
            code = app.wait_done()
            time.sleep(2)

    # OIL FUTURES
    if True:
        for CONFIG_TIME in CONFIG_TIMES:
            for CONFIG_CONTRACT in CONFIG_OILS:

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
                downloadHistoric(app, CONFIG_CONTRACT, CONFIG_TIME)
                code = app.wait_done()
                time.sleep(2)
    
    app.disconnect()



if __name__ == '__main__':
    main()