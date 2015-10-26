#By default id is not showed

from citoplasma.pages import Pages
from citoplasma.urls import add_get_parameters
from citoplasma.sessions import get_session
from bottle import request

class SimpleList:
    
    def __init__(self, model, url, t):
        
        self.t=t
        
        self.model=model
        
        if len(self.model.forms)==0:
        
            self.model.create_forms()
        
        self.fields=model.fields.keys()
        
        self.url=url
        
        self.limit_pages=20
        
        self.order_defaults=['ASC', 'DESC']
        
        self.order_class=['up', 'down']
        
        self.s=get_session()
        
        #self.s['order']=self.s.get('order', 0)
        
        self.order_by=self.order_defaults[0]
        
        self.change_order={}
        
        self.yes_search=True
        
        self.search_text=''
        
        self.begin_page=int(request.query.get('begin_page', '0'))
        
        if self.begin_page<0:
            self.begin_page=0
        
        self.search_fields=self.fields
    
    def set_fields_no_showed(self, fields_no_showed):
        
        self.fields=[field for field in self.fields if not field in fields_no_showed]
               
    
    def restore_fields(self):
        self.fields=self.model.fields.keys()
    
    def obtain_order(self):
        
        self.s['order']=self.s.get('order', 0)
        
        order_k=self.s['order']
        
        #Obtain from get
        
        if 'order' in request.query.keys():
            
            order_k=int(request.query.get('order', 0))
        
        if order_k>1 or order_k<0:
            order_k=0
        
        self.order_by=self.order_defaults[ order_k ]
        
        self.s['order']=order_k
        
        self.s.save()
    
    def obtain_field_search(self):
        
        self.s['order_field']=self.s.get('order_field', self.model.name_field_id)
        
        field_k=self.s['order_field']
        
        if 'order_field' in request.query.keys():
            field_k=request.query['order_field']
        
        if field_k in self.model.fields.keys():
            
            self.s['order_field']=field_k
        
        for field in self.fields:
            self.change_order[field]=self.s['order']
        
        if self.s['order']==0:
            self.change_order[field_k]=1
        else:
            self.change_order[field_k]=0
            
        self.s.save()
        
        self.order_field=self.s['order_field']
        
    def search(self):
        
        self.search_text=request.query.get('search_text', '')
        
        self.search_text=self.search_text.replace('"', '&quot;')
        
        #self.model.conditions='AND 
        
        self.search_field=request.query.get('search_field', '')
        
        if self.search_field not in self.model.fields.keys():
            self.search_field=''
        
        if self.search_field!='' and self.search_text!='':
            self.model.conditions[0]+=' AND '+self.search_field+' LIKE "%%s%"'
            self.model.conditions[1]=[self.search_text]
        
        pass
    
    def show(self):
        
        self.obtain_order()
        
        self.obtain_field_search()
        
        self.search()
        
        total_elements=self.model.select_count()
        
        num_elements=self.limit_pages
        
        link=add_get_parameters(self.url, search_text=self.search_text, search_field=self.search_field)
        
        begin_page=self.begin_page
        
        self.model.order_by='order by '+self.order_field+' '+self.order_by
        
        self.model.limit='limit '+str(begin_page)+','+str(self.limit_pages)
        
        list_items=self.model.select(self.fields)
        
        pages=Pages.show( begin_page, total_elements, num_elements, link ,initial_num_pages=5, variable='begin_page', label='', func_jscript='')
        
        self.begin_page=str(self.begin_page)
        
        return self.t.load_template('utils/list.phtml', simplelist=self, list=list_items, pages=pages)
