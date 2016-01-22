# Copyright 2015 Mark Spurgeon

from google.appengine.ext import ndb

from plugins import browsers

defaultAppList = [
        {'url':'http://www.youtube.com',
        'icon':'icon:http://www.youtube.com',
        'display_name':'Youtube',
        'bg_color':'rgb(230,100,90)',
        'position':1},
        {'url':'http://www.theguardian.com',
        'icon':'icon:http://www.theguardian.com',
        'display_name':'The Guardian',
        'bg_color':'rgb(230,100,90)',
        'position':2}
    ]


class ExternalUser(ndb.Model):
    source = ndb.StringProperty()
    username = ndb.StringProperty()
    userID = ndb.StringProperty()
    thumbnail = ndb.StringProperty()
    email = ndb.StringProperty()
    linksList = ndb.JsonProperty(default=defaultAppList, indexed=False)

    spTitle = ndb.StringProperty(default='The Startpage')
    themeName = ndb.StringProperty(default='dark')
    searchBrowser = ndb.StringProperty(default=browsers.defaultBrowser)
    backgroundImageKey = ndb.BlobKeyProperty()
    backgroundImageURL = ndb.StringProperty(default="http://that.startpage.rocks/static/images/crowd-1056764_1280.jpg")
class appIconProposed(ndb.Model):
    domains = ndb.StringProperty()
    imageKey = ndb.BlobKeyProperty()
    imageURL = ndb.StringProperty()
class appIcon(ndb.Model):
    domains = ndb.StringProperty()
    imageKey = ndb.BlobKeyProperty()
class spDownloadCount(ndb.Model):
    count = ndb.IntegerProperty(default=0)
