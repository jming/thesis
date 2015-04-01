import requests
from bs4 import BeautifulSoup
import os
import re
import time
import mechanize

from scrape_asdfriendly import save_posts

## the output fmt is:
## author,member_desc,avatar_img_link,group,num_bullets,num_posts,gender,location,interests,date_str,body_str,edit_str
##

#TODO may want to strip some of the text extracted

topic_re = re.compile('topic/(\d+)-')
page_re = re.compile('page=(\d+)')
cached_re = re.compile('cached-.+:[0-9]+:[0-9]')

def unspace(s): return s.replace(' ', '%20')

def scrape_asdforum(basedir="asdforum"):
    subforum_urls = [
    # 'http://www.asd-forum.org.uk/forum/index.php?/forum/15-diet-and-vitamins/',
    # 'http://www.asd-forum.org.uk/forum/index.php?/forum/16-herbalnatural-supplements/',
    # 'http://www.asd-forum.org.uk/forum/index.php?/forum/17-medication/',
    # 'http://www.asd-forum.org.uk/forum/index.php?/forum/18-other-interventions/',
    # 'http://www.asd-forum.org.uk/forum/index.php?/forum/19-vaccinations/',
    # 'http://www.asd-forum.org.uk/forum/index.php?/forum/20-miscellaneous/'
    # 'http://www.asd-forum.org.uk/forum/index.php?/forum/2-general-discussion/',
    # 'http://www.asd-forum.org.uk/forum/index.php?/forum/7-education/',
    # 'http://www.asd-forum.org.uk/forum/index.php?/forum/4-help-and-advice/',
    'http://www.asd-forum.org.uk/forum/index.php?/forum/25-asd-related-conditions/',
    'http://www.asd-forum.org.uk/forum/index.php?/forum/27-pda/',
    'http://www.asd-forum.org.uk/forum/index.php?/forum/28-add-and-adhd/',
    ]
    
    for url in subforum_urls:
        print "subforum", url
        savedir = os.path.join(basedir,url.split('/')[-2])
        if not os.path.isdir(savedir):
            os.mkdir(savedir)
        forum_page = 1
        browser = mechanize.Browser()
        browser.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0')]
        while True:
            time.sleep(0.5)
            print
            print "doing forum page", forum_page
            # soup = BeautifulSoup(requests.get(url).text, "lxml")
            browser.open(url)
            soup = BeautifulSoup(browser.response().read(), "lxml")
            topic_links = soup.find_all("a", class_="topic_title") # 
            print 'topics', len(topic_links)
            save_posts(topic_links,savedir,topic_re)
            # print 'nexts', soup.find('a')
            next_link = soup.find("a", rel="next")
            # print next_link
            if next_link is not None:
                url = unspace(next_link['href'])
                forum_page += 1
            else:
                break

scrape_asdforum('joy_asdforum2')

