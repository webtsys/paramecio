#!/usr/bin/python3

from citoplasma.mtemplates import ptemplate
from modules.admin.models.admin import UserAdmin
from citoplasma.i18n import load_lang, I18n
from citoplasma.urls import make_url, add_get_parameters
from citoplasma.sessions import get_session
from bottle import get,post
from settings import config
from settings import config_admin
from citoplasma.lists import SimpleList
from citoplasma.generate_admin_class import GenerateAdminClass
from citoplasma.httputils import GetPostFiles
from cromosoma.formsutils import show_form, pass_values_to_form
from cromosoma.coreforms import PasswordForm
from importlib import import_module, reload
from bottle import redirect
from collections import OrderedDict

#from citoplasma.login import LoginClass
# Check login

t=ptemplate('admin')

load_lang('admin', 'common')
@get('/'+config.admin_folder)
@get('/'+config.admin_folder+'/<module>')
@post('/'+config.admin_folder+'/<module>')
def home(module=''):
    
    t.clean_header_cache()
    
    #check if login
    
    user_admin=UserAdmin()
    
    s=get_session()
    
    if 'login' in s:
        
        s['id']=s.get('id', 0)
        
        user_admin.conditions=['WHERE id=%s', [s['id']]]
        
        c=user_admin.select_count()
        
        if c>0:
        
            if s['privileges']==2:
                
                #Load menu
                
                menu=OrderedDict()
                
                for key, mod in config_admin.modules_admin.items():
                    if type(mod[1]).__name__!='dict':
                        menu[key]=mod
                    else:
                        menu[key]=mod[0]
                        
                        for subkey, submod in mod[1].items():
                            menu[subkey]=submod
                            #pass
                        
                if module in menu:
                    
                    #Load module
                    
                    new_module=import_module(menu[module][1])
                    
                    if config.reloader:
                        reload(new_module)
                    
                    return t.load_template('admin/content.html', title=menu[module][0], content_index=new_module.admin(t), menu=menu)
                    
                else:
                    return t.load_template('admin/index.html', title=I18n.lang('admin', 'welcome_to_paramecio', "Welcome to Paramecio Admin!!!"), menu=menu)
                
        else:
            
            logout()
            
    else:
        
        user_admin.conditions=['WHERE privileges=%s', [2]]
        
        c=user_admin.select_count()
        
        if c>0:
            
            post={}
            
            user_admin.yes_repeat_password=False

            user_admin.fields['password'].required=True
            
            user_admin.create_forms(['username', 'password'])
            
            forms=show_form(post, user_admin.forms, t, yes_error=False)
            
            return t.load_template('admin/login.phtml', forms=forms)
            
        else:
        
            post={}
            
            set_extra_forms_user(user_admin)
            
            forms=show_form(post, user_admin.forms, t, yes_error=False)

            return t.load_template('admin/register.phtml', forms=forms)

@post('/'+config.admin_folder+'/login')
def login():
    
    user_admin=UserAdmin()
    
    GetPostFiles.obtain_post()
    
    GetPostFiles.post.get('username', '')
    GetPostFiles.post.get('password', '')
    
    username=user_admin.fields['username'].check(GetPostFiles.post['username'])
    
    password=GetPostFiles.post['password'].strip()
    
    user_admin.conditions=['WHERE username=%s', [username]]
    
    arr_user=user_admin.select_a_row_where(['id', 'password', 'privileges'])
    
    if arr_user==False:
        
        return {'error': 1}
    else:
        
        if user_admin.fields['password'].verify(password, arr_user['password']):
            
            s=get_session()
            
            s['id']=arr_user['id']
            s['login']=1
            s['privileges']=arr_user['privileges']
            
            return {'error': 0}
        else:
            return {'error': 1}
            
    
    
    

@post('/'+config.admin_folder+'/register')
def register():
    
    user_admin=UserAdmin()
    
    user_admin.conditions=['WHERE privileges=%s', 2]
    
    c=user_admin.select_count()
    
    if c==0:
        
        GetPostFiles.obtain_post()
        
        GetPostFiles.post['privileges']=2
        
        user_admin.valid_fields=['username', 'email', 'password', 'privileges']
        
        user_admin.create_forms()
        
        if user_admin.insert(GetPostFiles.post, False):
        
            error= {'error': 0}
            
            return error
        
        else:
            
            user_admin.check_all_fields(GetPostFiles.post, False)
            
            pass_values_to_form(GetPostFiles.post, user_admin.forms, yes_error=True)
            
            error={'error': 1}
            
            for field in user_admin.fields.values():
                    
                    error[field.name]=field.txt_error
            
            #error['password_repeat']=I18n.lang('common', 'password_no_match', 'Passwords doesn\'t match')
            
            return error
        
    else:
    
        return {'error': 1}
        
@get('/'+config.admin_folder+'/logout')
def logout():
    
    s=get_session()
    
    if 'login' in s.keys():
    
        del s['login']
        del s['privileges']
    
    redirect('/'+config.admin_folder)
    

def set_extra_forms_user(user_admin):
    
    user_admin.fields['password'].required=True
    user_admin.fields['email'].required=True

    user_admin.create_forms(['username', 'email', 'password'])
    
    user_admin.forms['repeat_password']=PasswordForm('repeat_password', '')
    
    user_admin.forms['repeat_password'].required=1
    
    user_admin.forms['repeat_password'].label=I18n.lang('common', 'repeat_password', 'Repeat Password')


    """user_admin.create_forms()
    
    users=user_admin.select()"""

#By default id is not showed
