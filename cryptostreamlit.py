import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import plotly.express as px
import sklearn
#Intro

path = "/Users/mj/Desktop/Python%20For%20Datascience/Clean%20Data.csv"
df_famala = pd.read_csv(path)
df_famala["Date"] = pd.to_datetime(df_famala["Date"])
df_famala.set_index(df_famala["Date"], inplace=True)
df_famala.drop("Date", axis=1, inplace=True)
st.title("The FaMaLa Index: Crypto Data Project")
st.write("Building my own crypto index and comparing returns of bitcoin to the market returns")
st.write("In this blog you will read about my datascience project. The topic of my project is cryptocurrencies. "
         "The goal of my project is to make an cryptocurrency index which could represent the market. An index is a method to track the performance of a group of assets in a standardized way. After making the index I always wanted to see how the returns are correlated to the returns of diverse cryptocurrencies. So my blog will be spread into multiple parts. The first part will cover how I collected the data and how I turned the raw data into clean data. The second part will be about how I created my own index. Which calculations I did to compute the values for the index. In the third part I will calculate the returns of the index and the cryptocurrencies to see what their graphs look like and if it is representable. And in the last part I will do some lineair regression and see if the index has a significant meaning for the market. ")
st.write("Quick sidenote: I called the index the FaMaLa index. This is because in my team for this project I had help from Fabian and Laurenz and my name is Marten. So that makes FaMaLa. You could also call it the Fuck My Life index, but that’s a little bit grim I would say.")
st.header("Step 1: Collecting Data")
st.write("In every step I will show the code in python if you would be interested in knowing what I did. You don’t have to read it, I will also explain my code in text so that people who don’t have any coding experience can understand this too.")
st.write("I started by downloading the datasets from Kaggle.com. I downloaded a zip-file in which I found 20 csv-files of cryptocurrencies. I loaded all the data of the CSV-files into pycharm and I made a whole dataset of all the cryptocurrencies. There were some uninteresting columns in the data so I had to delete those. I ended up with a dataset that contained the columns: “Name”, “Symbol”, “Price”, “Marketcap” and “Date” as the index. I only needed this data to start my project.")


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
st.write("To make my own index I needed to do a bit more work. I had to give all the cryptocurrencies a weight based on their market cap. So I started in 2016 and went all the way to July 2021 (this is where the data ends). But those weights change every time a new cryptocurrency enters the market. Not all the cryptocurrencies started around the same date. I started with 4 cryptos in 2016 and ended with 20 in 2021. Also every month I had to rebalance the index aswell, this meant again recalculating the weights of the cryptos.")
st.write("Then making the index was not hard anymore. I just used the weight of the crypto and multiplied that with its price of that day and summed it up for all the cryptos. I divided this number by the sum of all the market caps of the cryptos in the index at that time and then you get a value for the FaMaLa index. All these values were stored in a new dataframe.")
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

"""That dataset looks like this: """
st.dataframe(df_famala["Famala Index"])
"""Here is a visualization of the FaMaLa index."""
st.line_chart(df_famala["Famala Index"])
cryptos = ["Aave", "Bitcoin", "Cardano", "ChainLink", "Cosmos", "Dogecoin", "CryptocomCoin", "XRP", "WrappedBitcoin", "Uniswap", "Tron",
           "Stellar", "Solana", "Polkadot", "NEM", "EOS", "Ethereum", "Iota", "Litecoin", "Monero"]
selection = st.sidebar.selectbox("Choose the crypto you want to plot", cryptos)
st.header(f"Step 3: Comparing {selection} To The FaMaLa Index")
st.write("In this part I looked at the returns of the index and compared them to the returns of the cryptos in this dataset. There is sidebar where you can choose the crypto you want to look at and see how the plot differs from the the index. To calculate the returns of both the crypto and the index I used a logarithm. By taking the log of the price of a crypto on day 1 and dividing it by the price on day 0 you get the return on day 1. I did the same thing for the index and this was the result. ")
st.write("After calculating all this I had to take out day 0 out of the data because on that day there is no return as I don’t have data before that day.")
st.write("You can see the values of the index and the returns in this table.")
st.dataframe(df_famala[["Famala Index", "Famala Index Return"]])
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
st.write("Here you can see the visualization of the selected crypto returns and the index returns. I invite you to play around and see how the plot changes when you select a different crypto.")
st.line_chart(df_crypto[[f"{selection} Return", "Famala Index Return"]], use_container_width=True)
st.write(f"Here you can find a table of the {selection} returns aswell.")
st.dataframe(df_crypto[f"{selection} Return"])
#Making the lineair regression of the returns

st.header(f"Step 4: Performing a lineair regression between the FaMaLa Index and {selection}")
f"""In this part I looked at the different cryptocurrencies and performed a lineair regression. In this regression the index return is the independent variable and the {selection} return the dependent variable.
By using a lineair regression I you can check to the percentual change in crypto returns when the index changes with 1%. So this will tell us how the returns of a crypto will change when the returns of the index change by 1%. Also will this show how good the index is in explaining the volatility of a cryptocurrency compared to the market. You can see the volatility as the risk of a cryptocoin. A higher volatility results in higher returns but also higher losses.
"""
crypto_array = df_crypto[f"{selection} Return"].to_numpy()
famala_array = df_crypto["Famala Index Return"].to_numpy().reshape((-1,1))
model = LinearRegression().fit(famala_array, crypto_array)
r_sq = model.score(famala_array, crypto_array) * 100
fig = px.scatter(y=df_crypto[f"{selection} Return"], x=df_crypto["Famala Index Return"], trendline="ols", labels = {"x": "FaMaLa Index Returns","y": f"{selection} Returns"}, title="Scatterplot with lineair regression", trendline_color_override= "#FF0000")
st.plotly_chart(fig, use_container_width=True)
f"""Intercept of the regression: {model.intercept_}.
Percentual change of {selection} return when index changes by 1%: {model.coef_}%.
Percentage of variation of {selection} explained by the model: {r_sq}% """

code_3 = """crypto_array = df_crypto[f"{selection} Return"].to_numpy()
famala_array = df_crypto["Famala Index Return"].to_numpy().reshape((-1,1))
model = LinearRegression().fit(famala_array, crypto_array)
r_sq = model.score(famala_array, crypto_array)
fig = px.scatter(y=df_crypto[f"{selection} Return"], x=df_crypto["Famala Index Return"], trendline="ols", labels = {"x": "FaMaLa Index Returns","y": f"{selection} Returns"}, title="Scatterplot with lineair regression", trendline_color_override= "#FF0000")
st.plotly_chart(fig, use_container_width=True)"""
st.code(code_3, language="python")
"""
As you can see because of the marketcap Bitcoin has, its correlation to the index is very big. You could almost say that the bitcoin on its own
is a good indicator of the cryptomarket. It is even less volatile than the index itself. You can see how well the plot of the regression is when you compare Bitcoin to the FaMaLa index.
"""
st.subheader("Remarks for further research:")
st.write("I did not have enough time for the complete prject I intented to do. I also wanted to apply the CAPM model to the cryptomarket. This is why made my own index. With this CAPM model I could calculate the expected return of a crypto coin. As the risk free rate I would have used the US treasury yield rates. But I will do this another time.")
st.write("I also could have looked at the price of the crypto and the value of the index to see what a lineair regression would give as outcome.")
st.header("Thank you for reading!")
