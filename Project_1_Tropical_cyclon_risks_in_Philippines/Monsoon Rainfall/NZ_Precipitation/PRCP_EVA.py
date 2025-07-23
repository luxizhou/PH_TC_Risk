# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 10:38:58 2023

@author: Luxi
"""

import os
import numpy as np
import pandas as pd
from pyextremes import EVA

import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns; sns.set_theme(style='white')
from shapely.geometry import Point
import shapely
from pyproj import CRS

#shapely.speedups.enabled

# choose initialization projection
init_epsg = 4326    # WGS 1984

#infile = r'C:\Users\luxi\ClimateRisk\Data\Precipitation\GHCNd\NewZealand_metric.csv'
infile = r'D:\Precipitation\Data\GHCNd\NewZealand_metric.csv'
df = pd.read_csv(infile,usecols=['NAME','LATITUDE','LONGITUDE','ELEVATION','DATE','PRCP'],parse_dates=['DATE'])
df = df.dropna(subset=['PRCP'])
stations = df[['NAME','LATITUDE','LONGITUDE','ELEVATION']]
stations = stations.drop_duplicates().reset_index(drop=True)

#%% output stations to a shape file
# gdf = gpd.GeoDataFrame(stations, geometry=gpd.points_from_xy(stations.LONGITUDE,stations.LATITUDE))
# gdf.crs = CRS.from_epsg(init_epsg)
# outfile = os.path.join(r'C:\Users\luxi\ClimateRisk\ANZ\04 - GIS_maps','NZ_GHCN_stations.shp')
# gdf.to_file(outfile)
#%%

data = df[df.NAME == 'AUCKLAND AERO AWS, NZ'].copy()
#data = df[df.NAME.str.contains('Auckland')]
data = data[['DATE','PRCP']] 
data = data.dropna(subset=['PRCP']) 
data = data.set_index('DATE')
data = data.sort_index(ascending=True)
series = data.squeeze()

model = EVA(series)
model.get_extremes(method='BM',block_size="365.2425D")

model.plot_extremes()

model.fit_model()
rps = [2,5,10,25,50,100,250,500,1000]
summary = model.get_summary(return_period=rps,alpha=0.95,n_samples=1000)
print(summary)
model.plot_diagnostic(alpha=0.95)
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




