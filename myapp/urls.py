from django.urls import path 
from .views import*

urlpatterns = [
    path('',home,name='home'),
    path('adminlogin',Adminlogin,name='adminlogin'),
    path('loginsave',loginsave,name='loginsave'),
    path('dashboard',dashboard,name='dashboard'),
    # path('adminlayout',adminlayout,name='adminlayout'),
    path('userlogout',userlogout,name='userlogout'),
    path('adddep',adddep,name='adddep'),
    path('dep_save',dep_save,name='dep_save'),
    # path('adminlogin',login,name='adminlogin'),
    path('depshow',depshow,name='depshow'),
    path('empadd',empadd,name='empadd'),
    path('empshow',empshow,name='empshow'),
    path('userlogin',userlogin,name='userlogin'),
    path('userlogcode',userlogcode,name='userlogcode'),
    path('userdashboard',userdashboard,name='userdashboard'),
    path('userlayout',userlayout,name='userlayout'),    
    path('ur_upload_files',ur_upload_files,name='ur_upload_files'),
    path('createfile',createfile,name='createfile'),
    path('receivedfile',receivedfile,name='receivedfile'),
    path('sentfiles',sentfile,name='sentfiles'),
    path('pendingfiles',pendingfiles,name='pendingfiles'),
    path('managedep',managedep,name='managedep'),
    path('allfile',allfile,name='allfile'),
    path('filetrack',filetrack,name='filetrack'),
    path('manageemp',manageemp,name='manageemp'),
    path('ur_receivedfiles',ur_receivedfiles,name='ur_receivedfiles'),
    path('ur_sentfile',ur_sentfile,name='ur_sentfile'),
    path('pendingfile',pendingfile,name='pendingfile'),
    path('ur_allfiles',ur_allfiles,name='ur_allfiles'),
    path('trackfile',trackfile,name='trackfile'),
    path('fileupload',fileupload,name='fileupload'),
    path('us_showfile',us_showfile,name='us_showfile'),
    path('Details_file/<str:file_no>/',Details_file,name='Details_file'),
    path('ad_Details_file/<str:file_no>/',ad_Details_file,name='ad_Details_file'),
    path('editfile/<str:file_no>/', edit_file, name='edit_file'),
    path('deletefile/<str:file_no>/', delete_file, name='delete_file')
    
    
]
