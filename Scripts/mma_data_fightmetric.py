import os, sys
sys.path.append(os.path.dirname(__file__))
from mma_data_library import *


##import numpy as np
##import pandas as pd
##import re
##import datetime
##import traceback
##
##import urllib2
##from bs4 import BeautifulSoup
##
###for later use in replacing misspelled names
##def replace_if_in_dict(parm,mydict):
##    if not pd.isnull(parm) and parm in list(mydict.keys()):
##        parm = mydict[parm]
##    return parm













#get urls list for all ufc events
page = urllib2.urlopen(r'http://www.fightmetric.com/statistics/events/completed?page=all')
soup = BeautifulSoup(page)

urls_list = []
all_links = soup.find_all("a")
for link in all_links:
    link_text = link.get("href")
    if not pd.isnull(link_text):
        try:
            link_text = link_text.encode('ascii','ignore') #fix issue of str(link_text) not working due to unknown unicode character
        except:
            print link_text
        if str.find(link_text,r'http://www.fightmetric.com/event-details/') != -1:
            urls_list.append(link_text)









#iterate through each event, scraping data
fightmetric_dfs_list = []
for myurl in urls_list:


    #get date from list on website
    page = urllib2.urlopen(myurl)
    soup = BeautifulSoup(page)


    event_date = None #initialize
    for ul in soup.find_all('ul'):
        for idx, li in enumerate(ul.findChildren('li')):
            if idx in range(3):
                if str.find(str(li.text),r'Date:') != -1:
                    event_date = ' '.join(str(li.text).split()) #split then rejoin to strip whitespace properly
                    event_date = event_date[6:]
                    event_date = pd.to_datetime(event_date)

    event_title = soup.find_all('span',class_=r'b-content__title-highlight')[0].text
    event_title = ' '.join(str(event_title).split())





    if event_date < pd.to_datetime(datetime.datetime.now()):
        fightmetric_df = pd.read_html(myurl, attrs={'class': 'b-fight-details__table'})[0]

        #strip whitespace from column headers
        fightmetric_df.columns = [re.sub(r"\W", "",i) for i in fightmetric_df.columns]

##        fightmetric_df['Fight'] = fightmetric_df['Fighter'].map(lambda x: re.sub('  ',' vs. ',x))
        fightmetric_df['Fight Number'] = fightmetric_df.index

        #table is concatenated by '  ' with first element being winner's stats
        fightmetric_df_winner = fightmetric_df.copy()
        fightmetric_df_winner['Opponent'] = fightmetric_df_winner['Fighter'].map(lambda x: x.split('  ')[1])
        for mycol in ['Fighter','Str','Td','Sub','Pass']:
            fightmetric_df_winner[mycol] = fightmetric_df_winner[mycol].map(lambda x: x.split('  ')[0])


        fightmetric_df_loser = fightmetric_df.copy()
        fightmetric_df_loser['Opponent'] = fightmetric_df_loser['Fighter'].map(lambda x: x.split('  ')[0])
        for mycol in ['Fighter','Str','Td','Sub','Pass']:
            fightmetric_df_loser[mycol] = fightmetric_df_loser[mycol].map(lambda x: x.split('  ')[1])
        #replace win with loss (leave draw's in there)
        fightmetric_df_loser['WL'] = fightmetric_df_loser['WL'].map(lambda x: re.sub('win','loss',x))


        fightmetric_df = pd.concat([fightmetric_df_winner, fightmetric_df_loser],ignore_index=True)





        #append date to df
        fightmetric_df['Date'] = event_date
        fightmetric_df['Event'] = event_title
        fightmetric_df['Url'] = myurl


        fightmetric_df = fightmetric_df.sort_values('Fight Number')

        fightmetric_dfs_list.append(fightmetric_df)






fightmetric_df = pd.concat(fightmetric_dfs_list,ignore_index=True)





#clean double spaces, trip whitespace, etc
fightmetric_df['Fighter'] = fightmetric_df['Fighter'].map(clean_fighter_name)

fighter_name_standardization_dict = create_fighter_name_standardization_dict()
fightmetric_df['Fighter'] = fightmetric_df['Fighter'].map(lambda x: replace_if_in_dict(x,fighter_name_standardization_dict))



#change column names to be consistent across datasets
fightmetric_df = fightmetric_df.rename(columns={'WL':'Result',
                                                'Str':'Sig Strikes',
                                                'Td':'Takedowns',
                                                'Sub':'Sub Attempts',
                                                'Pass':'Guard Passes',
                                                'Weightclass':'Division'})

#convert Weightclass to numeric value
#todo: fix each of the catchweights
fightmetric_df['Weightclass'] = fightmetric_df['Division'].map(weightclass_dict)


fightmetric_df = fightmetric_df[['Event','Date','Fight Number','Division','Weightclass','Fighter','Opponent','Result','Method','Round','Time','Sig Strikes','Takedowns','Sub Attempts','Guard Passes','Url']]



#todo: add code to fix double spaces and trim in fighter name

fightmetric_df.to_csv(r'../output data/mma_data_fightmetric.csv',index=False)








