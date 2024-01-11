import pandas as pd
import math as ma
#导入数据
data=pd.read_csv(r"D:\教学安装软件\data.txt",
                 delimiter="\t",
                 names=["id","user_id","age","gender","item_id","behavior_type","item_category","time","province"],
                 skiprows=1)

#拿出2014-11-18的用户购买的数据
data1 = data[(data["time"] == "2014-11-18") & (data["behavior_type"] == 4)]

#求出这天每个用户的购买次数
data2 = data1.groupby(["user_id"]).agg(
    {
        "user_id":lambda x :len(x)
    }
)

#column的名称重命名
data2.rename(columns={
    'user_id':'购买次数'
},inplace=True)

#拿出2014-11-19的用户浏览的数据
data3 = data[(data["time"] == "2014-11-19") & (data["behavior_type"] == 1)]

#求出这天每个用户的浏览次数
data4 = data3.groupby(["user_id"]).agg(
    {
        "user_id":lambda x :len(x)
    }
)

#column的名称重命名
data4.rename(columns={
    'user_id':'浏览次数'
},inplace=True)

#判断2014-11-18的购买用户在2014-11-19是否留存了,即2014-11-18购买了，2014-11-19浏览了
data5 = pd.merge(data2,data4,on="user_id",how="left",suffixes=('_a','_b'))

#把index变成column
data6 = data5.reset_index()

#判断是否次日留存，判断条件是关联出来的浏览次数不为null，即浏览次数>0
data6['是否次日留存'] = data6.apply(lambda x:1 if x['浏览次数'] > 0 else 0,axis=1)

#设定初始值
max_MCC=0
#开始计算mcc
for i in range(0, 10):
    # FN <i次，留存
    FN = len(data6[(data6['购买次数'] < i) & (data6['是否次日留存'] == 1)])

    # TP >=i次，留存
    TP = len(data6[(data6['购买次数'] >= i) & (data6['是否次日留存'] == 1)])

    # TN <i次，不留存
    TN = len(data6[(data6['购买次数'] < i) & (data6['是否次日留存'] == 0)])

    # FP >=i次，不留存
    FP = len(data6[(data6['购买次数'] >= i) & (data6['是否次日留存'] == 0)])

    try:
        MCC = (TP * TN  - FP * FN) / (ma.sqrt((TP+FP) * (TP+FN) * (TN+FP) * (TN+FN)))
        print('i: %s MCC: %s' % (i, MCC))
    except Exception as e:
        print (e)
        # 如果出现异常，多半就是除数为0了。
        continue

    # 保存当前最大值
    if MCC > max_MCC:
        max_MCC = MCC
        max_i = i

print('MCC 最大为 %s 对应的i为 %d' % (max_MCC, max_i))