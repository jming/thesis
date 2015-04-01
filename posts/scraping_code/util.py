import os
import re
import codecs
import subprocess
import time

enc_tag_re = re.compile('<[^>]+>([^<]+)<[^>]+>') # corresponds to tag with something enclosed (assuming this is one token)
not_enc_tag_re = re.compile('<[^<>]+/?>')
punct_no_space_re1 = re.compile('(\S)([\.,;:\'"?!\(\)])')
punct_no_space_re2 = re.compile('([\.,;:\'"?!\(\)])(\S)')
url_re = re.compile('(?:http://\S+\s)|(?:www\.\S+\s)')


# direcs = ["asdfriendly", "talkaboutautism", "asdforum/17-medication",
#             "asdforum/15-diet-and-vitamins", "asdforum/19-vaccinations",
#             "asdforum/16-herbalnatural-supplements", "asdforum/18-other-interventions",
#             "asdforum/20-miscellaneous","autismweb"]

direcs = [
    'joy_asdfriendly',
    'joy_autismweb3',
    'joy_talkaboutautism',
    'joy_asdforum/2-general-discussion',
    'joy_asdforum/4-help-and-advice',
    'joy_asdforum/7-education',
    'joy_asdforum/25-asd-related-conditions',
    'joy_asdforum/27-pda',
    'joy_asdforum/28-add-and-adhd'
]

# will just put each post on a line, no identification
def prepare_for_postagging(direcs, outfi):
    with open(outfi,"w+") as g:
        for direc in direcs:
            print "doing directory:", direc
            for fi in os.listdir(direc):
                # print "fi", fi
                if not fi == '.DS_Store':
                    with codecs.open(os.path.join(direc,fi),"r","utf-8") as f:
                        _ = f.readline() # first line is just metada
                        for line in f:
                            #print line
                            try:
                                cleaned_up_body = clean_up(line.split('|')[10])
                                #if "{" in cleaned_up_body:
                                #    print fi
                                #    print cleaned_up_body
                                #    return
                                #if "<" in cleaned_up_body or ">" in cleaned_up_body:
                                #    print cleaned_up_body
                                #    time.sleep(10)
                                #assert "<" not in cleaned_up_body and ">" not in cleaned_up_body, cleaned_up_body
                            except IndexError as ex:
                                print line
                                print fi
                                raise ex
                            g.write(("%s\n" % cleaned_up_body).encode('utf8'))
                            #wtf = remove_html_stuff(line.split('|')[10])
                            #try:
                            #    nugz = [unicode(thing) for thing in wtf]
                            #except UnicodeDecodeError:
                            #    return wtf
                            #tokes = [unicode(s) for s in remove_html_stuff(line.split('|')[10])]
                            #g.write(unicode("%s\n" % " ".join(tokes)).encode('utf8'))

def replace_with_enclosed(matchobj):
    return matchobj.groups()[0]


def add_space(matchobj):
    return matchobj.groups()[0] + " " + matchobj.groups()[1]

# removes html tags, and adds spaces after punctuation
def clean_up(body):
    # remove tags with no stuff in em
    body = not_enc_tag_re.sub(" ",body)

    # replace tags that enclose stuff with what's inside
    # because there can be nested tags, do this until the stuff stops changing
    prev_len = len(body)
    body = enc_tag_re.sub(replace_with_enclosed,body)
    while(len(body) != prev_len):
        prev_len = len(body)
        body = enc_tag_re.sub(replace_with_enclosed,body)

    # remove urls (important to remove tags first, b/c they can have urls in them too)
    #body = url_re.sub(" ", body)
    #body = punct_no_space_re1.sub(add_space, body)
    #body = punct_no_space_re2.sub(add_space, body)
    return body
    
    #tokes = body.split()
    #newtokes = []
    #for toke in tokes:
    #    if "<" not in toke:
    #        newtokes.append(toke)
    #    else:
    #        m = enc_tag_re.match(toke)
    #        if m is not None:
    #            newtokes.extend(m.groups()[0].split())
    #        elif enc_tag_re.search(toke) is not None:
    #            print "this should not happen", toke
    #return newtokes

# somehow these nuggety ^M characters got in and they're screwing everything up
def remove_carets(direc):
    fis = os.listdir(direc)
    for fi in fis:
        full_fi = os.path.join(direc,fi)
        subprocess.call("tr '\015' ' ' < %s > nug.temp" % full_fi, shell=True)
        subprocess.call("mv nug.temp %s" % full_fi, shell=True)

def remove_unicode_line_sep(direc):
    fis = os.listdir(direc)
    for fi in fis:
        full_fi = os.path.join(direc,fi)
        subprocess.call("sed -i.old $'s/\xE2\x80\xA8/ /g' %s" % full_fi, shell=True)

skip_re = re.compile('-LRB-|-RRB-|\S*www\S*|\S*http\S*|\S*@\S|\S*php\S*|Edited by.*')
sent_end_re = re.compile('\s\s\s+') # at least 3 spaces
#eos_re = re.compile('.\.[A-Z]+')
eos_re = re.compile('([\.,;:?!\(\)])(\w)')
def clean_up_all_posts(fi="all_posts.txt", mark_post_end=False):
    with open(fi + ".cleaner","w+") as g:
        with open(fi) as f:
            for line in f:
                newline = sent_end_re.sub(". ", line.strip()) # add a period where there should prob be one
                newline = eos_re.sub(add_space,newline)
                g.write(skip_re.sub("",newline))
                g.write(".\n")
                if mark_post_end:
                    g.write("\n\nThe post has ended.\n\n")

prepare_for_postagging(direcs, 'joy_all_posts.txt')
    