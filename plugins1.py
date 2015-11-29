import httplib2
import json

def stripPrefix(q, l):
    return q[len(l):]
def pluginFilter(que):
    que=que.lstrip()
    if que.startswith('yt '):
        prefix = 'yt '
        q = stripPrefix(que, prefix)
        content = youtube(q)
    elif que.startswith('youtube '):
        prefix = 'youtube '
        q = stripPrefix(que, prefix)
        content = youtube(q)
    return content
################3
## Plugins
#
# == Officially supported plugins (early stages) ==
#
#   - youtube
#
# == TODO ==
#
# [NEWS]
#   - guardian
#   - new york times
#   - bbc news
# [MUSIC]
#   - souncloud
#   - lastfm
#   - 
# [VIDEO]
#   - vimeo
# [OTHER]
#   - 9gag?

################3
def youtube(query):
    yt_uri = "https://www.googleapis.com/youtube/v3/search?part=snippet&key=%20AIzaSyDZNbNhSHHGI_9aR9h9eDOU94XBIldIhCg&q={}".format(query)
    h = httplib2.Http()
    r, content = h.request(yt_uri, "GET")
    if content:
        c = json.loads(content)
        #BASIC RESPONSE: <TEXT> <URL> <BRANDCOLOR>
        #IMAGE RESPONSE: <IMG> <TEXT> <URL> <BRANDCOLOR>
        #CUSTOM RESPONSE: <DIV(HTML)> <BRANDCOLOR>

        vids = [ {'type':'image','text':l['snippet']['title'],'img':l['snippet']['thumbnails']['default']['url'],'url':"https://www.youtube.com/watch?v="+l['id']['videoId']} for l in c['items'] if l['id']['kind']=='youtube#video' ]
    else:
        vids=[]
    return vids
