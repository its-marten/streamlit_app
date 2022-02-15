import pandas as pd
import os
import glob
import datetime
from dateutil.relativedelta import relativedelta
import math
import numpy as np

path = "/Users/mj/Desktop/Python For Datascience/Data_prices"
files = glob.glob(os.path.join(path + "/*.csv"))
data_frame = pd.DataFrame()
content = []
for filename in files:
    df = pd.read_csv(filename, index_col=None)
    content.append(df)
    df["Name"] = filename
data_frame = pd.concat(content)
data_frame["Price"] = data_frame["Close"]
data_frame.drop(['Open', 'Low', 'High', 'SNo', 'Volume', 'Close'], inplace=True, axis=1)
data_frame = data_frame.reset_index()
split_column_name = data_frame["Name"].str.split("/", n=7, expand=True)
split_column_name = split_column_name[6]
split_column_name = split_column_name.str.split(".", n=1, expand=True)
split_column_name = split_column_name[0]
data_frame["Name"] = split_column_name
split_column_date = data_frame["Date"].str.split(" ", n=1, expand=True)
split_column_date = split_column_date[0]
data_frame["Date"] = split_column_date
data_frame = data_frame[data_frame['Date'] >= '2016-01-03']
data_frame = data_frame.reset_index()
data_frame.drop(['index', 'level_0'], inplace=True, axis=1)
data_frame.to_csv("/Users/mj/Desktop/Python For Datascience/Raw Data.csv")

weights = []
famala_index = 0
famala_index_data = []
date_list = []
s = 0
y = 0
t = 0
total_market_value = 0
start_date = datetime.date(2016, 1, 3)
rebalance_date = datetime.date(2016, 1, 3)
end_date = datetime.date(2021, 7, 6)
length_name_column_start = 4
while start_date <= end_date:
    start_date_string = start_date.strftime("%Y-%m-%d")
    rebalance_date_string = rebalance_date.strftime("%Y-%m-%d")
    date_df = data_frame[(data_frame['Date'] == start_date_string)]
    length_name_column_date = len(date_df["Name"])
    date_df = date_df.sort_values(["Marketcap"], ascending=False)
    if length_name_column_start != length_name_column_date or rebalance_date_string == start_date_string:
        while s < length_name_column_date:
            total_market_value = total_market_value + date_df.iloc[s]['Marketcap']
            s += 1
        while y < length_name_column_date:
            weight = (date_df.iloc[y]["Marketcap"] / total_market_value)
            weights.append(weight)

            weight = 0
            y += 1
        weights.sort(reverse=True)
        while t < length_name_column_date:
            famala_index = famala_index + (weights[t] * date_df.iloc[t]['Price'])
            t += 1
        famala_index_data.append(famala_index)
        famala_index = 0
        s = 0
        t = 0
        y = 0
        total_market_value = 0
        weights = []
        length_name_column_start = length_name_column_date
    else:
        date_df = date_df.sort_values(["Marketcap"], ascending=False)
        while s < length_name_column_start:
            total_market_value = total_market_value + date_df.iloc[s]['Marketcap']
            s += 1
        while y < length_name_column_start:
            weight = date_df.iloc[y]["Marketcap"] / total_market_value
            weights.append(weight)

            weight = 0
            y += 1
        weights.sort(reverse=True)
        while t < length_name_column_start:
            famala_index = famala_index + (weights[t] * date_df.iloc[t]['Price'])
            t += 1
        famala_index_data.append(famala_index)
        famala_index = 0
        s = 0
        t = 0
        y = 0
        weights = []
        total_market_value = 0
    rebalance_date = rebalance_date + relativedelta(months=+3)
    date_list.append(start_date_string)
    start_date = start_date + datetime.timedelta(days=1)
df_final = pd.DataFrame({"Date": date_list, "Famala Index": famala_index_data})
df_final.set_index("Date", inplace=True)

path_us_treasury = "/Users/mj/Downloads/DGS10.csv"
df_treasury = pd.read_csv(path_us_treasury)
df_treasury["Date"] = df_treasury["DATE"]
df_treasury.set_index("Date", inplace=True)
df_treasury["US Treasury Yield"] = df_treasury["DGS10"]
df_treasury.drop(["DATE", "DGS10"], axis=1, inplace=True)
df_final["US Treasury Yield"] = df_treasury["US Treasury Yield"]
df_final["US Treasury Yield"].replace({".": np.NaN}, inplace=True)
df_final.fillna(method="ffill", inplace=True)

q = 1
bitcoin_return = []
index_return = []
while q < len(df_final["US Treasury Yield"]):
    index_return.append((df_final.iloc[q]["Famala Index"] - df_final.iloc[q-1]["Famala Index"])/df_final.iloc[q-1]["Famala Index"])
    q += 1
q = 0
df_final = df_final.loc['2016-01-04':'2021-07-06']
df_final["Famala Index Return"] = index_return

data_frame.set_index("Date", inplace=True)

cryptos = ["Aave", "Bitcoin", "Cardano", "ChainLink", "Cosmos", "Dogecoin", "CryptocomCoin", "XRP", "WrappedBitcoin", "Uniswap", "Tron",
           "Stellar", "Solana", "Polkadot", "NEM", "EOS", "Ethereum", "Iota", "Litecoin", "Monero"]

crypto_return = []
for crypto in cryptos:
    path_crypto = f"/Users/mj/Desktop/Python For Datascience/Data_prices/{crypto}.csv"
    df_crypto = pd.read_csv(path_crypto)
    split_column_date = df_crypto["Date"].str.split(" ", n=1, expand=True)
    split_column_date = split_column_date[0]
    df_crypto["Date"] = split_column_date
    df_crypto = df_crypto[df_crypto['Date'] >= '2016-01-03']
    df_crypto.set_index("Date", inplace=True)
    df_crypto.drop(['Open', 'Low', 'High', 'SNo'], inplace=True, axis=1)
    while q < len(df_crypto["Close"]):
        return_day_1 = df_crypto.iloc[q]["Close"]
        return_day_0 = df_crypto.iloc[q - 1]["Close"]
        crypto_return.append(math.log(return_day_1/return_day_0))
        q += 1
    df_crypto = pd.DataFrame({f"{crypto} Return": crypto_return, f"{crypto} Price": df_crypto["Close"]})
    df_crypto.drop(df_crypto.index[0], axis=0, inplace=True)
    start_date_crypto = df_crypto.index[0]
    df_crypto = pd.concat([df_crypto, df_final[df_final.index >= start_date_crypto]], axis=1)

    df_crypto.to_csv(f"/Users/mj/Desktop/Python For Datascience/Crypto Returns/{crypto} Return.csv")
    crypto_return = []
    q = 0

df_final = df_final.reindex(sorted(df_final.columns), axis=1)
df_final["US Treasury Yield"] = df_final["US Treasury Yield"].apply(pd.to_numeric)
df_final = df_final.loc['2016-01-04':'2021-07-06']
df_final.to_csv("/Users/mj/Desktop/Python For Datascience/Clean Data.csv")
print(df_final.info())

