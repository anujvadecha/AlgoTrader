from django.contrib import admin

# Register your models here.
from AlgoApp.models import StrategyOrderHistory, Brokers


@admin.register(StrategyOrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ('created_at','broker', 'portfolio_id','instrument', 'quantity', 'side', 'type' )


@admin.register(Brokers)
class BrokerAdmin(admin.ModelAdmin):
    pass
