from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import*
from django.contrib import messages
from datetime import datetime
from django.db.models import Q  
from django.utils import timezone
from django.views.decorators.cache import cache_control
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
import re
# Create your views here.
def home(request):
    return render(request,'user/home.html')

def Adminlogin(request):
    return render(request,'admin/adminlogin.html')

def loginsave(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=login.objects.filter(username=username,password=password).first()
        if user:
            if user.role=='Admin' or user.role=='admin':
                request.session['adminid'] = username
                return redirect('dashboard')
            else:
                messages.success(request,'You are not admin please go to user login.')
                return redirect('adminlogin')    
        else:
             messages.success(request,'Invalid username ')
             return redirect('adminlogin') 
         
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    recent_files = fileupload.objects.order_by('-create_at')[:5]

    context = {
        'recent_files': recent_files,
        'total_files': fileupload.objects.count(),
        'employees': addemp.objects.count(),
        'departments': adddepartment.objects.count(),
    }

    return render(request, 'admin/dashboard.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout(request):
    request.session.flush()
    return redirect('adminlogin')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userlogout(request):
    request.session.flush()
    return redirect('userlogin')  
#===========================   
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adddep(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    if request.method == 'POST':
        dep_name = request.POST.get('dep_name')
        dep_code = request.POST.get('dep_code')
        dep_head = request.POST.get('dep_head')
        status = request.POST.get('status')
        dep_email = request.POST.get('dep_email')
        dep_number = request.POST.get('dep_number')
        create_at = datetime.now()
        ab = adddepartment(
            dep_name=dep_name,
            dep_code=dep_code,
            dep_head=dep_head,
            status=status,
            dep_email=dep_email,
            dep_number=dep_number
        )
    return render(request, 'admin/adddep.html') 

def allfile(request):
    return render(request,'admin/allfile.html') 
 

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manageemp(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    ab = addemp.objects.all()
    return render(request, 'admin/manageemp.html', {
        'ab': ab
    })
#===========
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dep_save(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    if request.method == "POST":
        dep_name = request.POST.get('dep_name')
        dep_code = request.POST.get('dep_code')
        dep_head = request.POST.get('dep_head')
        status = request.POST.get('status')
        dep_email = request.POST.get('dep_email')
        dep_number = request.POST.get('dep_number')
        create_at = timezone.now()
        av = adddepartment.objects.filter(
            dep_name=dep_name,
            dep_code=dep_code,
            dep_email=dep_email
        )
        if av.exists():
            messages.error(request, "This department is already exists")
            return redirect('adddep')
        else:
            ab = adddepartment(
                dep_name=dep_name,
                dep_code=dep_code,
                dep_head=dep_head,
                status=status,
                dep_email=dep_email,
                dep_number=dep_number,
                create_at=create_at
            )
            ab.save()
            messages.success(request, 'Add Department Successfully')
            return redirect('adddep')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def depshow(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    ab = adddepartment.objects.all()
    return render(request, 'admin/depshow.html', {'ab': ab})
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def empadd(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    else:
        if request.method=="POST":
            username=request.POST.get('username')
            emp_id=request.POST.get('emp_id')
            name=request.POST.get('name')
            password=request.POST.get('password')

            sv=login(username=username,password=password)
            sv.save()

            av=addemp.objects.filter(username=username,emp_id=emp_id)

            if av.exists():
                messages.success(request,"This employeee already exists.")
            else:
                addemp.objects.create(
                    name=request.POST.get('name'),
                    username=request.POST.get('username'),
                    email=request.POST.get('email'),
                    mobile=request.POST.get('mobile'),
                    emp_id=request.POST.get('emp_id'),
                    department=request.POST.get('department'),
                    disignation=request.POST.get('disignation'),
                    role=request.POST.get('role'),
                    status=request.POST.get('status'),
                    password=request.POST.get('password'),
                    photo=request.FILES.get('photo'),
                    address=request.POST.get('address')
                )

            messages.success(request,'Add Employee Successfully')

            message = f"""
Dear {name},

Greetings from Green Gas Limited (GGL).

Your account has been successfully created for the GGL File Tracking System.

You can log in using the following credentials:

--------------------------------------------------------
User ID / Email : {username}
Password        : {password}
--------------------------------------------------------

Login Instructions:
1. Open the GGL File Tracking System.
2. Enter your User ID and Password.
3. Change your password after your first login (if applicable).
4. Start managing and tracking your assigned files.

Important:
• Keep your login credentials confidential.
• Do not share your password with anyone.
• If you forget your password or face any login issues, please contact the System Administrator.

Thank you for using the GGL File Tracking System.

Regards,

System Administrator
GGL File Tracking System
Green Gas Limited (GGL)
"""

            send_mail(
                "GGL File Tracking System - Login Credentials",
                message,
                settings.EMAIL_HOST_USER,
                [username],
                fail_silently=False,
            )

            return redirect('empadd')

        return render(request, 'admin/empadd.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def empshow(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    bc = addemp.objects.all()
    return render(request, 'admin/empshow.html', {'bc': bc})
   
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ad_Details_file(request, file_no):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    else:
        sn = request.session.get('adminid')
        ur = login.objects.all()
        fileh = File_History.objects.filter(File_no=file_no)
        ab = fileupload.objects.get(file_no=file_no)
        if request.method == "POST":
            current_user = request.POST.get('current_user')
            action = request.POST.get('action')
            forwarded_user = request.POST.get('forwarded_user')
            remark = request.POST.get('remark')
            create_at = timezone.now()
            ab.current_user = forwarded_user
            ab.status = action
            ab.save()
            fh = File_History(
                File_no=ab.file_no,
                current_user=sn,
                action=action,
                forwarded_user=forwarded_user,
                remark=remark,
                create_at=create_at
            )
            fh.save()
            return redirect('receivedfile')
        context = {
            'ab': ab,
            'ur': ur,
            'fileh': fileh
        }
        return render(request, 'admin/ad_Details_file.html', context)


#============================================User Login =========================================#
def userlogin(request):
    return render(request,'user/userlogin.html')

def userlogcode(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = addemp.objects.filter(
            username=username,
            password=password
        ).first()
        if user:
            if user.role == "User" and user.status == "Active":
                request.session['userid'] = user.username
                request.session['name'] = user.name
                return redirect('userdashboard')
            else:
                messages.error(request, "Your account is inactive.")
                return redirect('userlogin')
        messages.error(request, "Invalid Username or Password")
        return redirect('userlogin')
    return redirect('userlogin')      

from django.db.models import Count

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userdashboard(request):
    if 'userid' not in request.session:
        return redirect('userlogin')

    username = request.session.get('userid')

    # Dashboard Counts
    my_files = fileupload.objects.filter(create_user=username).count()

    received_files = fileupload.objects.filter(
        current_user=username
    ).count()

    sent_files = File_History.objects.filter(
        current_user=username
    ).count()

    pending_files = fileupload.objects.filter(
        current_user=username,
        status="Pending"
    ).count()

    # Recent Movement
    recent_history = File_History.objects.filter(
        current_user=username
    ).order_by('-id')[:5]

    recent = []

    for h in recent_history:
        f = fileupload.objects.filter(file_no=h.File_no).first()

        recent.append({
            "file_no": h.File_no,
            "subject": f.subject if f else "",
            "from_user": h.current_user,
            "to_user": h.forwarded_user,
            "action": h.action,
            "date": h.create_at,
        })

    context = {
        "username": username,
        "my_files": my_files,
        "received_files": received_files,
        "sent_files": sent_files,
        "pending_files": pending_files,
        "recent": recent,
    }

    return render(request, "user/userdashboard.html", context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userlayout(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    else:
        return render(request, 'user/userlayout.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sentfiles(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    else:
        return render(request, 'admin/sentfiles.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def pendingfiles(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    else:
        return render(request, 'admin/pendingfiles.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def filetrack(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    else:
        return render(request, 'admin/filetrack.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def managedep(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    else:
        ab = adddepartment.objects.all()
        return render(request, 'admin/managedep.html', {
            'ab': ab
        })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ur_receivedfiles(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    else:
        sid = request.session.get('userid')
        ab = fileupload.objects.filter(current_user=sid)
        return render(request, 'user/ur_receivedfiles.html', {
            'ab': ab,
            'sid': sid
        })
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ur_sentfile(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    else:
        sid = request.session.get('userid')
        ab = fileupload.objects.filter(create_user=sid)
        return render(request, 'user/ur_sentfile.html', {
            'ab': ab
        })
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def pendingfile(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    else:
        return render(request, 'user/pendingfile.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ur_allfiles(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    else:
        sid = request.session.get('userid')
        ab = fileupload.objects.filter(create_user=sid)
        return render(request, 'user/ur_allfiles.html', {
            'ab': ab
        })

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def trackfile(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    else:
        return render(request, 'user/trackfile.html')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def createfile(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    else:

        adminid = request.session.get('adminid')
        dp = adddepartment.objects.all()
        em = login.objects.all()

        if request.method == "POST":

            # Auto Generate Unique File Number
            last = fileupload.objects.order_by('-file_no').first()

            if last and last.file_no:
                num = int(re.sub(r'\D', '', last.file_no))
            else:
                num = 0

            while True:
                num += 1
                file_no = f"FIL{num:03d}"   # FIL001, FIL002, FIL003...

                # Check Duplicate
                if not fileupload.objects.filter(file_no=file_no).exists():
                    break
            current_user=request.POST.get('current_user')
            description=request.POST.get('description')
            status="Forwarded"
            create_at=timezone.now()
            fhs=File_History(File_no=file_no,current_user=adminid,forwarded_user=current_user,remark=description,action=status,create_at=create_at)
            fhs.save()
            fileupload.objects.create(
                file_no=file_no,
                subject=request.POST.get('subject'),
                create_user=adminid,
                priority=request.POST.get('priority'),
                department=request.POST.get('department'),
                current_user=request.POST.get('current_user'),
                file=request.FILES.get('file'),
                description=request.POST.get('description'),
                create_at=datetime.now(),
                status="Forwarded"
            )

            messages.success(request, "File Create Successfully")
            return redirect('createfile')

        con = {
            'dp': dp,
            'em': em
        }

        return render(request, 'admin/createfile.html', con)
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def receivedfile(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    else:
        sid = request.session.get('adminid')
        ab = fileupload.objects.filter(current_user=sid)
        return render(request, 'admin/receivedfile.html', {'ab': ab}) 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sentfile(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    else:
        sid = request.session.get('adminid')
        ab = fileupload.objects.filter(
            Q(create_user=sid) | Q(current_user=sid)
        )
        return render(request, 'admin/sentfiles.html', {
            'ab': ab
        })
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def allfile(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    else:
        ab = fileupload.objects.filter()
        return render(request, 'admin/allfile.html', {'ab': ab})
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ur_upload_files(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    else:

        userid = request.session.get('userid')
        dp = adddepartment.objects.all()
        em = login.objects.all()

        if request.method == "POST":
            
            # Auto Generate Unique File Number
            last = fileupload.objects.order_by('-file_no').first()

            if last and last.file_no:
                num = int(re.sub(r'\D', '', last.file_no))
            else:
                num = 0

            while True:
                num += 1
                file_no = f"FIL{num:03d}"   # FIL001, FIL002, FIL003...

                # Check Duplicate
                if not fileupload.objects.filter(file_no=file_no).exists():
                    break
            current_user=request.POST.get('current_user')
            description=request.POST.get('description')
            status="Forwarded"
            create_at=timezone.now()
            fhs=File_History(File_no=file_no,current_user=userid,forwarded_user=current_user,remark=description,action=status,create_at=create_at)
            fhs.save()

            fileupload.objects.create(
                file_no=file_no,
                subject=request.POST.get('subject'),
                create_user=userid,
                priority=request.POST.get('priority'),
                department=request.POST.get('department'),
                current_user=request.POST.get('current_user'),
                file=request.FILES.get('file'),
                description=request.POST.get('description'),
                create_at=datetime.now(),
                status="Forwarded"
            )

            messages.success(request, "File Create Successfully")
            return redirect('ur_upload_files')

        con = {
            'dp': dp,
            'em': em
        }

        return render(request, 'user/ur_uploadfiles.html', con)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def us_showfile(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    else:
        sid = request.session.get('userid')
        ab = fileupload.objects.filter(current_user=sid)
        return render(request, 'admin/ad-showfile.html', {'ab': ab})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userlogout(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    else:
        del request.session['userid']
        return redirect('userlogin')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Details_file(request, file_no):
    if 'userid' not in request.session:
        return redirect('userlogin')
    else:
        sn = request.session.get('userid')
        ur = login.objects.all()
        fileh = File_History.objects.filter(File_no=file_no)
        ab = fileupload.objects.get(file_no=file_no)
        if request.method == "POST":
            current_user = request.POST.get('current_user')
            action = request.POST.get('action')
            forwarded_user = request.POST.get('forwarded_user')
            remark = request.POST.get('remark')
            create_at = timezone.now()
            ab.current_user = forwarded_user
            ab.status = action
            ab.save()
            fh = File_History(
                File_no=ab.file_no,
                current_user=sn,
                action=action,
                forwarded_user=forwarded_user,
                remark=remark,
                create_at=create_at
            )
            fh.save()
            return redirect('ur_receivedfiles')
        context = {
            'ab': ab,
            'ur': ur,
            'fileh': fileh
        }
        return render(request, 'user/Details_file.html', context)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_file(request, file_no):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    obj = fileupload.objects.get(file_no=file_no)

    if request.method == "POST":
        obj.subject = request.POST.get('subject')
        obj.priority = request.POST.get('priority')
        obj.department = request.POST.get('department')
        obj.description = request.POST.get('description')

        if request.FILES.get('file'):
            obj.file = request.FILES.get('file')

        obj.save()

        messages.success(request, "File Updated Successfully")
        return redirect('sentfiles')

    return render(request, 'admin/editfile.html', {'obj': obj})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_file(request, file_no):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    obj = fileupload.objects.get(file_no=file_no)
    obj.delete()

    messages.success(request, "File Deleted Successfully")
    return redirect('sentfiles')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def filetrack(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    search = request.GET.get('search')

    ab = fileupload.objects.all()

    if search:
        ab = ab.filter(
            Q(file_no__icontains=search) |
            Q(subject__icontains=search) |
            Q(create_user__icontains=search) |
            Q(current_user__icontains=search)
        )

    return render(request, 'admin/filetrack.html', {
        'ab': ab
    })

def dashboard(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    context = {
        'total_files': fileupload.objects.count(),
        'received_files': fileupload.objects.filter(status='Forwarded').count(),
        'pending_files': fileupload.objects.filter(status='Pending').count(),
        'closed_files': fileupload.objects.filter(status='Close').count(),
        'rejected_files': fileupload.objects.filter(status='Reject').count(),
        'employees': addemp.objects.count(),
        'departments': adddepartment.objects.count(),
    }

    return render(request, 'admin/dashboard.html', context)


    
        