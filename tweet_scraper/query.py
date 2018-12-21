from multiprocessing.pool import Pool
import requests
import json
import random
import time

from functools import partial

from tweet_scraper.tweet import Tweet

import pandas as pd
import os

class tweetScraper:
    def __init__(self, proxy=None):
        self.HEADERS_LIST = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0', 'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0']
        self.proxy = proxy

    def query_single_status(self, url, retry=10):
        print("Querying {}".format(url))
        
        headers = {'User-Agent': random.choice(self.HEADERS_LIST)}

        try:
            if (self.proxy == None):
                response = requests.get(url, headers=headers)
            else:
                response = requests.get(url, headers=headers, proxies=self.proxy)

            html = response.text or ''

            status = Tweet().from_html(html, url.replace('https://twitter.com/statuses/', ''))

            return status
        except requests.exceptions.HTTPError as e:
            print('HTTPError {} while requesting "{}"'.format(
                e, url))
        except requests.exceptions.ConnectionError as e:
            print('ConnectionError {} while requesting "{}"'.format(
                e, url))
        except requests.exceptions.Timeout as e:
            print('TimeOut {} while requesting "{}"'.format(
                e, url))
        except json.decoder.JSONDecodeError as e:
            print('Failed to parse JSON "{}" while requesting "{}".'.format(
                e, url))
        except ValueError as e:
            print('Failed to parse JSON "{}" while requesting "{}"'.format(e, url))

        if retry > 0:
            print("Retrying... (Attempts left: {})".format(retry))
            return self.query_single_status(url, retry-1)
        
        print("Giving up.")
        return 0


    def query_status(self, statuses, poolsize=20):
        '''
        statuses: List
        Unique status_id to scrape from

        poolsize: int
        Size of pool. Bigger - the more instance of browser is opened
        '''

        url = "https://twitter.com/statuses/{}"
        no_statuses = len(statuses)

        if (poolsize > no_statuses):
            poolsize = no_statuses

        urls = [url.format(x) for x in statuses]
        all_statuses = pd.DataFrame(columns={'username', 'id', 'timestamp', 'tweettext', 'replies', 'retweets', 'likes', 'reply_to_id', 'response_type', 'reply_info'})

        try:
            pool = Pool(poolsize)

            for tweet_data in pool.imap_unordered(partial(self.query_single_status), urls):
                try:
                    status_series = tweet_data['status']
                    status_series['reply_info'] = tweet_data['retweets']

                    all_statuses = all_statuses.append(status_series, ignore_index=True)
                    print("Got {} status (1 new).".format(all_statuses.shape[0]))
                except Exception as e:
                    print(str(e))

        finally:
            pool.close()
            pool.join()

        return all_statuses
    
