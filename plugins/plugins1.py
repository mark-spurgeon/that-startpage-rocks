#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib2
import json


from plugins import apikeys

def stripPrefix(q, l):
    return q[len(l):]
def pluginFilter(que):
    que=que.lstrip()
    que = que.lower()
    plugin=True
    if que.startswith('yt '):
        prefix = 'yt '
        q = stripPrefix(que, prefix)
        content = youtube(q)
    elif que.startswith('youtube '):
        prefix = 'youtube '
        q = stripPrefix(que, prefix)
        content = youtube(q)
    elif que.startswith('soundcloud '):
        prefix = 'soundcloud '
        q = stripPrefix(que, prefix)
        content = soundcloud(q)
    elif que.startswith('sc '):
        prefix = 'sc '
        q = stripPrefix(que, prefix)
        content = soundcloud(q)
    elif que.startswith('spotify '):
        prefix = 'spotify '
        q = stripPrefix(que, prefix)
        content = spotify(q)
    elif que.startswith('spot '):
        prefix = 'spot '
        q = stripPrefix(que, prefix)
        content = spotify(q)
    elif que.startswith('nytimes '):
        prefix = 'nytimes '
        q = stripPrefix(que, prefix)
        content = nytimes(q)
    elif que.startswith('guardian '):
        prefix = 'guardian '
        q = stripPrefix(que, prefix)
        content = guardian(q)
    elif que.startswith('gdn '):
        prefix = 'gdn '
        q = stripPrefix(que, prefix)
        content = guardian(q)
    elif que.startswith('wikipedia '):
        prefix = 'wikipedia '
        q = stripPrefix(que, prefix)
        content = wikipedia(q)
    elif que.startswith('wiki '):
        prefix = 'wiki '
        q = stripPrefix(que, prefix)
        content = wikipedia(q)
    elif que.startswith('pix '):
        prefix = 'pix '
        q = stripPrefix(que, prefix)
        content = pixabay(q)
    elif que.startswith('pixabay '):
        prefix = 'pixabay '
        q = stripPrefix(que, prefix)
        content = pixabay(q)
    else:
        plugin=False
        content = allPlugins

    if plugin==True:
        return ('found',content)
    else:
        return ('not-found',content)
################3
## Plugins
#
# == Officially supported plugins (early stages) ==
#
#   - youtube
#
# == Work In Progress
#
#   - soundcloud
#
# == TODO ==
#
# [NEWS]
#   - guardian
#   - new york times
#   - bbc news
# [MUSIC]
#   (- souncloud)
#   - lastfm
#   - spotify
# [VIDEO]
#   - vimeo
# [OTHER]
#   - 9gag?

################3

allPlugins = {
    'soundcloud':{'brand-color':'#ff3300',
                'domains':['soundcloud','sc']},
    'spotify': {'brand-color':'#23d05f',
                'domains':['spotify','spot']
                },
    'youtube': {'brand-color':'#e52d27',
                'domains':['youtube','yt']
                },
    'new york times': {'brand-color':'rgb(60,60,60)',
                'domains':['nytimes']
                },
    'the guardian': {'brand-color':'#005689',
                'domains':['guardian','gdn']
                },
    'wikipedia': {'brand-color':'rgb(80,80,80)',
                'domains':['wikipedia', 'wiki']
                },
    'pixabay' : {'brand-color':'#6ba72b',
                'domains':['pixabay','pix']

                }
    }










# VIDEO


def youtube(query):
    api = apikeys.keys['youtube']
    yt_uri = "https://www.googleapis.com/youtube/v3/search?part=snippet&key={0}&q={1}".format(api,query)
    h = httplib2.Http()
    r, content = h.request(yt_uri, "GET")
    if content:
        c = json.loads(content)
        #BASIC RESPONSE: <TEXT> <URL> <BRANDCOLOR>
        #IMAGE RESPONSE: <IMG> <TEXT> <URL> <BRANDCOLOR>
        #CUSTOM RESPONSE: <DIV(HTML)> <BRANDCOLOR>

        vids = [ {'type':'image','text':l['snippet']['title'],'img':l['snippet']['thumbnails']['default']['url'],'url':"https://www.youtube.com/watch?v="+l['id']['videoId'], 'brand_color':"#e52d27"} for l in c['items'] if l['id']['kind']=='youtube#video' ]
    else:
        vids=[]
    return vids


#MUSIC

def soundcloud(query):
    api = apikeys.keys['soundcloud']
    sc_uri = "https://api.soundcloud.com/tracks?client_id={0}&q={1}".format(api,query)
    h = httplib2.Http()
    r, content = h.request(sc_uri, "GET")
    if content:
        c = json.loads(content)
        sounds=[{'type':'image','text':u"<p>{0}</p><p><span style='opacity:.7'>by:</span> <a style='color:#ff3300;opacity:1;' href='{2}' tabindex='99'>{1}</a></p>".format(r['title'],r['user']['username'],r['user']['permalink_url']),'img':r['artwork_url'],'url':r['permalink_url']+'#t=0.1', 'brand_color':'#ff3300'} for r in c]
        print sounds
    else:
        sounds=[]
    return sounds

def spotify(query):
    query = query.replace(' ', "+")
    spo_uri="https://api.spotify.com/v1/search?type=track&q="+query
    h = httplib2.Http()
    r, content = h.request(spo_uri, "GET")

    sounds = []

    if content:
        c = json.loads(content)
        tracks = c['tracks']['items']
        for t in tracks:
            if t['type']=='track':
                s = {}
                s['brand_color']='#23d05f'
                s['type']='image'
                s['url'] = t['external_urls']['spotify']
                artists = ""
                for a in t['artists']:
                    artists+= "<a tabindex='99' style='color:#23d05f' href='"+a['external_urls']['spotify']+"'>"+ a["name"] + ";</a>"

                s['text'] = "<p>"+ t['name']+"</p><p>"+artists+"</p>"
                for i in t['album']['images']:
                    if i['height']==300:
                        s['img'] = i['url']
                    elif i['height']==64:
                        s['img'] = i['url']
                    else:
                        pass
            sounds.append(s)
    return sounds

#NEWS

def nytimes(query):
    api = apikeys.keys['nytimes']
    ny_uri="http://api.nytimes.com/svc/search/v2/articlesearch.json?api-key={0}&q{1}".format(api,query)
    h = httplib2.Http()
    r, content = h.request(ny_uri, "GET")

    arts = []

    if content:
        c=json.loads(content)
        r =c['response']['docs']
        for a in r:
            ar = {}
            ar['type']='basic'
            ar['text']="<p style='font-family:Georgia'>"+a['snippet']+"</p>"
            ar['brand-color']='white'
            #ar['img']='/static/icons/nytimes_white.png'
            ar['url']=a['web_url']
            arts.append(ar)
    return arts

def guardian(query):
    api = apikeys.keys['guardian']
    arts=[]
    print query
    if query == 'latest':
        gu_uri= "http://content.guardianapis.com/search?api-key={0}&show-fields=headline,thumbnail".format(api)
        #arts.append({'type':'basic','url':'','text':'Latest news from the Guardian'})
    else:
        gu_uri= "http://content.guardianapis.com/search?api-key={0}&show-fields=headline,thumbnail&q={1}".format(api,query)
    h = httplib2.Http()
    r, content = h.request(gu_uri, "GET")

    if content:
        c= json.loads(content)


        ar = c['response']['results']
        for a in ar:
            if a['type']=='article' or a['type']=='liveblog':
                l = {}
                l['brand_color']="#005689"
                l['type']='image'
                l['url']=a['webUrl']
                try:
                    l['img']=a['fields']['thumbnail']
                except:
                    l['img']=''
                if a['type']=='liveblog':
                    live = u"<span style='color:white;background-color:#B51800;padding:2px;'>LIVE</span>"
                else:
                    live=''
                l['text']="<p>"+live+" "+a['fields']['headline']+"</p><p>section: <span style='color:#005689'>"+a['sectionId']+"</span></p>"
                arts.append(l)
    return arts

#images
def pixabay(query):
    api = apikeys.keys['pixabay']
    query = query.replace(' ','+')
    px_uri="https://pixabay.com/api/?key={0}&username=theduckdev&q={1}".format(api,query)
    h = httplib2.Http()
    r, content = h.request(px_uri, "GET")

    arts = []
    if content:
        res = json.loads(content)
        for r in res['hits']:
            ar = {}
            ar['type']='image'
            ar['brand_color']='#6ba72b'
            ar['url'] = r['pageURL']
            ar['img']=r['previewURL']
            ar['text']="<a tabindex='99' style='color:#6ba72b' href='{0}'>Download it on <i>Pixabay</i></a>".format(r['previewURL'])
            arts.append(ar)

    return arts
#OTHER

def wikipedia(query):
    wk_uri="https://en.wikipedia.org/w/api.php?action=opensearch&list=search&format=json&search="+query
    h = httplib2.Http()
    r, content = h.request(wk_uri, "GET")

    arts = []
    if content:
        e,title,desc,url = json.loads(content)
        for i,t in enumerate(title):
            ar = {}
            ar['type']='basic'
            ar['brand_color']='white'
            ar['url']=url[i]
            ar['text']="<p style='font-size:1.4em;font-family:Times New Roman,serif;'>"+t+"</p><p style='font-family:Times New Roman,serif;'>"+desc[i]+"</p>"
            arts.append(ar)
    return arts
