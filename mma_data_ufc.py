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









urls_list = []


#go to first page then find how many pages to iterate through
myurl = r'http://www.ufc.com/event/Past_Events?offset=0&max=30&sort=eventDateGMT&order=desc'
page = urllib2.urlopen(myurl)
soup = BeautifulSoup(page)

row_count = str(soup.find_all('span',attrs={'class':'row-count'})[1])
row_count = int(re.match(r'(?i)(<span class="row-count">)(\d+)(.*|$)',row_count).group(2))



for mypageoffset in np.arange(1,row_count,30):
    myurl = r'http://www.ufc.com/event/Past_Events?offset=' + str(mypageoffset) + r'&max=30&sort=eventDateGMT&order=desc'
    page = urllib2.urlopen(myurl)
    soup = BeautifulSoup(page)
    events_table = soup.find_all('table',attrs={'class':'events-table'}) #subset soup to just events table so we eliminate unwanted links
    all_links = events_table[0].find_all("a")
    for link in all_links:
        link_text = link.get("href")
        if not pd.isnull(link_text):
            try:
                link_text = link_text.encode('ascii','ignore') #fix issue of str(link_text) not working due to unknown unicode character
            except:
                print link_text
                d=1
            #if str.find(link_text,r'/event/') != -1 or str.find(link_text,r'/event/the:
            if re.match(r'(?i)(^/event/)(.*|$)',link_text)!=None and re.match(r'(?i)(^/event/past_events)(.*|$)',link_text)==None:
                urls_list.append(link_text)
    print "page offset:",mypageoffset
    print len(urls_list)












dfs_list = []
for myurl in urls_list:

    try:
        #first open non-printer friendly version of event because it contains the full date
        myurl = r'http://www.ufc.com' + myurl
        #df = pd.read_html(myurl)

        page = urllib2.urlopen(myurl)
        soup = BeautifulSoup(page)


        event_header = soup.find_all('div',attrs={'id':'titleBar'})[0].get_text().encode('ascii','ignore')
        event_header = event_header.split('\n')

##        #data not in same order for tuesday night contender series
##        if str.find(myurl,"contender-series") != -1:
##            event_title = event_header[20].strip() + ' - ' + event_header[22].strip() #get rid of leading whitespace
##            event_date = pd.to_datetime(event_header[22].strip())
##            event_location = event_header[31].strip()
##        else:
##            event_title = event_header[17].strip() + ' - ' + event_header[22].strip() #get rid of leading whitespace
##            event_date = pd.to_datetime(event_header[19].strip())
##            event_location = event_header[29].strip()
        #data not in same order for tuesday night contender series
        if str.find(myurl,"contender-series") != -1:
            rownums = [20,22,22,31]
        else:
            rownums = [17,22,19,29]


        event_title = event_header[rownums[0]].strip()
        event_title_b = event_header[rownums[1]].strip()
        if len(event_title_b) > 1:
            event_title = event_title + ' - ' + event_title_b
        event_date = pd.to_datetime(event_header[rownums[2]].strip())
        event_location = event_header[rownums[3]].strip()











        #now scrape the printer friendly version of the event
        myurl = myurl + r'/printFightCard'

        #some printfightcard urls dont work if they have http:// in the front, some are the opposite
        try:
            page = urllib2.urlopen(myurl)
        except:
            print myurl
            myurl = unicode(myurl)
            print myurl
            d=1
            page = urllib2.urlopen(myurl)
            d=1


        soup = BeautifulSoup(page)


        fighter1 = soup.find_all('span',attrs={'class':'fighter1'})
        fighter2 = soup.find_all('span',attrs={'class':'fighter2'})

        stat_dfs_list = pd.read_html(myurl)
        fighter1[0].get_text().encode('ascii','ignore')




        #transpose and join info in tabular form
        fighter_dfs_list = []
        for i,myfighter in enumerate(fighter1):
            fighter_df = stat_dfs_list[i][[0,1]].set_index(1).T  #fighter1 stats in col1
            fighter_df['Fighter'] = myfighter.get_text().encode('ascii','ignore')
            fighter_df['Fight Number'] = i
            fighter_dfs_list.append(fighter_df)

        for i,myfighter in enumerate(fighter2):
            fighter_df = stat_dfs_list[i][[1,2]].set_index(1).T #fighter2 stats in col3
            fighter_df['Fighter'] = myfighter.get_text().encode('ascii','ignore')
            fighter_df['Fight Number'] = i
            fighter_dfs_list.append(fighter_df)

        event_df = pd.concat(fighter_dfs_list,ignore_index=True)


        event_df['Event'] = event_title
        event_df['Date'] = event_date
        event_df['Location'] = event_location
        event_df['Url'] = myurl

        dfs_list.append(event_df)


    except:
        print '\n\nerror for:',myurl
        print str(traceback.format_exc())









ufc_df = pd.concat(dfs_list,ignore_index=True)






# MISSING DATA for two fight cards
# http://www.ufc.com/event/UFC120-london-event/printFightCard  -- manually filled in
# http://www.ufc.com/event/Ultimate-Japan/printFightCard -- still missing

ufc_missing_data = pd.read_csv(r'mma_data_ufc_missing.csv',low_memory=False)

ufc_df = pd.concat([ufc_df,ufc_missing_data],ignore_index=True)


#change column order
ufc_df = ufc_df[['Event','Date','Location','Fight Number','Fighter','Record','Height','Weight','Reach','Leg Reach','Url']]

ufc_df = ufc_df.sort_values(['Date','Fight Number'], ascending=[False,True])



ufc_df.to_csv(r'mma_data_ufc.csv',index=False)

























































