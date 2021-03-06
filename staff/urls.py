from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from staff import views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^login/','staff.views.login', name = 'login'),
	url(r'^logout/','staff.views.logout',name = 'logout'),
	#url(r'^$',views.index,name='index'),
	url(r'^employee_list/',views.Employee_list, name = 'employee_list'),
	url(r'^employee_add/',views.AddEmployee, name = 'employee_add'),
	url(r'^employee_edit/(?P<employee_id>\d+)',views.EditEmployee, name = 'employee_edit'),
	url(r'^employee_useraccount/',views.Employee_Useraccount, name = 'employee_acc'),
	url(r'^$',views.Application_list, name = 'application_list'),
	url(r'^catalogs/',views.Catalogs, name = 'catalogs'),
	url(r'^catalogs_attrvalue/(?P<attribute_id>\d+)',views.Catalogs_attrvalue, name = 'catalogs_attrvalue'),
	url(r'^application_review/(?P<application_id>\d+)',views.Application_review, name = 'application_review'),
	url(r'get_attrs/',views.Get_Attrs,name='get_attrs'),
	url(r'get_attr/',views.Get_Attr,name='get_attr'),
	url(r'get_attr_val/',views.Get_Attr_val,name='get_attr_val'),
	url(r'contact_dels/',views.Contact_dels,name='contact_dels'),
	url(r'wiz_cont_dels/',views.Wiz_cont_dels, name='wiz_cont_dels'),
	url(r'wiz_cont_apply',views.Wiz_cont_apply, name='wiz_cont_apply'),
	url(r'^add_data_to_person/$',views.AddDataToPerson,name="add_data_to_person"),
					)