﻿from django.db import models

Sex = (
    (u'М',u'Мужской'),
    (u'Ж',u'Женский'),
    )
Eduform = (
    (u'О',u'Очное'),
    (u'З',u'Заочное')
    )

class AttrType(models.Model):
    name=models.CharField(u"", max_length=100)

class Attribute(models.Model):
    name = models.CharField(max_length=250)
    parent = models.ForeignKey('self', null=True, blank=True)
    type = models.ForeignKey(AttrType,verbose_name = u'Тип атрибута')
    def __unicode__(self):
        return self.name

class Person(models.Model):
    lname = models.CharField(u'Фамилия', max_length=30)
    nname = models.CharField(u'Имя', max_length=30)
    mname = models.CharField(u'Отчество', max_length=30)
    sex = models.CharField(u'Пол', choices=Sex, max_length=1, default='М')
    birthdate = models.DateField(u'Дата рождения')
    bithplace = models.CharField(u'Место рождения', max_length=100)
    nationality = models.ForeignKey(Attribute,verbose_name=u'Национальность(по желанию)', limit_choices_to={'type__name':u'Национальность'}, db_index = True, blank = True, null = True, related_name='Nationality')
    citizenship = models.ForeignKey(Attribute,verbose_name=u'Гражданство', db_index = True,related_name='Citizenship')
    hostel = models.BooleanField(u'Требуется общежитие',default=False)
    foreign_lang = models.ForeignKey('Attribute', verbose_name=u'Изучаемый иностранный язык',related_name='Foreign')
    father = models.ForeignKey('self',verbose_name= u'Отец', null = True, blank = True, related_name='Father')
    mother = models.ForeignKey('self',verbose_name= u'Мать', null = True, blank = True, related_name='Mother')

class Application(models.Model):
    Department = models.ForeignKey('Department', verbose_name = u'Институт/факультет')
    person = models.ForeignKey('Person', verbose_name = u'Абитуриент')
    date = models.DateField(u'Дата подачи')
    number = models.IntegerField(u'Номер зааявления', max_length=10)
    eduform = models.CharField(u'Форма обучения',choices=Eduform, default='О', max_length=10)
    budget = models.BooleanField(u'В рамках контрольных цифр приёма', default=False)
    withfee = models.BinaryField(u'по договорам об оказании платных обр. услуг', default=False)

class Address(models.Model):
    person = models.ForeignKey('Person')
    adrs_type = models.ForeignKey('Attribute', verbose_name=u'Тип адреса', related_name='Adrs_type')
    adrs_territory = models.ForeignKey('Attribute', verbose_name=u'область\край\респ.', null=True, blank=True, related_name='Adrs_territory')
    adrs_district = models.ForeignKey('Attribute', verbose_name=u'Район\улус', null=True, blank=True, related_name='Adrs_district')
    adrs_city = models.ForeignKey('Attribute', verbose_name=u'Город\село', related_name='Adrs_city')
    adrs_settlement = models.ForeignKey('Attribute', verbose_name=u'Посёлок', null = True, blank = True, related_name='Adrs_settlement')
    zipcode = models.CharField(u'Индекс', max_length=6, null=True, blank=True)
    street = models.CharField(u'Улица\проспект', max_length=151)
    house = models.CharField(u'дом', max_length=5)
    building = models.CharField(u'корпус', max_length=5, null=True, blank=True)
    flat = models.CharField(u'квартира', max_length=5, null=True, blank=True)

class Contacts(models.Model):
    person = models.ForeignKey('Person',verbose_name = u'Человек')
    value = models.CharField(u'Значение', max_length=30)
    contact_type = models.ForeignKey('Attribute',verbose_name=u'Тип')

class DocAttr(models.Model):
    doc = models.ForeignKey('Docs', verbose_name=u'Документ')
    attrName = models.ForeignKey(Attribute, verbose_name = u'Название атрибута', related_name='Attrname')
    attrValue = models.CharField(u'Значение атрибута', max_length = 150)

class Docs(models.Model):
    person = models.ForeignKey('Person')
    serialno = models.IntegerField(u'Серия документа', max_length=15)
    number = models.IntegerField(u'Номер документа', max_length=15)
    issueDate = models.DateField(u'Дата выдачи')
    isCopy = models.BooleanField(u'Оригинал документа', default=False)
    docType = models.ForeignKey('Attribute', verbose_name=u'Тип документа', related_name='DocType')
    docIssuer = models.ForeignKey('Attribute', verbose_name=u'Орган выдавший документ', related_name='DocIssuer')

class Exams(models.Model):
    person = models.ForeignKey('Person')
    exam_examType = models.ForeignKey('Attribute', verbose_name=u'Тип экзамена', related_name='ExamType')
    exam_subjects = models.ForeignKey('Attribute', verbose_name=u'Дисциплина',related_name='Exam_Subjects')
    points = models.IntegerField(u'Кол-во баллов', max_length=3, blank = True, null = True)
    year = models.IntegerField(u'Год', max_length=4)

class Department(models.Model):
    university = models.ForeignKey('University')
    name=models.CharField(u'Институт/факультет', max_length=100)

class University(models.Model):
    name=models.CharField(u'Университет', max_length=100)

class Qualification(models.Model):
    name=models.CharField(u'Название', max_length=100)

class Education_Prog(models.Model):
    department = models.ForeignKey(Department)
    qual=models.ForeignKey('Qualification')
    name=models.CharField(u'Направление/специальность', max_length=100)

class Profile(models.Model):
    edu_prog=models.ForeignKey('Education_Prog')
    name=models.CharField(u'Профиль', max_length=100)

class Exams_needed(models.Model):
    profile=models.ForeignKey('Profile')
    min_points=models.IntegerField(u'Мин-ое кол-во баллов', max_length=100)
    subject = models.ForeignKey('Attribute', verbose_name=u'Дисциплина', related_name='Subject')
    #Форма экзамена?

class Privilegies(models.Model):
    person = models.ForeignKey('Person')
    category = models.ForeignKey('Attribute', verbose_name=u'Категория', related_name='Category')
    priv_type = models.ForeignKey('Attribute', verbose_name=u'тип', related_name='Priv_type')

#YASOJGUVASHITRUPI

class Milit(models.Model):
    person=models.ForeignKey(Person, verbose_name = u'Абитуриент')
    liableForMilit = models.BooleanField(u'Военнообязанный', default=False)
    isServed=models.BooleanField(u'служил в армии', default=False, blank=True)
    yearDismissial=models.IntegerField(u'Год увольнения из рядов РА, max_length=4',blank=True, null= True)
    rank = models.ForeignKey(Attribute, verbose_name=u'Воинское звание',blank=True, null= True,related_name='Rank')

class DepAchieves(models.Model):
    department = models.ForeignKey(Department, verbose_name = u'Институт/факультет', db_index = True, blank = True, null = True)
    qual = models.ForeignKey(Qualification, verbose_name = u'Квалификация', db_index = True)
    name = models.CharField(u'Наименование', max_length = 1000, db_index = True)
    points = models.IntegerField(u'Баллы')

class Achievements(models.Model):
    person = models.ForeignKey(Person, verbose_name = u'Абитуриент', db_index = True)
    achieve = models.ForeignKey(DepAchieves, verbose_name = u'Достижение', db_index = True)
