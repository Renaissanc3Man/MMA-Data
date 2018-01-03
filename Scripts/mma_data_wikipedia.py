import os, sys
sys.path.append(os.path.dirname(__file__))
from mma_data_library import *














#go to first page then find how many pages to iterate through
myurl = r'https://en.wikipedia.org/wiki/List_of_UFC_events'
page = urllib2.urlopen(myurl)
soup = BeautifulSoup(page,'lxml')





event_rows = soup.find_all('table',attrs={'id':'Past_events'})[0].find_all('tr')
events_list = []
for i in range(1,len(event_rows)):
    event_url = event_rows[i].find_all('td')[1].find_all('a')[0].get("href")
    event_title = event_rows[i].find_all('td')[1].get_text().encode('ascii','ignore')
    event_date = event_rows[i].find_all('td')[2].find_all('span',attrs={'class':'sortkey'})[0].get_text().encode('ascii','ignore')
    event_date = event_date.replace('00000000','')
    event_date = event_date.replace(r'-0000','')
    event_date = pd.to_datetime(event_date)
    event_venue = event_rows[i].find_all('td')[3].get_text().encode('ascii','ignore')
    event_location = event_rows[i].find_all('td')[4].get_text().encode('ascii','ignore')
    event_attendance = event_rows[i].find_all('td')[5]
    try:
        event_attendance = re.search(r'(span>)(.*)(<sup)',str(event_attendance)).group(2)
        event_attendance = int(event_attendance.replace(',',''))
    except:
        event_attendance = np.nan #some events do not have n/a as their value and will fail the regex search
    events_list.append([event_url,event_title,event_date,event_venue,event_location,event_attendance])











#debug
##urls_list = urls_list[:10]
##urls_list = ['https://en.wikipedia.org/wiki/UFC_on_Fuel_TV:_Sanchez_vs._Ellenberger']


dfs_list = []
for myevent in events_list:

    try:
        #first open non-printer friendly version of event because it contains the full date
        myurl = r'https://en.wikipedia.org' + myevent[0]
        #df = pd.read_html(myurl)

        if myurl == r'https://en.wikipedia.org/wiki/UFC_on_Fuel_TV:_Sanchez_vs._Ellenberger':
            d=1

        if myurl == r'https://en.wikipedia.org/wiki/UFC_Fight_Night:_Lamas_vs._Penn':
            d=1

##        event_df = pd.read_html(myurl,attrs={'class':'toccolours'})[0]

        #issues with wikipedia page that has multiple events bundled together
        #solution: find the associated 'infobox's and check date
        event_dfs = pd.read_html(myurl,attrs={'class':'toccolours'})
        infobox_dfs = pd.read_html(myurl,attrs={'class':'infobox'})

        event_df = event_dfs[0]
        infobox_df = infobox_dfs[0]

        #for some events, there will be an extra infobox found at the beginning
        if len(event_dfs) != len(infobox_dfs):
            print len(event_dfs),len(infobox_dfs)
            infobox_dfs.pop(0)
            print len(event_dfs),len(infobox_dfs)
            d=1

        for i,myinfobox_df in enumerate(infobox_dfs):
            if 'Date' in list(myinfobox_df[0].unique()):
                infobox_date = myinfobox_df[myinfobox_df[0]=='Date'][1].iloc[0].encode('ascii','ignore')
                print infobox_date
                if not pd.isnull(re.match(r'(?i)(.*)(\()(\d\d\d\d\-\d\d\-\d\d)(\))',infobox_date)):
                    infobox_date = re.match(r'(?i)(.*)(\()(\d\d\d\d\-\d\d\-\d\d)(\))',infobox_date).group(3)
                elif not pd.isnull(re.match(r'(?i)(.*)(\[)(\d+)(\])(.*|$)',infobox_date)):
                    infobox_date = re.match(r'(?i)(.*)(\[)(\d+)(\])(.*|$)',infobox_date).group(1)
                if not infobox_date == 'Cancelled':
                    infobox_date = pd.to_datetime(infobox_date)
                else:
                    #check to see if we have any instances of cancelled events that are
                    #bundled together in the same wikipedia page
                    if len(event_dfs) > 1 or len(infobox_dfs) > 1:
                        d=1
                    else:
                        event_df = event_dfs[i]
                if infobox_date == myevent[2]:
                    event_df = event_dfs[i]
                    break






        event_df = event_df.rename(columns= {0:'Division',1:'Fighter1',2:'Result',3:'Fighter2',4:'Method',5:'Round',6:'Time',7:'Notes'})
        event_df = event_df.dropna(subset=['Fighter1'])
        event_df = event_df.dropna(subset=['Fighter2'])

        event_df['Fighter1'] = event_df['Fighter1'].map(lambda x: x.replace(' (c)','').replace(' (ic)','').replace('(c-FTW) ','').replace('(c - FTW) ',''))
        event_df['Fighter2'] = event_df['Fighter2'].map(lambda x: x.replace(' (c)','').replace(' (ic)','').replace('(c-FTW) ','').replace('(c - FTW) ',''))

        event_df['Fight Number'] = range(0,event_df.shape[0])


        def result_check(df):
            if df['Result'] in ['def','def.']:
                result = 'win'
            elif df['Result'] in ['vs','vs.']:
                if pd.isnull(df['Method']):
                    result = np.nan
                elif not pd.isnull(re.match(r'Draw',df['Method'].encode('ascii','ignore'))):
                    result = 'draw'
                elif not pd.isnull(re.match(r'No Contest',df['Method'].encode('ascii','ignore'))):
                    result = 'nc'
                else:
                    result = np.nan
            else:
                result = np.nan
            return result
        event_df['Result'] = event_df.apply(result_check,axis=1)

        fighter1_df = event_df.copy()
        fighter1_df = fighter1_df.rename(columns={'Fighter1':'Fighter','Fighter2':'Opponent'})

        fighter2_df = event_df.copy()
        fighter2_df = fighter2_df.rename(columns={'Fighter2':'Fighter','Fighter1':'Opponent'})
        fighter2_df['Result'] = fighter2_df['Result'].map(lambda x: replace_if_in_dict(x,{'win':'loss'}))


        event_df = pd.concat([fighter1_df,fighter2_df],ignore_index=True)

        event_df['Url'] = myurl
        event_df['Event'] = myevent[1]
        event_df['Date'] = myevent[2]
        event_df['Venue'] = myevent[3]
        event_df['Location'] = myevent[4]
        event_df['Attendance'] = myevent[5]

##        print event_df

        dfs_list.append(event_df)


    except:
        print '\n\nerror for:',myurl
        print str(traceback.format_exc())









wiki_df = pd.concat(dfs_list,ignore_index=True)








wiki_df['Weightclass'] = wiki_df['Division'].map(division_to_weightclass)



wiki_df = wiki_df[['Event','Date','Division','Weightclass','Fight Number','Fighter','Result','Opponent','Method','Round','Time','Location','Venue','Attendance','Url']]
wiki_df = wiki_df.sort_values(['Date','Fight Number'],ascending=[False,True])



#clean double spaces, trip whitespace, etc
wiki_df['Fighter'] = wiki_df['Fighter'].map(clean_fighter_name)

fighter_name_standardization_dict = create_fighter_name_standardization_dict()
wiki_df['Fighter'] = wiki_df['Fighter'].map(lambda x: replace_if_in_dict(x,fighter_name_standardization_dict))


print wiki_df[~(wiki_df['Fighter'].isin(list(fighter_name_standardization_dict.values())))]['Fighter'].unique()







#fix unicode issues when saving
for mycol in ['Division','Fighter','Opponent','Method','Url']:
    wiki_df[mycol] = wiki_df[mycol].map(lambda x: x.encode('ascii','ignore') if not pd.isnull(x) else x)

for mycol in ['Event','Date','Division','Weightclass','Fight Number','Fighter','Result','Opponent','Method','Round','Time','Location','Venue','Attendance','Url']:
    try:
        wiki_df[[mycol]].to_csv(r'../output data/mma_data_wikipedia.csv')
    except:
        print mycol
        print str(traceback.format_exc())

to_newexcel(wiki_df)
wiki_df.to_csv(r'../output data/mma_data_wikipedia.csv',index=False)
























































