import os, sys
sys.path.append(os.path.dirname(__file__))
from mma_data_library import *










### #############################################################################
### check the ufc events in the mmafighting.com weight results
### #############################################################################
##
##mma_df = pd.read_csv(r'../output data/mma_data_mmafighting_weight.csv',low_memory=False)
##
##filter_list = ['Strikeforce','Bellator','Invicta','WEC','Mayweather','Canelo','Pacquiao','PFL','Professional Fighters League','WSOF','World Series of Fighting','ONE FC']
##def filter_ufc(x):
##    result = 'y'
##    for myfilter in filter_list:
##        if str.find(x,myfilter) != -1:
##            result = 'n'
##            break
##    return result
##
##mma_df['UFC'] = mma_df['Event'].map(filter_ufc)
##mma_df = mma_df[mma_df['UFC']=='y']
##
##
##
##ufc_df = pd.read_csv(r'../output data/mma_data_ufc.csv',low_memory=False)
##
##
##
##mma_df['Date'] = pd.to_datetime(mma_df['Date'])
##ufc_df['Date'] = pd.to_datetime(ufc_df['Date'])
##
##mma_df['Dummy_mmafighting'] = 1
##ufc_df['Dummy'] = 1
##
##
##mma_df = mma_df[['Date','Event','Url','Dummy_mmafighting']].drop_duplicates()
##ufc_df = ufc_df[['Date','Event','Url','Dummy']].drop_duplicates()
##
##mma_df = mma_df.rename(columns={'Event':'Event_mmafighting','Url':'Url_mmafighting'})
##
##
##mma_df = mma_df.merge(ufc_df,on='Date',how='outer')
##mma_df = mma_df.sort_values('Date',ascending=False)
##
##mma_df['Cross Check'] = mma_df['Dummy_mmafighting'] == mma_df['Dummy']
##
##
##
##mma_df.to_clipboard(index=False)
##
##
### ##################################################################################







### ##################################################################################
###many of the fighters have their nicknames included from mmafighting.com
###check vs ufc dataset to create dictionary of alternative names so that
###we can ultimately join by ['Fighter','Date']
### ##################################################################################
##
##ufc_df = pd.read_csv(r'../output data/mma_data_ufc.csv',low_memory=False)
##mma_df = pd.read_csv(r'../output data/mma_data_mmafighting_weight.csv',low_memory=False)
##
##def force_datetime(x):
##    try:
##        x = pd.to_datetime(np.datetime64(pd.to_datetime(x).strftime('%Y-%m-%d')))
##    except:
##        print str(traceback.format_exc())
##        d=1
##    return x
##
##ufc_df['Date'] = ufc_df['Date'].map(force_datetime)
##mma_df['Date'] = mma_df['Date'].map(force_datetime)
##
##ufc_df['Date'] = pd.to_datetime(ufc_df['Date'])
##mma_df['Date'] = pd.to_datetime(mma_df['Date'])
##
##ufc_df = ufc_df.sort_values('Date',ascending=False)
##mma_df = mma_df.sort_values('Date',ascending=False)
##
##print ufc_df['Date'].unique()
##print mma_df['Date'].unique()
##
##filter_list = ['Strikeforce','Bellator','Invicta','WEC','Mayweather','Canelo','Pacquiao','PFL','Professional Fighters League','WSOF','World Series of Fighting','ONE FC']
##def filter_ufc(x):
##    result = 'y'
##    for myfilter in filter_list:
##        if str.find(x,myfilter) != -1:
##            result = 'n'
##            break
##    return result
##
##mma_df['UFC'] = mma_df['Event'].map(filter_ufc)
##mma_df = mma_df[mma_df['UFC']=='y']
##
##
##
##ufc_df['Dummy'] = 1
##
##mma_df = mma_df.merge(ufc_df[['Date','Event','Url']].drop_duplicates(),on='Date',how='outer')
##mma_df = mma_df.merge(ufc_df[['Fighter','Dummy']].drop_duplicates(),on='Fighter',how='outer')
##
##
##
##ufc_df[['Fighter']].drop_duplicates().to_clipboard(index=False)
##mma_df.to_clipboard(index=False)
##
##
### ##################################################################################







### ##################################################################################
###there are many variants of names which come from extra spaces, unicode conversion,
###nicknames, alternate spellings, etc
###generate a table of master_fighter_name and alternative_name's
### ##################################################################################
##
##ufc_df = pd.read_csv(r'../output data/mma_data_ufc.csv',low_memory=False)
##mma_df = pd.read_csv(r'../output data/mma_data_mmafighting_weight.csv',low_memory=False)
##fightmetric_df = pd.read_csv(r'../output data/mma_data_fightmetric.csv',low_memory=False)
##sherdog_df = pd.read_csv(r'../output data/mma_data_sherdog.csv',low_memory=False)
##
##
##mma_df = mma_df.dropna(subset=['Fighter'])
##
##
##
##ufc_df['Fighter'] = ufc_df['Fighter'].map(clean_fighter_name)
##mma_df['Fighter'] = mma_df['Fighter'].map(clean_fighter_name)
##fightmetric_df['Fighter'] = fightmetric_df['Fighter'].map(clean_fighter_name)
##sherdog_df['Fighter'] = sherdog_df['Fighter'].map(clean_fighter_name)
##
##
##fighter_name_standardization_dict = create_fighter_name_standardization_dict()
##ufc_df['Fighter'] = ufc_df['Fighter'].map(lambda x: replace_if_in_dict(x,fighter_name_standardization_dict))
##mma_df['Fighter'] = mma_df['Fighter'].map(lambda x: replace_if_in_dict(x,fighter_name_standardization_dict))
##fightmetric_df['Fighter'] = fightmetric_df['Fighter'].map(lambda x: replace_if_in_dict(x,fighter_name_standardization_dict))
##sherdog_df['Fighter'] = sherdog_df['Fighter'].map(lambda x: replace_if_in_dict(x,fighter_name_standardization_dict))
##
##
###make combined column of all fighter names
##fighters_df = pd.concat([ufc_df[['Fighter']],mma_df[['Fighter']],fightmetric_df[['Fighter']],sherdog_df[['Fighter']]],ignore_index=True)
##fighters_df = fighters_df.drop_duplicates()
##
##
##
###pivot urls to look up fighters
##ufc_df['Dummy'] = 'Url'
##ufc_df = safe_reset_index(ufc_df[['Fighter','Url','Dummy']].pivot_table('Url','Fighter','Dummy',aggfunc= lambda x: pivot_concat_helper_function(x,delimiter=', ')))
##
##mma_df['Dummy'] = 'Url'
##mma_df = safe_reset_index(mma_df[['Fighter','Url','Dummy']].pivot_table('Url','Fighter','Dummy',aggfunc= lambda x: pivot_concat_helper_function(x,delimiter=', ')))
##
##fightmetric_df['Dummy'] = 'Url'
##fightmetric_df = safe_reset_index(fightmetric_df[['Fighter','Url','Dummy']].pivot_table('Url','Fighter','Dummy',aggfunc= lambda x: pivot_concat_helper_function(x,delimiter=', ')))
##
##sherdog_df['Dummy'] = 'Url'
##sherdog_df = safe_reset_index(sherdog_df[['Fighter','Url','Dummy']].pivot_table('Url','Fighter','Dummy',aggfunc= lambda x: pivot_concat_helper_function(x,delimiter=', ')))
##
##
##
##
##ufc_df['Fighter_UFC'] = ufc_df['Fighter']
##mma_df['Fighter_MMAFighting'] = mma_df['Fighter']
##fightmetric_df['Fighter_FightMetric'] = fightmetric_df['Fighter']
##sherdog_df['Fighter_Sherdog'] = sherdog_df['Fighter']
##
##
##ufc_df = ufc_df.rename(columns={'Url':'Url_UFC'})
##mma_df = mma_df.rename(columns={'Url':'Url_MMAFighting'})
##fightmetric_df = fightmetric_df.rename(columns={'Url':'Url_FightMetric'})
##sherdog_df = sherdog_df.rename(columns={'Url':'Url_Sherdog'})
##
##
###join each dataset
##
####def force_datetime(x):
####    try:
####        x = pd.to_datetime(np.datetime64(pd.to_datetime(x).strftime('%Y-%m-%d')))
####    except:
####        print str(traceback.format_exc())
####        d=1
####    return x
####
####ufc_df['Date'] = ufc_df['Date'].map(force_datetime)
####mma_df['Date'] = mma_df['Date'].map(force_datetime)
####
####ufc_df['Date'] = pd.to_datetime(ufc_df['Date'])
####mma_df['Date'] = pd.to_datetime(mma_df['Date'])
####fightmetric_df['Date'] = pd.to_datetime(fightmetric_df['Date'])
####sherdog_df['Date'] = pd.to_datetime(sherdog_df['Date'])
##
##
##fighters_df = fighters_df.merge(ufc_df,on='Fighter',how='left')
##fighters_df = fighters_df.merge(mma_df,on='Fighter',how='left')
##fighters_df = fighters_df.merge(fightmetric_df,on='Fighter',how='left')
##fighters_df = fighters_df.merge(sherdog_df,on='Fighter',how='left')
##
##
##fighters_df['Last Name'] = fighters_df['Fighter'].map(lambda x: x.split()[-1])
##
##fighters_df = fighters_df[['Last Name','Fighter','Fighter_UFC','Fighter_MMAFighting','Fighter_FightMetric','Fighter_Sherdog','Url_UFC','Url_MMAFighting','Url_FightMetric','Url_Sherdog']]
##
##fighters_df = fighters_df.sort_values(['Last Name','Fighter'],ascending=[True,True])
##
##
##fighters_df.to_clipboard(index=False)










# ##################################################################################
#now that we have a fighter name standardization table
# ##################################################################################

ufc_df = pd.read_csv(r'../output data/mma_data_ufc.csv',low_memory=False)
mma_df = pd.read_csv(r'../output data/mma_data_mmafighting_weight.csv',low_memory=False)
fightmetric_df = pd.read_csv(r'../output data/mma_data_fightmetric.csv',low_memory=False)
sherdog_df = pd.read_csv(r'../output data/mma_data_sherdog.csv',low_memory=False)


mma_df = mma_df.dropna(subset=['Fighter'])


ufc_df['Date'] = pd.to_datetime(ufc_df['Date'])
mma_df['Date'] = pd.to_datetime(mma_df['Date'])
fightmetric_df['Date'] = pd.to_datetime(fightmetric_df['Date'])
sherdog_df['Date'] = pd.to_datetime(sherdog_df['Date'])



ufc_df['Fighter'] = ufc_df['Fighter'].map(clean_fighter_name)
mma_df['Fighter'] = mma_df['Fighter'].map(clean_fighter_name)
fightmetric_df['Fighter'] = fightmetric_df['Fighter'].map(clean_fighter_name)
sherdog_df['Fighter'] = sherdog_df['Fighter'].map(clean_fighter_name)


#copy of a slice issue
ufc_df = ufc_df.copy()
mma_df = mma_df.copy()
fightmetric_df = fightmetric_df.copy()
sherdog_df = sherdog_df.copy()


fighter_name_standardization_dict = create_fighter_name_standardization_dict()
ufc_df['Fighter'] = ufc_df['Fighter'].map(lambda x: replace_if_in_dict(x,fighter_name_standardization_dict))
mma_df['Fighter'] = mma_df['Fighter'].map(lambda x: replace_if_in_dict(x,fighter_name_standardization_dict))
fightmetric_df['Fighter'] = fightmetric_df['Fighter'].map(lambda x: replace_if_in_dict(x,fighter_name_standardization_dict))
sherdog_df['Fighter'] = sherdog_df['Fighter'].map(lambda x: replace_if_in_dict(x,fighter_name_standardization_dict))






#make combined column of all fighter names
fighters_df = pd.concat([ufc_df[['Fighter','Date']].drop_duplicates(),
                         mma_df[['Fighter','Date']].drop_duplicates(),
                         fightmetric_df[['Fighter','Date']].drop_duplicates(),
                         sherdog_df[['Fighter','Date']].drop_duplicates()],
                                                        ignore_index=True)
fighters_df = fighters_df.drop_duplicates()



#pivot urls to look up fighters
ufc_df['Dummy'] = 'Event'
ufc_df = safe_reset_index(ufc_df[['Date','Fighter','Event','Dummy']].pivot_table('Event',['Date','Fighter'],'Dummy',aggfunc= lambda x: pivot_concat_helper_function(x,delimiter=', ')))

mma_df['Dummy'] = 'Event'
mma_df = safe_reset_index(mma_df[['Date','Fighter','Event','Dummy']].pivot_table('Event',['Date','Fighter'],'Dummy',aggfunc= lambda x: pivot_concat_helper_function(x,delimiter=', ')))

fightmetric_df['Dummy'] = 'Event'
fightmetric_df = safe_reset_index(fightmetric_df[['Date','Fighter','Event','Dummy']].pivot_table('Event',['Date','Fighter'],'Dummy',aggfunc= lambda x: pivot_concat_helper_function(x,delimiter=', ')))

sherdog_df['Dummy'] = 'Event'
sherdog_df = safe_reset_index(sherdog_df[['Date','Fighter','Event','Dummy']].pivot_table('Event',['Date','Fighter'],'Dummy',aggfunc= lambda x: pivot_concat_helper_function(x,delimiter=', ')))




ufc_df['Fighter_UFC'] = ufc_df['Fighter']
mma_df['Fighter_MMAFighting'] = mma_df['Fighter']
fightmetric_df['Fighter_FightMetric'] = fightmetric_df['Fighter']
sherdog_df['Fighter_Sherdog'] = sherdog_df['Fighter']


ufc_df = ufc_df.rename(columns={'Event':'Event_UFC'})
mma_df = mma_df.rename(columns={'Event':'Event_MMAFighting'})
fightmetric_df = fightmetric_df.rename(columns={'Event':'Event_FightMetric'})
sherdog_df = sherdog_df.rename(columns={'Event':'Event_Sherdog'})


#join each dataset

##def force_datetime(x):
##    try:
##        x = pd.to_datetime(np.datetime64(pd.to_datetime(x).strftime('%Y-%m-%d')))
##    except:
##        print str(traceback.format_exc())
##        d=1
##    return x
##
##ufc_df['Date'] = ufc_df['Date'].map(force_datetime)
##mma_df['Date'] = mma_df['Date'].map(force_datetime)
##
##ufc_df['Date'] = pd.to_datetime(ufc_df['Date'])
##mma_df['Date'] = pd.to_datetime(mma_df['Date'])
##fightmetric_df['Date'] = pd.to_datetime(fightmetric_df['Date'])
##sherdog_df['Date'] = pd.to_datetime(sherdog_df['Date'])


fighters_df = fighters_df.merge(ufc_df,on=['Date','Fighter'],how='left')
fighters_df = fighters_df.merge(mma_df,on=['Date','Fighter'],how='left')
fighters_df = fighters_df.merge(fightmetric_df,on=['Date','Fighter'],how='left')
fighters_df = fighters_df.merge(sherdog_df,on=['Date','Fighter'],how='left')


fighters_df['Last Name'] = fighters_df['Fighter'].map(lambda x: x.split()[-1])

fighters_df = fighters_df[['Date','Last Name','Fighter','Fighter_UFC','Fighter_MMAFighting','Fighter_FightMetric','Fighter_Sherdog','Event_UFC','Event_MMAFighting','Event_FightMetric','Event_Sherdog']]

fighters_df = fighters_df.sort_values(['Date','Event_UFC','Last Name','Fighter'],ascending=[False,True,True,True])


fighters_df.to_clipboard(index=False)







