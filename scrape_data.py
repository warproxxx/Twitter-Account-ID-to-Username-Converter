from tweet_scraper import tweetScraper
import pandas as pd

df = pd.read_csv('scrape_me.csv', header=None)

t = tweetScraper()
at_once = 500

for i in range(at_once, df.shape[0], at_once):
    currStatus = list(df[0].values[i-at_once:i])
    new_df = t.query_status(currStatus, poolsize=50)
    new_df.to_csv('status_data/curr_{}_{}.csv'.format(i-at_once,i), index=False)
