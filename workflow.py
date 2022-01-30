import os
import json
import requests
from datetime import datetime
import praw

NOTION_API_KEY= os.environ['NOTION_API_KEY']
REDDIT_CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
REDDIT_CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
REDDIT_USER_AGENT = os.environ['REDDIT_USER_AGENT']

DATABASE_KEY = os.environ['DATABASE_KEY']
PAGE_KEY = os.environ['PAGE_KEY']

def create_notionpost(title, contenturl, actualurl, series):

    headers = {
        'Authorization': f"Bearer {NOTION_API_KEY}",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16',
    }
    post_data = { "parent": { "database_id": DATABASE_KEY }, 
            "icon": {
        "type": "emoji",
        "emoji": '👾'},
        "properties": { 
        "Title": {"title": [ { "text": { "content": title } } ] },
        #"score": { "number": score },
        #"subreddit": { "select": { "name": subreddit } },
        # "subreddit": { "rich_text": [ { "text": { "content": subreddit } } ] },
        "ContentURL": {"url": contenturl}, 
        "Link": {"url": actualurl},
        "Tags": {"multi_select": [{"name": "👨‍👩‍👧‍👦 Community"}]},
        "Series":{"multi_select": [{"name": series}]}
        #"created": {"date" : {"start": created_date}}, 
    },  }

    requests.post(f'https://api.notion.com/v1/pages', headers=headers, data=json.dumps(post_data)).json()
    #if c.status_code != 200:
        #raise RuntimeError(c.content)
        #print(data)


## checks the notion block and retrieve subreddits in form of list of strings
mylist=[]
def get_subreddits():
    headers = {
        'Notion-Version': '2021-08-16',
        'Authorization': f"Bearer {NOTION_API_KEY}",
    }
    
    #response = requests.get(f'https://api.notion.com/v1/blocks/{PAGE_KEY}/children?page_size=10', headers=headers)
    #mylist = response.json()['results'][1]['bulleted_list_item']['text'][0]['plain_text'].split()
    #return mylist
    post_data = {"filter":
                 {"and":[
                    {"property": "Enabled", 
                       "checkbox" : {"equals":True}
                      }, 
                      {"property": "Source", 
                       "select": {"equals" : [{"name": "Reddit"}]}
                      }
                  ]
                 }
                }
    response  = requests.post(f'https://api.notion.com/v1/databases/{PAGE_KEY}/query', data=json.dumps(post_data), headers=headers).json()
    #print(response["results"])
    for i in response["results"]:
        subreddit=i['properties']['Title']['title'][0]['plain_text']
        mylist.append(subreddit)
    return mylist
    #print(mylist)
    
def reddit_notion(subreddits, series):

    ## first: retrieve database and create searchable set 

    headers = {
        'Authorization': f"Bearer {NOTION_API_KEY}",
        'Notion-Version': '2021-08-16',
        'Content-Type': 'application/json',
    }
    response = requests.post(f'https://api.notion.com/v1/databases/{DATABASE_KEY}/query', headers=headers)
    myneeded = response.json()['results']
    myset = set()
    #print(myneeded)

    for i in myneeded:
        try:
            myurl = i['properties']['Link']['url']
            myset.add(myurl)
        except:
            pass
    
    reddit = praw.Reddit(client_id= REDDIT_CLIENT_ID,
                        client_secret= REDDIT_CLIENT_SECRET,
                        user_agent= REDDIT_USER_AGENT)
    for subreddit in subreddits:
        #print(subreddit)
        try:
            #sub=i['Title']
            #test_reddit = reddit.subreddit(sub).top("month", limit = 10)
            test_reddit = reddit.subreddit(subreddit).top("day")
            #print(test_reddit)

            # test_reddit = reddit.multireddit("reactjs", "programming").top("day")
            # ml_subreddit = reddit.subreddit(mysub)
            for post in test_reddit:
                #print(post)
                if ("https://www.reddit.com" + post.permalink) not in myset:
                    #print(myset)
                    create_notionpost(post.title, post.url, ("https://www.reddit.com" + post.permalink), series)
        except:
            pass

#targetlist = get_subreddits()
targetlist = [http://feeds.bbci.co.uk/sport/0/formula1/rss.xml, 
              http://feeds2.feedburner.com/f1fanatic, 
              https://f1bythenumbers.com/feed/, 
              https://www.formula1.com/content/fom-website/en/latest.articlefeed.xml, 
              https://www.grandprix.com/rss.xml,
              https://www.racecar-engineering.com/feed/,
              https://wwww.autosport.com/rss/feed/f1,
              https://wwww.f1-fansite.com/feed,
              https://wwww.f1technical.net/rss/news.xml,
              https://wwww.fia.com/rss/press-release,
              https://wwww.planetf1.com/news/feed/,
              https://wwww.reddit.com/r/formula1/.rss,
              https://wwww.wtf.1.com/rss]

reddit_notion(targetlist, "Formula 1")

targetlist = [https://www.autosport.com/rss/feed/w]
reddit_notion(targetlist, "W Series")

targetlist = [https://wwww.autosport.com/rss/feed/f2]
reddit_notion(targetlist, "Formula 2")

targetlist = [https://wwww.autosport.com/rss/feed/f3]
reddit_notion(targetlist, "Formula 3")
