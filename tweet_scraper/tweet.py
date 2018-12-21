from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup

class Tweet:
    def __init__(self):
        pass
        
    def from_soup(self, tweet):        
                
        response_type = 'tweet'
        reply_to_id  = None
        
        try:
            reply_to_id=tweet.find('div', 'tweet')['data-conversation-id'] or '0'
            response_type = 'reply'
        except:
            reply_to_id = None
            
        try:
            reply_to_id=tweet.find('a', 'QuoteTweet-link')['data-conversation-id'] or '0'
            response_type='quoted_retweet'
        except:
            pass
                
        tweettext=""
        username=""
        id=""
        timestamp=""
        
        try:
            tweettext=tweet.find('p', 'tweet-text').text or ""
        except:
            pass      
        
        try:
            tweettext = tweettext + " <quoted_status>" + tweet.find('div', 'QuoteTweet-text').text + "</quoted_status>"                           
        except:
            pass

        try:
            username=tweet.find('span', 'username').text or ""
        except:
            pass
        
        try:
            id = tweet['data-item-id'] or ""
        except:
            pass
        
        try:
            timestamp = tweet.find('span', '_timestamp')['data-time'] #this is gmt time
        except:
            pass
        
        replies='0'
        retweets='0'
        likes='0'
        html=""
        
        try:
            replies=tweet.find(
                    'span', 'ProfileTweet-action--reply u-hiddenVisually').find(
                        'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0'
        except:
            pass
        
        try:
            retweets=tweet.find(
                    'span', 'ProfileTweet-action--retweet u-hiddenVisually').find(
                        'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0'
        except:
            pass
        
      
        try:
            likes=tweet.find(
                    'span', 'ProfileTweet-action--favorite u-hiddenVisually').find(
                        'span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0'
        except:
            pass
        
        
        try:
            html=str(tweet.find('p', 'tweet-text')) or ""
        except:
            pass
        
        tweettext = tweettext.replace("…", "")

        if ("http" in tweettext):
            tweettext = tweettext.replace("http", " http")
            tweettext = tweettext.replace("  http", " http")

        if (reply_to_id == "0" or reply_to_id == id):
            response_type="tweet"
        
        ser = pd.Series({'username': username.strip('\@'), 'id': id, 'timestamp': timestamp, 'tweettext': tweettext, 'replies': int(replies), 'retweets': int(retweets), 'likes': int(likes), 'reply_to_id': reply_to_id, 'response_type': response_type})
        return ser
    

    def from_html(self, html, curr_id):
        soup = BeautifulSoup(html, "lxml")
        tweets = soup.find_all('div', 'tweet')
        retweets = []

        return_details = {}

        if tweets:
            for tweet in tweets:
                try:
                    status = self.from_soup(tweet)

                    if curr_id in status['id']:
                        return_details['status'] = status
                    else:
                        retweets.append(status)

                except AttributeError:
                    return_details['status'] = ''
                    return_details['retweets'] = ''
                    return return_details

        return_details['retweets'] = retweets
        return return_details