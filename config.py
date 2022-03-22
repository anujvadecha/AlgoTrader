from Strategies.Choppy import Choppy
from Strategies.DemoStrategy import DemoStrategy
from Strategies.ViralATR import ViralATR

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
#
# zerodhaconfigurations = {
#     "apikey": "zcp3cclegx91hff7",
#     "apisecret": "dl2si4dfxddj3t3fwk8zhd7xl0itl5k9",
#     "userid": "XB5720",
#     "password": "Chiadi98@&",
#     "pin": "141014"
# }
