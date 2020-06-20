# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 20:49:58 2020

@author: LetianZ
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 10:50:52 2020

@author: LetianZ
"""


import tushare as ts
import requests
import pandas as pd
import time
import json
import datetime
import matplotlib
from pyecharts import options as opts
from pyecharts.charts import Map


# 将提取数据的方法封装为函数
def get_data(data, info_list):
    info = pd.DataFrame(data)[info_list]  # 主要信息

    today_data = pd.DataFrame([i['today'] for i in data])  # 提取today的数据
    today_data.columns = ['today' + i for i in today_data.columns]  # 修改列名 columns

    total_data = pd.DataFrame([i['total'] for i in data])  # 提取total的数据
    total_data.columns = ['total' + i for i in total_data.columns]  # 修改列名 columns

    return pd.concat([info, total_data, today_data], axis=1)  # info、today和total横向合并最终得到汇总的数据

# 定义保存数据方法
def save_data(data,name): 
    file_name = name+'_'+time.strftime('%Y_%m_%d',time.localtime(time.time()))+'.csv'
    data.to_csv(file_name,index=None,encoding='utf_8_sig')
    print(file_name+' 保存成功！')



#根据股票码获取股票信息并绘图
def getstock(stockscope):
    pro=ts.pro_api()
    
    #取上市公司股票代码、省、市、经营范围
    
    df = pro.stock_company(fields='ts_code,province,city,business_scope')
    #df.to_csv("d:/b.csv",encoding="gbk",index=False)  #存储一个文件
    kouzhaodf=df[df['business_scope'].str.contains(stockscope)]
    
    '''''''''画厂家分布图'''''''''
    factProv=kouzhaodf.groupby(['province']).count()
    province=factProv.index.tolist()
    data_prov=factProv['ts_code'].tolist()
    
    data = [(province[i], data_prov[i]) for i in range(0,len(province))]
    
    _map = (
            Map()
            .add("工厂数量", data, "china")
            .set_global_opts(
                title_opts=opts.TitleOpts(title=stockscope+"工厂数量"),
                legend_opts=opts.LegendOpts(is_show=False),
                visualmap_opts=opts.VisualMapOpts(max_=130, is_piecewise=True),
            )
        )
    
    _map.render()    
    ''''''''''生成平均折线'''''''''''
    matplotlib.rcParams['font.family']='SimHei'
    i=0
    for stockcode in kouzhaodf['ts_code']:
            
            
        if i%400 == 1:
        	begintime=datetime.datetime.now()
        if i%400 == 399:
            endtime=datetime.datetime.now() 
            difftime=(endtime-begintime).seconds
            if difftime <= 60:
                time.sleep(62-difftime)
            
        
        
        #取每个股票的交易数据
        stockdaily =pro.daily(ts_code=stockcode, start_date='20200101', end_date='20200605')
        if i==0:
            dailyarray=stockdaily[['trade_date']]
            #归一化处理
            dailyarray[stockcode]=(stockdaily['close']-stockdaily['close'].min())/(stockdaily['close'].max()-stockdaily['close'].min())
            i=i+1
        else:
            dailyarray[stockcode]=(stockdaily['close']-stockdaily['close'].min())/(stockdaily['close'].max()-stockdaily['close'].min())
            i=i+1
    dailyarray["mean"] =dailyarray.mean(1)
    dailyarray=dailyarray.sort_values(by ='trade_date')
    dailyarray.to_csv("D:/Pydocument/stock/b.csv",encoding="gbk",index=False)
    dailyarray[['mean']].plot(kind='line',title=stockscope,x=None,y=None)
    return dailyarray[['trade_date','mean']]




#获取新冠疫情的数据并绘制曲线图
def getcov19():
    pd.set_option('max_rows',500)
    url = "https://c.m.163.com/ug/api/wuhan/app/data/list-total"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'}
    r = requests.get(url,headers=headers)
        # print(r.status_code)
        # print(type(r.text))
        # print(len(r.text))
    data_json = json.loads(r.text)
    type(data_json)
    data_json.keys()
    data = data_json['data']  # 取出json中的数据
    chinaDayList = data['chinaDayList']
    alltime_China = get_data(chinaDayList, ['date'])
#    save_data(alltime_China, 'alltime_China')
    alltime_China['currconfirm']=alltime_China['totalconfirm']-alltime_China['totalheal']-alltime_China['totaldead']
    alltime_China[['todayconfirm']].plot(kind='line',title='todayconfirm',x=None,y=None)
    alltime_China[['currconfirm']].plot(kind='line',title='currconfirm',x=None,y=None)
    return alltime_China[['date','todayconfirm','currconfirm']]



#主函数
cov=getcov19()
cov['dateindex']=pd.to_datetime(cov['date'])
cov=cov.set_index('dateindex')
del cov['date']
    
    
strKind = input( '请输入你想分析的行业名称：')
stockmean=getstock(strKind)
stockmean['dateindex']=pd.to_datetime(stockmean['trade_date'])
stockmean=stockmean.set_index('dateindex')
del stockmean['trade_date']
result = pd.concat([cov, stockmean], axis=1)
result=result.dropna()

intMax=result.todayconfirm.max()
result = result.drop(result[result. todayconfirm==intMax].index)

result.plot(kind="scatter",x="todayconfirm",y="mean",title=strKind)
result.plot(kind="scatter",x="currconfirm",y="mean",title=strKind)

print(strKind)
print('pearson')
print(result.corr())
result.corr().to_csv("D:/Pydocument/stock/pearson.csv",encoding="gbk",index=False)
print('spearman')
print(result.corr('spearman'))
result.corr('spearman').to_csv("D:/Pydocument/stock/spearman.csv",encoding="gbk",index=False)
print('kendall')
print(result.corr('kendall'))
result.corr('kendall').to_csv("D:/Pydocument/stock/kendall.csv",encoding="gbk",index=False)
    
    



'''''
stockmean=getstock('口罩')
cov=getcov19()
cov['dateindex']=pd.to_datetime(cov['date'])
stockmean['dateindex']=pd.to_datetime(stockmean['trade_date'])
stockmean=stockmean.set_index('dateindex')
cov=cov.set_index('dateindex')

del cov['date']
del stockmean['trade_date']

result = pd.concat([cov, stockmean], axis=1)
result.dropna()

print('kouzhao')
print(result.corr())
print(result.corr('spearman'))
print(result.corr('kendall'))




stockmean=getstock('旅游')
stockmean['dateindex']=pd.to_datetime(stockmean['trade_date'])
stockmean=stockmean.set_index('dateindex')
del stockmean['trade_date']
result = pd.concat([cov, stockmean], axis=1)
result.dropna()

print('旅游')
print(result.corr())
print(result.corr('spearman'))
print(result.corr('kendall'))

stockmean=getstock('电子商务')
stockmean['dateindex']=pd.to_datetime(stockmean['trade_date'])
stockmean=stockmean.set_index('dateindex')
del stockmean['trade_date']
result = pd.concat([cov, stockmean], axis=1)
result.dropna()

print('电子商务')
print(result.corr())
print(result.corr('spearman'))
print(result.corr('kendall'))


stockmean=getstock('餐饮')
stockmean['dateindex']=pd.to_datetime(stockmean['trade_date'])
stockmean=stockmean.set_index('dateindex')
del stockmean['trade_date']
result = pd.concat([cov, stockmean], axis=1)
result.dropna()

print('餐饮')
print(result.corr())
print(result.corr('spearman'))
print(result.corr('kendall'))

    # 中国历史数据爬取

#    alltime_China[['todayconfirm']].plot(kind='line',title='Confirm',x=None,y=None)
#    alltime_China[['totalconfirm']].plot(kind='line',title='Confirm',x=None,y=None)
    
'''''


