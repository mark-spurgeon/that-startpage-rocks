# Copyright 2015 Mark Spurgeon
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask
from flask import Flask
from flask import g, make_response, request, current_app,send_from_directory,render_template,redirect,url_for, Markup, Response, session, Markup
from werkzeug import parse_options_header

from google.appengine.api import search

from traceback import print_exc

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.blobstore.blobstore import BlobKey
from google.appengine.api import images

from apiclient import discovery
from oauth2client import client
import httplib2
import json
import markdown

import uuid


import app_list
from plugins import plugins1 as plugins
import sp_data

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = str(uuid.uuid4())

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
def checkUserLoggedIn():
    user=False
    user_type=''
    user_info=None
    #print flask.session['ext-user']
    ext = request.cookies.get('ext-user')
    ext_s = request.cookies.get('ext-user-s')
    users = [ u for u in sp_data.ExternalUser.query() if str(u.userID)==ext and u.source==ext_s ]
    if len(users)>0:
        user = True
        user_info = users[0].to_dict()
    return (user, user_info)
def jsonResponse(json_dict):
    return Response(json.dumps(json_dict,indent=4, separators=(',', ': ')), mimetype="application/json")

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/old')
def index_old():
    return render_template('the-index.html')
@app.route('/features')
def features():
    return redirect(url_for("index"))
@app.route('/features/search')
def features_searcj():
    return render_template('feature-search.html')

@app.route('/browsers')
def browsers():
    return render_template('browsers.html')
@app.route('/browsers/firefox')
def browsers_f():
    return redirect(url_for("browsers"))
@app.route('/browsers/chrome')
def browsers_c():
    return redirect(url_for("browsers"))
@app.route('/browsers/safari')
def browsers_s():
    return redirect(url_for("browsers"))
@app.route('/browsers/ie')
def browsers_e():
    return redirect(url_for("browsers"))
@app.route('/browsers/opera')
def browsers_o():
    return redirect(url_for("browsers"))
@app.route('/browsers/other')
def browsers_other():
    return redirect(url_for("browsers"))
@app.route('/login')
def login():
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        return redirect(url_for('edit'))
    else:
        return render_template('login.html')
@app.route('/signup')
def signup():
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        return redirect(url_for('edit'))
    else:
        return render_template('signup.html')

#blobstore image
@app.route("/image/<bkey>")
def imag(bkey):
    blob_info = blobstore.get(bkey)
    response = make_response(blob_info.open().read())
    response.headers['Content-Type'] = blob_info.content_type
    return response

###
# Main Startpage
###
@app.route('/sp/<source>/<user>')
def sp(source,user):
    sp_l = sp_data.ExternalUser.query()
    u  =  [u for u in sp_l if str(u.source)==source and str(u.userID) == str(user)]
    if len(u)>0:
        theme = u[0].themeName
        apps = u[0].linksList
        apps = sorted(apps, key=lambda k: k['position'])
        a_list = []
        for a in apps :
            if a['icon'].startswith('icon:'):
                ur  = a['icon'].replace('icon:','')
                a['icon']='/icons/get?url='+ur
        img_url =  str(u[0].backgroundImageURL)+"=s0"#"http://startpage-1072.appspot.com/image/"+str(u[0].backgroundImageKey)
        #md = markdown.Markdown()
        title = u[0].spTitle #Markup(md.convert(u[0].spTitle))
        manifest_url = "http://startpage-1072.appspot.com/manifest/{0}/{1}".format(u[0].source,u[0].userID)

        resp = make_response(render_template('sp.html',title=title,apps=apps, theme=theme,img=img_url,manifest=manifest_url))
        resp.set_cookie('first-login',str(False))
        return resp
    else:
        abort(404)

@app.route('/manifest/<source>/<user>')
def sp_manifest(source,user):
    sp_l = sp_data.ExternalUser.query()
    u  =  [u for u in sp_l if str(u.source)==source and str(u.userID) == str(user)]
    if len(u)>0:
        img =   str(u[0].backgroundImageURL)+"=s0"
        apps = u[0].to_dict()['linksList']
        theme = u[0].themeName
        print apps
        resp = Response(render_template('manifest.html', img=img,apps=apps,theme=theme))
        resp.headers["Content-Type"]="text/cache-manifest"
        resp.headers["Cache-Control"]="max-age=0, no-cache, public"
        return resp
    else:
        abort(404)
@app.route('/sp-debug/<source>/<user>')
def sp_debug(source,user):
    sp_l = sp_data.ExternalUser.query()
    u  =  [u for u in sp_l if str(u.source)==source and str(u.userID) == str(user)]
    if len(u)>0:
        theme = u[0].themeName
        apps = u[0].linksList
        img_url = u[0].backgroundImageURL
        manifest_url = "http://startpage-1072.appspot.com/manifest/{0}/{1}".format(u[0].source,u[0].userID)
        return jsonResponse({'apps':apps, 'theme':theme,'img':img_url,'manifest':manifest_url})
    else:
        abort(404)



#####
## First Setup
#####

#Give a title
@app.route('/setup/1')
def setup_one():
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        return render_template('setup/1.html')
    else:
        return redirect(url_for('login'))
#Upload a background url
@app.route('/setup/2')
def setup_two():
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        uploadUri = blobstore.create_upload_url('/config/upload-bg')
        return render_template('setup/2.html', uploadUri=uploadUri)
    else:
        return redirect(url_for('login'))

#Add websites
@app.route('/setup/3')
def setup_three():
    return redirect(url_for('setup_four'))

#Enjoy
@app.route('/setup/4')
def setup_four():
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:
            url = '/sp/{0}/{1}'.format(us[0].source,us[0].userID)
            return render_template('setup/4.html',url=url)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

#####
## Startpage Edition
#####
@app.route('/edit')
def edit():
    msg = request.args.get('message')
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:
            img = "/image/"+str(us[0].backgroundImageKey)
            theme =  us[0].themeName
            title =  us[0].spTitle
            apps = us[0].linksList
            apps = sorted(apps, key=lambda k: k['position'])
            for a in apps :
                if a['icon'].startswith('icon:'):
                    ur  = a['icon'].replace('icon:','')
                    a['icon']='/icons/get?url='+ur
            uploadUri = blobstore.create_upload_url('/config/upload-bg')

            if request.cookies.has_key('first-login') and request.cookies.get('first-login')==str(True):
                return redirect(url_for('setup_one'))
            else:
                return render_template('edit.html', user=u_i, upload_bg=uploadUri, title = title, img = img, theme= theme, apps = apps,message=msg)
    else:
        return redirect(url_for('login'))



##config changes [backend]
@app.route('/config/upload-bg',methods=['POST'])
def cfg_upload_bg():
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:
            user = us[0]
            image=request.files["filename"]
            header = image.headers['Content-Type']
            parsed_header = parse_options_header(header)
            blob_key = parsed_header[1]['blob-key']
            l = images.get_serving_url(blob_key)
            user.backgroundImageURL = l
            user.backgroundImageKey=BlobKey(blob_key)

            #import datetime
            #user.imgUrl="http://startpage-1072.appspot.com/img/{0}/{1}/{2}".format(us[0].source,us[0].userID,datetime.datetime.now())
            user.put()
            if request.cookies.has_key('first-login') and request.cookies.get('first-login')==str(True):
                return redirect(url_for('setup_three'))
            else:
                return redirect(url_for('edit',message="Success! Your startpage's got a new background image.")+"#image")
        else:
            return jsonResponse({'status':'error'})
    else:
        return redirect(url_for('login'))


#TODO : private -> post
@app.route('/config/add-website',methods=['POST'])
def cfg_add_website():


    url  = request.form.get('url')
    title = ""#request.args.get('title')


    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:

            user = us[0]

            #Find Webapp Image Url + Title
            h = httplib2.Http()
            r, content = h.request(url, "GET")
            from BeautifulSoup import BeautifulSoup
            par = BeautifulSoup(content)

            the_title = par.find('title').string

            #find icon in repo
            img_url=None
            icos = sp_data.appIconProposed.query()
            for i in icos:
                if ',' in i.domains:
                    d_list = [ l.replace(' ','') for l in i.domains.split(',')]
                else:
                    d_list = [i.domains.replace(' ','')]
                if  getDomainFromUrl(url) in d_list:
                    img_url="icon:"+url
            if not img_url:


                d = par.find('link',attrs={'rel':'icon','sizes':'96x96'})
                if not d:
                    d = par.find('link',attrs={'rel':'icon','sizes':'48x48'})
                if not d:
                    d = par.find('link',attrs={'rel':'apple-touch-icon-precomposed'})
                if not d:
                    d = par.find('link',attrs={'rel':'apple-touch-icon'})
                if not d:
                    d = par.find('link',attrs={'rel':'icon'})

                if d:
                    static = d.get('href')
                    if not static.startswith('http://') or not static.startswith('https://'):
                        if static.startswith('//'):
                            n_url = url.replace('https://','')
                            n_url = url.replace('http://','')
                            l  = n_url.split('/')
                            if url.startswith('http://'):
                                img_url = 'http://'
                            if url.startswith('https://'):
                                img_url = 'https://'

                            for a  in l[:-1]:
                                img_url+=a
                            img_url+=static.replace('//','')
                        elif static.startswith('/'):
                            n_url = url.replace('https://','')
                            n_url = url.replace('http://','')
                            l  = n_url.split('/')
                            if url.startswith('http://'):
                                img_url = 'http://'
                            if url.startswith('https://'):
                                img_url = 'https://'
                            for a  in l:
                                img_url+=a
                            if not img_url.endswith('/'):
                                img_url+='/'
                            img_url+=static[1:]
                        else:
                            img_url='letter'
                    else:
                        img_url=static
                else:
                    img_url='letter'


            #Get BG color
            if img_url == 'letter':
                #img = image_url = 'http://www.google.com/s2/favicons?domain='+url
                #h = httplib2.Http()
                #r, content = h.request(img, "GET")
                #from PIL import Image
                #i = Image.fromstring('RGB',(5,5),content)
                #r,g,b = i.getpixel((1,1))
                #bg_color="rgb({0},{1},{2})".format(r,g,b)
                bg_color="#F4D03F"
            else:
                bg_color="rgb(30,30,30)"
            ##
            wa_list = user.linksList#json.loads(user.linksList)
            print len(wa_list)+1
            new_webapp = {'url':url,
                        'icon':img_url,
                        'display_name':the_title,
                        'bg_color':bg_color,
                        'position':len(wa_list)+1}
            wa_list.append(new_webapp)
            user.linksList = wa_list
            user.put()
            return redirect(url_for('edit',message='Success! The website has been added!')+"#apps")
            #return jsonResponse({'status':'ok','url':url,'img':img_url,'title':the_title})
        else:
            #user not logged in
            return redirect(url_for('login'))

@app.route('/config/modify-website/<web>/position')#,methods=['POST'])
def cfg_mod_website_pos(web):
    #website, depending on position
    website  = int(web)
    #new position
    new_pos = int(request.args.get('value'))

    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:

            user = us[0]

            apps = user.linksList
            for f in apps:
                if website>new_pos:
                    leng = website-new_pos
                    if new_pos<=f['position']<website:
                        f['position']+=1
                    elif f['position']==website:
                        f['position']=new_pos
                elif website<new_pos:
                    if new_pos>=f['position']>website:
                        f['position']-=1
                    elif f['position']==website:
                        f['position']=new_pos
            user.put()
            return jsonResponse({'status':'ok','results':sorted(apps, key=lambda k: k['position'])})

        else:
            return redirect(url_for('login'))
    else:
        redirect(url_for('login'))

@app.route('/config/modify-website/<web>/url')#,methods=['POST'])
def cfg_mod_website_url(web):
    #website, depending on position
    website  = int(web)
    #new position
    new_url = str(request.args.get('value'))

    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:

            user = us[0]

            apps = user.linksList
            for f in apps:
                if f['position']==website:
                    f['url']=new_url
            user.put()
            return jsonResponse({'status':'ok','url':new_url})

@app.route('/config/modify-website/<web>/title',methods=['POST'])
def cfg_mod_website_title(web):
    #website, depending on position
    website  = int(web)
    #new position
    new_title = str(request.form.get('value'))

    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:

            user = us[0]

            apps = user.linksList
            for f in apps:
                if f['position']==website:
                    f['display_name']=new_title
            user.put()
            return redirect(url_for('edit',message="Success! The website's got a new name."))
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
@app.route('/config/delete-website')#,methods=['POST'])
def cfg_del_website():
    #website, depending on position
    website  = int(request.args.get('website'))
    #new position
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:

            user = us[0]

            apps = user.linksList
            new_apps = []
            for f in apps:
                if f['position']==website:
                    pass
                else:
                    if f['position']>website:
                        f['position']-=1
                    new_apps.append(f)
            user.linksList=new_apps
            user.put()
            #return jsonResponse({'status':'ok','results':sorted(new_apps, key=lambda k: k['position'])})
            return redirect(url_for('edit',message='Success! The Website has been deleted.'))
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
@app.route('/config/change-theme',methods=['POST'])
def cfg_change_color():

    theme = request.form.get('theme')

    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:
            us[0].themeName=theme
            us[0].put()
            return redirect(url_for('edit',message="Success! You've changed your startpage's theme.")+"#theme")
        else:
            return redirect(url_for('edit'))
    else:
        return redirect(url_for('edit'))

@app.route('/config/change-title',methods=['POST'])
def cfg_change_title():
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:
            us[0].spTitle = request.form.get('title')
            us[0].put()
            if request.cookies.has_key('first-login') and request.cookies.get('first-login')==str(True):
                return redirect(url_for('setup_two'))
            else:
                return redirect(url_for('edit',message="Success! Your startpage's got a new name.")+"#title")
        else:
            return redirect(url_for('edit',message="Error"))
    else:
        return redirect(url_for('edit'))

@app.route('/config/change-apps-positions',methods=['POST'])
def cfg_change_apps_order():
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:
            new_order = request.form.get('value')
            new_order = [int(f.replace(',','')) for f in new_order.split(',')]
            print new_order
            user = us[0]
            apps = sorted(user.linksList, key=lambda k: k['position'])
            new_apps = []
            if len(apps) == len(new_order):
                for i, a in enumerate(new_order):
                    a = int(a)
                    new_app = apps[a-1]
                    print new_app, i+1
                    new_app['position']=i+1
                    print new_app
                    new_apps.append(new_app)
            user.linksList=new_apps
            user.put()
            return redirect(url_for('edit',message="Success! You've changed the order of your apps")+"#apps")
        else:
            return redirect(url_for('edit',message="Error.. You are not logged in"))
    else:
        return redirect(url_for('edit',message="Error.. You are not logged in"))
####
# Search Functio
####
@app.route('/search')
def search_():
    query = request.args['q']
    f, resp = plugins.pluginFilter(query)
    if f == 'found':
        return jsonResponse({'status':'ok','responseType':'plugin-results','results':resp})
    elif f=='not-found':
        return jsonResponse({'status':'ok','responseType':'plugins-available','results':resp})

@app.route('/customsearch_xml')
def customsearch():
    return render_template('customsearch.html')


#####
## Icon repo
#####
def getDomainFromUrl(u):
    dom = u.replace('http://','')
    dom = dom.replace('https://','')
    dom1 = dom.split('/')[0].split('.')
    f_dom = dom1[-2]+'.'+dom1[-1]
    return f_dom
@app.route('/icons')
def icons():
    uploadUri = blobstore.create_upload_url('/icons/add')
    q = sp_data.appIconProposed.query()
    icoList = [{'imageUrl':l.imageURL,'domains':[e.replace(' ','') for e in l.domains.split(',')]} for l in q]
    return render_template('icons.html', uploadUri=uploadUri, icons=icoList)
@app.route('/icons/add', methods=['POST'])
def add_icon():
    domainlist = request.form.get('domains')
    image = request.files.get('icon')
    header = image.headers['Content-Type']
    parsed_header = parse_options_header(header)
    blob_key = parsed_header[1]['blob-key']
    theKey =BlobKey(blob_key)
    theDomains = domainlist.split(',')

    newDomain = sp_data.appIconProposed(domains=domainlist, imageKey=theKey, imageURL=images.get_serving_url(blob_key))
    newDomain.put()
    return redirect(url_for('icons'))
@app.route('/icons/get')
def get_icon():
    domain = request.args.get('url')
    s = sp_data.appIconProposed.query()
    image_url = None
    for ap in s:
        if ap.imageURL==None:
            ap.imageURL = images.get_serving_url(ap.imageKey)
            ap.put()
        if ',' in ap.domains:

            do = [ str(a).replace(' ', '') for a in ap.domains.split(',')]
        else:
            do= [ap.domains.replace(' ','')]
        if getDomainFromUrl(domain) in do:
            image_url = ap.imageURL
        else:
            pass
    if image_url==None:
        image_url = 'http://www.google.com/s2/favicons?domain='+domain

    return redirect(image_url)


################33
##### USER AUTHENTIFICATION
################
#local auth methods
def getUserInfoGoogle(credentials):
    user_info_service = discovery.build(
        serviceName='oauth2',
        version='v2',
        http=credentials.authorize(httplib2.Http()))
    userInfo={}
    user_info_ = None
    try:
        user_info_ = user_info_service.userinfo().get().execute()
    except:
        print_exc()
    if user_info_ and user_info_.get('id'):
        print user_info_
        userInfo['source']='google'
        userInfo['username']=user_info_['name']
        userInfo['picture']=user_info_['picture']
        userInfo['id']=str(user_info_['id'])

    return userInfo
def getUserInfoFacebook(cred):
    user_info = {}
    try:
        user_info['source']='facebook'
        user_info['username']=cred['name']
        user_info['picture']=cred['picture']['data']['url']
        user_info['id']=str(cred['id'])
    except:
        user_info=None
    return user_info

@app.route("/login-google")
def auth_login():
    if 'ext-user' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    #credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    #if credentials.access_token_expired:
    #    return flask.redirect(flask.url_for('oauth2callback'))
    if 1==1: #else:
        u = 1#getUserInfoGoogle(credentials)
        if u!=None:
            return flask.redirect(flask.url_for('edit'))
        else:
            return flask.redirect(flask.url_for('auth_logout'))
@app.route('/oauth2callback')
def oauth2callback():

    signup=False

    flow = client.flow_from_clientsecrets(
        'client_secrets.json',
        scope='https://www.googleapis.com/auth/userinfo.profile',
        redirect_uri=flask.url_for('oauth2callback', _external=True))
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        #flask.session['credentials']=credentials.to_json()
        u = getUserInfoGoogle(credentials)
        flask.session['ext-user']= str(u['id'])
        flask.session['ext-user-s']=u['source']
        l = sp_data.ExternalUser.query()
        g_user = [f for f in l if f.source=='google' and f.userID==u["id"] ]
        if len(g_user)>0:
            g_user[0].thumbnail=u['picture']
            g_user[0].put()
        else:
            signup=True
            fb = sp_data.ExternalUser(source='google', userID=u['id'],username=u['username'],thumbnail=u['picture'])
            fb.put()
        resp = make_response(flask.redirect(flask.url_for('edit')))
        resp.set_cookie('ext-user', u['id'])
        resp.set_cookie('ext-user-s',u['source'])
        resp.set_cookie('first-login',str(signup))
        return resp

@app.route("/login-fb")
def auth_login_fb():
    if 'ext-user' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback_fb'))

    return redirect(flask.url_for('auth_logout'))
@app.route('/oauth2callback-fb')
def oauth2callback_fb():

    signup=False


    if 'code' not in flask.request.args and 'token' not in flask.request.args:
        auth_uri = "https://www.facebook.com/dialog/oauth?client_id=153041951709457&scope=public_profile&redirect_uri=http://startpage-1072.appspot.com/oauth2callback-fb"
        return flask.redirect(auth_uri)
    elif 'code' in flask.request.args:
        auth_code = flask.request.args.get('code')

        #e
        expired=False
        #get tokens
        try:
            app_token_uri = '''https://graph.facebook.com/v2.4/oauth/access_token?client_id=153041951709457&redirect_uri=http://startpage-1072.appspot.com/oauth2callback-fb&client_secret=41c6a4277b9d0dba15428c139d99bf68&grant_type=client_credentials'''
            h = httplib2.Http()
            r, content = h.request(app_token_uri, "GET")
            app_tok = json.loads(content)
        except:
            expired=True
            #not correct, but it's allright for now
        try:
            token_uri = '''https://graph.facebook.com/v2.4/oauth/access_token?client_id=153041951709457&redirect_uri=http://startpage-1072.appspot.com/oauth2callback-fb&client_secret=41c6a4277b9d0dba15428c139d99bf68&code={}
            '''.format(auth_code)
            r2, content2 = h.request(token_uri, "GET")
            tok = json.loads(content2)
        except:
            expired=True #now that's accurate

        if expired == False:
            try:
                #verify token
                print tok, app_tok
                dat_uri = 'https://graph.facebook.com/debug_token?input_token={0}&access_token={1}'.format(tok['access_token'],app_tok['access_token'])
                r3, content3 = h.request(dat_uri, "GET")
                dat = json.loads(content3)
                if "data" in dat and "user_id" in dat['data']:
                    #get user data
                    data_uri= 'https://graph.facebook.com/{0}?access_token={1}&fields=name,id,picture'.format(dat['data']['user_id'],app_tok['access_token'])
                    r4, content4 = h.request(data_uri, "GET")
                    data = json.loads(content4)

                    #This is a user!!!!!
                    u = getUserInfoFacebook(data)
                    flask.session['ext-user']= str(u['id'])
                    flask.session['ext-user-s']=u['source']
                    l = sp_data.ExternalUser.query()
                    fb_user = [f for f in l if f.source=='facebook' and f.userID==u['id'] ]
                    if len(fb_user)>0:
                        fb_user[0].thumbnail=u['picture']
                        fb_user[0].put()
                    else:
                        signup=True
                        fb = sp_data.ExternalUser(source='facebook', userID=data['id'],username=data['name'],thumbnail=u['picture'])
                        fb.put()
                    resp = make_response(flask.redirect(flask.url_for('edit')))
                    resp.set_cookie('ext-user', u['id'])
                    resp.set_cookie('ext-user-s',u['source'])
                    resp.set_cookie('first-login',str(signup))
                    return resp
                else:
                    print "no data"
                    return flask.redirect(flask.url_for('auth_login'))
            except:
                print_exc()
                print ""
                return flask.redirect(flask.url_for('auth_login_fb'))
        elif expired ==True:
            print "expired"
            return flask.redirect(flask.url_for('auth_login_fb'))
    elif 'token' in flask.request.args:
        return flask.request.args['token']
@app.route("/logout")
def auth_logout():
    if 'ext-user' in flask.session:
        flask.session.pop("ext-user")
        flask.session.pop('ext-user-s')
    resp = make_response(flask.redirect(flask.url_for('login')))
    resp.set_cookie('ext-user',expires=0)
    resp.set_cookie('ext-user-s',expires=0)
    return resp


#####
# Errors
####
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
