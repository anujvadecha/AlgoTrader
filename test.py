# import pandas as pd
#
# # df = pd.read_csv('resources/trade_disc_nf choppy.xlsx-bearish.csv')
# # print(df.head())
# # reference_dicts = df.to_dict('records')
# # print(reference_dicts[1])
# # for three15, in reference_dicts:
# import csv
# def read_matrix(datafile, identifier="", script=""):
#     data = list(csv.reader(open(datafile)))
#     todays_values = data[0]
#     print(todays_values)
#     conditions = []
#     for i in range(1, len(todays_values)-1):
#         print(data[i])
#         for j in range(1,len(data[i])-1):
#             dict_to_append = {
#                 "yesterdays_candle": data[0][j],
#                 "todays_candle": data[i][0],
#                 "condition": data[i][j],
#                 "candle_type": identifier,
#                 "script": script
#             }
#             conditions.append(dict_to_append)
#     return conditions
#         # print(dict_to_append)
# datafile='resources/trade_disc_nf choppy.xlsx-bearish.csv'
# conditions = read_matrix(datafile, identifier="bearish", script="nifty")
# datafile='resources/trade_disc_nf choppy.xlsx - bullish.csv'
# conditions.extend(read_matrix(datafile, identifier="bullish", script="nifty"))
# datafile='resources/trade_disc_bnf choppy.xlsx - bullish.csv'
# conditions.extend(read_matrix(datafile, identifier="bullish", script="banknifty"))
# datafile='resources/trade_disc_bnf choppy.xlsx - bearish.csv'
# conditions.extend(read_matrix(datafile, identifier="bearish", script="banknifty"))
# df = pd.DataFrame(conditions)
# df.to_csv("Choppy_conditions.csv", index=False)
#
from datetime import datetime, timedelta
from pytimeparse.timeparse import timeparse
import pandas as pd

from Core.Enums import CandleInterval
from Core.Utils import get_candle_time_series_for_date_range, is_within_market_time_range

from_date = datetime.now() - timedelta(hours=50)
to_date = datetime.now()
print(from_date)
print(to_date)
data = get_candle_time_series_for_date_range(from_date, to_date, CandleInterval.hourly)
print(data)
# for data in data:
#     print(f"{data} {is_within_market_time_range(data)}")
range = list(time for time in data if is_within_market_time_range(time))
print(range)

    # print(fdata+ " "+is_within_market_time_range(data))
