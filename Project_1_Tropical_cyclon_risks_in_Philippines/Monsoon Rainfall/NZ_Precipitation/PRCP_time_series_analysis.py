# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 01:39:36 2023

@author: Luxi Zhou
"""

import os
import numpy as np
import pandas as pd
from pyextremes import EVA

import matplotlib.pyplot as plt
import seaborn as sns


from statsmodels.tsa.stattools import adfuller


infile = r'C:\Users\luxi\ClimateRisk\Data\Precipitation\GHCNd\NewZealand_metric.csv'
#infile = r'D:\Precipitation\Data\GHCNd\NewZealand_metric.csv'
df = pd.read_csv(infile,usecols=['NAME','LATITUDE','LONGITUDE','ELEVATION','DATE','PRCP'],parse_dates=['DATE'])
df = df.dropna(subset=['PRCP'])
stations = df[['NAME','LATITUDE','LONGITUDE','ELEVATION']]
stations = stations.drop_duplicates().reset_index(drop=True)
stations.to_csv('')
#%% get monthly max. daily prcp.
data = df[df.NAME == 'AUCKLAND AERO AWS, NZ'].copy()
data['MONTH'] = data['DATE'].apply(lambda x:x.month)
data['YEAR'] = data['DATE'].apply(lambda x:x.year)
data['YYYYMM'] = data['YEAR']*100.+data['MONTH']
data['YYYYMM'] = data.YYYYMM.astype(int)

daily_series = data[['DATE','PRCP']].copy()
daily_series = daily_series.set_index('DATE')
daily_series = daily_series.squeeze()
rolling_mean=daily_series.rolling(3).mean()
rolling_std = daily_series.rolling(3).std()

# #%%
# plt.plot(daily_series,color='blue',label='Monthly Max. Daily Precipitation')
# plt.plot(rolling_mean,color='red',label='Rolling Mean')
# plt.plot(rolling_std,color='black',label='Rollling STD')

prcp_monthly_max = data.groupby('YYYYMM')['PRCP'].max().reset_index()
prcp_monthly_max['YYYYMM'] = prcp_monthly_max.YYYYMM.astype(str)
prcp_monthly_max['TIME'] = pd.to_datetime(prcp_monthly_max['YYYYMM'],format='%Y%m') 
#prcp_monthly_max.plot(x='TIME',y='PRCP')
series = prcp_monthly_max[['PRCP','TIME']].copy()
series = series.set_index('TIME')
series = series.squeeze()

#%%
rolling_mean=series.rolling(3).mean()
rolling_std = series.rolling(3).std()
#%%
#plt.plot(series,color='blue',label='Monthly Max. Daily Precipitation')
plt.plot(rolling_mean,color='red',label='Rolling Mean')
plt.plot(rolling_std,color='black',label='Rollling STD')
#%%
adft = adfuller(series,autolag="AIC")
#%%
output_df = pd.DataFrame({"Values":[adft[0],adft[1],adft[2],adft[3], adft[4]['1%'], adft[4]['5%'], adft[4]['10%']], \
                          "Metric":["Test Statistics","p-value","No. of lags used","Number of observations used", "critical value (1%)", "critical value (5%)", "critical value (10%)"]})
print(output_df)
print("The time series is stationary because the test statistics is smaller than any of the critical value with p-value in this case not applicable.")
#%% Read in enso data

infile = r'C:/Users/luxi/ClimateRisk/ENSO/nina34.anom.data.txt'
f = open(infile)
content = f.readlines()
f.close()
test = [x.split() for x in content]

for ii in np.arange(0,len(test)):
    tt = test[ii]
    tt = [float(x) for x in tt]    
    dummy = pd.DataFrame(columns=['YEAR','MONTH','DAY','NINO34'],index=np.arange(0,12))
    dummy['YEAR'] = int(tt[0])
    dummy['MONTH'] = np.arange(1,13)
    dummy['DAY'] = 1
    dummy['NINO34'] = tt[1:]
    if ii == 0:
        enso = dummy.copy()
    else:
        enso = pd.concat([enso,dummy],axis=0,ignore_index=True)

enso['TIME'] = pd.to_datetime(enso[['YEAR','MONTH','DAY']])
enso = enso[enso.NINO34>-99.]
ofile = os.path.join(r'C:\Users\luxi\ClimateRisk\ENSO','NINO34_anomaly.csv')
enso.to_csv(ofile,index=False)
#%%
prcp_enso = pd.merge(prcp_monthly_max,enso,how='inner',on='TIME')
#%%
fig,ax = plt.subplots(figsize=(8,5))
#prcp_enso.plot(x='TIME',y='NINO34',ax=ax)
prcp_enso.plot(x='TIME',y='PRCP',color='orange',ax=ax,legend=False)
#prcp_enso.plot(x='TIME',y='PRCP',ax=ax,secondary_y=True)
ax.set_title('Monthly Max. Daily Precipitation at Auckland Aero AWS Station')
ax.set_xlabel('Date')
ax.set_ylabel('Precipitation [mm]')
#ax.set_title('NINO 3.4 VS. Monthly Max. Daily Precipitation [mm] \n Station: Auckland Aero AWS')
#ofile = os.path.join(r'C:\Users\luxi\ClimateRisk\ANZ\03 - Scripts_Output\Figures','Auckland_montly_max_prcp_nino34.png')
#fig.savefig(ofile,bbox_inches='tight')
#%%
sns.relplot(data=prcp_enso,x="NINO34",y="PRCP")
fig = plt.gcf()
ofile = os.path.join(r'C:\Users\luxi\ClimateRisk\ANZ\03 - Scripts_Output\Figures','Auckland_montly_max_prcp_nino34_scatter_plot.png')
fig.savefig(ofile,bbox_inches='tight')