import streamlit as st
import pandas as pd
import datetime as dt
import requests
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import plotly.express as px
import altair as alt

#Intro
path = "/Users/mj/Desktop/Python For Datascience/Clean Data.csv"
df_famala = pd.read_csv(path)
df_famala["Date"] = pd.to_datetime(df_famala["Date"])
df_famala.set_index(df_famala["Date"], inplace=True)
df_famala.drop("Date", axis=1, inplace=True)
st.title("The FaMaLa Index: Crypto Data Project")
st.write("Building my own crypto index and comparing returns of bitcoin to the market returns")
"""In this blog I will guide you through the steps I took to make my own index to represent the crypto market. Also I will be performing statistical anaylis on the different cryptocurrencies. 
By doing this I can look at how they are affected by the crypto index.
"""
st.header("Step 1: Collecting Data")
"""The data was received from Kaggle.com. I downloaded a complete zipfile of historical prices of multiple cryptocurrencies. In total there is data on 20 cryptocurrencies in this project.
After I downloaded the data, I loaded it into Pycharm and started to make changes to the data. This way I would end up with a dataset that has everything I needed."""
code = """
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
    data_frame.drop(['index', 'level_0'], inplace=True, axis=1)"""
st.code(code, language="python")
"""After doing all this the dataset was looking like this:"""
path_raw_data = "/Users/mj/Desktop/Python For Datascience/Raw Data.csv"
df_raw = pd.read_csv(path_raw_data)
df_raw.set_index("Date", inplace=True)
df_raw.drop("Unnamed: 0", inplace=True, axis=1)
st.dataframe(df_raw)


st.header("Step 2: Making My Own Index")
"""In this section you can see how I calculated and programmed my own index to represent the crypto market. The code is as following:"""
code_2 = """weights = []
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
df_final.set_index("Date", inplace=True)"""
st.code(code_2, language="python")

"""After all this the value for the index was stored in a new dataframe. That dataset looks like this: """
st.dataframe(df_famala["Famala Index"])
"""Here is a visualization of the FaMaLa index."""
st.line_chart(df_famala["Famala Index"])
"""I also calculated the return of the index as you can see in this table."""
st.dataframe(df_famala)
cryptos = ["Aave", "Bitcoin", "Cardano", "ChainLink", "Cosmos", "Dogecoin", "CryptocomCoin", "XRP", "WrappedBitcoin", "Uniswap", "Tron",
           "Stellar", "Solana", "Polkadot", "NEM", "EOS", "Ethereum", "Iota", "Litecoin", "Monero"]
selection = st.sidebar.selectbox("Choose the crypto you want to plot", cryptos)
st.header(f"Step 3: Comparing {selection} To The FaMaLa Index")
"""To be able to compare the return of cryptocurrencies to the market return, I first had to calculate the return of the cryptocurrency.
"""
code_4 = """cryptos = ["Aave", "Bitcoin", "Cardano", "ChainLink", "Cosmos", "Dogecoin", "CryptocomCoin", "XRP", "WrappedBitcoin", "Uniswap", "Tron",
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
"""
st.code(code_4, language="python")
path_crypto = f"/Users/mj/Desktop/Python For Datascience/Crypto Returns/{selection} Return.csv"
df_crypto = pd.read_csv(path_crypto)
df_crypto["Date"] = pd.to_datetime(df_crypto["Date"])
df_crypto.set_index(df_crypto["Date"], inplace=True)
#fig_crypto = px.line(df_famala["Famala Index"], labels = {"x":"Year", "y": "Famala Index"}, title = "Famala Index")
#st.plotly_chart(fig_crypto, use_container_width=True)
"""After coding all this I had a datasets for all the cryptocurrencies with their returns. With the sidebar in this blog you can switch between the different
visualizations of the cryptocurrencies plotted with the index returns aswell. This way you can see the difference between the index and the cryptocurrency.
"""
st.line_chart(df_crypto[[f"{selection} Return", "Famala Index Return"]], use_container_width=True)

#Making the lineair regression of the returns

st.header(f"Step 4: Performing a lineair regression between the FaMaLa Index and {selection}")
f"""In this part I looked at the different cryptocurrencies and performed a lineair regression. In this regression the index return is the independent variable and the {selection} return the dependent variable.
By using a lineair regression I you can check to the percentual change in crypto returns when the index changes with 1%. Also will this show how good the index is in explaining the volatility of a cryptocurrency compared to the market.
I used a logarithm to calculate the return of the cryptocurrency."""
crypto_array = df_crypto[f"{selection} Return"].to_numpy()
famala_array = df_crypto["Famala Index Return"].to_numpy().reshape((-1,1))
model = LinearRegression().fit(famala_array, crypto_array)
r_sq = model.score(famala_array, crypto_array)
fig = px.scatter(y=df_crypto[f"{selection} Return"], x=df_crypto["Famala Index Return"], trendline="ols", labels = {"x": "FaMaLa Index Returns","y": f"{selection} Returns"}, title="Scatterplot with lineair regression", trendline_color_override= "#FF0000")
st.plotly_chart(fig, use_container_width=True)
f"""Intercept of the regression: {model.intercept_}.
Percentual change of {selection} return when index changes by 1%: {model.coef_}%.
Percentage of variation of {selection} explained by the model: {r_sq*100}% """

code_3 = """crypto_array = df_crypto[f"{selection} Return"].to_numpy()
famala_array = df_crypto["Famala Index Return"].to_numpy().reshape((-1,1))
model = LinearRegression().fit(famala_array, crypto_array)
r_sq = model.score(famala_array, crypto_array)
fig = px.scatter(y=df_crypto[f"{selection} Return"], x=df_crypto["Famala Index Return"], trendline="ols", labels = {"x": "FaMaLa Index Returns","y": f"{selection} Returns"}, title="Scatterplot with lineair regression", trendline_color_override= "#FF0000")
st.plotly_chart(fig, use_container_width=True)"""
st.code(code_3, language="python")
"""
As you can see because of the big marketcap the Bitcoin has, its correlation to the index is very big. You could almost say that the bitcoin on its own
is a good indicator of the cryptomarket. It is even less volatile than the index itself. 
Remarks for follow up projects:
I could equally weight all the cryptocurrencies and see how big of an impact that had on the index. 
"""
