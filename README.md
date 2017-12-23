<h1>MMA Data</h1>

__Goal:__ Gather MMA data from as many sources as possible.

__Status:__ FightMetric.com and UFC.com data scraped. (Only matchup data from UFC.com currently, need to add results.) Also, unverified weight-cutting data from twitter user @dimspace.

__Todo:__ UFC.com results data, Sherdog.com data, confirm accuracy of weight-cutting data, join all data and cross check.



__Scripts:__
* _mma_data_fightmetric.py_ - scrapes FightMetric.com (fight results)
	* _Input:_ none
	* _Output:_ mma_data_fightmetric.csv

* _mma_data_ufc.py_ - scrapes UFC.com "printFightCard" for matchup data
	* _Input:_ mma_data_ufc_missing.csv - missing data from UFC120
	* _Output:_ mma_data_ufc.csv

* _mma_data_weight_cutting_join.py_ - joins FightMetric with weight-cutting data
	* _Input:_ mma_data_weight_cutting.csv (from @dimspace), mma_data_fightmetric.csv
	* _Output:_ mma_data_weight_cutting_joined.csv



__Python Version:__ Anaconda2-5.0.0 (Python 2.7) 64bit
