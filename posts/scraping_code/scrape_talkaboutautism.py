#import requests
import mechanize
from bs4 import BeautifulSoup
import os
import re
import time

from scrape_asdfriendly import textify_contents, one_line

# TODO: for links that also have text i think i generally put the link not the text, not
# sure if that's right...

threadid_re = re.compile('threadId=(\d+)')
page_re = re.compile('page=(\d+)')

def unspace(s): return s.replace(' ', '%20')

def scrape_talkaboutautism(savedir="talkaboutautism"):
    # just the medical/health subforum for now
    # base_url = "http://www.talkaboutautism.org.uk/page/forums/medicalandhealth/index.cfm"
    # base_url = "http://www.talkaboutautism.org.uk/page/forums/diagnosis/index.cfm"

    urls = ["http://www.talkaboutautism.org.uk/page/forums/medicalandhealth/index.cfm", 
            "http://www.talkaboutautism.org.uk/page/forums/diagnosis/index.cfm"]

    for url in urls:
        base_url = url
    # url = base_url
        forum_page = 1
        browser = mechanize.Browser()
        browser.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0')]
        while True:
            time.sleep(0.5)
            print
            print "doing forum page", forum_page
            #soup = BeautifulSoup(requests.get(url).text, "lxml")
            browser.open(url)
            soup = BeautifulSoup(browser.response().read(), "lxml")
            topics = soup.find_all("td", class_="tdTopic") # 
            curr_post_links = [topic.a for topic in topics] #soup.find_all("a", href=re.compile("forumid="))
            save_posts(curr_post_links,base_url,savedir,browser)
            next_img = soup.find("img", title="Next Page")
            next_link = next_img.find_parent("a")
            next_page = page_re.search(next_link['href'])
            if next_page is not None and int(next_page.groups()[0]) > forum_page:
                forum_page = int(next_page.groups()[0])
                url = base_url + unspace(next_link['href'])
            else:
                break

def save_posts(links, base_url, savedir, browser):
    for link in links:
        current_page = 1 # not always in url, but implied
        print "doing", base_url + unspace(link['href'])
        #soup = BeautifulSoup(requests.get(base_url + link['href']).text, "lxml")
        browser.open(base_url + unspace(link['href']))
        soup = BeautifulSoup(browser.response().read(), "lxml")
        threadid = threadid_re.search(link['href'])
        assert threadid is not None
        page_title = soup.find('h1')
        assert page_title is not None
        # get time we scraped
        ct = time.localtime()
        curr_timestamp = "%d-%d-%d-%d:%d:%d" % (ct.tm_year, ct.tm_mon, ct.tm_mday, ct.tm_hour, ct.tm_min, ct.tm_sec)
        did_topic = False
        with open(os.path.join(savedir,threadid.groups()[0]+"_"+curr_timestamp), "w+") as f:
            # the first line will be metadata
            f.write(("%s|%s\n" % (base_url+unspace(link['href']), one_line(page_title.text))).encode('utf8'))
            while True:
                if not did_topic: # topic post is repeated on every page
                    # get the topic post
                    topic_table = soup.find_all(id="topicTable")
                    assert len(topic_table) == 1
                    topic_rows = topic_table[0].find_all(class_="topicRow")
                    assert len(topic_rows) == 1
                    did_topic = True
                else:
                    topic_rows = []
                thread_table = soup.find_all(id="threadTable")
                if len(thread_table) != 1:
                    break
                assert len(thread_table) == 1
                # add the rest of the posts so we can do them all at once
                topic_rows.extend(thread_table[0].find_all(class_="topicRow"))
                for row in topic_rows:
                    # print 'row', row
                    member_td = row.find(class_="tdMember")
                    assert member_td is not None
                    try:
                        member_num = one_line(member_td.a["name"]) if member_td.a is not None else ""
                    except KeyError as ex: # sometimes href, sometimes name
                        member_num = one_line(member_td.a["href"]) if member_td.a is not None else ""
                    member_divs = member_td.find_all("div", recursive=False)
                    # print len(member_divs)
                    # assert len(member_divs) == 3
                    author = one_line(member_divs[0].a.text)
                    member_ref = one_line(member_divs[0].a["href"])
                    try:
                        avatar = one_line(member_divs[1].img["src"])
                    except TypeError as ex: # not everyone has an avatar
                        avatar = ""
                    date_str = one_line(member_divs[2].text)  
                    # print 'row2', row
                    msg_div = row.find(class_="tdMessage")
                    # print 'msg_div', msg_div
                    print author, "'s post"
                    body_str, member_desc, quote, quote_url = get_msg_body(msg_div)
                    assert len(body_str) > 0 or len(quote) > 0
                    # stuff we don't have on the forum pages here
                    group = "N/A"
                    num_bullets = "N/A"
                    num_posts = "N/A"
                    gender = "N/A"
                    location = "N/A"
                    interests = "N/A"
                    edit = "N/A"
                    citation_str = "N/A"
                    row = unicode("%s" % "|".join([author,member_desc,avatar,group,unicode(num_bullets),
                                            unicode(num_posts), gender, location, interests,
                                            date_str, body_str, edit,member_num, member_ref, quote, quote_url, citation_str]))#.encode('utf8')
                    assert isinstance(row, unicode), type(row)
                    assert "\n" not in row
                    f.write(unicode("%s\n" % row).encode('utf8'))

                # there's always a next button, unfortunately
                next_img = soup.find("img", title="Next Page")
                next_link = next_img.find_parent("a")
                next_page = page_re.search(next_link['href'])
                if next_page is not None and int(next_page.groups()[0]) > current_page:
                    current_page = int(next_page.groups()[0])
                    #soup = BeautifulSoup(requests.get(base_url + next_link['href']).text, "lxml")
                    print "looking for more posts at:", base_url + unspace(next_link['href'])
                    browser = mechanize.Browser()
                    browser.open(base_url + unspace(next_link['href']))
                    soup = BeautifulSoup(browser.response().read(), "lxml")
                    #print soup
                else:
                    break

def get_msg_body(content_div):
    # print 'content_div', content_div
    member_desc = one_line(content_div.find("strong").text)
    # member_desc = ''
    body_ps = content_div.find_all("p")
    if len(body_ps) > 0:
        body = " ".join([textify_contents(bp.contents) for bp in body_ps])
        quote = ""
        quote_url = ""
    elif content_div.find("span", class_="postbody") is not None and content_div.find("td", class_="quote") is not None: # could be a quote i think
        postbody = content_div.find("span", class_="postbody")
        assert postbody is not None
        quote_url = one_line(postbody.a["href"])
        quote_td = content_div.find("td", class_="quote")
        assert quote_td is not None 
        quote = textify_contents(quote_td)
        body = ""
    else: # sometimes the stuff is not in p tags
        quote = ""
        quote_url = ""
        body = textify_contents(content_div.contents)
        
    return body, member_desc, quote, quote_url

scrape_talkaboutautism('joy_talkaboutautism')