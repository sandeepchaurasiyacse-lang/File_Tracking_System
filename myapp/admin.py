from django.contrib import admin

from .models import*
# Register your models here.
admin.site.register(login)
admin.site.register(adddepartment)
admin.site.register(addemp)
admin.site.register(fileupload)
admin.site.register(File_History)

