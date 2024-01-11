import numpy as np
import pandas as pd
from dateutil import relativedelta
from lifetimes import BetaGeoFitter, ModifiedBetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data
from sklearn.metrics import mean_squared_error
from lifetimes.plotting import plot_period_transactions, plot_frequency_recency_matrix 
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False  
import warnings
warnings.filterwarnings("ignore")

#数据导入
data = pd.read_csv(r'D:\data.txt', parse_dates=['trans_date'])
data.head()
data.info()

#客户的单次购买金额、购买总金额及频次分布图
plt.subplots(figsize=(10,6))
data.tran_amount.hist()
plt.show()

plt.subplots(figsize=(10,6))
data.groupby('customer_id').tran_amount.sum().hist(bins=20)
plt.show()

plt.subplots(figsize=(10,6))
data.groupby('customer_id').customer_id.count().hist(bins=20)
plt.show()

#划分训练集及测试集（以最后2023年为界）
period_months = 6
date = data.trans_date.max() - relativedelta.relativedelta(months=period_months)
train = data[data.trans_date <= date]
test = data[data.trans_date > date]

train_df = summary_data_from_transaction_data(
    train,
    customer_id_col="customer_id",
    datetime_col="trans_date",
    monetary_value_col="tran_amount",
    freq="D",
)
train_df.head()

#BG/NBD 模型
bgf = BetaGeoFitter(penalizer_coef=0.000001)  
bgf.fit(train_df['frequency'], train_df['recency'], train_df['T'])
bgf.summary

#可视化
plt.subplots(figsize=(10,8))
plot_frequency_recency_matrix(bgf, T=90)  
plt.show()

plt.subplots(figsize=(10,8))
plot_probability_alive_matrix (bgf)
plt.show()

t = 180  
train_df['predicted_purchases'] = bgf.conditional_expected_number_of_purchases_up_to_time(t, train_df['frequency'], train_df['recency'], train_df['T'])
train_df.sort_values(by='predicted_purchases').tail(5)

#评估
customers = train_df.reset_index()[['customer_id']]  
customers["pred_purchase_count"] = bgf.predict(
    90, train_df["frequency"], train_df["recency"], train_df["T"],
).values
test_count = test.groupby('customer_id').customer_id.count().rename('true_purchase_count').reset_index()
test_df = pd.merge(customers, test_count, on='customer_id', how='left')
test_df.fillna(0, inplace=True)
test_df.head()
test_df[['pred_purchase_count', 'true_purchase_count']].sum().round()
print('RMSE: ', np.sqrt(mean_squared_error(test_df.true_purchase_count, test_df.pred_purchase_count)))


#Gamma-Gamma 模型
from lifetimes import GammaGammaFitter

ggf = GammaGammaFitter(penalizer_coef = 0.1)
ggf.fit(train_df['frequency'],
        train_df['monetary_value'])

ggf.conditional_expected_average_profit(train_df['frequency'],
        train_df['monetary_value']).head()
bgf.fit(train_df['frequency'], train_df['recency'], train_df['T'])

test_pred_amount = ggf.customer_lifetime_value(
        bgf, 
        train_df['frequency'],
        train_df['recency'],
        train_df['T'],
        train_df['monetary_value'],
        time=6, 
        discount_rate=0.01 
).reset_index()

test_pred_amount.head()

#评估
test_amount = test.groupby('customer_id').tran_amount.sum().reset_index()
test_amount_df = pd.merge(test_pred_amount, test_amount, on='customer_id', how='left')
test_amount_df.fillna(0, inplace=True)
test_amount_df.describe()
print('RMSE: ', np.sqrt(mean_squared_error(test_amount_df.tran_amount, test_amount_df.clv)))
