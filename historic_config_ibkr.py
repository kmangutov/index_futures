



CONFIG_TIMES = [
    {
        'lastTradeDateOrContractMonth': '202306',
        'endDateTime': '20230407-00:00:00'
    },
    {
        'lastTradeDateOrContractMonth': '202309',
        'endDateTime': '20230401-00:00:00'
    },
    {
        'lastTradeDateOrContractMonth': '202312',
        'endDateTime': '20230401-00:00:00'
    }
]

# https://www.interactivebrokers.com/en/index.php?f=1562&p=asia
# https://www.interactivebrokers.com/en/index.php?f=exchanges
# https://interactivebrokers.github.io/tws-api/basic_contracts.html

CONFIG_CONTRACTS = [
    {
        'symbol': 'ES',
        'secType': 'FUT',
        'exchange': 'CME',
        'currency': 'USD', 
    },
    {
        # https://www.interactivebrokers.com/en/index.php?f=2222&exch=hkfe&showcategories=
        'symbol': 'HSI',
        'secType': 'FUT',
        'exchange': 'HKFE',
        'currency': 'HKD'
    },
    {
        # https://www.interactivebrokers.com/en/index.php?f=2222&exch=kse&showcategories=FUTGRP#productbuffer
        'symbol': 'K200',
        'secType': 'FUT',
        'exchange': 'KSE',
        'currency': 'KRW'
    },
    {
        # https://www.interactivebrokers.com/en/index.php?f=2222&exch=ose.jpn&showcategories=
        'symbol': 'N225',
        'secType': 'FUT',
        'exchange': 'OSE.JPN',
        'currency': 'JPY'
    }#, 
    #{
    #    #https://medium.com/@hochiho/grab-forex-data-from-interactive-brokers-using-python-74dd9e420b11
    #    'symbol': 'KRW',
    #    'secType': 'CASH',
    #    'currency': 'USD',
    #    'exchange': 'IDEALPRO'
    #}
]

CONFIG_CURRENCIES = [
    {
        #https://medium.com/@hochiho/grab-forex-data-from-interactive-brokers-using-python-74dd9e420b11
        'symbol': 'KRW',
        'secType': 'CASH',
        'currency': 'USD',
        'exchange': 'IDEALPRO'
    },
    {
        #https://medium.com/@hochiho/grab-forex-data-from-interactive-brokers-using-python-74dd9e420b11
        'symbol': 'USD',
        'secType': 'CASH',
        'currency': 'HKD',
        'exchange': 'IDEALPRO'
    },
    {
        #https://medium.com/@hochiho/grab-forex-data-from-interactive-brokers-using-python-74dd9e420b11
        'symbol': 'USD',
        'secType': 'CASH',
        'currency': 'JPY',
        'exchange': 'IDEALPRO'
    }
]


CONFIG_OILS = [
    {
        'symbol': 'CL',
        'secType': 'FUT',
        'exchange': 'NYMEX',
        'currency': 'USD', 
    },
    {
        'symbol': 'BZ',
        'secType': 'FUT',
        'exchange': 'NYMEX',
        'currency': 'USD', 
    },
]