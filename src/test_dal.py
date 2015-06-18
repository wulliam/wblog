'''
Created on Sep 19, 2011

@author: winton.wu
'''

from gluon.dal import *

db = DAL('mysql://wulliam:wintonwu@localhost/wblog')

db.define_table('ray_about', 
    Field('title'),
    Field('name'),
    Field('value'),
    Field('description'),
    Field('type'))

print db(db.ray_about).select(orderby=db.ray_about.name)
    


if __name__ == '__main__':
    pass