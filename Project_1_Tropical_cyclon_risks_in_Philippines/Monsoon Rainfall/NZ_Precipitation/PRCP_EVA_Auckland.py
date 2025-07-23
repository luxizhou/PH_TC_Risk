# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 10:38:58 2023

@author: Luxi
"""

import os
import numpy as np
import pandas as pd
from pyextremes import EVA
from pyextremes import plot_mean_residual_life
from pyextremes import plot_parameter_stability
from pyextremes import plot_return_value_stability
from pyextremes import plot_threshold_stability
from pyextremes import get_extremes, get_return_periods

import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme(style='white')
from shapely.geometry import Point
import shapely
from pyproj import CRS

# choose initialization projection
init_epsg = 4326    # WGS 1984
infile = r'C:/Users/luxi/ClimateRisk/ANZ/00 - Data/Precipitation/GHCN/NewZealand_metric.csv'
df = pd.read_csv(infile,usecols=['NAME','LATITUDE','LONGITUDE','ELEVATION','DATE','PRCP'],parse_dates=['DATE'])
df = df.dropna(subset=['PRCP'])
stations = df[['NAME','LATITUDE','LONGITUDE','ELEVATION']]
stations = stations.drop_duplicates().reset_index(drop=True)
#ofile = r'C:/Users/luxi/ClimateRisk/ANZ/00 - Data/Precipitation/GHCN/NewZealand_ghcn_stations.csv'
#stations.to_csv(ofile,index=False)
#%%output stations to a shape file
# gdf = gpd.GeoDataFrame(stations, geometry=gpd.points_from_xy(stations.LONGITUDE,stations.LATITUDE))
# gdf.crs = CRS.from_epsg(init_epsg)
# outfile = os.path.join(r'C:\Users\luxi\ClimateRisk\ANZ\04 - GIS_maps','NZ_GHCN_stations.shp')
# gdf.to_file(outfile)
#%%

data = df[df.NAME == 'AUCKLAND AERO AWS, NZ'].copy()
#data = df[df.NAME.str.contains('Auckland')]
data = data[['DATE','PRCP']] 
data.rename(columns={'PRCP':'Precipitation'},inplace=True)
data = data.set_index('DATE')
data = data.sort_index(ascending=True)
series = data.squeeze()
#%%
# # to find threshold value
plot_mean_residual_life(series)
plot_parameter_stability(series)
plot_return_value_stability(series, return_period=20, thresholds=np.linspace(30, 80, 5),alpha=0.95)
plot_threshold_stability(series, return_period=100, thresholds=np.linspace(30,80,5))
#%%
model = EVA(series)
#model.get_extremes(method='BM',block_size="365.2425D")
model.get_extremes(method='POT',threshold=50,r="5D")

model.plot_extremes()
model.fit_model()
rps = np.arange(1,1001)
#rps = [2,5,10,25,50,100,250,500,1000]
summary = model.get_summary(return_period=rps,alpha=0.95,n_samples=1000)
print(summary)
model.plot_diagnostic(alpha=0.95)

#%%
#ofile = os.path.join(out_dir,'Data',location+'_GHCNd_prcp_POT_'+block+'_'+str(int(ts))+'_threshold_RP_analysis.xlsx')
ofile = r'C:\Users\luxi\ClimateRisk\ANZ\03 - Scripts_Output\Data\Auckland_food_GHCNd_prcp_POT_daily_max_threshold_30mm_RP_analysis.xlsx'
#%%
with pd.ExcelWriter(ofile) as writer: 
    summary.to_excel(writer,sheet_name='RP_table')  
    model.extremes.to_excel(writer,sheet_name='Extreme_Values')  
#%%


# extremes = get_extremes(
#     ts=series,
#     method="BM",
#     block_size="365.2425D",
# )

# return_periods = get_return_periods(
#     ts=data,
#     extremes=extremes,
#     extremes_method="BM",
#     extremes_type="high",
#     block_size="365.2425D",
#     return_period_size="365.2425D",
#     plotting_position="weibull",
# )
# return_periods.sort_values("return period", ascending=False).head()

extremes = get_extremes(
    ts=series,
    method="POT",
    extremes_type= "high",
    threshold=30.,
    r="5D",
)
#model.get_extremes(method='POT',threshold=40,r="5D")
#%%
return_periods = get_return_periods(
    ts=series,
    extremes=extremes,
    extremes_method="POT",
    extremes_type="high",
    return_period_size="365.2425D",
    plotting_position="weibull",
)
#%%
return_periods.sort_values("return period", ascending=False).head()
ofile = os.path.join(out_dir,filename+'_RP.csv')
return_periods.to_csv(ofile)
#%% get monthly max. prcp
data = df[df.NAME == 'AUCKLAND AERO AWS, NZ'].copy()
data['MONTH'] = data['DATE'].apply(lambda x:x.month)
data['YEAR'] = data['DATE'].apply(lambda x:x.year)
data['YYYYMM'] = data['YEAR']*100.+data['MONTH']
data['YYYYMM'] = data.YYYYMM.astype(int)
prcp_monthly_max = data.groupby('YYYYMM')['PRCP'].max().reset_index()
prcp_monthly_max['YYYYMM'] = prcp_monthly_max.YYYYMM.astype(str)
prcp_monthly_max['TIME'] = pd.to_datetime(prcp_monthly_max['YYYYMM'],format='%Y%m') 
prcp_monthly_max.plot(x='TIME',y='PRCP')

#%%
infile = r'C:/Users/luxi/ClimateRisk/ANZ/03 - Scripts_Output/Figures/Auckland_GHCNd_precipitation_POT_5D_50mm_threshold_RP.txt.txt'

f = open(infile)
content = f.readlines()
f.close()
content = [x.split() for x in content]
rps = np.zeros(len(content)-2)
prcp = rps.copy()
ci_low = rps.copy()
ci_high = rps.copy()

for idx in np.arange(2,len(content)):
    rps[idx-2]=float(content[idx][0])
    prcp[idx-2]=float(content[idx][1])
    ci_low[idx-2]=float(content[idx][2])
    ci_high[idx-2]=float(content[idx][3])

#%%
plt.plot(rps,prcp, 'b-', label='Precipitation [mm]')
plt.fill_between(rps, ci_low, ci_high, color='b', alpha=0.2)
plt.legend()
plt.show()
   
#%%
station_id = [x[0:11] for x in content]
latitude = [float(x[12:20]) for x in content]
longitude = [float(x[21:30]) for x in content]
elevation = [float(x[31:37]) for x in content]
name = [x[41:71].strip() for x in content]