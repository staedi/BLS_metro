# pylint: disable=unused-variable
# pylint: disable=anomalous-backslash-in-string

import numpy as np
import pandas as pd
from datetime import datetime
import streamlit as st

state_cbsa = {'AL':'N300','LA':'N300','AR':'N300','DE':'N300','DC':'N300','FL':'N300','GA':'N300','KY':'N300','MD':'N300','MS':'N300','NC':'N300','OK':'N300','SC':'N300','TN':'N300','TX':'N300','VA':'N300','WV':'N300','AZ':'N400','CA':'N400','CO':'N400','ID':'N400','MT':'N400','NV':'N400','OR':'N400','UT':'N400','WA':'N400','WY':'N400','NM':'N400','CT':'N100','ME':'N100','MA':'N100','NH':'N100','NJ':'N100','NY':'N100','PA':'N100','VT':'N100','RI':'N100','IL':'N200','IN':'N200','IA':'N200','KS':'N200','MI':'N200','MN':'N200','MO':'N200','NE':'N200','ND':'N200','OH':'N200','SD':'N200','WI':'N200'}

# 'RI':'N100',

cpi_columns=['All items','Commodities','Food and beverages','Housing','Medical care','Recreation','Transportation']


##################################################################
## Preprocessing parts
# @st.cache
def read_dataset(filepath, filelist):
    data_list = {}
    if type(filelist) == dict:
        for key, filename in filelist.items():
            data = pd.read_csv(filepath+filename,dtype=str,sep='\t+',engine='python')
            data.rename(columns=lambda x:x.strip(),inplace=True)

            if key == 'area_map':
                # Self-representing area resetting
                data.loc[data['CPI_code'].str[0].isin(['A','S']),'CPI_code'] = data.loc[data['CPI_code'].str[0].isin(['A','S']),'CPI_code'].apply(lambda x:'S'+x[1]+'00')

            elif key == "area":
                # NECTA regions
                def find_necta(region):
                    necta_loc = region.find('NECTA')
                    if necta_loc != -1:
                        return region[:necta_loc-1]
                    else:
                        return region
                data['area_name'] = data['area_name'].apply(find_necta)

            elif key == "industry":
                # Supersector & wage data available only
                data.drop(data.loc[(data['industry_name'].isin(['Government','Information','Durable Goods','Mining and Logging','Mining, Logging and Construction','Non-Durable Goods','Retail Trade','Service-Providing','Total Nonfarm','Transportation, Warehousing, and Utilities','Wholesale Trade'])) | (data['industry_code'].astype(int)%1e6!=0),].index,inplace=True)

            data_list[key] = data

        return data_list

    else:
        data = pd.read_csv(filepath+filelist,sep='\t+',engine='python')
        data.rename(columns=lambda x:x.strip(),inplace=True)
        return data

def merge_dataset(type,data,supp_data):
    if type == 'sm':
        merged_data = data.merge(supp_data['state'][['state_code','state_abbr']],how='inner',left_on='state',right_on='state_code')
        merged_data = merged_data.merge(supp_data['area'],how='inner',left_on='area',right_on='area_code')
        merged_data = merged_data.merge(supp_data['industry'],how='inner',left_on='industry',right_on='industry_code')
        merged_data = merged_data.merge(supp_data['datatype'],how='inner',left_on='datatype',right_on='data_type_code')

        # Area mapping for SM to CPI
        merged_data = merged_data.merge(supp_data['area_map'],how='inner',left_on='area',right_on='SM_code')

        # After-Cleaning processes
        merged_data.loc[merged_data['datatype']=='01','data_type_text'] = 'All Employees'
        merged_data.loc[merged_data['datatype']=='03','data_type_text'] = 'Avg Hourly Wages'
        merged_data.loc[merged_data['datatype']=='01','value'] = merged_data.loc[merged_data['datatype']=='01','value']

        # CBSA regions mapping
        merged_data.loc[merged_data['CPI_code'].isnull(),'CPI_code'] = merged_data.loc[merged_data['CPI_code'].isnull(),'state_abbr'].apply(lambda x:state_cbsa.get(x))

        merged_data.drop(['state','state_code','area_code','industry_code','data_type_code','SM_code','area','datatype','industry'],axis=1,inplace=True)
        merged_data.rename(columns={'state_abbr':'state','area_name':'cbsa_area','industry_name':'industry','data_type_text':'type'},inplace=True)

    elif type == 'cpi':
        merged_data = data.merge(supp_data['area'][['area_code','area_name']],how='inner',left_on='area',right_on='area_code')

        merged_data = merged_data.merge(supp_data['item'][['item_code','item_name']],how='inner',left_on='item',right_on='item_code')

        merged_data = merged_data.loc[merged_data['item_name'].isin(cpi_columns),]

        merged_data.drop(['item','item_code'],axis=1,inplace=True)
        merged_data.rename(columns={'item_name':'type','area_name':'CPI_area'},inplace=True)

    else:
        merged_data = data.merge(supp_data,how='inner',left_on=['year','CPI_code'],right_on=['year','area'])
        merged_data.drop(['area_code','CPI_code','area'],axis=1,inplace=True)

    return merged_data


def clean_dataset(type,data,sel_year):
    data.drop(data.loc[((data['year']!=sel_year) & (data['year']!=2010)) | (data['period']!='M13'),].index,inplace=True)
    data.loc[:,'series_id'] = data.loc[:,'series_id'].str.strip()

    if type == 'sm':
        data.loc[:,'state'] = data.loc[:,'series_id'].str[3:5]
        data.loc[:,'area'] = data.loc[:,'series_id'].str[5:10]
        data.loc[:,'industry'] = data.loc[:,'series_id'].str[10:18]
        data.loc[:,'datatype'] = data.loc[:,'series_id'].str[18:20]

        data = data.loc[(data['industry'].astype(int))%1e6==0,:]
        data = data.loc[data['datatype'].isin(['01','03']),]

    elif type == 'cpi':
        data.loc[:,'area'] = data.loc[:,'series_id'].str[4:8]
        data.loc[:,'item'] = data.loc[:,'series_id'].str[8:]

    data.drop(['series_id','footnote_codes','period'],axis=1,inplace=True)

    return data


def spread_dataset(type,data,sel_year):
    index_cols = list(data.columns)
    index_cols.remove('type')
    index_cols.remove('value')

    data = pd.pivot(data,index=index_cols,columns='type',values='value').reset_index().fillna(0)

    if type == 'sm':
        data['Avg Hourly Wages'] = data.groupby(['state','year'])['Avg Hourly Wages'].transform('max')

        # Calculate percentage Chg
        data['wage_inc'] = (data.groupby(['state','cbsa_area'])['Avg Hourly Wages'].transform('last')/data.groupby(['state','cbsa_area'])['Avg Hourly Wages'].transform('first')).apply(lambda x:round(100*x,2))

        data = data.loc[data['cbsa_area']!='Statewide',]

    elif type == 'cpi':
        # Calculate percentage Chg
        data[cpi_columns] = (data.groupby(['area'])[cpi_columns].transform('last')/data.groupby(['area'])[cpi_columns].transform('first')).apply(lambda x:round(100*x,2))

    data.drop(data.loc[data['year']!=sel_year,].index,inplace=True)

    return data

# Aggregate preprocessing functions
def preprocess_data(type,file_path,file_name,sel_year,presets):
    loaded_data = read_dataset(file_path,file_name)
    loaded_data = clean_dataset(type,loaded_data,sel_year)
    loaded_data = merge_dataset(type,loaded_data,presets)
    loaded_data = spread_dataset(type,loaded_data,sel_year)
    return loaded_data


def simplify_area(data):
    data['Metro area'] = data.apply(lambda x:x['cbsa_area'].replace('-','/').replace('/',',').split(',')[0]+', '+x['state'],axis=1)

    return data

##################################################################
## Analyzing parts
def calc_ranks(data,sel_limit):
    data.drop(data.loc[data['All Employees']<data['All Employees'].mean(),:].index,inplace=True)

    data.loc[:,'emp_score'] = len(data)-(data['All Employees']-min(data['All Employees']))/((max(data['All Employees'])-min(data['All Employees']))/(len(data)-1))
    data.loc[:,'wage_score'] = len(data)-(data['Avg Hourly Wages']-min(data['Avg Hourly Wages']))/((max(data['Avg Hourly Wages'])-min(data['Avg Hourly Wages']))/(len(data)-1))
    data.loc[:,'score'] = (data['emp_score']+data['wage_score'])/2
    data.loc[:,'rank'] = data['score'].rank(method='dense')

    data.drop(data.loc[data['rank']>sel_limit,:].index,inplace=True)

    # Normalize score (Up to 1)
    data.loc[:,'score'] = 1/data['score']

    data.drop(['emp_score','wage_score'],axis=1,inplace=True)

    return data

def calc_CPI(data,weights):
    wt_key = list(weights.keys())
    wt_val = list(weights.values())

    data.loc[:,wt_key] = data[wt_key].apply(lambda x:x*wt_val,axis=1)
    data.loc[:,'eCPI'] = data[wt_key].sum(axis=1)

    # data.loc[:,'eCPI'] = data[weights.keys()].dot(pd.Series(weights))
    data.loc[:,'eWage'] = (data.loc[:,'wage_inc']/data.loc[:,'eCPI']).apply(lambda x:round(100*x,2))

    return data
