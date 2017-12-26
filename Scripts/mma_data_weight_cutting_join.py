import numpy as np
import pandas as pd
import re
import datetime
import traceback

import urllib2
from bs4 import BeautifulSoup

#for later use in replacing misspelled names
def replace_if_in_dict(parm,mydict):
    if not pd.isnull(parm) and parm in list(mydict.keys()):
        parm = mydict[parm]
    return parm

def fillna_from_other_col(df,from_col,to_col):
    original_df_cols = list(df.columns)
    cols_minus_to_col = list(df.columns)
    cols_minus_to_col.remove(to_col)
    df = pd.concat([df[cols_minus_to_col],df[[to_col]].apply(lambda x: x.fillna(value=df[from_col]))],axis=1)
    df = df[original_df_cols] #preserve column order
    return df




# #####################################################################################################
#
# NOTE: the weight cutting data came from a twitter user. It is mostly accurate from spot checking, but
#       there was at least one instance where a weight I checked vs ufc.com was wrong.
#
#       https://twitter.com/dimspace/status/943181086330425346 @dimspace https://t.co/2ulRCwzxkx
#
# #####################################################################################################







#import mma wins/losses data (scraped from fightmetric)
mma = pd.read_csv(r'../output data/mma_data_fightmetric.csv',low_memory=False)
mma['Date'] = pd.to_datetime(mma['Date'])









#import weight cutting data, source (manually modified, removed name formatting issues, etc) = https://twitter.com/dimspace/status/943181086330425346 @dimspace https://t.co/2ulRCwzxkx
wcut = pd.read_csv(r"../input data/mma_data_weight_cutting.csv",low_memory=False)
wcut['Date'] = pd.to_datetime(wcut['Date'])
del wcut['Event'] #fill in with more accurate fightmetric data





wcut = mma[['Date','Fight Number','Result','Fighter','Opponent','Method']].merge(wcut,on=['Fighter','Date'],how='right')



#for fights that never happened, fill details from
wcut = mma[['Event','Date']].drop_duplicates().merge(wcut,on='Date',how='right')






#i want to compare main and co-main with rest of fights
def main_co_main_ucard(fight_number):
    if fight_number in [0,1]:
        result = 'Main or Co-Main'
    else:
        result = 'Undercard'
    return result
wcut['Main Co-Main vs Undercard'] = wcut['Fight Number'].map(main_co_main_ucard)







wcut.to_csv(r"../output data/mma_data_weight_cutting_joined.csv",index=False)










































