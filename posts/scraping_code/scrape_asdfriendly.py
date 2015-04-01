import requests
import bs4
from bs4 import BeautifulSoup
import os
import re
import time

## the output fmt is:
## author,member_desc,avatar_img_link,group,num_bullets,num_posts,gender,location,interests,date_str,body_str,edit_str
##

# note: this doesn't handle multiple quotes really; it just picks the first...

topic_re = re.compile('showtopic=(\d+)')
cached_re = re.compile('cached-.+:[0-9]+:[0-9]')

def scrape_asdfriendly(savedir="asdfriendly"):
    # just the medical/health subforum for now
    url = "http://board.asdfriendly.org/index.php?showforum=5"
    while True:
        time.sleep(0.5)
        soup = BeautifulSoup(requests.get(url).text, "lxml")
        curr_post_links = soup.find_all("a", class_="topic_title")
        save_posts(curr_post_links,savedir,topic_re)
        next_link = soup.find("a", rel="next") # could use title="Next page"
        if next_link is not None and next_link.has_attr('href'):
            url = next_link['href']
        else:
            break

def save_posts(links, savedir, topic_re):
    print 'links', len(links)
    for link in links:
        print "doing", link['href']
        topic = topic_re.search(link['href'])
        assert topic is not None
        soup = BeautifulSoup(requests.get(link['href']).text, "lxml")
        page_title = soup.find('h1', class_="ipsType_pagetitle")
        poster = ""
        num_poster_posts = 0
        assert page_title is not None
        # get time we scraped
        ct = time.localtime()
        curr_timestamp = "%d-%d-%d-%d:%d:%d" % (ct.tm_year, ct.tm_mon, ct.tm_mday, ct.tm_hour, ct.tm_min, ct.tm_sec)
        with open(os.path.join(savedir,topic.groups()[0]+"_"+curr_timestamp), "w+") as f:
            # the first line will be metadata
            f.write(("%s|%s\n" % (link['href'], one_line(page_title.text))).encode('utf8'))
            # get total number of posts
            subtitle_div = soup.find("div", class_="maintitle clear clearfix")
            assert subtitle_div is not None
            replies = subtitle_div.span.text
            try:
                num_replies = int(replies.split()[0].replace(',',''))
            except ValueError as ex:
                if replies.split()[0] == "No":
                    num_replies = 0
                else:
                    raise ex
            num_done = 0
            while True:
                # get all the posts
                posts = soup.find_all("div", class_="post_wrap")
                for post in posts:
                    post_divs = post.find_all("div", recursive=False)
                    # should be two
                    # print len(post_divs)
                    if len(post_divs) < 2:
                        break
                    assert len(post_divs) == 2, post_divs
                    author_deets = post_divs[0].div
                    author = one_line(author_deets.span.text)
                    if poster == "":
                        poster = author
                    if author == poster:
                        num_poster_posts += 1
                    member_desc_p = author_deets.ul.p
                    if member_desc_p is not None:
                        member_desc = one_line(author_deets.ul.p.text)
                    else:
                        member_desc = "" # guests don't have a description
                    author_info = author_deets.find(class_="basic_info")
                    author_lis = author_info.find_all("li")
                    assert len(author_lis) == 4 or member_desc == "", author_lis
                    avatar = one_line(author_lis[0].img["src"])
                    group = one_line(author_lis[1].text)
                    # bullets seem to be assigned based on how many posts, etc
                    if member_desc != "":
                        num_bullets = len(author_lis[2].find_all("img"))
                        num_posts = int(author_lis[3].text.split()[0].replace(',',''))
                    # there can be optional gender,location,interest info
                    extra_info = author_deets.find(class_="custom_fields")
                    gender = ""
                    location = ""
                    interests = ""
                    if extra_info is not None:
                        extra_lis = extra_info.find_all("li")
                        for extra_li in extra_lis:
                            extra_field = extra_li.find(class_="ft")
                            extra_val = extra_li.find(class_="fc")
                            if (extra_field is not None and len(extra_field.text) > 0
                                and extra_val is not None and len(extra_val.text) > 0):
                                if extra_field.text.strip() == "Gender:":
                                    gender = one_line(extra_val.text)
                                elif extra_field.text.strip() == "Location:":
                                    location = one_line(extra_val.text)
                                elif extra_field.text.strip() == "Interests:":
                                    interests = textify_contents(extra_val.contents)
                    
                    # print 'post_divs', post_divs
                    # print post_divs[1].p.abbr
                    # print post_divs[1]

                    # print 'herp', post_divs[1].p.abbr
                    

                    if not post_divs[1].p.abbr:
                        break

                    # print 'derp', post_divs[1].p.abbr["title"]

                    if not post_divs[1].p.abbr['class'] == 'published':
                        break
                    # print post_divs[1].abbr
                    # if post_divs[1].p.abbr



                    date_str = one_line(post_divs[1].p.abbr["title"])

                    # second div usually has class "post_body"
                    # if not post_divs[1].find('div'):
                    #     break
                    body_str, edit, citation_str, quote = get_body_str(post_divs[1].find('div'))
                    # stuff we only have in talkaboutautism
                    member_num = "N/A"
                    member_ref = "N/A"
                    quote_url = "N/A"
                    if len(body_str) == 0:
                        break
                    assert len(body_str) != 0
                    row = unicode("%s" % "|".join([author,member_desc,avatar,group,unicode(num_bullets),
                                            unicode(num_posts), gender, location, interests,
                                            date_str, body_str, edit,member_num, member_ref, quote, quote_url, citation_str]))#.encode('utf8')
                    assert isinstance(row, unicode), type(row)
                    assert "\n" not in row
                    f.write(unicode("%s\n" % row).encode('utf8'))
                num_done += len(posts)
                # see if more
                next_link = soup.find("a", rel="next")
                if next_link is not None:
                      soup = BeautifulSoup(requests.get(next_link['href']).text, "lxml")
                else:
                    break
            # inconsistency on the site about which it is..
            # print num_done, num_replies, num_poster_posts
            # if (num_done != num_replies+1 and num_done != num_replies+num_poster_posts):
            #     break
            # assert (num_done == num_replies+1 or num_done == num_replies+num_poster_posts)

#def content_pars(tag):
#    print tag
#    a = isinstance(tag, bs4.element.Tag)
#    print a
#    b = not tag.has_attr("class")
#    print b
#    c = tag["class"] == "edit"
#    print c
#    return isinstance(tag, bs4.element.Tag) and (not tag.has_attr("class") or tag["class"] == "edit")

# the content div usually has class "post entry-content"
def get_body_str(content_div):
    # sometimes there's an enclosing formatting div, around the div we really want...
    rul_div = content_div.find("div", recursive=False)
    if rul_div is not None and rul_div.has_attr("style"):
        content_div = rul_div
    # see if there's a quote
    citation_str, quote = get_quote(content_div)
    body_ps = [p for p in content_div.find_all("p", recursive=False) if not p.has_attr("class") or p["class"] == "edit"]                    
    if len(body_ps) > 0 and body_ps[-1].has_attr("class") and body_ps[-1]["class"] == "edit":
        edit = one_line(body_ps[-1].text)
        body_ps = body_ps[:-1]
    else:
        edit = ""
    # conveniently, sometimes the post is in <p> tags, and sometimes it's not
    if len(body_ps) == 0:
        align_div = content_div.find("div", align="left")
        if align_div is None:
            # we still need to get rid of any citation or blockquote crap
            body = textify_contents([el for el in content_div.contents 
                                       if not isinstance(el, bs4.element.Tag) or 
                                       (el.name != "blockquote" and 
                                       (not el.has_attr("class") 
                                         or el["class"] not in ["citation","quotemain","quotetop"]))])
        else: # there's a stupid align div so only take stuff after it
            i = 0
            while i < len(align_div.contents):
                if content_div.contents[i].name == "div":
                    break
                else:
                    i += 1
            body = textify_contents(content_div.contents[i:])
    else:
        body = "<br/>".join([textify_contents(bp.contents) for bp in body_ps])
    return body, edit, citation_str, quote


def one_line(s):
    # the zillion newline unicode type things
    ignores = set([u'\u000a',u'\u000d',u'\u001d',u'\u001c',u'\u001e',u'\u0085',u'\u2028',u'\u2029'])
    return "".join([c if c not in ignores else ' ' for c in s.strip()])
    #return (s.strip().replace(u'\xa0','').replace('\n',' ')
    #        .replace("\r", ' ').replace(u'\u001c',' ').replace(u'\u001d',' ')
    #        .replace(u'\001e', ' ').replace(u'\0085', ' ').replace()

def textify_contents(contents):
    #text_formatters = set(["span","sup","sub","b","i","em","strong","small","mark"])
    content_strs = []
    for thing in contents:
        if isinstance(thing, unicode) and thing == u'\xa0':
            content_strs.append("<br/>")
        elif isinstance(thing, bs4.element.Comment):
            pass
        elif (isinstance(thing, str) or isinstance(thing, unicode)) and cached_re.search(thing) is not None:
            pass # ignore these guys
        elif isinstance(thing, bs4.element.NavigableString) or isinstance(thing, str) or isinstance(thing, unicode):
            content_strs.append(one_line(thing))
        elif isinstance(thing, bs4.element.Tag) and thing.name == "br":
            content_strs.append("<br/>")
        elif isinstance(thing, bs4.element.Tag) and thing.name == "p":
            content_strs.append("<br/>")
            content_strs.append(textify_contents(thing.contents))
        elif isinstance(thing, bs4.element.Tag) and thing.name == "a":
            one_liner = one_line(thing.text)
            if len(one_liner) > 0:
                content_strs.append(one_liner)
            if thing.has_attr("href"):
                content_strs.append('( ' + one_line(thing["href"]) + ' )')
        elif isinstance(thing, bs4.element.Tag) and thing.name in ["span","div"]:
            content_strs.append(textify_contents(thing.contents)) 
        elif isinstance(thing, bs4.element.Tag):
            unitab = one_line(unicode(thing))
            content_strs.append(unitab)
    #return content_strs
    return " ".join(content_strs)

def get_quote(content_div):
    citation = content_div.find("p", class_="citation")
    if citation is not None:
        citation_str = one_line(citation.text)
    elif content_div.find("div", class_="quotetop"):
        citation_str = textify_contents(content_div.find("div", class_="quotetop").contents)
    else:
        citation_str = ""
    blockquote = content_div.find("blockquote")
    if blockquote is not None:
        quote = textify_contents(blockquote.contents)
    elif content_div.find("div", class_="quotemain") is not None:
        quote = textify_contents(content_div.find("div", class_="quotemain").contents)
    else:
        quote = ""
    return citation_str, quote


# scrape_asdfriendly("joy_asdfriendly")

