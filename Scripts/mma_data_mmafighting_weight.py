import os, sys
sys.path.append(os.path.dirname(__file__))
from mma_data_library import *
import requests








#there are many issues with extra text being picked up by regex, get list of all
#fighters names to help filter
ufc_df = pd.read_csv(r'../output data/mma_data_ufc.csv',low_memory=False)
sherdog_df = pd.read_csv(r'../output data/mma_data_sherdog.csv',low_memory=False)
fightmetric_df = pd.read_csv(r'../output data/mma_data_fightmetric.csv',low_memory=False)

fighter_df = pd.concat([ufc_df[['Fighter']],sherdog_df[['Fighter']],fightmetric_df[['Fighter']]],ignore_index=True)

all_fighter_names_list = list(fighter_df['Fighter'].unique())
all_fighter_names_list = all_fighter_names_list + ['Brett Rogers','Alexis Vila','Quinton "Rampage" Jackson','B.J. Penn',
                                                    'Georges St. Pierre','Mirko "Cro Cop" Filipovic','Ben Henderson','Antonio Rodrigo Nogueira',
                                                    'Blagoi Ivanov','Fedor Emelianenko','Mike "The Joker" Guymon','Douglas Lima','Ayaka Hamasaki',
                                                    'Pat Curran','Rogerio de Lima','Chris Lozano','Jason "Mayhem" Miller','Gesias Cavalcante',
                                                    'Mauricio "Shogun" Rua','Hiroyuki Takaya','Garrett Nybakken','Thomas Diagne','Lionel Lanham',
                                                    'Kevin Ferguson Jr.','Waachiim Spirtwolf','Marcus Surin','Manjit Kolekar','Nik Fekete','Gesias Cavalcante',
                                                    'Sergei Kharitonov','Amber Brown','Jeff Smith','Richard Arsenault','Gustavo Falciroli','Zhang Tie Quan',
                                                    'Shane Krutchen','Chinzo Machida','Justin DeMoney','Timothy Elliott','James Champman','Manny Pacquiao',
                                                    'Robbie Peralta','Nicholas Mann','Andy Murad','Brian Van Hoven','Ho Jin Kim','Costa Philippou']








#generate list of all mmafighting.com archives by year/month/date
##link_urls_list = []
##for i in np.arange('2010-01-01',str(datetime.datetime.now().date()),dtype='datetime64[D]'):
##    link_urls_list.append(r'https://www.mmafighting.com/archives/' + str(i) + '/' + str(j))
##
##print len(link_urls_list)
link_urls_df = pd.DataFrame(pd.Series(np.arange('2010-01-01',str(datetime.datetime.now().date()),dtype='datetime64[D]')),columns=['Date'])
link_urls_df['Date'] = pd.to_datetime(link_urls_df['Date'])
link_urls_df['Link Urls'] = link_urls_df['Date'].map(lambda x: r'https://www.mmafighting.com/archives/' + x.strftime(r'%Y') + '/' + str(int(x.strftime(r'%m'))) + '/' + str(int(x.strftime(r'%d'))))

link_urls_list = link_urls_df['Link Urls'].tolist()


###debug
##link_urls_list = [r'https://www.mmafighting.com/archives/2010/4/4']


urls_list = []
for i,mylink_url in enumerate(link_urls_list):
    print i, mylink_url
    page_found = True
    try:
        page = urllib2.urlopen(mylink_url) #workaround for http error 429: too many requests
    except urllib2.HTTPError, err:
        if err.code == 404:
            page_found = False
            print 'page not found, skipping', mylink_url
        else:
            print mylink_url
            print str(traceback.format_exc())
            for j in range(0,500):
                try:
                    print 'sleeping 15 seconds'
                    time.sleep(15)
                    print 'done'
                    page = urllib2.urlopen(mylink_url)
                    break
                except:
                    print mylink_url
                    print '\n\n\n' + str(j) + '\n\n\n'
                    print str(traceback.format_exc())

    if page_found == True:
        soup = BeautifulSoup(page,'lxml')
        events_table = soup.find_all('div',attrs={'class':'c-compact-river__entry'})
        d=1


        for myevent_table in events_table:
            myevent_url = myevent_table.find_all("a")[0].get("href").encode('ascii','ignore')
            if not pd.isnull(re.match(r'(?i)(.*)(weigh\-in\-results|weigh\-in\-video)(.*|$)',myevent_url)):
                urls_list.append(myevent_url)

    time.sleep(1)


#manually add urls for events that dont conform to naming standard
urls_list.append(r'https://www.mmafighting.com/2017/6/24/15868124/johny-hendricks-misses-weight-again-at-ufc-fight-night-112-weigh-ins')
urls_list.append(r'https://www.mmafighting.com/2017/2/3/14500308/bec-rawlings-explains-why-she-missed-weight-at-ufc-fight-night-104')
urls_list.append(r'https://www.mmafighting.com/2014/1/31/5366204/ufc-169-weigh-ins-results-once-again-john-lineker-comes-in-over-all')
urls_list.append(r'https://www.mmafighting.com/2013/11/15/5108736/ufc-167-weight-in-results')
urls_list.append(r'https://www.mmafighting.com/2013/8/27/4664136/ufc-fight-night-weigh-ins')
urls_list.append(r'https://www.mmafighting.com/2013/3/2/4055862/silva-stann-both-on-weight-as-each-returns-to-familiar-place')
urls_list.append(r'https://www.mmafighting.com/2011/12/09/jon-jones-smiles-at-the-haters-at-ufc-140-weigh-ins')
urls_list.append(r'https://www.mmafighting.com/2011/12/02/michael-bisping-makes-tuf-14-finale-weigh-ins-a-memorable-affair')
urls_list.append(r'https://www.mmafighting.com/2010/03/20/dana-white-separates-jon-jones-brandon-vera')

#remove duplicate for ufc ufn 52
urls_to_remove_list = [r'https://www.mmafighting.com/2014/9/18/6337315/ufc-fight-night-52-weigh-in-video',
                       r'https://www.mmafighting.com/ufc/2012/2/3/2769362/ufc-143-weigh-in-results-diaz-vs-condit-mma-news']
for myurl_to_remove in urls_to_remove_list:
    try:
        urls_list.remove(myurl_to_remove)
    except:
        pass

#todo: manually add data for UFC Fight Night - Lewis vs Abdurakhimov 12/9/2016 (no mmafighting.com article for weight results, two event weekend)
#                            UFC Fight Night - Henderson vs Masvidal 11/28/2015 (another 2 event weekend)
#                            UFC Fight Night - Chiesa vs Lee 6/25/2017






###debug
##urls_list = [r'https://www.mmafighting.com/2017/11/23/16694996/ufc-shanghai-weigh-in-video']




event_dfs_list = []
error_urls_list = []
error_fights_list = []
for myurl in urls_list:

    try:

        page = urllib2.urlopen(myurl)
        soup = BeautifulSoup(page)

        event_title = soup.find_all('h1',attrs={'class':'c-page-title'})[0].get_text().encode('ascii','ignore')
        event_title = event_title.replace(' weigh-in video','')

        article_date = pd.to_datetime(pd.to_datetime(soup.find_all('time',attrs={'class':'c-byline__item'})[0].get_text()).date())

        #first regex "greedy" search for pattern of fighter1_name fighter1_weight vs. fighter2_name fighter2_weight
        #                                        or fighter1_name (fighter1_weight) vs. fighter2_name (fighter2_weight)
        #then split those up into fighter1 and fighter2 data
        #create a list of dataframes, then concat
        content = soup.find_all('div',attrs={'class':'c-entry-content'})[0].get_text().encode('ascii','ignore')

        #a few of the urls contain unwanted tabs
        if myurl in [r'https://www.mmafighting.com/2016/3/18/11258340/ufc-fight-night-85-weigh-in-video',r'https://www.mmafighting.com/2015/6/26/8838279/ufc-fight-night-70-weigh-in-video']:
            content = content.replace('\t',' ')

        #fix formatting for ufn36
        if myurl in [r'https://www.mmafighting.com/2014/2/14/5410180/ufc-fight-night-36-weigh-in-video',r'https://www.mmafighting.com/2013/12/13/5200370/ufc-on-fox-9-weigh-in-video']:
            content = content.replace(r'), ',') vs. ')

        if myurl in [r'https://www.mmafighting.com/2017/6/24/15868124/johny-hendricks-misses-weight-again-at-ufc-fight-night-112-weigh-ins']:
            content = content.replace(r'*','')

        if myurl in [r'https://www.mmafighting.com/2017/2/3/14500308/bec-rawlings-explains-why-she-missed-weight-at-ufc-fight-night-104']:
            content = content.replace(r' - missed weight','')

        #fix formatting for (84.2 kg / 185 lbs.)
        if myurl in [r'https://www.mmafighting.com/2011/02/25/ufc-127-weigh-in-results']:
            content = re.sub(r'\(\d+\skg\s\/\s|\(\d+\.\d+\skg\s\/\s',r'(',content)
            content = re.sub(r'\slbs\.\)',r')',content)

        #a few instances where formatting is broken by not having a space, manually fix
        if myurl == r'https://www.mmafighting.com/2011/12/09/jon-jones-smiles-at-the-haters-at-ufc-140-weigh-ins':
            content = content.replace(r'Mark Hominick(145)',r'Mark Hominick (145)')
        if myurl == r'https://www.mmafighting.com/2010/02/19/ufc-110-weigh-in-results':
            content = content.replace(r'C.B. Dollaway(185)',r'C.B. Dollaway (185)')
        if myurl == r'https://www.mmafighting.com/2017/2/3/14500308/bec-rawlings-explains-why-she-missed-weight-at-ufc-fight-night-104':
            content = content.replace(r'Alex Morono(170)',r'Alex Morono (170)')
        if myurl == r'https://www.mmafighting.com/2017/4/7/15183462/ufc-210-weigh-in-video':
            content = content.replace(r'(135.6)Jenel Lausa(124.8)',r'(135.6) Jenel Lausa (124.8)')
        if myurl == r'https://www.mmafighting.com/2014/4/15/5617110/tuf-nations-finale-weigh-in-video':
            content = content.replace(r'ET)Michael Bisping(186)',r'ET) Michael Bisping (186)')
            content = content.replace(r'Mark Bocek vs.',r'Mark Bocek (156) vs.')
        if myurl == r'https://www.mmafighting.com/ufc/2012/5/14/3019982/ufc-on-fuel-3-jung-vs-poirier-weigh-in-results':
            content = content.replace(r'Brad Tavares(185)',r'Brad Tavares (185)')
        if myurl == r'https://www.mmafighting.com/2016/6/16/11945662/wsof-31-weigh-in-video':
            content = content.replace(r'Tyler King(238)',r'Tyler King (238)')
        if myurl == r'https://www.mmafighting.com/2017/5/18/15658046/bellator-179-weigh-in-video-results':
            content = content.replace(r'Check Kongo  (244)',r'Check Kongo (244)')
        if myurl == r'https://www.mmafighting.com/2011/02/04/ufc-126-weigh-in-results':
            content = content.replace(r'Mike Pierce* (171)',r'Mike Pierce (171)')
        if myurl == r'https://www.mmafighting.com/2016/1/1/10695244/ufc-195-weigh-in-video':
            content = content.replace(r'Justine Kish ()',r'Justine Kish (116)')
            content = content.replace(r'Kyle Noke(170.5)',r'Kyle Noke (170.5)')
        if myurl == r'https://www.mmafighting.com/2015/1/2/7475913/ufc-182-weigh-in-video':
            content = content.replace(r'Alexis Dufresne (138 - will be fined 20 percent of her purse)',r'Alexis Dufresne (138)')




        #there is an issue with regex picking up extra text for the first fighter
        #we can get ~75% of fighter names from the auto-links
        #its not perfect, but will fix many of the errors
        fighters_with_links = soup.find_all('div',attrs={'class':'c-entry-content'})[0].find_all('a',attrs={'class':'sbn-auto-link','class':'injectedLink'})
        fighters_with_links = [fighter_link.get_text().encode('ascii','ignore') for fighter_link in fighters_with_links]



        #fights_regex_iterator = re.finditer(r'(?i)([a-z|\.]+\s)*(\d+\s)(vs\.\s)([a-z|\.]+\s)*(\d+)|([a-z|\.]+\s)*(\(\d+\)|\(\d+\.\d+\))(\svs\.\s)([a-z|\.]+\s)*(\(\d+\)|\(\d+\.\d+\))',content)
        fights_regex_iterator = re.finditer(r'(?i)([a-z|\.|\'|\-|\"]+\s)*(\d+|\d+\.\d+)(\svs\.\s|\svs\s)([a-z|\.|\'|\-|\"]+\s)*(\d+|\d+\.\d+)|([a-z|\.|\'|\-|\"]+\s)*(\(\d+\)|\(\d+\.\d+\))(\svs\.\s|\svs\s)([a-z|\.|\'|\-|\"]+\s)*(\(\d+\)|\(\d+\.\d+\))',content)

        fights_list = [myfight.group() for myfight in fights_regex_iterator]
        d=1

        if len(fights_list) > 0:
            fighter_dfs_list = []
            for myfight in fights_list:
                try:
                    myfight_debug = myfight[:]
                    #sometimes formatting includes parenthesis
                    myfight = myfight.replace('(','')
                    myfight = myfight.replace(')','')

                    myfight = myfight.replace(' vs ',' vs. ')
                    myfight = myfight.split(' vs. ')

                    fighter1 = myfight[-2] #less errors by taking end of list
                    fighter2 = myfight[-1]

                    fighter1_name = ' '.join(fighter1.split()[:-1])
                    fighter1_weight = np.round(float(fighter1.split()[-1]),1)

                    fighter2_name = ' '.join(fighter2.split()[:-1])
                    fighter2_weight = np.round(float(fighter2.split()[-1]),1)

                    if len(fighter1_name) < 3:
                        print myfight
                        d=1


                    #fix some of the issues with regex picking up extra text by replacing with fighters_with_links list
                    #dont just search normally because it might pick up an unintended fighter
                    for myfighter_with_link in fighters_with_links + all_fighter_names_list:
                        fighter1_name_resized = ' '.join(fighter1_name.split()[-len(myfighter_with_link.split()):])
                        if  str.find(fighter1_name_resized,myfighter_with_link) != -1:
                            fighter1_name = myfighter_with_link
                            break

                    for myfighter_with_link in fighters_with_links + all_fighter_names_list:
                        fighter2_name_resized = ' '.join(fighter2_name.split()[-len(myfighter_with_link.split()):])
                        if  str.find(fighter2_name_resized,myfighter_with_link) != -1:
                            fighter2_name = myfighter_with_link
                            break

                    if pd.isnull(fighter1_name):
                        print myfight
                        d=1


                    fighter1_df = pd.DataFrame({'Fighter':fighter1_name,'Opponent':fighter2_name,'Weight':fighter1_weight,'Fight':myfight_debug},index=[0])
                    fighter2_df = pd.DataFrame({'Fighter':fighter2_name,'Opponent':fighter1_name,'Weight':fighter2_weight,'Fight':myfight_debug},index=[0])

                    fighter_dfs_list.append(fighter1_df)
                    fighter_dfs_list.append(fighter2_df)
                except:
                    print myurl
                    print myfight
                    print str(traceback.format_exc())
                    error_fights_list.append(article_date)
                    error_fights_list.append(myurl)
                    error_fights_list.append(myfight)
                    error_fights_list.append(str(traceback.format_exc()))



            event_df = pd.concat(fighter_dfs_list,ignore_index=True)

            event_df['Event'] = event_title
            event_df['Date'] = article_date + np.timedelta64(1,'D') #weigh-in's 1 day before event
            event_df['Url'] = myurl
    ##        print event_df
            event_dfs_list.append(event_df)


    except:
        error_urls_list.append(myurl)
        print '\n\nerror for:',myurl
        print str(traceback.format_exc())









mma_df = pd.concat(event_dfs_list,ignore_index=True)





#Fix issue of certain cards in other timezones giving incorrect date
date_fix_dict = {r'https://www.mmafighting.com/2017/11/23/16694996/ufc-shanghai-weigh-in-video':'2017-11-25',
                 r'https://www.mmafighting.com/2017/7/28/16055118/ufc-214-weigh-in-video':'2017-07-29',
                 r'https://www.mmafighting.com/2014/6/26/5843720/ufc-fight-night-43-weigh-in-video':'2014-06-28',
                 r'https://www.mmafighting.com/2014/1/2/5266576/ufc-fight-night-34-weigh-in-video':'2014-01-04'}
date_fix_df = pd_dict_to_df(date_fix_dict,['Url','Date'])
date_fix_df['Date'] = date_fix_df['Date'].map(lambda x: pd.to_datetime(np.datetime64(x)).date())
date_fix_df['Date'] = pd.to_datetime(date_fix_df['Date'])
mma_df = mma_df.rename(columns={'Date':'Date_temp'})
mma_df = mma_df.merge(date_fix_df,on='Url',how='left')
mma_df = fillna_from_other_col(mma_df,'Date_temp','Date')
mma_df['Date'] = pd.to_datetime(mma_df['Date'])
del mma_df['Date_temp']







#clean double spaces, trip whitespace, etc
mma_df['Fighter'] = mma_df['Fighter'].map(clean_fighter_name)

fighter_name_standardization_dict = create_fighter_name_standardization_dict()
mma_df['Fighter'] = mma_df['Fighter'].map(lambda x: replace_if_in_dict(x,fighter_name_standardization_dict))

##non_name_filter_list = ['Preliminary Card','Undercard','Pay-Per-View Bout','catchweight','Spike TV Fights','Preliminary Bouts','percent of purse',
##                        'Facebook prelims',r'pounds\. Main Card']
##mma_df['Fighter'] = mma_df['Fighter'].map(lambda x: re.sub())


#change column order
##mma_df = mma_df[['Organization','Event','Date','Fight Number','Result','Fighter','Opponent','Method','Round','Time','Url']]






###debug
##mma_df['len'] = mma_df['Fighter'].map(lambda x: len(x))
##mma_df = mma_df.sort_values(['len'],ascending=[False])



#todo: fix issue of nan's in fighter name


###debug
##mma_df = pd.read_csv(r'../output data/mma_data_mmafighting_weight.csv',low_memory=False)




#join missing data that we have manually filled in
mma_missing_df = pd.read_csv(r'../input data/mma_data_mmafighting_weight_missing.csv',low_memory=False)

mma_df = pd.concat([mma_df,mma_missing_df],ignore_index=True)

mma_df = mma_df.sort_values(['Date'], ascending=[False])




#remove duplicate entries
urls_to_remove_list = [r'https://www.mmafighting.com/2014/3/14/5509874/ufc-171-weigh-in-results-johny-hendricks-misses-weight-on-first',
                       r'https://www.mmafighting.com/2014/3/14/5510068/ufc-171-weigh-in-results-johny-hendricks-makes-weight-on-second',
                       r'https://www.mmafighting.com/2010/02/05/ufc-109-weigh-in-video']
mma_df = mma_df[~(mma_df['Url'].isin(urls_to_remove_list))]



mma_df.to_csv(r'../output data/mma_data_mmafighting_weight.csv',index=False)

























































