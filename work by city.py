# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 11:34:29 2024

@author: hanit
"""


import pandas as pd
import plotnine as pn

pop_df = pd.read_excel(r'C:\Users\hanit\Desktop\dataton 2025\data\population 2022.xlsx')
df_license = pd.read_csv(r'C:\Users\hanit\Desktop\dataton 2025\data\Business license 2022.csv')


pop_df.dropna(subset=['LocalityCode'], inplace=True)

pop_df['LocalityCode'] = pop_df['LocalityCode'].astype(int)
pop_df['LocalityCode'] = pop_df['LocalityCode'].astype(str)

df_license['SEMEL_YESUV'] = df_license['SEMEL_YESUV'].astype(str)



work_df = pop_df[['LocNameHeb','LocalityCode','pop_approx','Rova_cmb','SubQuarter',
                  'm_age0_4_pcnt',	'm_age5_9_pcnt',	'm_age10_14_pcnt',
                  'm_age15_19_pcnt',	'm_age20_24_pcnt',	'm_age25_29_pcnt',	'm_age30_34_pcnt',	
                  'm_age35_39_pcnt',	'm_age40_44_pcnt',	'm_age45_49_pcnt',	'm_age50_54_pcnt',	
                  'm_age55_59_pcnt',	'm_age60_64_pcnt',	'm_age65_69_pcnt',	'm_age70_74_pcnt',	
                  'm_age75_79_pcnt',	'm_age80_84_pcnt',	'm_age85_89_pcnt',	'm_age90_pcnt',
                  'w_age0_4_pcnt',	'w_age5_9_pcnt',	'w_age10_14_pcnt',	'w_age15_19_pcnt',	
                  'w_age20_24_pcnt',	'w_age25_29_pcnt',	'w_age30_34_pcnt',	'w_age35_39_pcnt',	
                  'w_age40_44_pcnt',	'w_age45_49_pcnt',	'w_age50_54_pcnt',	'w_age55_59_pcnt',	
                  'w_age60_64_pcnt',	'w_age65_69_pcnt',	'w_age70_74_pcnt',	'w_age75_79_pcnt',	
                  'w_age80_84_pcnt',	'w_age85_89_pcnt',	'w_age90_pcnt',
                  'WrkOutLoc_pcnt','IndstA_pcnt',
                  'IndstB_pcnt','IndstC_pcnt','IndstD_pcnt','IndstE_pcnt',
                  'IndstF_pcnt','IndstG_pcnt','IndstH_pcnt','IndstI_pcnt',
                  'IndstJ_pcnt','IndstK_pcnt','IndstL_pcnt','IndstM_pcnt',
                  'IndstN_pcnt','IndstO_pcnt','IndstP_pcnt','IndstQ_pcnt',
                  'IndstR_pcnt','IndstS_pcnt','IndstT_pcnt','IndstU_pcnt','IndstX_pcnt']]

work_df_new = work_df.copy()

work_df_new['age15_and_below_pcnt'] =  work_df_new['m_age0_4_pcnt'] + work_df_new['m_age5_9_pcnt'] + work_df_new['m_age10_14_pcnt'] + \
                                        work_df_new['w_age0_4_pcnt'] + work_df_new['w_age5_9_pcnt'] + work_df_new['w_age10_14_pcnt']

work_df_new['age15_and_above_pcnt'] = 100 - work_df_new['age15_and_below_pcnt']
work_df_new['age15_and_above_abs'] = work_df_new['pop_approx'] * (work_df_new['age15_and_above_pcnt']/100)

work_df_new[['pop_approx','age15_and_above_abs']] 
 
work_df_new['WrkOutLoc_abs'] = work_df_new['age15_and_above_abs'] * (work_df_new['WrkOutLoc_pcnt']/100) 


work_df_new[['pop_approx','age15_and_above_abs','WrkOutLoc_abs']] 

for col in work_df_new:
    print(col)
    
for col in work_df_new:
    if 'Indst' in col:        
        work_df_new[(col.replace('_pcnt', '_abs'))] = (work_df_new[col]/100)* work_df_new['age15_and_above_abs']


drop_list = []

for col in work_df_new:
    if '_pcnt' in col:
        drop_list.append(col)
        
        
work_df_new.drop(columns=drop_list, inplace=True)
work_df_new.drop(columns=['Rova_cmb','SubQuarter'], inplace=True)

work_by_city = work_df_new.groupby(['LocNameHeb','LocalityCode']).sum().reset_index()


df = pd.merge(work_by_city, df_license, how='left', left_on='LocalityCode', right_on='SEMEL_YESUV')

for col in df:
    print(col)

for col in df:
    if col not in  ['LocalityCode','pop_approx','Yesuv_type', 'SEMEL_YESUV', 'LocNameHeb', 'age15_and_above_abs']:
        try: df[(col.replace('_abs', ''))] = df[col]/df['age15_and_above_abs']
        except TypeError: pass