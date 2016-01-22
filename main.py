# Copyright 2015 Mark Spurgeon
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import flask
from flask import Flask
from flask import g, make_response, request, current_app,send_from_directory,render_template,redirect,url_for, Markup, Response, session, Markup
from werkzeug import parse_options_header
from flask.ext.cache import Cache

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

import uuid

import app_list
from plugins import plugins1 as plugins
from plugins import browsers as sp_browsers
from plugins import apikeys
import sp_data

app = Flask(__name__)
app.config['DEBUG'] = False
app.secret_key = str(uuid.uuid4())
cache = Cache(app,config={'CACHE_TYPE': 'gaememcached'})


# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
def checkUserLoggedIn():
    user=False
    user_type=''
    user_info=None
    #print flask.session['ext-user']
    cookieAdd = "&key=" + apikeys.keys['self']
    if request.cookies.has_key("sp-user"):
        ext = request.cookies.get('sp-user').replace(cookieAdd,'')
        try :
            sp_item = sp_data.ExternalUser.get_by_id(int(ext))
            if sp_item:
                user = True
                user_info = sp_item.to_dict()
                user_info['user-id']=sp_item.key.id()
        except:pass
    else: pass
    return (user, user_info)
def jsonResponse(json_dict):
    resp = Response(json.dumps(json_dict,indent=4, separators=(',', ': ')), mimetype="application/json")
    resp.headers['Access-Control-Allow-Origin']="*"
    return resp

@app.route('/')
def index():
    #return redirect(url_for("signup"))
    return render_template('index.html')
@app.route('/home')
def homepage():
    return render_template('index.html')
@app.route('/robots.txt')
def bots():
    return render_template('robots.txt')

@app.route('/_data_info')
@cache.cached(timeout=7200)
def info():
    l = [ i for i in sp_data.ExternalUser.query()]
    count = len(l)
    l2 = [ i for i in sp_data.appIconProposed.query()]
    count2 = len(l2)
    return render_template('data.html', userCount=count,iconCount=count2 )

@app.route('/sitemap')
def index_sitemap():
    return render_template('sitemap.html')
@app.route('/terms')
def tos():
    return render_template("tos.html")
@app.route('/privacy')
def privacy():
    return render_template("privacy.html")
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
    return render_template('browsers/firefox.html')
@app.route('/browsers/chrome')
def browsers_c():
    return render_template('browsers/chrome.html')
@app.route('/browsers/safari')
def browsers_s():
    return render_template('browsers/safari.html')
@app.route('/browsers/ie')
def browsers_e():
    return render_template('browsers/ie.html')
@app.route('/browsers/opera')
def browsers_o():
    return render_template('browsers/opera.html')
@app.route('/browsers/other')
def browsers_other():
    return render_template('browsers/other.html')
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
    return redirect(url_for('edit'))

@app.route('/<id_>')
def sp_short(id_):
    #sp_l = sp_data.ExternalUser.query()
    sp_item = sp_data.ExternalUser.get_by_id(int(id_))
    if sp_item:
        user = sp_item
        theme = user.themeName
        apps = user.linksList
        apps = sorted(apps, key=lambda k: k['position'])
        a_list = []
        for a in apps :
            if a['icon'].startswith('icon:'):
                ur  = a['icon'].replace('icon:','')
                a['icon']='/icons/get?url='+ur
        img_url =  str(user.backgroundImageURL)+"=s0"#"http://startpage-1072.appspot.com/image/"+str(u[0].backgroundImageKey)
        #md = markdown.Markdown()
        title = user.spTitle #Markup(md.convert(u[0].spTitle))
        manifest_url = "http://startpage-1072.appspot.com/manifest/{0}/{1}".format(user.source,user.userID)

        #search browser
        if not user.searchBrowser:
            user.searchBrowser = 'google'
            user.put()
        if user.searchBrowser in sp_browsers.browserOptions:
            se = user.searchBrowser
        else:
            se = sp_browsers.defaultBrowser
        se_info = sp_browsers.browsers[se]
        searchEngine = user.searchBrowser
        searchEngineURL = se_info['url']
        searchEngineArg_search = se_info['#search']


        resp = make_response(render_template('sp.html',title=title,apps=apps, theme=theme,img=img_url,manifest=manifest_url,searchEngine = searchEngine,searchEngineURL =searchEngineURL,searchEngineArg_search=searchEngineArg_search))
        resp.set_cookie('first-login',str(False))
        return resp
    else:
        abort(404)


@app.route('/firefox_addon/<id_>')
def sp_firefox_addon(id_):
    sp_item = sp_data.ExternalUser.get_by_id(int(id_))
    if sp_item:
        user=sp_item
        theme = user.themeName
        apps = user.linksList
        apps = sorted(apps, key=lambda k: k['position'])
        a_list = []
        for a in apps :
            if a['icon'].startswith('icon:'):
                ur  = a['icon'].replace('icon:','')
                a['icon']='/icons/get?url='+ur
        if user.backgroundImageURL:
            img_url =  str(user.backgroundImageURL)+"=s0"#"http://startpage-1072.appspot.com/image/"+str(u[0].backgroundImageKey)
        else:
            img_url=''
        #md = markdown.Markdown()
        title = user.spTitle #Markup(md.convert(u[0].spTitle))
        manifest_url = "http://startpage-1072.appspot.com/manifest/{0}/{1}".format(user.source,user.userID)

        resp = make_response(render_template('sp_firefox_addon.html',title=title,apps=apps, theme=theme,img=img_url,manifest=manifest_url))
        resp.set_cookie('first-login',str(False))
        return resp
    else:
        abort(404)


@app.route('/resources/zipfile/<id_>')
def sp_zip(id_):
    sp_item = sp_data.ExternalUser.get_by_id(int(id_))
    if sp_item:
        import zipfile
        import urllib2
        import StringIO
        ##create zip file object
        output = StringIO.StringIO()
        z = zipfile.ZipFile(output,'w')
        ## add static files
        # -> js
        jq = urllib2.urlopen('http://that.startpage.rocks/static/js/jquery.js').read()
        z.writestr("js/jquery.min.js",jq)
        js = urllib2.urlopen('http://that.startpage.rocks/static/js/main-local.js').read()
        z.writestr("js/main.js",js)
        # -> css
        css = urllib2.urlopen('http://that.startpage.rocks/static/styles/main.css').read()
        z.writestr("css/main.css",css)
        if sp_item.themeName !="white":
            css2 = urllib2.urlopen('http://that.startpage.rocks/static/styles/{}Theme.css'.format(sp_item.themeName)).read()
        else:
            css2=""
        z.writestr("css/theme.css",css2)
        # -> background image
        bg = urllib2.urlopen(sp_item.backgroundImageURL+"=s0").read()
        z.writestr("image.png",bg)

        ## generate html

        user = sp_item
        theme = user.themeName
        apps = user.linksList
        apps = sorted(apps, key=lambda k: k['position'])
        a_list = []
        for a in apps :
            if a['icon'].startswith('icon:'):
                ur  = a['icon'].replace('icon:','')
                a['icon']='http://that.startpage.rocks/icons/get?url='+ur
        img_url =  str(user.backgroundImageURL)+"=s0"#"http://startpage-1072.appspot.com/image/"+str(u[0].backgroundImageKey)
        #md = markdown.Markdown()
        title = user.spTitle #Markup(md.convert(u[0].spTitle))
        #manifest_url = "http://that.startpage.rocks/resources/manifest/{}".format(int(id_))

        #search browser
        if not user.searchBrowser:
            user.searchBrowser = 'google'
            user.put()
        if user.searchBrowser in sp_browsers.browserOptions:
            se = user.searchBrowser
        else:
            se = sp_browsers.defaultBrowser
        se_info = sp_browsers.browsers[se]
        searchEngine = user.searchBrowser
        searchEngineURL = se_info['url']
        searchEngineArg_search = se_info['#search']
        html = render_template('sp-local.html',
                                title=title,
                                apps=apps,
                                theme=theme,
                                img=img_url,
                                searchEngine = searchEngine,
                                searchEngineURL =searchEngineURL,
                                searchEngineArg_search=searchEngineArg_search)
        html = html.encode('utf-8')
        z.writestr("index.html",html)
        z.close()
        #response
        resp = Response(output.getvalue())
        resp.headers['Content-Type'] = 'application/zip'
        resp.headers['Content-Disposition'] = 'attachment; filename=startpage.zip'
        return resp
    else:
        abort(404)
@app.route('/resources/manifest/<id_>')
def sp_manifest(id_):
    sp_item = sp_data.ExternalUser.get_by_id(int(id_))
    if sp_item:
        user=sp_item
        img =   str(user.backgroundImageURL)+"=s0"
        apps = user.to_dict()['linksList']
        theme = user.themeName
        resp = Response(render_template('manifest.html', img=img,apps=apps,theme=theme))
        resp.headers["Content-Type"]="text/cache-manifest"
        resp.headers["Cache-Control"]="max-age=0, no-cache, public"
        return resp
    else:
        abort(404)
@app.route('/resources/json/<id_>')
def sp_debug(id_):
    sp_item = sp_data.ExternalUser.get_by_id(int(id_))
    if sp_item:
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

#Choose a theme
@app.route('/setup/3')
def setup_three():
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:
            #url = '/sp/{0}/{1}'.format(us[0].source,us[0].userID)
            bg_image = us[0].backgroundImageURL
            return render_template('setup/3.html',bg_image=bg_image)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


#Add websites
@app.route('/setup/4')
def setup_four():
    return redirect(url_for('setup_five'))



#Enjoy
@app.route('/setup/5')
def setup_five():
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:
            url = 'http://that.startpage.rocks/{}'.format(us[0].key.id())
            return render_template('setup/5.html',url=url)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

#####
## Startpage Edition
#####

@app.route("/add")
def edit_add():
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        try:
            user = [ue for ue in usr if str(ue.source)==str(u_i['source']) and str(ue.userID)==u_i['userID']][0]
            return render_template("edit-add.html")
        except:
            return render_template("edit-add-error.html")
    else:
        return render_template("edit-add-error.html")
@app.route('/edit')
def edit():
    msg = request.args.get('message')
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [ue for ue in usr if str(ue.source)==str(u_i['source']) and str(ue.userID)==u_i['userID']]
        if len(us)>0:
            if us[0].backgroundImageURL:
                img = us[0].backgroundImageURL+"=s0"
            else:
                img=''
            theme =  us[0].themeName
            title =  us[0].spTitle
            apps = us[0].linksList
            apps = sorted(apps, key=lambda k: k['position'])
            for a in apps :
                if a['icon'].startswith('icon:'):
                    ur  = a['icon'].replace('icon:','')
                    a['icon']='/icons/get?url='+ur
            linkUrl = "http://that.startpage.rocks/"+str(us[0].key.id())
            zipUrl = "http://that.startpage.rocks/resources/zipfile/"+str(us[0].key.id())
            uploadUri = blobstore.create_upload_url('/config/upload-bg')

            searchEngine = us[0].searchBrowser
            searchEngineOptions = sp_browsers.browserOptions

            if request.cookies.has_key('first-login') and request.cookies.get('first-login')==str(True):
                return redirect(url_for('setup_one'))
            else:
                return render_template('edit.html', user=u_i, upload_bg=uploadUri, title = title, img = img, theme= theme, apps = apps,linkUrl=linkUrl, message=msg,searchEngine = searchEngine,searchEngineOptions = searchEngineOptions, zipUrl=zipUrl)
    else:
        return redirect(url_for('login'))
@app.route('/edit-dummy')
def edit_du():
    linkUrl = "http://that.startpage.rocks/"
    searchEngine = "google"
    searchEngineOptions = sp_browsers.browserOptions
    return render_template('edit.html',user={'usermane':"Dummy"}, upload_bg="", title = "KA", img = "", theme= "white", apps = [{'position':1, 'icon':'','display_name':"DUmmy",'url':'tralala'}],linkUrl=linkUrl, message="",searchEngine = searchEngine,searchEngineOptions = searchEngineOptions,zipUrl="/")


##config changes [backend]
@app.route('/config/upload-bg',methods=['POST'])
def cfg_upload_bg():
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:
            user = us[0]
            try:
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
            except:
                return redirect(url_for('edit',message="Error. Sorry, we could not upload this image.")+"#image")
        else:
            if request.cookies.has_key('first-login') and request.cookies.get('first-login')==str(True):

                return redirect(url_for('setup_three'))
            else:
                return jsonResponse({'status':'error'})
    else:
        return redirect(url_for('login'))


#TODO : private -> post
@app.route('/config/add-website',methods=['POST'])
def cfg_add_website():

    url  = request.form.get('url')
    if url.startswith('http://') or url.startswith('https://'):
        pass
    else:
        url = "http://"+url
    title = ""#request.args.get('title')


    u, u_i = checkUserLoggedIn()
    if u and u_i:



        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:

            user = us[0]


            #redirect
            redi  = request.args.get('redirect')
            if redi and redi!="":
                redi = str(redi).replace("<user>",str(user.key.id()))
            else:
                redi=url_for('edit',message='Success! The website has been added!')+"#apps"


            try:
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
                    d = par.find('link',attrs={'rel':'icon','sizes':'128x128'})
                    if not d:
                        d = par.find('link',attrs={'rel':'icon','sizes':'96x96'})
                    if not d:
                        d = par.find('link',attrs={'rel':'icon','sizes':'64x64'})
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
                    from plugins import names
                    if names.colors[the_title[0].lower()]:
                        bg_color=names.colors[the_title[0].lower()]
                    else:
                        bg_color="#F4D03F"


                else:
                    bg_color="rgb(30,30,30)"
                ##
                wa_list = user.linksList#json.loads(user.linksList)
                new_webapp = {'url':url,
                            'icon':img_url,
                            'display_name':the_title,
                            'bg_color':bg_color,
                            'position':len(wa_list)+1}
                wa_list.append(new_webapp)
                user.linksList = wa_list
                user.put()
                return redirect(redi)
                #return jsonResponse({'status':'ok','url':url,'img':img_url,'title':the_title})
            except:
                wa_list = user.linksList#json.loads(user.linksList)
                new_webapp = {'url':url,
                            'icon':"letter",
                            'display_name':"UNTITLED",
                            'bg_color':"#F4D03F",
                            'position':len(wa_list)+1}
                wa_list.append(new_webapp)
                user.linksList = wa_list
                user.put()
                return redirect(redi)
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
    new_title = request.form.get('value')

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
            return redirect(url_for('edit',message='Success! The Website has been deleted.')+"#apps")
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
            if request.cookies.has_key('first-login') and request.cookies.get('first-login')==str(True):
                return redirect(url_for('setup_four'))
            else:
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

@app.route('/config/change-search-engine',methods=['POST'])
def cfg_change_search_engine():
    u, u_i = checkUserLoggedIn()
    if u and u_i:
        usr = sp_data.ExternalUser.query()
        us = [u for u in usr if str(u.source)==str(u_i['source']) and str(u.userID)==u_i['userID']]
        if len(us)>0:
            user = us[0]

            new_browser = str(request.form.get('value'))

            from plugins import browsers as sp_browsers

            if new_browser in sp_browsers.browserOptions:
                user.searchBrowser = new_browser
                user.put()
                return redirect(url_for('edit',message="Success! You've changed you search engine.")+"#search")
            else:
                return redirect(url_for('edit',message="Error.. Somehow, the search engine you've chosen is not valid")+"#search")




        else:
            return redirect(url_for('edit',message="Error.. You are not logged in"))
    else:
        return redirect(url_for('edit',message="Error.. You are not logged in"))
####
# Search Functio
####
def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return (path + args).encode('utf-8')

@app.route('/search')
@cache.cached(timeout=7200, key_prefix=make_cache_key)
def search_():
    query = request.args['q']
    f, resp = plugins.pluginFilter(query)
    if f == 'found':
        return jsonResponse({'status':'ok','responseType':'plugin-results','results':resp})
    elif f=='not-found':
        return jsonResponse({'status':'ok','responseType':'plugins-available','results':resp})


@app.route('/emails')
def emails():
    a = request.args.get('key')
    if a:

        from plugins import apikeys
        if str(a)==str(apikeys.keys['self']):
            l = [e.email for e in sp_data.ExternalUser.query() if e.email!=None]
            text = ""
            for e in l:
                text+="<p>"
                text+=e
                text+="</p>"
                text+=" "
            return text
        else:
            return jsonResponse({'status':'error', 'details':'key is not valid'})
    else:
        return jsonResponse({'status':'error', 'details':"please add a 'key' argument with the right key.."})
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
@app.route('/icons/')
def icons():
    uploadUri = blobstore.create_upload_url('/icons/add')
    q = sp_data.appIconProposed.query()
    icoList = [{'imageUrl':l.imageURL,'domains':[e.replace(' ','') for e in l.domains.split(',')]} for l in q]
    return render_template('icons.html', uploadUri=uploadUri, icons=icoList)
@app.route('/admin/icons/')
def admin_icons():
    q = sp_data.appIconProposed.query()
    icoList = [{'imageUrl':l.imageURL,'domains':[e.replace(' ','') for e in l.domains.split(',')], 'iconID':l.key.id()} for l in q]
    return render_template('icons-auth.html', icons=icoList)
@app.route('/admin/icons/<id_>')
def admin_icon_edit(id_):
    l = sp_data.appIconProposed.get_by_id(int(id_))
    icon = {'imageUrl':l.imageURL,'domains':l.domains, 'iconID':l.key.id()}
    uploadUri = blobstore.create_upload_url('/admin/icons/{}/change'.format(str(l.key.id())))
    return render_template('icon-edit.html', uploadUri=uploadUri, icon=icon)

@app.route('/admin/icons/<id_>/delete')
def admin_delete_icon(id_):
    u, u_i = checkUserLoggedIn()
    from plugins import admin_users
    admin_usrs = admin_users.users
    if u and u_i and str(u_i['user-id']) in admin_usrs :
        item = sp_data.appIconProposed.get_by_id(int(id_))
        item.key.delete()
        return redirect(url_for('admin_icons'))
    else:
        return redirect(url_for('admin_icons'))
@app.route('/admin/icons/<id_>/change', methods=['POST'])
def admin_edit_icon(id_):
    u, u_i = checkUserLoggedIn()
    from plugins import admin_users
    admin_usrs = admin_users.users
    if u and u_i and str(u_i['user-id']) in admin_usrs :
        image = request.files.get('icon')
        header = image.headers['Content-Type']
        parsed_header = parse_options_header(header)
        blob_key = parsed_header[1]['blob-key']
        theKey =BlobKey(blob_key)

        item = sp_data.appIconProposed.get_by_id(int(id_))

        theDomains = item.domains.split(',')
        theParsedDomains = []
        from plugins import domains
        for dom in theDomains:
            newdo = domains.parseDomain(dom)
            if newdo!=None and newdo!=' ' and newdo!='\n':
                theParsedDomains.append(newdo)
        if len(theParsedDomains)>0:
            domainslist = ""
            for do in theParsedDomains:
                domainslist+=do+","

            item.domains = domainslist
            try:
                item.imageURL=images.get_serving_url(blob_key)
                images.delete_serving_url(item.imageKey)
                item.imageKey=theKey
            except:
                pass
            item.put()
            return redirect(url_for('admin_icons'))
        else:
            return redirect(url_for('admin_icons'))
    else:
        return redirect(url_for('admin_icons'))

@app.route('/icons/add', methods=['POST'])
def add_icon():
    domainlist = request.form.get('domains')
    image = request.files.get('icon')
    header = image.headers['Content-Type']
    parsed_header = parse_options_header(header)
    blob_key = parsed_header[1]['blob-key']
    theKey =BlobKey(blob_key)
    theDomains = domainlist.split(',')
    theParsedDomains = []
    from plugins import domains
    for dom in theDomains:
        newdo = domains.parseDomain(dom)
        if newdo!=None and newdo!=' ' and newdo!='\n':
            theParsedDomains.append(newdo)
    if len(theParsedDomains)>0:
        domainslist = ""
        for do in theParsedDomains:
            domainslist+=do+","
        newDomain = sp_data.appIconProposed(domains=domainslist[:-1], imageKey=theKey, imageURL=images.get_serving_url(blob_key))
        newDomain.put()
        return redirect(url_for('icons'))
    else:
        return redirect(url_for('icons'))
'''
@app.route('/icons/reset')
def reset_icons():
    from plugins import domains
    a = sp_data.appIconProposed.query()
    all_icons = []
    for i in a :

        dom = [a.replace(' ',"") for a in i.domains.split(',')]
        new_dom = ""
        for d in dom:
            new = domains.parseDomain(d)
            if new!=None:
                new_dom+=new
                new_dom+=","
            else:
                pass
            all_icons.append(new_dom[:-1])
        if new_dom!='':
            i.domains = new_dom[:-1]
            i.put()
        else:
            i.key.delete()

    return jsonResponse({'status':'ok',"results":all_icons})
'''
@app.route('/icons/get')
@cache.cached(timeout=86400, key_prefix=make_cache_key)
def get_icon():
    domain = request.args.get('url')
    s = sp_data.appIconProposed.query()
    image_url = None
    for ap in s:
        if ap.imageURL==None:
            ap.imageURL = images.get_serving_url(ap.imageKey)
            ap.put()
        if ',' in ap.domains:

            do = [ str(a).replace(' ', '').replace('\n', '') for a in ap.domains.split(',')]
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
        userInfo['email']=user_info_['email']
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
        user_info['email']=cred['email']
        user_info['picture']=cred['picture']['data']['url']
        user_info['id']=str(cred['id'])
    except:
        user_info=None
    return user_info
def getUserInfoGithub(cred):
    user_info = {}
    try:
        user_info['source']='github'
        user_info['username']=cred['name']
        user_info['email']=cred['email']
        user_info['picture']=cred['avatar_url']
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
        scope='https://www.googleapis.com/auth/userinfo.email',
        redirect_uri=flask.url_for('oauth2callback', _external=True))
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        #flask.session['credentials']=credentials.to_json()
        u = getUserInfoGoogle(credentials)
        l = sp_data.ExternalUser.query()
        g_user = [f for f in l if f.source=='google' and f.userID==u["id"] ]
        if len(g_user)>0:
            g_user[0].email=u['email']
            g_user[0].thumbnail=u['picture']
            g_user[0].put()

            userId = g_user[0].key.id()
        else:
            signup=True
            fb = sp_data.ExternalUser(source='google', userID=u['id'],username=u['username'],thumbnail=u['picture'], email=u['email'])
            fb.put()
            userId = fb.key.id()
        # expiration date
        import datetime
        expire_date = datetime.datetime.now()
        expire_date = expire_date + datetime.timedelta(days=90)

        #cookie content
        cookieAdd = "&key=" + apikeys.keys['self']

        cookieContent = str(userId)+cookieAdd

        #
        resp = make_response(flask.redirect(flask.url_for('edit')))
        resp.set_cookie('sp-user', cookieContent,expires=expire_date)
        resp.set_cookie('ext-user-s',u['source'],expires=expire_date)
        resp.set_cookie('first-login',str(signup))
        return resp

@app.route("/login-fb")
def auth_login_fb():
    if 'ext-user' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback_fb'))

    return redirect(flask.url_for('auth_logout'))
@app.route('/oauth2callback-fb')
def oauth2callback_fb():

    from plugins import apikeys
    fb_key=apikeys.keys['facebook']

    signup=False


    if 'code' not in flask.request.args and 'token' not in flask.request.args:
        auth_uri = "https://www.facebook.com/dialog/oauth?client_id=153041951709457&scope=public_profile,email&redirect_uri=http://that.startpage.rocks/oauth2callback-fb"
        return flask.redirect(auth_uri)
    elif 'code' in flask.request.args:
        auth_code = flask.request.args.get('code')

        #e
        expired=False
        #get tokens
        try:
            app_token_uri = '''https://graph.facebook.com/v2.4/oauth/access_token?client_id=153041951709457&redirect_uri=http://that.startpage.rocks/oauth2callback-fb&client_secret={0}&grant_type=client_credentials'''.format(fb_key)
            h = httplib2.Http()
            r, content = h.request(app_token_uri, "GET")
            app_tok = json.loads(content)
        except:
            expired=True
            #not correct, but it's allright for now
        try:
            token_uri = '''https://graph.facebook.com/v2.4/oauth/access_token?client_id=153041951709457&redirect_uri=http://that.startpage.rocks/oauth2callback-fb&client_secret={0}&code={1}
            '''.format(fb_key,auth_code)
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
                    data_uri= 'https://graph.facebook.com/{0}?access_token={1}&fields=name,id,picture,email'.format(dat['data']['user_id'],app_tok['access_token'])
                    r4, content4 = h.request(data_uri, "GET")
                    data = json.loads(content4)

                    #This is a user!!!!!
                    u = getUserInfoFacebook(data)
                    flask.session['ext-user']= str(u['id'])
                    flask.session['ext-user-s']=u['source']
                    l = sp_data.ExternalUser.query()
                    fb_user = [f for f in l if f.source=='facebook' and f.userID==u['id'] ]
                    if len(fb_user)>0:
                        fb_user[0].email=u['email']
                        fb_user[0].thumbnail=u['picture']
                        fb_user[0].put()

                        userId = fb_user[0].key.id()
                    else:
                        signup=True
                        fb = sp_data.ExternalUser(source='facebook', userID=data['id'],username=data['name'],thumbnail=u['picture'], email=u['email'])
                        fb.put()
                        userId = fb.key.id()
                    # expiration date
                    import datetime
                    expire_date = datetime.datetime.now()
                    expire_date = expire_date + datetime.timedelta(days=90)

                    #cookie content
                    cookieAdd = "&key=" + apikeys.keys['self']
                    cookieContent = str(userId)+cookieAdd

                    #
                    resp = make_response(flask.redirect(flask.url_for('edit')))
                    resp.set_cookie('sp-user',cookieContent,expires=expire_date)
                    resp.set_cookie('ext-user-s',u['source'],expires=expire_date)
                    resp.set_cookie('first-login',str(signup))
                    return resp
                else:
                    print "no data"
                    return flask.redirect(flask.url_for('auth_login'))
            except:
                print_exc()
                return flask.redirect(flask.url_for('auth_login_fb'))
        elif expired ==True:
            print "expired"
            return flask.redirect(flask.url_for('auth_login_fb'))
    elif 'token' in flask.request.args:
        return flask.request.args['token']
#twitter
@app.route("/login-twit")
def auth_login_twit():
    if 'ext-user' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback_twit'))

    return redirect(flask.url_for('auth_logout'))
@app.route('/oauth2callback-twit')
def oauth2callback_twit():

    from plugins import apikeys

    twit_key=apikeys.keys['twitter']
    twit_sec_key=apikeys.keys['twitter_secret']
    twit_token=apikeys.keys['twitter_token']
    twit_sec_token=apikeys.keys['twitter_secret_token']
    signup=False


    if 'code' not in flask.request.args and 'token' not in flask.request.args:
        import httplib2
        import urllib
        oauth="http%3A%2F%2Fbeta-dot-that-startpage.appspot.com%2Foauth2callback-twit"
        auth_uri = "https://api.twitter.com/oauth/request_token"
        h = httplib2.Http()
        data = urllib.urlencode({'oauth_callback':oauth,"oauth_consumer_key":twit_key,"oauth_token":twit_token})
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        r, content = h.request(auth_uri, "POST", data,headers)
        return content
        #return flask.redirect(auth_uri,code=307)
    elif 'code' in flask.request.args:
        auth_code = flask.request.args.get('code')

        #e
        expired=False
        #get tokens
        try:
            app_token_uri = '''https://graph.facebook.com/v2.4/oauth/access_token?client_id=153041951709457&redirect_uri=http://that.startpage.rocks/oauth2callback-fb&client_secret={0}&grant_type=client_credentials'''.format(fb_key)
            h = httplib2.Http()
            r, content = h.request(app_token_uri, "GET")
            app_tok = json.loads(content)
        except:
            expired=True
            #not correct, but it's allright for now
        try:
            token_uri = '''https://graph.facebook.com/v2.4/oauth/access_token?client_id=153041951709457&redirect_uri=http://that.startpage.rocks/oauth2callback-fb&client_secret={0}&code={1}
            '''.format(fb_key,auth_code)
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
                    data_uri= 'https://graph.facebook.com/{0}?access_token={1}&fields=name,id,picture,email'.format(dat['data']['user_id'],app_tok['access_token'])
                    r4, content4 = h.request(data_uri, "GET")
                    data = json.loads(content4)

                    #This is a user!!!!!
                    u = getUserInfoFacebook(data)
                    flask.session['ext-user']= str(u['id'])
                    flask.session['ext-user-s']=u['source']
                    l = sp_data.ExternalUser.query()
                    fb_user = [f for f in l if f.source=='facebook' and f.userID==u['id'] ]
                    if len(fb_user)>0:
                        fb_user[0].email=u['email']
                        fb_user[0].thumbnail=u['picture']
                        fb_user[0].put()
                    else:
                        signup=True
                        fb = sp_data.ExternalUser(source='facebook', userID=data['id'],username=data['name'],thumbnail=u['picture'], email=u['email'])
                        fb.put()

                    # expiration date
                    import datetime
                    expire_date = datetime.datetime.now()
                    expire_date = expire_date + datetime.timedelta(days=90)
                    #
                    resp = make_response(flask.redirect(flask.url_for('edit')))
                    resp.set_cookie('ext-user', u['id'],expires=expire_date)
                    resp.set_cookie('ext-user-s',u['source'],expires=expire_date)
                    resp.set_cookie('first-login',str(signup))
                    return resp
                else:
                    print "no data"
                    return flask.redirect(flask.url_for('auth_login'))
            except:
                print_exc()
                return flask.redirect(flask.url_for('auth_login_fb'))
        elif expired ==True:
            print "expired"
            return flask.redirect(flask.url_for('auth_login_fb'))
    elif 'token' in flask.request.args:
        return flask.request.args['token']

#github
@app.route("/login-github")
def auth_login_gh():
    if 'ext-user' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback_github'))

    return redirect(flask.url_for('auth_logout'))
@app.route('/oauth2callback-github')
def oauth2callback_github():

    from plugins import apikeys

    git_client_id="5ad12c1688855215b4ad"
    git_client_secret="4eaafce79dceb55c06d0a938f2033d0830cbdff8"
    signup=False
    oauth="http://that.startpage.rocks/oauth2callback-github"

    if 'code' not in flask.request.args and 'token' not in flask.request.args:
        #import random,string
        #N=5
        #ran =''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
        auth_uri = "https://github.com/login/oauth/authorize?client_id={0}&redirect_uri={1}&scope=user".format(git_client_id,oauth)
        return redirect(auth_uri)
        #return flask.redirect(auth_uri,code=307)
    elif 'code' in flask.request.args:
        code = flask.request.args.get('code')
        auth_uri = "https://github.com/login/oauth/access_token?client_id={0}&redirect_uri={1}&code={2}&client_secret={3}".format(git_client_id,oauth,code,git_client_secret)
        print auth_uri
        import httplib2
        h = httplib2.Http()
        r, content = h.request(auth_uri, "GET")
        if content:
            new = "https://api.github.com/user?"+content
            h = httplib2.Http()
            r, content = h.request(new, "GET")
            if content:
                data = json.loads(content)
                #This is a user!!!!!
                u = getUserInfoGithub(data)
                l = sp_data.ExternalUser.query()
                fb_user = [f for f in l if f.source=='github' and f.userID==u['id'] ]
                if len(fb_user)>0:
                    fb_user[0].email=u['email']
                    fb_user[0].thumbnail=u['picture']
                    fb_user[0].put()
                    userId = fb_user[0].key.id()
                else:
                    signup=True
                    fb = sp_data.ExternalUser(source='github', userID=u['id'],username=u['username'],thumbnail=u['picture'], email=u['email'])
                    fb.put()
                    userId = fb.key.id()
                # expiration date
                import datetime
                expire_date = datetime.datetime.now()
                expire_date = expire_date + datetime.timedelta(days=90)

                #cookie content
                cookieAdd = "&key=" + apikeys.keys['self']
                cookieContent = str(userId)+cookieAdd

                #
                resp = make_response(flask.redirect(flask.url_for('edit')))
                resp.set_cookie('sp-user',cookieContent,expires=expire_date)
                resp.set_cookie('ext-user-s',u['source'],expires=expire_date)
                resp.set_cookie('first-login',str(signup))
                return resp

            else:
                return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))

@app.route("/logout")
def auth_logout():
    if 'ext-user' in flask.session:
        flask.session.pop("ext-user")
        flask.session.pop('ext-user-s')
    resp = make_response(flask.redirect(flask.url_for('login')))
    resp.set_cookie('ext-user',expires=0)
    resp.set_cookie('ext-user-s',expires=0)
    resp.set_cookie('sp-user',expires=0)
    return resp


#####
# Errors
####
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return '404 Error', 404
@app.errorhandler(500)
def int_server_error(e):
    return """
    <h1>Internal Server Error</h1>
    <p>The server encountered an internal error and was unable to complete your request. You are probably seeing this because we have reached our daily quota of requests to the datastore. Please come back tomorrow.</p>


    """, 404
