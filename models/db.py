# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('google:datastore')              # connect to Google BigTable
                                              # optional DAL('gae://namespace')
    session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
else:                                         # else use a normal relational database
    #db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB ,fake_migrate=True
    db = DAL('mysql://root:@localhost/wblog',migrate_enabled=True,entity_quoting=True)

# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Mail, Auth, Crud, Service, PluginManager, prettydate
mail = Mail()                                  # mailer
auth = Auth(db)                                # authentication/authorization
crud = Crud(db)                                # for CRUD helpers using auth
service = Service()                            # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()                      # for configuring plugins

mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'you@gmail.com'         # your email
mail.settings.login = 'username:password'      # your credentials or None

auth.settings.hmac_key = 'sha512:616072f2-76ca-409a-844c-6e0a48f3f010'   # before define_tables()
#auth.define_tables()                           # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['reset_password'])+'/%(key)s to reset your password'

#########################################################################
## If you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, uncomment and customize following
# from gluon.contrib.login_methods.rpx_account import RPXAccount
# auth.settings.actions_disabled = \
#    ['register','change_password','request_reset_password']
# auth.settings.login_form = RPXAccount(request, api_key='...',domain='...',
#    url = "http://localhost:8000/%s/default/user/login" % request.application)
## other login methods are in gluon/contrib/login_methods
#########################################################################

crud.settings.auth = None        # =auth to enforce authorization on crud

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################
import datetime
now = datetime.datetime.today()

#db = DAL('sqlite://storage.db')

db.define_table('ray_about', 
    Field('title'),
    Field('name'),
    Field('value'),
    Field('description'),
    Field('type'))
    
db.define_table('ray_admin', 
    Field('admin_name', required=True),
    Field('admin_pass', required=True))

db.define_table('ray_category',
    Field('name', required=True),
    Field('corder', 'integer', required=True),
    Field('is_public', default=1, required=True))
        
db.define_table('ray_blog',
    Field('title', required=True),
    Field('text', 'text', required=True),
    Field('category_id', db.ray_category,  required=True),
    Field('created_date', 'datetime', required=True, default=now, writable=False),
    Field('count', 'integer',writable=False,readable=False),
    Field('isMarkdown', default=False, required=True))

db.ray_blog.category_id.requires=IS_IN_DB(db, 'ray_category.id', '%(name)s')
    
db.define_table('ray_comment',
    Field('title', required=True),
    Field('text', required=True),
    Field('name', required=True),
    Field('email', required=True, requires = IS_EMAIL(error_message=T('invalid email!'))),
    Field('created_date', 'datetime', readable=False, writable=False, required=True, default=now),
    Field('blog_id', db.ray_blog, required=True,writable=False,readable=False),
    Field('category_id', db.ray_category, required=True,writable=False,readable=False),
    Field('comment_id', 'integer', writable=False,readable=False))

db.ray_comment.comment_id.type='reference ray_comment'
db.ray_comment.comment_id.requires=IS_NULL_OR(IS_IN_DB(db, 'ray_comment.id', '%(title)s'))

db.define_table('ray_count',
    Field('count', 'integer'))

db.define_table('ray_visit',
    Field('remote_addr'),
    Field('user_agent'),    
    Field('created_date', 'datetime', required=True, default=now))

db.define_table('ray_visitlog',
    Field('remote_addr'),
    Field('visit_url'),
    Field('created_date', 'datetime', required=True, default=now))

    
db.define_table('ray_guestbook',
    Field('name', required=True),
    Field('email', required=True, requires = IS_EMAIL(error_message=T('invalid email!'))),
    Field('text', required=True),
    Field('created_date', 'datetime', required=True, default=now),
    Field('reply'),
    Field('site'))
    
db.define_table('ray_link',
    Field('name', required=True),
    Field('url', required=True),
    Field('description'),
    Field('visible'))

db.define_table('ray_setting',
    Field('key', required=True),
    Field('value', required=True),
    Field('description'))
