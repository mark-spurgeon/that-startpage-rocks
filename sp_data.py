# Copyright 2015 Mark Spurgeon

from google.appengine.ext import ndb

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

    linksList = ndb.JsonProperty(default=defaultAppList)

    spTitle = ndb.StringProperty(default='The Startpage')
    themeName = ndb.StringProperty(default='dark')
    backgroundImageKey = ndb.BlobKeyProperty()
    backgroundImageURL = ndb.StringProperty()
class appIconProposed(ndb.Model):
    domains = ndb.StringProperty()
    imageKey = ndb.BlobKeyProperty()
    imageURL = ndb.StringProperty()
class appIcon(ndb.Model):
    domains = ndb.StringProperty()
    imageKey = ndb.BlobKeyProperty()
