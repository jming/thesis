import requests
import bs4
from bs4 import BeautifulSoup
import os
import re
import time

from scrape_asdfriendly import textify_contents, one_line

topic_re = re.compile('t=(\d+)')
num_posts_re = re.compile("posts")
cached_re = re.compile('cached-.+:[0-9]+:[0-9]')

def scrape_autismweb(savedir="autismweb"):
    # just the medical/health subforum for now
    base_url = "http://www.autismweb.com/forum"
    urls = ["/viewforum.php?f=4", "/viewforum.php?f=7"]
    for u in urls:
        url = base_url + u
        if u == "/viewforum.php?f=4":
            page = 266
        else:
            page = 1
        # doing this so i don't have to start all over again
        # url = base_url + "/viewforum.php?f=4&start=16453"
        # page = 330
        while True:
            time.sleep(0.5)
            print "doing forum page", page
            soup = BeautifulSoup(requests.get(url).text, "lxml")
            curr_post_links = soup.find_all("a", class_="topictitle")
            save_posts(curr_post_links,base_url, savedir,topic_re)
            next_link = soup.find("a", text="Next")
            if next_link is not None and next_link.has_attr('href'):
                url = base_url + next_link['href'][1:] # get rid of the dot
                page += 1
            else:
                break

def save_posts(links, base_url, savedir, topic_re):
    for link in links:
        print "doing", link['href']
        topic = topic_re.search(link['href'])
        assert topic is not None
        soup = BeautifulSoup(requests.get(base_url + link['href'][1:]).text, "lxml")
        page_title = soup.find('a', class_="titles")
        poster = ""
        num_poster_posts = 0
        #assert page_title is not None
        if page_title is None: # missing links
            print "skipping!!!"
            continue
        # get time we scraped
        ct = time.localtime()
        curr_timestamp = "%d-%d-%d-%d:%d:%d" % (ct.tm_year, ct.tm_mon, ct.tm_mday, ct.tm_hour, ct.tm_min, ct.tm_sec)
        with open(os.path.join(savedir,topic.groups()[0]+"_"+curr_timestamp), "w+") as f:
            # the first line will be metadata
            f.write(("%s|%s\n" % (link['href'], one_line(page_title.text))).encode('utf8'))
            # get total number of posts
            subtitle_td = soup.find("td", class_="gensmall", nowrap="nowrap", text=num_posts_re)
            if subtitle_td is not None:
            #assert subtitle_div is not None
                if subtitle_td.span is not None:
                    replies = subtitle_td.span.text
                else:
                    replies = subtitle_td.text
                try:
                    num_replies = int(replies.split()[1].replace(',',''))
                except ValueError as ex:
                    if replies.split()[0] == "No":
                        num_replies = 0
                    else:
                        raise ex
            else:
                num_replies = 1
            num_done = 0
            while True:
                # get all the posts
                posts = soup.find_all("table", class_="tablebg")[2:-2]
                for post in posts:
                    post_trs = post.find_all("tr", class_=["row1","row2"], recursive=False)
                    # should be two
                    assert len(post_trs) == 3, post_trs
                    author = one_line(post_trs[0].find("b", class_="postauthor").text)
                    print author, "'s post"
                    date_str = one_line(post_trs[0].find("div", style="float: right;").text)
                    if poster == "":
                        poster = author
                    if author == poster:
                        num_poster_posts += 1
                    author_deets = post_trs[1].find("span", class_="postdetails")
                    gender = ""
                    location = ""
                    interests = ""
                    num_posts = ""
                    joined = ""
                    curr_field = None
                    curr_val = None
                    for thing in author_deets.contents:
                        if isinstance(thing, bs4.element.Tag) and thing.name == "b":
                            curr_field = thing.text.strip()
                        elif curr_field is not None:
                            curr_val = one_line(thing)
                            if curr_field == "Joined:":
                                joined = curr_val
                            elif curr_field == "Posts:":
                                num_posts = int(curr_val)
                            elif curr_field == "Location:":
                                location = curr_val
                            curr_field = None
                        else:
                            curr_field = None
                            curr_val = None
                    # it seems like in 2007 even this info is not required
                    #assert joined != ""
                    #assert posts != ""
                    # first div has content and second (if it exists) has like a tagline
                    body_divs = post_trs[1].find_all("div", class_="postbody")
                    assert len(body_divs) > 0
                    if len(body_divs) > 1:
                        tagline = textify_contents(body_divs[1].span.contents if body_divs[1].span is not None else body_divs[1].contents)
                    edit_span = body_divs[0].next_sibling
                    if edit_span is not None and edit_span.name == "span":
                        edit = textify_contents(edit_span.contents)
                    else:
                        edit = ""
                    body_str, quote, citation_str = get_body_str(body_divs[0])
                    member_desc = "N/A"
                    avatar = "N/A"
                    group = "N/A"
                    num_bullets = "N/A"
                    member_num = "N/A"
                    member_ref = "N/A"
                    quote_url = "N/A"
                    quote = "N/A"
                    citation_str = "N/A"
                    assert len(body_str) != 0 or len(tagline) != 0
                    row = unicode("%s" % "|".join([author,member_desc,avatar,group,unicode(num_bullets),
                                            unicode(num_posts), gender, location, interests,
                                            date_str, body_str, edit,member_num, member_ref, quote, quote_url, citation_str, tagline]))
                    assert "\n" not in row
                    f.write(unicode("%s\n" % row).encode('utf8'))
                num_done += len(posts)
                # see if more
                next_link = soup.find("a", text="Next")
                if next_link is not None:
                      soup = BeautifulSoup(requests.get(base_url + next_link['href'][1:]).text, "lxml")
                else:
                    break
            # print 'num_done', num_done, 'num_replies', num_replies
            # assert (num_done == num_replies)

# this will only take the first quote, as in the others
def get_body_str(div):
    # TODO get edits
    citation = div.find("div", class_="quotetitle")
    if citation is not None:
        citation_str = one_line(citation.b.text if citation.b is not None else citation.text)
    else:
        citation_str = ""
    quote_div = div.find("div", class_="quotecontent")
    if quote_div is not None:
        quote = textify_contents(quote_div.contents)
    else:
        quote = ""
    # remove quote and citation str from post body
    body_contents = [thing for thing in div.contents if not isinstance(thing, bs4.element.Tag)
                       or not thing.has_attr("class") or thing["class"] not in ["quotetitle","quotecontent"]]
    return textify_contents(body_contents),quote,citation_str

scrape_autismweb('joy_autismweb3')