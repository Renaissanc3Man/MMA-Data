<h1>MMA Data</h1>

__Goal:__ Gather MMA data from as many sources as possible. Join/crosscheck data and use to gain insights.

__Status:__ FightMetric.com, UFC.com, Sherdog.com (UFC, Pride, WEC, Strikeforce), Wikipedia data scraped. (Only matchup data from UFC.com currently, need to add results.) Weight-cutting data from twitter user @dimspace and from MMAFighting.com.

__Todo:__ UFC.com results data, Sherdog.com data, confirm accuracy of weight-cutting data (add MMAFighting.com weight data), join all data and cross check. Fix nan's in mmafighting weight dataset



__Libraries:__
* __mma_data_library.py__ - Library of functions reused across scripts
	* _Input:_ mma_data_fighter_name_standardization.csv
	* _Output:_ none
	* _Key Functions:_ Standardize fighter names, Division to Weightclass conversion

__Web Scraping Scripts:__
* __mma_data_fightmetric.py__ - scrapes FightMetric.com (fight results)
	* _Input:_ none
	* _Output:_ mma_data_fightmetric.csv

* __mma_data_ufc.py__ - scrapes UFC.com "printFightCard" for matchup data
	* _Input:_ mma_data_ufc_missing.csv - missing data from UFC120
	* _Output:_ mma_data_ufc.csv

* __mma_data_sherdog.py__ - scrapes Sherdog.com (fight results for UFC, Pride, WEC, Strikeforce)
	* _Input:_ none
	* _Output:_ mma_data_sherdog.csv

* __mma_data_wikipedia.py__ - scrapes Wikipedia (fight results)
	* _Input:_ none
	* _Output:_ mma_data_wikipedia.csv

* __mma_data_mmafighting_weight.py__ - scrapes MMAFighting.com for weigh-in results
	* _Input:_ mma_data_fightmetric.csv, mma_data_ufc.csv, mma_data_sherdog.csv (fighter names)
	* _Output:_ mma_data_mmafighting_weight.csv

__Data Joining Scripts:__
* __mma_data_weight_cutting_join.py__ - joins FightMetric with weight-cutting data
	* _Input:_ mma_data_weight_cutting.csv (from @dimspace), mma_data_fightmetric.csv
	* _Output:_ mma_data_weight_cutting_joined.csv

* __mma_data_validation.py__ - playground for cross checking data
	* _Input:_ mma_data_event_standardization.csv, mma_data_fighter_name_standardization.csv, all output files
	* _Output:_ temp dataframes to clipboard



__Python Version:__ Anaconda2-5.0.0 (Python 2.7) 64bit