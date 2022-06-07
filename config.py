from Strategies.ViralATR_nifty import ViralATRNifty
from Strategies.Choppy import Choppy
from Strategies.DemoStrategy import DemoStrategy
from Strategies.ViralATR import ViralATR
from Strategies.ATR_new import Viral_ATR
import os


brokers = [
    {
        "broker_alias": "viral",
        "broker": "ZERODHA",
        "config": {
            "apikey": "kpnnt4xthv187j8p",
            "apisecret": "lrmz7qdh8ell903yh8mujw4paegipm33",
            "userid": "ZN8507",
            "password": "mail0007",
            "pin": "123456",
            "totp_access_key": "UXD562SLG66TEGX7OTQ7YLFJILH5V5FG",
            "live": True
        },
        "dataSource": True,

    },{
        "broker_alias": "viral_test",
        "broker": "ZERODHA",
        "config": {
            "apikey": "kpnnt4xthv187j8p",
            "apisecret": "lrmz7qdh8ell903yh8mujw4paegipm33",
            "userid": "ZN8507",
            "password": "mail0007",
            "pin": "123456",
            "totp_access_key": "UXD562SLG66TEGX7OTQ7YLFJILH5V5FG",
            "live": False
        },
        "dataSource": False,
    }

]


strategies = {
    "ViralATR": ViralATR,
    "ATR new": Viral_ATR,
    "Choppy": Choppy
}

logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': "[%(asctime)s] %(levelname)s [%(name)s: %(funcName)s: %(lineno)s] %(message)s",
                'datefmt': "%Y-%m-%dT%H:%M:%S%z"
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
            'algo_trader_log_file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join('', 'algotrader.log'),
                'maxBytes': 16777216,  # 16megabytes
                'backupCount': 5,
                'formatter': 'verbose'
            },
        },
        'loggers': {
            '': {
                'handlers': ['console', 'algo_trader_log_file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }
#
# zerodhaconfigurations = {
#     "apikey": "zcp3cclegx91hff7",
#     "apisecret": "dl2si4dfxddj3t3fwk8zhd7xl0itl5k9",
#     "userid": "XB5720",
#     "password": "Chiadi98@&",
#     "pin": "141014"
# }
