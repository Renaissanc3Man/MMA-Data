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






#todo: figure out why http://www.sherdog.com/events/UFC-Fight-Night-121-Werdum-vs-Tybura-61985 data is missing




link_urls_list = [r'http://www.sherdog.com/organizations/Pride-Fighting-Championships-3/recent-events/1',
                  r'http://www.sherdog.com/organizations/World-Extreme-Cagefighting-48/recent-events/1',
                  r'http://www.sherdog.com/organizations/World-Series-of-Fighting-5449/recent-events/1',
                  r'http://www.sherdog.com/organizations/Ultimate-Fighting-Championship-2/recent-events/1',
                  r'http://www.sherdog.com/organizations/Ultimate-Fighting-Championship-2/recent-events/2',
                  r'http://www.sherdog.com/organizations/Ultimate-Fighting-Championship-2/recent-events/3',
                  r'http://www.sherdog.com/organizations/Ultimate-Fighting-Championship-2/recent-events/4',
                  r'http://www.sherdog.com/organizations/Ultimate-Fighting-Championship-2/recent-events/5',
                  r'http://www.sherdog.com/organizations/Bellator-MMA-1960/recent-events/1',
                  r'http://www.sherdog.com/organizations/Bellator-MMA-1960/recent-events/2',
                  r'http://www.sherdog.com/organizations/Strikeforce-716/recent-events/1']




urls_list = []
for mylink_url in link_urls_list:
    page = urllib2.urlopen(mylink_url)
    soup = BeautifulSoup(page)
    events_table = soup.find_all('tr',attrs={'class':'even','class':'odd'})


    for myevent_table in events_table:
        urls_list.append(myevent_table.find_all("a")[0].get("href").encode('ascii','ignore'))

print urls_list











event_dfs_list = []
for myurl in urls_list:

    try:
        #first open non-printer friendly version of event because it contains the full date
        myurl = r'http://www.sherdog.com' + myurl
        #df = pd.read_html(myurl)

        page = urllib2.urlopen(myurl)
        soup = BeautifulSoup(page)


        event_date = pd.to_datetime(soup.find_all('span',attrs={'class':'date'})[1].get_text())

        #even though the links are not shown, future scheduled event links will be picked up by beautifulsoup
        #only gather data for past events
        if event_date < pd.to_datetime(datetime.datetime.now()):
            event_organization = soup.find_all('div',attrs={'itemprop':'attendee'})[0]
            event_organization = event_organization.find_all('span',attrs={'itemprop':'name'})[0].get_text().encode('ascii','ignore')
            d=1
            event_title = soup.find_all('div',attrs={'class':'section_title'})[0]
            event_title = str(event_title.find_all('span',attrs={'itemprop':'name'})[0])
            event_title = re.match(r'(<span itemprop="name">)(.*)(<br/>)(.*)(</span>)',event_title)
            event_title = event_title.group(2) + ' - ' + event_title.group(4)


            #sherdog page organization is strange, so we must manually scrape main event data, then join to
            # pd.read_html for all other data
            fighter_left_side = soup.find_all('div',attrs={'class':'fighter left_side'})[0]
            fighter_left_side_name = fighter_left_side.find_all('span',attrs={'itemprop':'name'})[0].get_text().encode('ascii','ignore')
            fighter_left_side_win_loss = fighter_left_side.find_all('span',attrs={'class':'final_result'})[0].get_text().encode('ascii','ignore')


            fighter_right_side = soup.find_all('div',attrs={'class':'fighter right_side'})[0]
            fighter_right_side_name = fighter_right_side.find_all('span',attrs={'itemprop':'name'})[0].get_text().encode('ascii','ignore')
            fighter_right_side_win_loss = fighter_right_side.find_all('span',attrs={'class':'final_result'})[0].get_text().encode('ascii','ignore')



            #the rest of the data is in table form, so we can more easily import with pd.read_html
            tables_df = pd.read_html(myurl)


            #get result details from main event
            main_event_method = tables_df[0][1].iloc[0].encode('ascii','ignore')[7:]  #get rid of word "method "
            main_event_round = int(tables_df[0][3].iloc[0].encode('ascii','ignore')[6:])
            main_event_time = tables_df[0][4].iloc[0].encode('ascii','ignore')[5:]

            main_event_dict = {'Fight Number':0,
                               'Fighter1': fighter_left_side_name + ' ' + fighter_left_side_win_loss, #match formatting on table_df
                               'vs': 'vs',
                               'Fighter2': fighter_right_side_name + ' ' + fighter_right_side_win_loss,
                               'Method': main_event_method,
                               'Round': main_event_round,
                               'Time': main_event_time}
            main_event_df = pd.DataFrame(main_event_dict,index=[0])



            #reorganize table
            table_df = tables_df[1]
            table_df.columns = ['Fight Number','Fighter1','vs','Fighter2','Method','Round','Time']
            table_df = table_df.drop([0]) #drop row with mislabled headers
            table_df = table_df.copy() #fix issue with copy/slice
            table_df['Fight Number'] = range(1,table_df.shape[0]+1) #reorder fights to match convention from other data sources


            #join with main_event_df
            table_df = pd.concat([main_event_df,table_df],ignore_index=True)
            table_df = table_df[['Fight Number','Fighter1','vs','Fighter2','Method','Round','Time']] #reorder columns
            table_df = table_df.copy() #get rid of slice/copy error for later


            #by convention, winning fighter is on the left side, but in the case of a draw,
            # we need to handle manually
            def extract_win_loss_draw(x):
                return x.split(' ')[-1]

            table_df['Fighter1 Result'] = table_df['Fighter1'].map(lambda x: x.split(' ')[-1])
            table_df['Fighter2 Result'] = table_df['Fighter2'].map(lambda x: x.split(' ')[-1])


            #strip result from fighter names
            table_df['Fighter1'] = table_df['Fighter1'].map(lambda x: ' '.join(x.split(' ')[:-1]))
            table_df['Fighter2'] = table_df['Fighter2'].map(lambda x: ' '.join(x.split(' ')[:-1]))

            del table_df['vs'] #get rid of useless column



            #split into fighter1 and fighter2 tables to obtain tabular form
            fighter1_df = table_df.copy()
            fighter1_df = fighter1_df = fighter1_df.rename(columns={'Fighter1':'Fighter',
                                                                    'Fighter2': 'Opponent',
                                                                    'Fighter1 Result':'Result'})
            del fighter1_df['Fighter2 Result']

            fighter2_df = table_df.copy()
            fighter2_df = fighter2_df = fighter2_df.rename(columns={'Fighter2':'Fighter',
                                                                    'Fighter1': 'Opponent',
                                                                    'Fighter2 Result':'Result'})
            del fighter2_df['Fighter1 Result']


            #combine to make final event df
            event_df = pd.concat([fighter1_df,fighter2_df],ignore_index=True)

            event_df['Date'] = event_date
            event_df['Organization'] = event_organization
            event_df['Url'] = myurl
            event_df['Event'] = event_title





            event_dfs_list.append(event_df)


    except:
        print '\n\nerror for:',myurl
        print str(traceback.format_exc())









sherdog_df = pd.concat(event_dfs_list,ignore_index=True)



#in the fight end method column, for some reason the refaree's name is included,
#strip it away
# most will be in the format: result (detail)  refaree
# some stragglers will be formatted as result - detail  refaree
def strip_ref_name(x):
    try:
        mymatch = re.match(r'(?i)(.*)(\(.*\))(.*|$)',x)
        if not pd.isnull(mymatch):
            result = mymatch.group(1) + mymatch.group(2)
        else:
            mymatch = re.match(r'(?i)(.*)( - )(.*)(  )(.*|$)',x)
            if not pd.isnull(mymatch):
                result = mymatch.group(1) + '(' + mymatch.group(3) + ')'
            else:
                result = x.split('  ')[0]

        return result

    except:
        print '\n',x
        return x

sherdog_df['Method'] = sherdog_df['Method'].map(strip_ref_name)



#clean double spaces, trip whitespace, etc
sherdog_df['Fighter'] = sherdog_df['Fighter'].map(clean_fighter_name)

fighter_name_standardization_dict = create_fighter_name_standardization_dict()
sherdog_df['Fighter'] = sherdog_df['Fighter'].map(lambda x: replace_if_in_dict(x,fighter_name_standardization_dict))




#change column order
sherdog_df = sherdog_df[['Organization','Event','Date','Fight Number','Result','Fighter','Opponent','Method','Round','Time','Url']]

sherdog_df = sherdog_df.sort_values(['Date','Fight Number'], ascending=[False,True])







sherdog_df.to_csv(r'../output data/mma_data_sherdog.csv',index=False)

























































