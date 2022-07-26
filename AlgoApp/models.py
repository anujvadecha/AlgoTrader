from django.db import models

from base.models import BaseModel


class StrategyOrderHistory(BaseModel):
    portfolio_id = models.IntegerField(default=0)
    broker = models.CharField(max_length=255, blank=True, null=True)
    strategy = models.CharField(max_length=255, blank=True, null=True)
    inputs = models.TextField(null=True, blank=True)
    instrument = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    side = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    order_type = models.CharField(max_length=255, blank=True, null=True)
    identifier = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    is_squared = models.BooleanField(default=False)
    instrument_identifier = models.CharField(default=None, blank=True, null=True, max_length=255)

    def __str__(self):
        return f"{self.portfolio_id}_{self.strategy}_{self.instrument}"


class Brokers(BaseModel):
    # {
    #     "broker_alias": "viral_test",
    #     "broker": "ZERODHA",
    #     "config": {
    #         "apikey": "kpnnt4xthv187j8p",
    #         "apisecret": "lrmz7qdh8ell903yh8mujw4paegipm33",
    #         "userid": "ZN8507",
    #         "password": "mail0007",
    #         "pin": "123456",
    #         "totp_access_key": "UXD562SLG66TEGX7OTQ7YLFJILH5V5FG",
    #         "live": False
    #     },
    #     "dataSource": False,
    # }
    broker_alias = models.CharField(max_length=255, null=True, blank=True)
    broker = models.CharField(max_length=255, null=True, blank=True)
    api_key = models.CharField(max_length=255, null=True, blank=True)
    api_secret = models.CharField(max_length=255, null=True, blank=True)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    pin = models.CharField(max_length=255, null=True, blank=True)
    totp_access_key = models.CharField(max_length=255, null=True, blank=True)
    live = models.BooleanField(default=False)
    datasource = models.BooleanField(default=False)
