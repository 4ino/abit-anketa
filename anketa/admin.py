from django.contrib import admin

# Register your models here.
from staff.models import Employee
import anketa.models# import University, Department, AttrType, Attribute, AttrValue

#staff
#admin.site.register(News)
admin.site.register(Employee)
#admin.site.register(Img)
#anketa
admin.site.register(anketa.models.University)
admin.site.register(anketa.models.Department)
admin.site.register(anketa.models.AttrType)
admin.site.register(anketa.models.Attribute)
admin.site.register(anketa.models.AttrValue)
admin.site.register(anketa.models.Person)
