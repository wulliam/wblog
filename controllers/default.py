# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
import random,string
import Image, ImageDraw, io
from gluon.contrib.markdown.markdown2 import markdown
from gluon.storage import Storage

session.blogs = session.blogs or []

def _load_settings_from_cache():
    if session.settings is None:
        print 'set to cache'
        _set_settings_to_cache()
        #pass

def _set_settings_to_cache():
    cache.ram.storage['settings'] = Storage(dict([(r.key, r.value)
                 for r in db().select(db.ray_setting.ALL)]))
    session.settings = cache.ram.storage['settings']

_load_settings_from_cache()

##identifyingCode
def __txt2img(label, imgformat="PNG",
            fgcolor=(0,0,0), bgcolor=(255,255,255),
            rotate_angle=0):
    """Render label as image."""
    imgOut = Image.new("RGBA", (20,49), bgcolor)

    # calculate space needed to render text
    draw = ImageDraw.Draw(imgOut)
    sizex, sizey = draw.textsize(label)

    imgOut = imgOut.resize((sizex,sizey))

    # render label into image draw area
    draw = ImageDraw.Draw(imgOut)
    draw.text((0, 0), label, fill=fgcolor)

    if rotate_angle:
        imgOut = imgOut.rotate(rotate_angle)

    return imgOut

def __random_code():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(5))

def __get_categories():
    return db(db.ray_category).select(orderby=db.ray_category.id,cache=(cache.ram,60*10))

def __get_latest_comments():
    return db(db.ray_comment).select(orderby=~db.ray_comment.created_date,limitby=(0,10),distinct=True,cache=(cache.ram,60*5))

def __get_links():
    return db(db.ray_link.visible == 1).select(orderby=db.ray_link.id,cache=(cache.ram,60*5))

def __calc_pagesize(count):
    totalpage = count / PAGE_SIZE
    if count % PAGE_SIZE != 0:
        totalpage = totalpage + 1
    return totalpage

def __append_share_dict(dict_data):
    total_number_of_blogs = cache.ram('total_number_of_blogs', lambda: db(db.ray_blog).count(), time_expire=60*5)
    total_number_of_comments = cache.ram('total_number_of_comments', lambda: db(db.ray_comment).count(), time_expire=60*5)
    total_number_of_visit = cache.ram('total_number_of_visit', lambda: db(db.ray_count).select().first().count, time_expire=60*5)
    return dict(dict_data.items() + dict(categories=__get_categories(), latest_comments=__get_latest_comments()).items(), links=__get_links(), \
        total_number_of_blogs = total_number_of_blogs, total_number_of_comments = total_number_of_comments, total_number_of_visit = total_number_of_visit)

def __add_extra_identify_code(form):
    form[0].insert(-1, TR(LABEL('Identifing Code', _class='w2p_fw'), INPUT(_name='identifing_code', requires=IS_NOT_EMPTY()), IMG(_src=URL('identifing_code'), _alt='verify code')))

def __validate_extra_identify_code(form):
    if form.vars.identifing_code is None or session.identifing_code is None or form.vars.identifing_code.lower() != session.identifing_code.lower():
        form.errors.message = 'identifing code is incorrect'

def __update_visit_log(func):
    def myfunction(*args, **kv):
        if session.settings.get('enable.visit.log') != str(1):
            return func(*args, **kv)
        try:
            if 'visit' not in request.cookies:
                db.ray_visit.insert(remote_addr=request.env.remote_addr, user_agent=request.env.http_user_agent, created_date=now)
                response.cookies['visit'] = ''.join([request.env.remote_addr,'-',str(now)])
                response.cookies['visit']['expires'] = now + datetime.timedelta(days=1)
                response.cookies['visit']['path'] = '/'
            else:
                pass
            db.ray_visitlog.insert(remote_addr=request.env.remote_addr, visit_url=request.env.path_info, created_date=now)
        finally:
            return func(*args, **kv)
    return myfunction

def __update_blog_count(func):
    def myfunction(*args, **kv):
        if session.settings.get('enable.visit.log') != str(1):
            return func(*args, **kv)
        visit = False
        if request.args(0) is not None:
            blog_id = request.args(0)
            if "blog_ids" in request.cookies and blog_id in request.cookies['blog_ids'].value.split('-'):
                visit = True
            if visit:
                pass
            else:
                row_count = db(db.ray_blog.id == blog_id).select(db.ray_blog.count).first()
                db(db.ray_blog.id == blog_id).update(count = row_count.count + 1 if row_count.count is not None else 1)
                if "blog_ids" not in request.cookies:
                    response.cookies['blog_ids'] = blog_id
                    response.cookies['blog_ids']['expires'] = now + datetime.timedelta(days=1)
                    response.cookies['blog_ids']['path'] = '/'
                else:
                    response.cookies['blog_ids'] = '-'.join([str(request.cookies['blog_ids'].value),blog_id])
                    response.cookies['blog_ids']['path'] = '/'
        return func(*args, **kv)
    return myfunction

def __get_request_number(key_word):
    number = None
    if len(request.args) > 0:
        for var in request.args:
            if var is not None and var.find(key_word) == 0:
                number = int(var.replace(key_word, ''))
    return number


def __get_page_start():
    start = __get_request_number('page_')
    if start is None or start < 1:
        start = 1
    return start - 1

def __get_category_id():
    return __get_request_number('category_')


left_sidebar_enabled = True
PAGE_SIZE = 10

def identifing_code():
    id_code = __random_code()
    session.identifing_code = id_code
    response.headers['Content-Type'] = 'image/PNG'
    response.headers['Pragma'] = 'No-cache'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Expireds'] = 0
    #print id_code
    imgbuff = io.BytesIO()
    __txt2img(id_code).save(imgbuff, 'PNG')
    #print imgbuff.getvalue()
    #print 'io:',imgbuff,len(imgbuff.getvalue())
    #print imgbuff.getvalue()
    __txt2img(id_code).save('out.PNG')
    #return response.stream(imgbuff, chunk_size=len(imgbuff.getvalue()))
    return response.stream(open('out.PNG'))

@cache.action()
@__update_visit_log
def blog():
    if session.visit is None:
        session.visit = True
        ray_count = db(db.ray_count).select().first()
        ray_count.update_record(count = ray_count.count + 1)
    start = __get_page_start()
    #print start,PAGE_SIZE,start*PAGE_SIZE
    blogs = db().select(db.ray_blog.ALL, limitby=(start*PAGE_SIZE, (start + 1)*PAGE_SIZE), orderby=~db.ray_blog.created_date)
    blogs_totalpages = __calc_pagesize(db(db.ray_blog.id > 0).count())
    return __append_share_dict(dict(blogs=blogs,blogs_totalpages = blogs_totalpages, blogs_pageid = start + 1))

@cache.action()
@__update_visit_log
def category():
    start = __get_page_start()
    category_id = __get_category_id()
    selected_category =  db(db.ray_category.id == category_id).select().first()
    blogs = db(db.ray_blog.category_id == selected_category.id).select(limitby=(start*PAGE_SIZE, (start+1)*PAGE_SIZE), orderby=~db.ray_blog.created_date)
    blogs_totalpages = __calc_pagesize(db(db.ray_blog.category_id == selected_category.id).count())
    return __append_share_dict(dict(blogs=blogs,blogs_totalpages = blogs_totalpages, blogs_pageid = start + 1, selected_category = selected_category))

@cache.action()
@__update_visit_log
@__update_blog_count
def view():
    if len(request.args) > 0:
        blog_id = int(request.args(0))
    if blog_id is None:
        raise HTTP(403)
    blog = db(db.ray_blog.id == blog_id).select().first()
    if blog.id not in session.blogs:
        session.blogs.append(blog.id)
        blog.  update_record(count = blog.count + 1)
    #print blog,type(blog)
    comment_form = SQLFORM(db.ray_comment)
    __add_extra_identify_code(comment_form)
    comment_form.vars.created_date = now
    comment_form.vars.blog_id = blog.id
    comment_form.vars.category_id = blog.category_id.id
    comment_form.vars.title = "RE:" + blog.title
    comment_form.vars.comment_id = None
    if comment_form.accepts(request.vars, formname='comment', onvalidation=__validate_extra_identify_code):
        response.flash = 'comment saved'
    elif comment_form.errors:
        response.flash = ' '.join(['comment has errors'] + [ error for error in comment_form.errors])
    else:
        pass
    blog_comments = db(db.ray_comment.blog_id == blog.id).select(orderby=~db.ray_comment.created_date)
    return __append_share_dict(dict(blog=blog,blog_comments = blog_comments,comment_form=comment_form))

@cache.action()
@__update_visit_log
def guestbook():
    guestbook_form = SQLFORM(db.ray_guestbook, fields = ['name', 'email', 'text', 'site'])
    __add_extra_identify_code(guestbook_form)
    if guestbook_form.accepts(request.vars, formname = 'guestbook_form', onvalidation=__validate_extra_identify_code):
        response.flash = 'guestbook saved'
    elif guestbook_form.errors:
        response.flash = ' '.join(['guestbook has errors'] + [ error for error in guestbook_form.errors])
    start = __get_page_start()
    guestbooks = db(db.ray_guestbook).select(limitby=(start*PAGE_SIZE, (start+1)*PAGE_SIZE), orderby=db.ray_guestbook.created_date)
    guestbooks_totalpages = __calc_pagesize(db(db.ray_guestbook).count())
    return __append_share_dict(dict(guestbooks = guestbooks, guestbooks_totalpages = guestbooks_totalpages, guestbooks_pageid = start + 1, guestbook_form = guestbook_form))

## admin
def login_validation(form):
    import hashlib
    #print form.vars.admin_name,form.vars.admin_pass
    #print db((db.ray_admin.admin_name == form.vars.admin_name)).select().first()
    #print hashlib.md5(form.vars.admin_pass).hexdigest()
    #print form.vars.identifing_code.lower(),session.identifing_code.lower()
    __validate_extra_identify_code(form)
    if db((db.ray_admin.admin_name == form.vars.admin_name) \
          & (db.ray_admin.admin_pass == hashlib.md5(form.vars.admin_pass).hexdigest())).select().first() is not None:
        #print 'login done'
        #print form.vars.admin_name,form.vars.admin_pass
        return
    else:
        form.errors = 'login failed'

def create_user():
    import hashlib
    if db(db.ray_admin).select().first() is None:
        db.ray_admin.insert(admin_name='wulliam', admin_pass=hashlib.md5('password').hexdigest())

def login():
    admin_form=FORM(TABLE(TR('Name:', INPUT(_name='admin_name', requires=IS_NOT_EMPTY()), ''),
                          TR('Password', INPUT(_name='admin_pass',  _type='password', requires=IS_NOT_EMPTY()), ''),
                          TR('Identifing Code', INPUT(_name='identifing_code', requires=IS_NOT_EMPTY()), IMG(_src=URL('identifing_code'), _alt='verify code')),
                          TR('', INPUT(_type='submit'), '')))
    if admin_form.accepts(request.vars, formname='admin_form', onvalidation=login_validation):
        session.login = True
        session.username = admin_form.vars.admin_name
        return redirect(URL('admin_category'))
    elif admin_form.errors:
        response.flash = ' '.join(['login failed'] + [ error for error in admin_form.errors])
    return dict(admin_form = admin_form)

def logout():
    if session.login is not None:
        session.login = None
        session.username = None
    return redirect(URL('blog'))

def password_validation(form):
    #print 'pasword_validation:',form.vars.pass1 == form.vars.pass2 and form.vars.pass1 is not None and str(form.vars.pass1).strip()
    if form.vars.pass1 == form.vars.pass2 and form.vars.pass1 is not None and str(form.vars.pass1).strip():
        return
    else:
        form.errors = 'password and re-password is not match'

def change_password():
    import hashlib
    if not check_login():
        return redirect(URL('login'))
        #pass
    if session.login is not None:
        #session.login = None
        password_form = FORM(TABLE(
                            TR('密码', INPUT(_name='pass1', _type='password')),
                            TR('确认密码', INPUT(_name='pass2', _type='password', requires=IS_NOT_EMPTY())),
                            TR('', INPUT(_type='submit',requires=IS_NOT_EMPTY())) ))
    if password_form.accepts(request.vars, formname='password_form', onvalidation=password_validation):
        #ray_admin = db(db.ray_admin).select().first()
        #ray_admin.admin_pass = hashlib.md5(password_form.vars.pass1).hexdigest()
        #db(db.ray_admin).save(ray_admin)
        db(db.ray_admin.admin_name == session.username).update(admin_pass = hashlib.md5(password_form.vars.pass1).hexdigest())
        response.flash = 'password changed'
    elif password_form.errors:
        response.flash = 'password change failed'
    return dict(password_form = password_form)


def check_login():
    return session.login is not None and session.login == True

def preview_blog():
    if not check_login():
        return redirect(URL('login'))
    blog_text = "Empty"
    if request.post_vars['preview_text'] is not None:
        blog_text = markdown(request.post_vars['preview_text'])
    return blog_text

def new_blog():
    if not check_login():
        return redirect(URL('login'))
    blog_form = SQLFORM(db.ray_blog)
    blog_form.vars.created_date = now
    if blog_form.accepts(request.vars, formname='blog_from'):
        response.flash = 'blog saved'
    elif blog_form.errors:
        response.flash = 'blog has errors'
    blog_attachments = db(db.ray_attachment.blog_id==None).select(orderby=~db.ray_attachment.created_date)
    return dict(blog_form=blog_form, blog_comments=None, blog_attachments = blog_attachments)

def edit_blog():
    if not check_login():
        return redirect(URL('login'))
    if request.args(0) is not None:
        blog = db(db.ray_blog.id == request.args(0)).select().first()
        blog_form = SQLFORM(db.ray_blog, record = blog)
    else:
        blog_form = SQLFORM(db.ray_blog)
    blog_form.vars.updated_date = now
    if blog_form.accepts(request.vars, formname='blog_form'):
        response.flash='blog saved'
        return redirect(URL("admin_blog", args=["category_" + request.vars.get("category_id")]))
    elif blog_form.errors:
        response.flash = 'blog has error'
    blog_attachments = db(db.ray_attachment.blog_id==blog.id).select(orderby=~db.ray_attachment.created_date)
    blog_comments = db(db.ray_comment.blog_id == blog.id).select(orderby=~db.ray_comment.created_date)
    return response.render('default/new_blog.html', dict(blog_form = blog_form, blog_comments = blog_comments, blog_attachments = blog_attachments))

def delete_blog():
    if not check_login():
        return redirect(URL('login'))
    if request.args(0) is not None:
        db(db.ray_blog.id == request.args(0)).delete()
        response.flash = 'blog deleted'
    redirect(URL('admin_blog'))


def admin_blog():
    if not check_login():
        return redirect(URL('login'))
    start = __get_page_start()
    categoryId = __get_category_id()
    if categoryId is not None:
        selected_category = db(db.ray_category.id == categoryId).select().first()
    else:
        selected_category = db(db.ray_category).select().first()
    blogs = db(db.ray_blog.category_id == selected_category.id).select(limitby=(start*PAGE_SIZE,(start+1)*PAGE_SIZE), orderby=~db.ray_blog.created_date)
    blogs_totalpages = __calc_pagesize(db(db.ray_blog.category_id == selected_category.id).count())
    return dict(blogs = blogs, selected_category = selected_category, blogs_totalpages = blogs_totalpages, categories=__get_categories(), blogs_pageid = start + 1)


def admin_category():
    if not check_login():
        return redirect(URL('login'))
    if request.args(0) is not None:
        category = db(db.ray_category.id == request.args(0)).select().first()
        category_form = SQLFORM(db.ray_category, record = category)
    else:
        category_form = SQLFORM(db.ray_category)
    if category_form.accepts(request.vars, formname='category'):
        response.flash = 'category saved'
    elif category_form.errors:
        response.flash = 'category has errors'
    return dict(categories=__get_categories(), category_form = category_form)

def edit_category():
    if not check_login():
        return redirect(URL('login'))
    if request.args(0) is not None:
        category = db(db.ray_category.id == request.args(0)).select().first()
        category_form = SQLFORM(db.ray_category, record = category)
    else:
        category_form = SQLFORM(db.ray_category)
    if category_form.accepts(request.vars, formname='category'):
        response.flash = 'category saved'
    elif category_form.errors:
        response.flash = 'category has errors'
    return dict(category_form = category_form)

def delete_category():
    if not check_login():
        return redirect(URL('login'))
    if request.args(0) is not None:
        db(db.ray_category.id == request.args(0)).delete()
        response.flash = 'category deleted'
    redirect(URL('admin_category'))

def admin_links():
    if not check_login():
        return redirect(URL('login'))
    link_form = SQLFORM(db.ray_link)
    if link_form.accepts(request.vars, formname='link_form'):
        response.flash = 'link saved'
    elif link_form.errors:
        response.flash = 'link has error'
    start = __get_page_start()
    if request.args(0) is not None and request.args(0) != 'page':
        link_id = request.args(0)
        link = db(db.ray_link.id == link_id).select().first()
        link_form = SQLFORM(db.ray_link, record = link)
    else:
        link_form = SQLFORM(db.ray_link)
    if link_form.accepts(request.vars, formname = 'link_form'):
        response.flash = 'link saved'
    elif link_form.errors:
        response.flash = 'link has errors'
    links = db(db.ray_link).select(limitby = (start*PAGE_SIZE, (start+1)*PAGE_SIZE), orderby=db.ray_link.id)
    links_totalpages = __calc_pagesize(db(db.ray_link).count())
    return dict(link_form = link_form, links = links, links_totalpages = links_totalpages, links_pageid = start+1)

def admin_settings():
    if not check_login():
        return redirect(URL('login'))
    if request.args(0) is not None:
        setting_id = request.args(0)
	setting = db(db.ray_setting.id == setting_id).select().first()
        setting_form = SQLFORM(db.ray_setting, record = setting)
    else:
        setting_form = SQLFORM(db.ray_setting)
    if setting_form.accepts(request.vars, formname='setting_form'):
       response.flash = 'setting saved'
    elif setting_form.errors:
       response.flash = 'setting have error'
    _set_settings_to_cache()
    return dict(ray_settings=db(db.ray_setting).select(), setting_form=setting_form)

def delete_link():
    if not check_login():
        return redirect(URL('login'))
    if request.args(0) is not None:
        db(db.ray_link.id == request.args(0)).delete()
        response.flash = 'link deleted'
    redirect(URL('admin_links'))


def delete_setting():
    if not check_login():
        return redirect(URL('login'))
    if request.args(0) is not None:
        db(db.ray_setting.id == request.args(0)).delete()
        response.flash = 'settign deleted'
    redirect(URL('admin_settings'))

def admin_guestbook():
    if not check_login():
        return redirect(URL('login'))
    start = __get_page_start()
    if request.args(0) is not None and request.args(0) != 'page':
        guestbook_id = request.args(0)
	guestbook = db(db.ray_guestbook.id == guestbook_id).select().first()
        guestbook_form = SQLFORM(db.ray_guestbook, record = guestbook)
    else:
        guestbook_form = SQLFORM(db.ray_guestbook)
    if guestbook_form.accepts(request.vars, formname='guestbook_form'):
       response.flash = 'guestbook saved'
    elif guestbook_form.errors:
       response.flash = 'guestbook have error'
    guestbooks = db(db.ray_guestbook).select(limitby=(start*PAGE_SIZE, (start+1)*PAGE_SIZE))
    guestbooks_totalpages = __calc_pagesize(db(db.ray_guestbook).count())
    return dict(guestbook_form = guestbook_form, guestbooks = guestbooks, guestbooks_totalpages = guestbooks_totalpages, guestbooks_pageid = start + 1)


def delete_guestbook():
    if not check_login():
        return redirect(URL('login'))
    if request.args(0) is not None:
        db(db.ray_guestbook.id == request.args(0)).delete()
        response.flash = 'guestbook deleted'
    redirect(URL('admin_guestbook'))

def delete_comment():
    if not check_login():
        return redirect(URL('login'))
    blog_id = None
    if request.args(0) is not None:
        blog_id = db(db.ray_comment.id == request.args(0)).select().first().blog_id
        db(db.ray_comment.id == request.args(0)).delete()
        response.flash = 'comment deleted'
    redirect(URL('edit_blog', args=[str(blog_id)]))

def show_attachment():
    if not check_login():
        return redirect(URL('login'))
    if request.args(0) is not None:
        attachment = db(db.ray_attachment.id == request.args(0)).select().first()
    return dict(attachment = attachment)

def new_attachment():
    if not check_login():
        return redirect(URL('login'))
    my_extra_element1 =  SPAN('上传中 ', IMG(_src=URL('static','images/spinner.gif'), _alter="test"), _class='test', _style="display:none;", _id='upload-tip')
    my_extra_element2 =  SPAN('', _class='test', _style="display:none;", _id="upload-tip")
    attachment_form = SQLFORM(db.ray_attachment, fields=['file'] )
    attachment_form[0].insert(-1,my_extra_element1)
    attachment_form[0].insert(-1,my_extra_element2)
    attachment_form.element('input', _type = 'submit')['_style'] = 'display:none'
    if request.vars.file!=None:
        attachment_form.vars.title = request.vars.file.filename
    if attachment_form.vars.title is None:
        attachment_form.vars.title = "default"
    if request.args(0) is not None:
        attachment_form.vars.blog_id = request.args(0)
    #if attachment_form.process().accepted:
    if attachment_form.accepts(request.vars, formname='attachment_form'):
        attachment = db(db.ray_attachment.id == attachment_form.vars.id).select()
        redirect(URL("show_attachment", args=[attachment_form.vars.id]))
    else:
        return dict(attachment_form=attachment_form)

def delete_attachment():
    if not check_login():
        return redirect(URL('login'))
    attachment_id = None
    if request.args(0) is not None:
        db(db.ray_attachment.id == request.args(0)).delete()
        return dict(status="0K")
    else:
        return dict(error="no id")



def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    #return dict(message=T('Hello World'))
    if session.visit is None:
        session.visit = True
        ray_count = db(db.ray_count).select().first()
        ray_count.update_record(count = ray_count.count + 1)
    redirect(URL('blog'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    #print 'download' + str(request.args(0))
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id[
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs bust be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
