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




# #####################################################################################################
#
# NOTE: the weight cutting data came from a twitter user. It is mostly accurate from spot checking, but
#       there was at least one instance where a weight I checked vs ufc.com was wrong.
#
#       https://twitter.com/dimspace/status/943181086330425346 @dimspace https://t.co/2ulRCwzxkx
#
# #####################################################################################################







#import mma wins/losses data (scraped from fightmetric)
mma = pd.read_csv(r'mma_data_fightmetric.csv',low_memory=False)
#fix typographic error from fightmetric for Jessica Rose-Clark
namefix_dict = {'Jessica-Rose Clark':'Jessica Rose-Clark'}
mma['Fighter'] = mma['Fighter'].map(lambda x: replace_if_in_dict(str(x),namefix_dict))


#mma = mma[['WL','Fighter','Weightclass','Method','Opponent','Date']]

mma['Date'] = pd.to_datetime(mma['Date'])




#create a month column because the weight cutting data is only given at that level
#we need this to join to the wins/losses dataset
#note: this will cause an error on the ultra rare occasion a fighter fights twice in a month
def get_month(mydate):
    if mydate.day != 1:
        mydate = mydate - np.timedelta64(mydate.day - 1,'D')
    return mydate
mma['Month'] = mma['Date'].map(get_month)






#import weight cutting data, source (manually modified, removed name formatting issues, etc) = https://twitter.com/dimspace/status/943181086330425346 @dimspace https://t.co/2ulRCwzxkx
wcut = pd.read_csv(r"mma_data_weight_cutting.csv",low_memory=False)
wcut['Month'] = pd.to_datetime(wcut['Month'])
wcut = wcut.rename(columns={'Event':'Event (Weight-Cut)'})







wcut = mma.merge(wcut,on=['Fighter','Month'],how='inner')












#i want to compare main and co-main with rest of fights
def main_co_main_ucard(fight_number):
    if fight_number in [0,1]:
        result = 'Main or Co-Main'
    else:
        result = 'Undercard'
    return result
wcut['Main Co-Main vs Undercard'] = wcut['Fight_Number'].map(main_co_main_ucard)







wcut.to_csv(r"mma_data_weight_cutting_joined.csv",index=False)










































