from django.db import models
class login(models.Model):
    id=models.IntegerField(primary_key=True,auto_created=True)
    username = models.CharField(max_length=225)
    password = models.CharField(max_length=16)
    role=models.CharField(max_length=50)
    
class adddepartment(models.Model):
    id=models.IntegerField(primary_key=True,auto_created=True)
    dep_name = models.CharField(max_length=225)
    dep_code = models.IntegerField()
    dep_head = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    dep_email = models.EmailField()
    dep_number = models.CharField(max_length=12)
    create_at = models.TimeField()
    
class addemp(models.Model):
    name=models.CharField(max_length=225)
    username=models.CharField(max_length=225)
    email=models.CharField(max_length=100)
    mobile=models.IntegerField()
    emp_id=models.IntegerField()
    department=models.CharField(max_length=500)
    disignation=models.CharField(max_length=20)
    role=models.CharField(max_length=20)
    status=models.CharField(max_length=20)
    password=models.CharField(max_length=16)
    photo=models.ImageField(upload_to='profile')
    address=models.TextField(max)
    
#=================================User login ======================#

class fileupload(models.Model):
    file_no= models.CharField(max_length=50) 
    subject = models.CharField(max_length=500) 
    priority = models.CharField(max_length=50) 
    create_user = models.CharField(max_length=100) 
    department = models.CharField(max_length=225) 
    current_user = models.CharField(max_length=100) 
    file = models.FileField(upload_to="upload_file") 
    description = models.CharField(max)
    status=models.CharField(max_length=100)
    create_at = models.TimeField()
    
class File_History(models.Model):
    id=models.IntegerField(primary_key=True,auto_created=True)
    File_no=models.CharField(max_length=225)       
    current_user=models.CharField(max_length=225)       
    forwarded_user=models.CharField(max_length=225)       
    action=models.CharField(max_length=225)       
    remark=models.CharField()       
    create_at=models.DateField()     
    