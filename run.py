from newsapi import NewsApiClient
from datetime import datetime, timedelta
import pickledb
import praw
import configparser
import schedule
from time import sleep

config = configparser.ConfigParser()
config.read('conf.ini')
reddit_user = config['REDDIT']['reddit_user']
reddit_pass = config['REDDIT']['reddit_pass']
client_id = config['REDDIT']['client_id']
client_secret = config['REDDIT']['client_secret']
target_subreddit = config['REDDIT']['target_subreddit']
test_mode = int(config['REDDIT']['test_mode'])
api_key = config['NEWS']['api_key']
query = config['NEWS']['query']
days = int(config['NEWS']['days'])
sources = config['NEWS']['sources']
interval = int(config['SETTINGS']['interval'])

db = pickledb.load('data.db', False)
newsapi = NewsApiClient(api_key=api_key)


reddit = praw.Reddit(
    username=reddit_user,
    password=reddit_pass,
    client_id=client_id,
    client_secret=client_secret,
    user_agent='News Poster (by u/impshum)'
)


class C:
    W, G, R, P, Y, C = '\033[0m', '\033[92m', '\033[91m', '\033[95m', '\033[93m', '\033[36m'


if test_mode:
    t = f'{C.R}TEST MODE{C.Y}'
else:
    t = ''

print(f"""{C.Y}
╔╗╔╔═╗╦ ╦╔═╗  ╔═╗╔═╗╔═╗╔╦╗╔═╗╦═╗
║║║║╣ ║║║╚═╗  ╠═╝║ ║╚═╗ ║ ║╣ ╠╦╝  {t}
╝╚╝╚═╝╚╩╝╚═╝  ╩  ╚═╝╚═╝ ╩ ╚═╝╩╚═  {C.C}v1.0{C.W}

{C.P}Checking every {interval} hours{C.W}
""")


def do_db(title, url):
    if test_mode:
        return True
    if not db.exists(title):
        db.set(title, url)
        db.dump()
        return True
    else:
        return False


def runner():
    now = datetime.now()
    then = now - timedelta(days=days)
    now = now.strftime('%Y-%m-%d')
    then = then.strftime('%Y-%m-%d')
    all_articles = newsapi.get_everything(q=query,
                                          sources=sources,
                                          from_param=then,
                                          to=now,
                                          language='en')

    for article in all_articles['articles']:
        title = article['title']
        url = article['url']
        if do_db(title, url):
            if not test_mode:
                reddit.subreddit(target_subreddit).submit(title=title, url=url)
            print(f'{C.G}{title}{C.W}')
        else:
            print(f'{C.R}{title}{C.W}')


def main():
    runner()
    if not test_mode:
        schedule.every(interval).hours.do(runner)
        while True:
            schedule.run_pending()
            sleep(1)


if __name__ == '__main__':
    main()
