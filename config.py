from Strategies.Choppy import Choppy
from Strategies.DemoStrategy import DemoStrategy
from Strategies.ViralATR import ViralATR
import os

live = False

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
            "totp_access_key": "UXD562SLG66TEGX7OTQ7YLFJILH5V5FG"
        },
        "dataSource": True
    }
]


strategies = {
    "DemoStrategy": DemoStrategy,
    "ViralATR": ViralATR,
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
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join('', 'algotrader.log'),
                'maxBytes': 16777216,  # 16megabytes
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
