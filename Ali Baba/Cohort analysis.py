import pandas as pd
import dataframe_image as dfi

df=pd.read_csv(r"D:\data.txt",
                 delimiter="\t",
                 names=["id","user_id","age","gender","item_id","behavior_type","item_category","time","province"],
                 skiprows=1)

df['来访日期'] = pd.to_datetime(df.time).dt.to_period("D")

data = df[(df['behavior_type'] == 1)]

observe = data.groupby(["user_id", "来访日期"], as_index=False).agg(
    日来访次数=("user_id","count"),
)

observe["首次来访日期"] = observe.groupby('user_id')['来访日期'].transform("min")

observe["标签"] = (observe.来访日期 - observe.首次来访日期).apply(lambda x:"同期群人数" if x.n==0 else f"+{x.n}日")

#留存率
cohort_number = observe.pivot_table(index="首次来访日期", columns="标签",
                             values="user_id", aggfunc="count",
                             fill_value=0).rename_axis(columns="留存率")
cohort_number.insert(0, "同期群人数", cohort_number.pop("同期群人数"))
cohort_number.iloc[:, 1:] = cohort_number.iloc[:,1:].divide(cohort_number.同期群人数, axis=0)
out1 = (cohort_number.style
        .format("{:.2%}", subset=cohort_number.columns[1:])
        .bar(subset="同期群人数", color="green")
        .background_gradient("Reds", subset=cohort_number.columns[1:], high=1, axis=None)
        )

#人均来访次数
cohort_count =observe.pivot_table(index="首次来访日期", columns="标签",
                                 values="日来访次数", aggfunc="sum",
                                 fill_value=0).rename_axis(columns="人均来访次数")
cohort_count.insert(0, "首日人均频次", cohort_count.pop("同期群人数"))
cohort_count.insert(0, "同期群人数", cohort_number.同期群人数)
cohort_count.iloc[:, 1:] = cohort_count.iloc[:,1:].divide(cohort_count.同期群人数, axis=0)
out2 = (cohort_count.style
        .format("{:.2f}", subset=cohort_count.columns[1:])
        .background_gradient("Reds", subset=cohort_count.columns[1:], axis=None)
        .bar(subset="同期群人数", color="green")
        )

outs = [out1, out2]
with open("out.html", "w") as f:
    for out in outs:
        f.write(out.render())

dfi.export(obj=out1, filename='留存率.jpg')
dfi.export(obj=out2, filename='人均付款金额.jpg')








