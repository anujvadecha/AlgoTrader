import pandas as pd

# df = pd.read_csv('resources/trade_disc_nf choppy.xlsx-bearish.csv')
# print(df.head())
# reference_dicts = df.to_dict('records')
# print(reference_dicts[1])
# for three15, in reference_dicts:
import csv
def read_matrix(datafile, identifier="", script=""):
    data = list(csv.reader(open(datafile)))
    todays_values = data[0]
    print(todays_values)
    conditions = []
    for i in range(1, len(todays_values)-1):
        print(data[i])
        for j in range(1,len(data[i])-1):
            dict_to_append = {
                "yesterdays_candle": data[0][j],
                "todays_candle": data[i][0],
                "condition": data[i][j],
                "candle_type": identifier,
                "script": script
            }
            conditions.append(dict_to_append)
    return conditions
        # print(dict_to_append)
datafile='resources/trade_disc_nf choppy.xlsx-bearish.csv'
conditions = read_matrix(datafile, identifier="bearish", script="nifty")
datafile='resources/trade_disc_nf choppy.xlsx - bullish.csv'
conditions.extend(read_matrix(datafile, identifier="bullish", script="nifty"))
datafile='resources/trade_disc_bnf choppy.xlsx - bullish.csv'
conditions.extend(read_matrix(datafile, identifier="bullish", script="banknifty"))
datafile='resources/trade_disc_bnf choppy.xlsx - bearish.csv'
conditions.extend(read_matrix(datafile, identifier="bearish", script="banknifty"))
df = pd.DataFrame(conditions)
df.to_csv("Choppy_conditions.csv", index=False)

