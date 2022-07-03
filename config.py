
from Strategies.Eighteen import Eighteen
from Strategies.EighteenOrderTest import EighteenOrderTest
from Strategies.OptionMarketDataCollector import OptionMarketDataCollector
from Strategies.Choppy import Choppy
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
            "live": True,
        },
        "dataSource": True,
    },
    {
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
    "Choppy": Choppy,
    "Option Market Data": OptionMarketDataCollector,
    "Eighteen": Eighteen,
    "EighteenOrderTest": EighteenOrderTest
}

