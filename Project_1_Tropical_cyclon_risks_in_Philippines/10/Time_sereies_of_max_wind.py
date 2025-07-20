#%%
import os
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
import warnings
warnings.filterwarnings('ignore')

tc_points = gpd.read_file(r'C:\Users\luxi\OneDrive - Peak Reinsurance Company Ltd\Documents\ClimateRisk\TC\00 - Data\IBTrACS.WP.list.v04r01.points\IBTrACS.WP.list.v04r01.points.shp')
phl_buffer= gpd.read_file(r"C:\Users\luxi\OneDrive - Peak Reinsurance Company Ltd\Documents\ClimateRisk\SEA\02_Scripts\PH_TC_Risk\Project_1_Tropical_cyclon_risks_in_Philippines\01\PHL_1degree_buffer.shp")
phl_land = gpd.read_file(r"C:\Users\luxi\OneDrive - Peak Reinsurance Company Ltd\Documents\ClimateRisk\SEA\02_Scripts\PH_TC_Risk\Project_1_Tropical_cyclon_risks_in_Philippines\01\PHL_adm0.shp")
# %%
tc_points = tc_points[(tc_points['SEASON'] >= 1980) & (tc_points['SEASON'] <= 2024)]

def categorize_tc(wind):
    if pd.isna(wind):
        return None
    if wind >= 137:
        return 'Category 5'
    elif wind >= 113:
        return 'Category 4'
    elif wind >= 96:
        return 'Category 3'
    elif wind >= 83:
        return 'Category 2'
    elif wind >= 64:
        return 'Category 1'
    elif wind > 34:
        return 'Tropical Storm'
    return 'Tropical depression'
tc_points['category'] = tc_points['USA_WIND'].apply(categorize_tc)

tc_points = tc_points.to_crs(epsg=4326)
phl_buffer = phl_buffer.to_crs(epsg=4326)
phl_land = phl_land.to_crs(epsg=4326)

impacting_points = gpd.sjoin(tc_points, phl_buffer[['geometry']], how='inner', predicate='within')
# %%
event_max_wind = impacting_points.groupby(['SEASON', 'SID']).agg({'USA_WIND': 'max'}).reset_index()
event_max_wind = event_max_wind.rename(columns={'USA_WIND': 'max_wind'})
# %%
event_date = impacting_points.groupby(['SEASON', 'SID']).agg({'ISO_TIME': 'min'}).reset_index()
event_date['date'] = pd.to_datetime(event_date['ISO_TIME']).dt.date
# %%
event_max_wind = event_max_wind.merge(event_date[['SEASON', 'SID', 'date']], on=['SEASON', 'SID'], how='left')
event_max_wind = event_max_wind.sort_values(by=['SEASON', 'date'])
event_max_wind['Year'] = pd.to_datetime(event_max_wind['date']).dt.year
#%%
annual_max_wind = event_max_wind.groupby('Year')['max_wind'].max().reset_index()
annual_max_wind['Year'] = annual_max_wind['Year'].astype(int)   

# %%

#plt.style.use('seaborn-darkgrid')
plt.rcParams.update({'font.size': 16})
fig,ax = plt.subplots(figsize=(12, 6))
plt.plot(annual_max_wind['Year'], annual_max_wind['max_wind'], marker='o', linestyle='-', label='Annual Max Wind Speed')
#plt.scatter(event_max_wind['date'], event_max_wind['max_wind'], alpha=0.5, s=10)
#plt.plot(annual_max_wind['Year'], annual_max_wind['max_wind'], s=50, label='Annual Max Wind Speed', zorder=5    )
plt.title('Annual Max. Wind Speed of Tropical Cyclones Impacting the Philippines (1980-2024)')
plt.xlabel('Year')
plt.ylabel('Wind Speed (knots)')
#plt.xticks(rotation=45)

z = np.polyfit(annual_max_wind['Year'], annual_max_wind['max_wind'], 1)
p = np.poly1d(z)
plt.plot(annual_max_wind['Year'], p(annual_max_wind['Year']), linestyle = '--',color='red', linewidth=2, label='Trend Line')
plt.legend()
slope_ts_td = z[0]  # Slope from polyfit
plt.text(0.05, 0.95, f'slope: {slope_ts_td:.3f}', transform=plt.gca().transAxes,
         fontsize=16, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.5))     
plt.grid()
plt.tight_layout()
fig.savefig('annual_max_wind_speed_impacting_tc_phl.png', dpi=300, bbox_inches='tight')
#ofile = 'max_wind_speed_tc_phl.png'
#fig.savefig(ofile, dpi=300, bbox_inches='tight')
# %%
