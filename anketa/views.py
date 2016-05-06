# -*- coding: utf-8 -*-
import json
import numpy as np
import datetime

from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.forms.formsets import formset_factory
from django.utils import timezone


from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect

from django.shortcuts import render_to_response, render,get_object_or_404
from django.template import RequestContext

from kladr.models import Street
from anketa.models import Person, Address, Attribute, AttrValue, Abiturient, Department, Education_Prog, Profile, Application, Education_Prog_Form, EduForm, ApplicationProfiles, Milit, Docs
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth.decorators import login_required

class StartPage(TemplateView):
	template_name = 'anketa/start.html'

def StartApp(request):
	return render(request, 'anketa/wizardform.html')

@login_required(login_url='authapp:index')
def PersonProfile(request):
	args={'currentpage':1}
	args.update(csrf(request))
	return render(request, 'anketa/profile.html', args)

@login_required(login_url='authapp:index')
def PersonData(request):
	args={'currentpage':2}
	person=Abiturient.objects.get(user=request.user)
	# 1
	args['fname']=person.fname
	args['sname']=person.sname
	args['mname']=person.mname
	args['birthdate']=person.birthdate
	args['sex']=person.sex
	if person.birthplace is not None:
		args['birthplace']=person.birthplace
	if person.citizenship is not None:
		args['citizenship']=person.citizenship.value
		args['citizenship_id']=person.citizenship.id
	if person.nationality is not None:
		args['nationality']=person.nationality.value
		args['nationality_id']=person.nationality.id
	if person.docs_set.filter(docType__value__icontains=u'СНИЛС').first() is not None:
		args['snils']=person.docs_set.filter(docType__value__icontains=u'СНИЛС').first()
	# 7 
	args['hostel']=person.hostel
	milit = Milit.objects.filter(abiturient = person).first()
	if milit is not None:
		args['liableForMilit']=milit.liableForMilit
		if milit.liableForMilit==True:
			args['isServed']=milit.isServed
			if milit.isServed==True:
				args['rank']=milit.rank.value
				args['rank_id']=milit.rank.id
				args['yeararmy']=milit.yearDismissial
	if person.foreign_lang is not None:
		args['flang_id']=person.foreign_lang.id
		args['flang']=person.foreign_lang.value
	address = person.address_set.filter(adrs_type__value__icontains=u'прописке').first()
	if address is not None:
		args['zipcode']=address.zipcode
		args['street']=address.street
		args['house']=address.house
		args['building']=address.building
		args['flat']=address.flat
	#print(args)
	args.update(csrf(request))
	return render(request,'anketa/persondata.html',args)

@login_required(login_url='authapp:index')
def Applications(request):
	args={'currentpage':3}
	applications=Application.objects.filter(abiturient__user=request.user)
	args['applications']=applications
	return render(request,'anketa/applicationList.html',args)

@login_required(login_url='authapp:index')
def Account(request):
	args={'currentpage':4}
	args['email'] = request.user.email
	args.update(csrf(request))
	return render(request,'anketa/account.html',args)

def GetSelectedApplication(request):
	result={}
	application =Application.objects.get(pk = request.GET.get('id',''))
	app_profiles = ApplicationProfiles.objects.filter(application = application)
	result['department_id']=application.department.id
	result['department_name']=application.department.name
	result['edu_prog_id']=application.edu_prog.edu_prog.id
	result['edu_prog_name']=application.edu_prog.edu_prog.name+' ' + application.edu_prog.edu_prog.qualification.value
	result['edu_prog_eduform_id']=application.edu_prog.id
	result['edu_prog_eduform_name']=[x[1] for x in EduForm if x[0] == application.edu_prog.eduform][0]
	result['profiles_count']=len(app_profiles)
	profiles=[]
	count=0
	for item in app_profiles:
		count=count+1
		profiles.append({'id':item.profile.id,'profile':item.profile.name})
	result['profiles']=profiles
	result['profiles_len']=len(profiles)
	#print(result['profiles'])
	return HttpResponse(json.dumps(result), content_type="application/json")

def AddDataToPerson(request):
	result="success"
	#print(request.POST)
	if request.method == 'POST':
		try:
			page=int(request.POST.get('currentPage',''))
			abit=Abiturient.objects.get(user=request.user)
			if page==1: #Личные данные
				abit.sname=request.POST.get('sname','')
				abit.fname=request.POST.get('name','')
				abit.mname=request.POST.get('mname','')
				abit.birthplace=request.POST.get('birthplace','')
				if(len(request.POST.get('birthday','')))>0:
					abit.birthdate=datetime.datetime.strptime(request.POST.get('birthday',''),'%d/%m/%Y').strftime('%Y-%m-%d')
				if(len(request.POST.get('nation','')))>0:
					abit.nationality=AttrValue.objects.get(pk=request.POST.get('nation',''))
				else:
					abit.nationality=None
				if(len(request.POST.get('citizenship','')))>0:
					abit.citizenship=AttrValue.objects.get(pk=request.POST.get('citizenship',''))
				if(len(request.POST.get('sex','')))>0:
					abit.sex=request.POST.get('sex','')
			if page==2:
				doctype = abit.docs_set.filter(docType__attribute__name__icontains=u'удостоверяющего личность').first()
				if doctype is None:
					doctype=Docs()
					doctype.abiturient=abit
				else:
					doctype.number=None
					doctype.serialno=None
					doctype.issueDate=None
					doctype.docIssuer=None
					doctype.docType=None
				if(len(request.POST.get('doctype',''))>0):
					doctype.docType=AttrValue.objects.get(pk=request.POST.get('doctype',''))
				if(len(request.POST.get('serialdoc',''))>0):
					doctype.serialno=request.POST.get('serialdoc','')
				if(len(request.POST.get('numberdoc',''))>0):
					doctype.number=request.POST.get('numberdoc','')
				if(len(request.POST.get('datedoc',''))>0):
					doctype.issueDate=datetime.datetime.strptime(request.POST.get('datedoc',''),'%d/%m/%Y').strftime('%Y-%m-%d')
				if(len(request.POST.get('docIssuer',''))>0):
					doctype.docIssuer=request.POST.get('docIssuer','')
				doctype.save()
				edudoc = abit.docs_set.filter(docType__attribute__name__icontains=u'об образовании').first()
				if edudoc is None:
					edudoc=Docs()
					edudoc.abiturient=abit
				else:
					edudoc.number=None
					edudoc.serialno=None
					edudoc.issueDate=None
					edudoc.docIssuer=None
					edudoc.docType=None
				
				snils = Docs()
				snils.abiturient=abit
			
			if page==3:
				if request.POST.get('adrstype','')=="perm":
					adrs_type=u'По прописке'
				else:
					adrs_type=u'Фактический'
				abiturient=Abiturient.objects.get(user=request.user)
				adrs=Address.objects.filter(abiturient=abiturient).filter(adrs_type__value__icontains=adrs_type).first()
				if adrs is None:
					adrs=Address()
					adrs.abiturient=abiturient
				adrs.adrs_type=AttrValue.objects.filter(value__icontains=adrs_type).first()
				adrs.zipcode=request.POST.get('adrsindex','')
				adrs.street=Street.objects.filter(name__icontains=request.POST.get('street','')).first()
				adrs.house=request.POST.get('adrshouse','')
				adrs.building=request.POST.get('adrsbuilding','')
				adrs.flat=request.POST.get('adrsflat','')
				if ((request.POST.get('adrsisthesame','')) == "yes"):
					adrs.adrs_type_same=True
					adrs.adrs_type=AttrValue.objects.filter(value__icontains=u'прописке').first()
					Address.objects.filter(abiturient=abiturient).delete()
				else:
					adrs.adrs_type_same=False
				adrs.save()
			"""
			if(page==4):

			if(page==5):

			if(page==6):
			"""
			if page==7:
				if(len(request.POST.get('hostel','')))>0:
					abit.hostel=False
					if(request.POST.get('hostel','')=="yes"):
						abit.hostel=True
				if(len(request.POST.get('flang','')))>0:
					abit.foreign_lang=AttrValue.objects.get(pk=request.POST.get('flang',''))

				if Milit.objects.filter(abiturient = abit).first() is not None:
					Milit.objects.filter(abiturient = abit).first().delete()
				milit = Milit()
				milit.abiturient=abit
				if (len(request.POST.get('liableForMilit','')))>0:
					if request.POST.get('liableForMilit','')=="yes":
						milit.liableForMilit=True
						if (len(request.POST.get('isServed','')))>0:
							if request.POST.get('isServed','')=="yes":
								milit.isServed=True
								if(len(request.POST.get('rank','')))>0:
									milit.rank=AttrValue.objects.get(pk=request.POST.get('rank'))
								if (len(request.POST.get('yeararmy','')))>0:
									milit.yearDismissial=int(request.POST.get('yeararmy',''))
									# АХАХАХАХАХ ХКАКОЙ ККРАСИВЫЙ КОД АХАХАХАХАХХААХХА
				milit.save()

			abit.save()
		except Exception as e:
					result=str(e)
	return HttpResponse(json.dumps(result), content_type="application/json")

def SaveApplication(request):
	result = {'result':0, 'error_msg':''}
	print(request.POST)
	if request.method == 'POST':
		if(int(request.POST.get('facepalm',''))>0):
			application=Application.objects.get(pk=request.POST.get('facepalm'))
			ApplicationProfiles.objects.filter(application=application).delete()
		else:
			application = Application()
		application.abiturient=Abiturient.objects.get(user=request.user)
		application.department = Department.objects.get(pk = request.POST.get('department',''))
		application.date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
		application.edu_prog=Education_Prog_Form.objects.get(pk=request.POST.get('eduform',''))
		application.eduform = application.edu_prog.eduform
		application.budget = True
		application.withfee = False
		kaketomenyabesit = AttrValue.objects.filter(attribute__name__icontains=u'Статус заявления').filter(value__icontains=u'Подано').get(value__icontains=u'Подан')
		print(kaketomenyabesit.value)
		application.appState = kaketomenyabesit
		application.points =100
		application.save()
		if (len(request.POST.get('eduprof'))>0):
			profs=request.POST.get('eduprof','').split(',')
			for item in profs:
				appProf = ApplicationProfiles()
				appProf.application=application
				appProf.profile=Profile.objects.get(pk=item)
				appProf.save()
	return HttpResponse(json.dumps(result), content_type="application/json")

def DeleteApplication(request):
	result = {'result':0, 'error_msg':''}
	if request.method == 'GET':
		Application.objects.get(pk=request.GET.get('id')).delete()
	return HttpResponse(json.dumps(result), content_type="application/json")

@transaction.atomic
def Save_Abiturient(values):
	abit = Abiturient()
	abit.user = User.objects.create_user(username=values.get('username',''), email=values.get('email',''), password=values.get('password',''))
	abit.user.save()
	abit.fname=values.get('fName','')
	abit.sname=values.get('sName','')
	abit.mname=values.get('mName','')
	abit.sex=values.get('sex','')
	abit.birthdate=datetime.datetime.strptime(values.get('birthday',''),'%Y-%m-%d')
	abit.save()

def rpHash(person):
	hash = 5381 
	value = person.upper() 
	for caracter in value: 
		hash = (( np.left_shift(hash, 5) + hash) + ord(caracter)) 
	hash = np.int32(hash)
	return hash

def CreatePerson(request):
	result = {'result':0, 'error_msg':''}
	if request.method =='POST':
		if (rpHash(request.POST.get('captcha','')) == int(request.POST.get('captchaHash',''))):
			try:
				Save_Abiturient(request.POST)
				username = request.POST.get('username', '')
				password = request.POST.get('password', '')
				user = authenticate(username=username, password=password)
				if user is not None:
					login(request, user)
			except Exception as e:
				result['result']=1
				result['error_msg']=str(e)#"Что-то пошло не так."
		else:
			result['result']=1
			result['error_msg']="Неправильно введена капча!"
	return HttpResponse(json.dumps(result), content_type="application/json")

def GetAddressTypeValues(request):
	result={}
	result['success']=0
	if request.method == "POST":
		if request.POST.get('adrstype','')=="current":
			adrs_type=u'По прописке'
			needed_adrs_type=u'Фактический'
		else:
			adrs_type=u'Фактический'
			needed_adrs_type=u'По прописке'
		abiturient=Abiturient.objects.get(user=request.user)
		adrs=Address.objects.filter(abiturient=abiturient).filter(adrs_type__value__icontains=adrs_type).first()
		if adrs is None:
			adrs=Address()
			adrs.abiturient=abiturient
		adrs.adrs_type=AttrValue.objects.filter(value__icontains=adrs_type).first()
		adrs.zipcode=request.POST.get('adrsindex','')
		adrs.street=Street.objects.filter(name__icontains=request.POST.get('street','')).first()
		adrs.house=request.POST.get('adrshouse','')
		adrs.building=request.POST.get('adrsbuilding','')
		adrs.flat=request.POST.get('adrsflat','')
		if ((request.POST.get('adrsisthesame','')) == "yes"):
			adrs.adrs_type_same=True
			adrs.adrs_type=AttrValue.objects.filter(value__icontains=u'прописке').first()
			Address.objects.filter(abiturient=abiturient).delete()
		else:
			adrs.adrs_type_same=False
		adrs.save()
		needed_adrs=Address.objects.filter(abiturient=abiturient).filter(adrs_type__value__icontains=needed_adrs_type).first()
		if needed_adrs is not None:
			result['success']=1
			result['index']=needed_adrs.zipcode	
			result['street']=needed_adrs.street.name
			result['house']=needed_adrs.house
			result['building']=needed_adrs.building
			result['flat']=needed_adrs.flat
	return HttpResponse(json.dumps(result), content_type="application/json")

################################## AJAX ###################################################

def Territory(request):
	trry = AttrValue.objects.filter(attribute__id = 5)
	part = request.GET.get('query','')
	if len(part)>0:
		trry = trry.filter(value__icontains = part)
	trry = trry.values('id', 'value')
	result = []
	for item in trry:
		result.append(item)
	return HttpResponse(json.dumps(result), content_type="application/json")

def District(request):
	dist = AttrValue.objects.filter(attribute__id = 7)
	part = request.GET.get('query','')
	region = request.GET.get('id','')
	if len(part)>0:
		dist = dist.filter(value__icontains = part, parent__id = region)
	dist = dist.values('id', 'value')
	result = []
	for item in dist:
		result.append({'id':item['id'],'value':item['value']})
	return HttpResponse(json.dumps(result), content_type="application/json")

def City(request):
	cty = AttrValue.objects.filter(attribute__id = 6)
	part = request.GET.get('query','')
	district = request.GET.get('id', '')
	if len(part)>0:
		cty = cty.filter(value__icontains = part, parent__id = district)
	cty = cty.values('id', 'value')
	result = []
	for item in cty:
		result.append({'id':item['id'],'value':item['value']})
	return HttpResponse(json.dumps(result), content_type="application/json")

def Streets(request):
	strs =  AttrValue.objects.filter(attribute__name__icontains=u'Улица')
	part = request.GET.get('query','')
	region = request.GET.get('id','')
	if len(part)>0:
		strs = strs.filter(value__icontains = part, parent__id = region)
	strs = strs.values('id', 'value')
	result = []
	for item in strs:
		result.append({'id':item['id'],'value':item['value']})
	return HttpResponse(json.dumps(result), content_type="application/json")
	trry = AttrValue.objects.filter(attribute__name__icontains=u'тип докумета')
	part = request.GET.get('query','')

def Citizenship(request):
	trry = AttrValue.objects.filter(attribute__name__icontains = u'гражданство')
	part = request.GET.get('query','')
	if len(part)>0:
		trry = trry.filter(value__icontains = part)
	trry = trry.values('id', 'value')
	result = []
	for item in trry:
		result.append({'id':item['id'], 'text':item['value']})
	return HttpResponse(json.dumps(result), content_type="application/json")

def Nation(request):
	trry = AttrValue.objects.filter(attribute__name__icontains=u'национальность')
	part = request.GET.get('query','')
	if len(part)>0:
		trry = trry.filter(value__icontains = part)
	trry = trry.values('id', 'value')
	result = []
	for item in trry:
		result.append({'id':item['id'], 'text':item['value']})
	return HttpResponse(json.dumps(result), content_type="application/json")
	
def DocType(request):
	trry = AttrValue.objects.filter(attribute__name__icontains=u'тип документа удостоверяющего личность')
	part = request.GET.get('query','')
	if len(part)>0:
		trry = trry.filter(value__icontains = part)
	result = []
	for item in trry:
		result.append({'id':item.id, 'text':item.value})
	return HttpResponse(json.dumps(result), content_type="application/json")

def DocIssuer(request):
	trry = AttrValue.objects.filter(attribute__name__icontains=u'выдавший')
	part = request.GET.get('query','')
	if len(part)>0:
		trry = trry.filter(value__icontains = part)
	trry = trry.values('id', 'value')
	result = []
	for item in trry:
		result.append({'id':item['id'], 'text':item['value']})
	return HttpResponse(json.dumps(result), content_type="application/json")

def EduDocType(request):
	trry = AttrValue.objects.filter(value__icontains=u'диплом')|AttrValue.objects.filter(value__icontains=u'аттестат')
	part = request.GET.get('query','')
	if len(part)>0:
		trry = trry.filter(value__icontains = part)
	trry = trry.values('id', 'value')
	result = []
	for item in trry:
		result.append({'id':item['id'], 'text':item['value']})
	return HttpResponse(json.dumps(result), content_type="application/json")

def PrevEduName(request):
	trry = AttrValue.objects.filter(attribute__name__icontains=u'выдавший')
	part = request.GET.get('query','')
	
	if len(part)>0:
		trry = trry.filter(value__icontains = part)
	trry = trry.values('id', 'value')
	result = []
	for item in trry:
		result.append({'id':item['id'], 'text':item['value']})
	return HttpResponse(json.dumps(result), content_type="application/json")

def Institute(request):
	institute = Department.objects.filter(name__icontains = request.GET.get('query',''))
	institute = institute.values('id', 'name')
	result = []
	for item in institute:
		result.append({'id':item['id'], 'text':item['name']})
	return HttpResponse(json.dumps(result), content_type="application/json")

def EduName(request):
	institute = Department.objects.get(pk = request.GET.get('id',''))
	eduname=institute.education_prog_set.filter(name__icontains=request.GET.get('query',''))
	eduname=eduname.values('id','name', 'qualification__value')
	result = []
	for item in eduname:
		result.append({'id':item['id'], 'text':item['name'] + ' ' + item['qualification__value']})
	return HttpResponse(json.dumps(result), content_type="application/json")

def EduProf(request):
	eduname = Education_Prog.objects.get(pk = request.GET.get('id',''))
	eduprof = eduname.profile_set.filter(name__icontains=request.GET.get('query',''))
	eduprof = eduprof.values('id', 'name')
	result = []
	for item in eduprof:
		result.append({'id':item['id'],'text':item['name']})
	return HttpResponse(json.dumps(result), content_type="application/json")

def EduProfForm(request):
	eduname = Education_Prog.objects.get(pk = request.GET.get('id',''))
	eduprof = eduname.education_prog_form_set.all()
	eduprof = eduprof.values('id', 'eduform')
	result = []
	for item in eduprof:
		item['eduform'] = [x[1] for x in EduForm if x[0] == item['eduform']][0]
		result.append({'id':item['id'],'text':item['eduform']})
	return HttpResponse(json.dumps(result), content_type="application/json")

def Privilegies(request):
	trry = AttrValue.objects.filter(attribute__name__icontains=u'выдавший')
	part = request.GET.get('query','')
	if len(part)>0:
		trry = trry.filter(value__icontains = part)
	trry = trry.values('id', 'value')
	result = []
	for item in trry:
		result.append(item)
	return HttpResponse(json.dumps(result), content_type="application/json")

def Rank(request):
	trry = AttrValue.objects.filter(attribute__name__icontains=u'Воинское')
	part = request.GET.get('query','')
	if len(part)>0:
		trry = trry.filter(value__icontains = part)
	trry = trry.values('id', 'value')
	result = []
	for item in trry:
		result.append({'id':item['id'], 'text':item['value']})
	return HttpResponse(json.dumps(result), content_type="application/json")

def Flang(request):
	trry = AttrValue.objects.filter(attribute__name__icontains=u'Изучаемый') 
	part = request.GET.get('query','')
	if len(part)>0:
		trry = trry.filter(value__icontains = part)
	trry = trry.values('id', 'value')
	result = []
	for item in trry:
		result.append({'id':item['id'], 'text':item['value']})
	return HttpResponse(json.dumps(result), content_type="application/json")