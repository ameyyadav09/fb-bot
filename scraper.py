# code to scrape data from facebook for statistical analysis
"""
If you have ever done twitter sentiment analysis I am sure you must have obtained the tweets from twitter API.
Facebook also has a similar API and requires us to have an access token, without which our ip will be block after few requests. Now
these access tokens are of two types namely user access tokens and application access tokens. User access tokens
expire within an hour, that is why we will be using application access tokens. So, we will be creating a demo
application only for scraping and use that application ID and use the access token generated for that app which
will never expire. Once you signup as a developer and create a demo app, you can get your APP ID and APP SECRET
"""
app_id = "XXXXXXXXXXXXX"
app_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
access_token = app_id + "|" + app_secret
"""
Now we have our access token ready we can now access the facebook API without any interruption. To test it let's try to
fetch the data of time magazine.
"""
page_id = "time"

import requests
import json
"""
method to handle the exceptions
"""
import time
import datetime
def getAbsoluteContent(url):
    flag = True
    i = 1
    while flag:
        try:
            response = requests.get(url)
            flag = False
        except Exception:
            time.sleep(10)
            print("Attemp {} failed, will be retrying after 10 seconds".format(i))
            i+=1
    return response.content

"""
There are a bunch of parameters we can pass in an API call
limit: to restrict the number of posts in response
fields: To specify whats fields should be returned for each individual post. we can ask for, message, link, created_time, type, name, id
likes.limit(),comments.limit(), shares

###fields=message,link,created_time,type,name,id,likes.limit(1).summary(true),comments.limit(1).summary(true),shares
"""

def fbPageData(page_id, access_token, n_counts = 10):
    params = "fields=message,link,created_time,type,name,id,\
                likes.limit(1).summary(true),\
                comments.limit(1).summary(true),\
    shares&limit={}&access_token={}".format(n_counts, access_token)
    url = "https://graph.facebook.com/v2.4/{}/feed/?{}".format(page_id, params)
    data = json.loads(getAbsoluteContent(url))
    return data
    # return json.dumps(data, indent = 4, sort_keys = True)

# dem = fbPageData(page_id, access_token)
# print(len(dem["data"]))

def processPost(post):
    post_id = post['id']
    post_type = post['type'].encode('ascii', 'ignore')
    n_likes = 0 if 'likes' not in post.keys() else post['likes']['summary']['total_count']
    n_comments = 0 if 'comments' not in post.keys() else post['comments']['summary']['total_count']
    n_shares = 0 if 'shares' not in post.keys() else post['shares']['count']
    post_message = '' if 'message' not in post.keys() else post['message'].encode('ascii', 'ignore')
    link_name = '' if 'name' not in post.keys() else post['name'].encode('ascii', 'ignore')
    post_link = '' if 'link' not in post.keys() else post['link'].encode('ascii', 'ignore')
    post_published = datetime.datetime.strptime(post['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
    post_published = post_published + datetime.timedelta(hours=-5)
    post_published = post_published.strftime('%Y-%m-%d %H:%M:%S')
    return [post_id, post_message, n_likes, n_comments, n_shares, link_name, post_type, post_link, post_published]
# print(processPost(dem))


def scrapePosts(page_id, access_token):
    flag = True
    i = 1
    with open ("D:/times_fd_data.csv", "w+") as fp:
        posts = fbPageData(page_id, access_token, 100)
        while flag:
            if i % 10 == 0:
                print ("Scraped {} Posts".format(i))
            for post in posts["data"]:
                temp = [*map(lambda x: str(x), processPost(post))]
                fp.write(",".join(temp))
                fp.write("\n")
            if 'paging' in posts.keys():
                post = json.loads(getAbsoluteContent(posts['paging']['next']))
            else:
                flag = False
            i += 1
            print ("we have scraped {} posts.".format(i*100))

if __name__ == "__main__":
    scrapePosts(page_id, access_token)