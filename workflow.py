import os
import json
import requests
from datetime import datetime
import praw


NOTION_API_KEY= 'secret_JycCdih4STec1Ba5OJqiBZdKlcdw8iMzBELV8bVCa6v'
REDDIT_CLIENT_ID = 'notion'
REDDIT_CLIENT_SECRET = '9Kps6gibdsm8dlImP9KioZoOIDOVaA'
REDDIT_USER_AGENT =  'V53TNiGno12ao4EfPItL2A'

DATABASE_KEY = '7cfa100e6ac044ceadc81330482e1b8d'
PAGE_KEY = '118ad8e790fa439bac32a5d78ff98ef3'

def create_notionpost(title, contenturl, actualurl):

    headers = {
        'Authorization': f"Bearer {NOTION_API_KEY}",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16',
    }
    data = { "parent": { "database_id": DATABASE_KEY }, "properties": { 
        "Title": {"title": [ { "text": { "content": title } } ] },
        #"score": { "number": score },
        #"subreddit": { "select": { "name": subreddit } },
        # "subreddit": { "rich_text": [ { "text": { "content": subreddit } } ] },
        "ContentURL": {"url": contenturl}, 
        "Link": {"url": actualurl}, 
        #"created": {"date" : {"start": created_date}}, 
    },  }

    requests.post('https://api.notion.com/v1/pages', headers=headers, json=data)


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
    post_data = {'filter':
                 {'and':
                  [
                      {"property": "Enabled", 
                       "checkbox" : {"equals":True}
                      }, 
                      {"property": "Source", 
                       {"equals" : "Reddit"}
                      }
                  ]
                 }
                }
    response  = requests.post(f'https://api.notion.com/v1/databases/{PAGE_KEY}/query', data=json.dumps(post_data), headers=headers).json()
    print(response)
    for i in response["results"]:
        subreddit=i['properties']['Title']['title'][0]['plain_text']
        mylist.append(subreddit)
    return mylist

def reddit_notion(subreddits):

    ## first: retrieve database and create searchable set 

    headers = {
        'Authorization': f"Bearer {NOTION_API_KEY}",
        'Notion-Version': '2021-08-16',
        'Content-Type': 'application/json',
    }
    response = requests.post(f'https://api.notion.com/v1/databases/{DATABASE_KEY}/query', headers=headers)
    myneeded = response.json()['results']
    myset = set()

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
        try:
            #sub=i['Title']
            #test_reddit = reddit.subreddit(sub).top("month", limit = 10)
            test_reddit = reddit.subreddit(subreddit).top("day", limit = 2)

            # test_reddit = reddit.multireddit("reactjs", "programming").top("day")
            # ml_subreddit = reddit.subreddit(mysub)
            for post in test_reddit:
                if ("https://www.reddit.com" + post.permalink) not in myset:
                    create_notionpost(post.title, post.url, ("https://www.reddit.com" + post.permalink))
        except:
            pass

targetlist = get_subreddits()
reddit_notion(targetlist)
