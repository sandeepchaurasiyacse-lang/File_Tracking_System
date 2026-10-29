from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
from django.contrib import messages
from datetime import datetime
from django.db.models import Q  
from django.utils import timezone
from django.views.decorators.cache import cache_control
from django.core.mail import send_mail
from django.conf import settings
import re

def home(request):
    return render(request, 'user/home.html')

def Adminlogin(request):
    saved_admin_username = request.COOKIES.get('remember_admin', '')
    return render(request, 'admin/adminlogin.html', {'saved_admin_username': saved_admin_username})

def loginsave(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        remember = request.POST.get('remember')

        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return redirect('adminlogin')

        user = login.objects.filter(username=username, password=password).first()
        if user:
            if user.role and (user.role.lower() == 'admin'):
                request.session['adminid'] = username
                response = redirect('dashboard')
                if remember:
                    request.session.set_expiry(1209600)
                    response.set_cookie('remember_admin', username, max_age=1209600)
                else:
                    request.session.set_expiry(0)
                    response.delete_cookie('remember_admin')
                return response
            else:
                messages.error(request, 'You are not admin please go to user login.')
                return redirect('adminlogin')    
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('adminlogin')
    return redirect('adminlogin')

def admin_forgot_password(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not username or not new_password or not confirm_password:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'admin/admin_forgot_password.html')

        if len(new_password) < 4:
            messages.error(request, "Password must be at least 4 characters long.")
            return render(request, 'admin/admin_forgot_password.html')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match. Please try again.")
            return render(request, 'admin/admin_forgot_password.html')

        admin_user = login.objects.filter(username=username, role__iexact='Admin').first()
        if admin_user:
            admin_user.password = new_password
            admin_user.save()
            addemp.objects.filter(username=username).update(password=new_password)
            messages.success(request, "Admin password reset successfully! Please login with your new password.")
            return redirect('adminlogin')
        else:
            messages.error(request, "No Admin account found with this email/username.")
            return render(request, 'admin/admin_forgot_password.html')

    return render(request, 'admin/admin_forgot_password.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dashboard(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    recent_history = File_History.objects.order_by('-id')[:5]
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
        'total_files': fileupload.objects.count(),
        'received_files': fileupload.objects.filter(Q(status__iexact='Forwarded') | Q(status__iexact='Received')).count(),
        'pending_files': fileupload.objects.filter(status__iexact='Pending').count(),
        'closed_files': fileupload.objects.filter(status__iexact='Close') | fileupload.objects.filter(status__iexact='Closed'),
        'closed_count': fileupload.objects.filter(Q(status__iexact='Close') | Q(status__iexact='Closed')).count(),
        'rejected_files': fileupload.objects.filter(status__iexact='Reject') | fileupload.objects.filter(status__iexact='Rejected'),
        'rejected_count': fileupload.objects.filter(Q(status__iexact='Reject') | Q(status__iexact='Rejected')).count(),
        'employees': addemp.objects.count(),
        'departments': adddepartment.objects.count(),
        'recent': recent,
    }
    context['closed_files'] = context['closed_count']
    context['rejected_files'] = context['rejected_count']
    return render(request, 'admin/dashboard.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminlogout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('adminlogin')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adddep(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    return render(request, 'admin/adddep.html') 

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def dep_save(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    if request.method == "POST":
        dep_name = request.POST.get('dep_name', '').strip()
        dep_code = request.POST.get('dep_code', '').strip()
        dep_head = request.POST.get('dep_head', '').strip()
        status = request.POST.get('status', 'Active').strip()
        dep_email = request.POST.get('dep_email', '').strip()
        dep_number = request.POST.get('dep_number', '').strip()

        if not dep_name or not dep_code or not dep_head or not dep_email or not dep_number:
            messages.error(request, "Please fill in all required department fields.")
            return redirect('adddep')

        if len(dep_number) != 10 or not dep_number.isdigit():
            messages.error(request, "Contact number must be exactly 10 digits.")
            return redirect('adddep')

        if adddepartment.objects.filter(Q(dep_name__iexact=dep_name) | Q(dep_code__iexact=dep_code) | Q(dep_email__iexact=dep_email)).exists():
            messages.error(request, "A department with this Name, Code, or Email already exists.")
            return redirect('adddep')

        create_at = timezone.now().time()
        adddepartment.objects.create(
            dep_name=dep_name,
            dep_code=dep_code,
            dep_head=dep_head,
            status=status,
            dep_email=dep_email,
            dep_number=dep_number,
            create_at=create_at
        )
        messages.success(request, 'Add Department Successfully')
        return redirect('adddep')

    return redirect('adddep')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def depshow(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    ab = adddepartment.objects.all()
    return render(request, 'admin/depshow.html', {'ab': ab})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def managedep(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    ab = adddepartment.objects.all()
    return render(request, 'admin/managedep.html', {'ab': ab})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def empadd(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    dp = adddepartment.objects.all()

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        emp_id = request.POST.get('emp_id', '').strip()
        department = request.POST.get('department', '').strip()
        disignation = request.POST.get('disignation', '').strip()
        role = request.POST.get('role', '').strip()
        status = request.POST.get('status', 'Active').strip()
        password = request.POST.get('password', '').strip()
        photo = request.FILES.get('photo')
        address = request.POST.get('address', '').strip()

        # Validation Checks
        if not name or not username or not email or not mobile or not emp_id or not department or not disignation or not role or not password:
            messages.error(request, "Please fill in all required fields.")
            return redirect('empadd')

        if len(name) < 2:
            messages.error(request, "Please enter a valid full name.")
            return redirect('empadd')

        if len(mobile) != 10 or not mobile.isdigit():
            messages.error(request, "Mobile number must be a valid 10-digit number.")
            return redirect('empadd')

        if len(password) < 4:
            messages.error(request, "Password must be at least 4 characters long.")
            return redirect('empadd')

        if addemp.objects.filter(Q(username__iexact=username) | Q(email__iexact=email) | Q(emp_id__iexact=emp_id)).exists():
            messages.error(request, "An employee with this Username, Email or Employee ID already exists.")
            return redirect('empadd')

        if login.objects.filter(username__iexact=username).exists():
            messages.error(request, "This username/email is already registered in the login system.")
            return redirect('empadd')

        # Save credentials to login model
        login.objects.create(username=username, password=password, role=role)

        # Save employee details to addemp model
        addemp.objects.create(
            name=name,
            username=username,
            email=email,
            mobile=mobile,
            emp_id=emp_id,
            department=department,
            disignation=disignation,
            role=role,
            status=status,
            password=password,
            photo=photo,
            address=address
        )
        messages.success(request, 'Add Employee Successfully')

        # Send credentials email to employee
        message = f"""Dear {name},

Greetings from Green Gas Limited (GGL).

Your account has been successfully created for the GGL File Tracking System.

User ID / Email : {username}
Password        : {password}
Role            : {role}

Regards,
System Administrator
Green Gas Limited (GGL)"""

        try:
            send_mail(
                "GGL File Tracking System - Login Credentials",
                message,
                settings.EMAIL_HOST_USER,
                [username],
                fail_silently=True,
            )
        except Exception:
            pass

        return redirect('empadd')

    return render(request, 'admin/empadd.html', {'dp': dp})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def empshow(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    bc = addemp.objects.all()
    return render(request, 'admin/empshow.html', {'bc': bc})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manageemp(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    ab = addemp.objects.all()
    return render(request, 'admin/manageemp.html', {'ab': ab})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def createfile(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    adminid = request.session.get('adminid')
    dp = adddepartment.objects.all()
    em = addemp.objects.all()

    if request.method == "POST":
        subject = request.POST.get('subject', '').strip()
        priority = request.POST.get('priority', 'Medium').strip()
        department = request.POST.get('department', '').strip()
        current_user = request.POST.get('current_user', '').strip()
        description = request.POST.get('description', '').strip()
        custom_file_no = request.POST.get('file_no', '').strip()

        if not subject or not priority or not department or not current_user:
            messages.error(request, "Please fill in all required file details (Subject, Priority, Department, Assign User).")
            return redirect('createfile')

        if custom_file_no:
            if fileupload.objects.filter(file_no__iexact=custom_file_no).exists():
                messages.error(request, f"File number {custom_file_no} already exists. Please choose a different number.")
                return redirect('createfile')
            file_no = custom_file_no
        else:
            all_files = fileupload.objects.all()
            max_num = 0
            for f in all_files:
                nums = re.findall(r'\d+', f.file_no)
                if nums:
                    num = int(nums[-1])
                    if num > max_num:
                        max_num = num
            file_no = f"FIL{max_num + 1:03d}"

        status = "Forwarded"
        create_at = timezone.now().date()

        fhs = File_History(
            File_no=file_no,
            current_user=adminid,
            forwarded_user=current_user,
            remark=description,
            action=status,
            create_at=create_at
        )
        fhs.save()

        fileupload.objects.create(
            file_no=file_no,
            subject=subject,
            create_user=adminid,
            priority=priority,
            department=department,
            current_user=current_user,
            file=request.FILES.get('file'),
            description=description,
            create_at=timezone.now().time(),
            status=status
        )

        messages.success(request, "File Created Successfully")
        return redirect('createfile')

    con = {'dp': dp, 'em': em}
    return render(request, 'admin/createfile.html', con)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def receivedfile(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    sid = request.session.get('adminid')
    ab = fileupload.objects.filter(current_user=sid)
    return render(request, 'admin/receivedfile.html', {'ab': ab}) 

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def sentfile(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    sid = request.session.get('adminid')
    ab = fileupload.objects.filter(create_user=sid)
    return render(request, 'admin/sentfiles.html', {'ab': ab})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def pendingfiles(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    ab = fileupload.objects.filter(status__iexact='Pending')
    return render(request, 'admin/pendingfiles.html', {'ab': ab})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def allfile(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')
    ab = fileupload.objects.all()
    return render(request, 'admin/allfile.html', {'ab': ab})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def filetrack(request):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    search = request.GET.get('search', '').strip()
    ab = fileupload.objects.all()
    if search:
        ab = ab.filter(
            Q(file_no__icontains=search) |
            Q(subject__icontains=search) |
            Q(create_user__icontains=search) |
            Q(current_user__icontains=search)
        )

    return render(request, 'admin/filetrack.html', {'ab': ab})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ad_Details_file(request, file_no):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    sn = request.session.get('adminid')
    ur = addemp.objects.all()
    fileh = File_History.objects.filter(File_no=file_no).order_by('-id')
    ab = fileupload.objects.filter(file_no=file_no).first()

    if not ab:
        messages.error(request, "File not found")
        return redirect('allfile')

    if request.method == "POST":
        action = request.POST.get('action', '').strip()
        forwarded_user = request.POST.get('forwarded_user', '').strip()
        remark = request.POST.get('remark', '').strip()
        create_at = timezone.now().date()

        if not action:
            messages.error(request, "Please select an action.")
            return redirect('ad_Details_file', file_no=file_no)

        if action.lower() in ['forward', 'forwarded'] and not forwarded_user:
            messages.error(request, "Please select a user to forward the file.")
            return redirect('ad_Details_file', file_no=file_no)

        if action.lower() in ['close', 'closed']:
            ab.status = 'Closed'
            ab.current_user = sn
        else:
            ab.current_user = forwarded_user if forwarded_user else ab.current_user
            ab.status = action.capitalize() if action else ab.status
        ab.save()

        fh = File_History(
            File_no=ab.file_no,
            current_user=sn,
            action=ab.status,
            forwarded_user=forwarded_user if forwarded_user else sn,
            remark=remark,
            create_at=create_at
        )
        fh.save()
        messages.success(request, "File action updated successfully")
        return redirect('receivedfile')

    context = {'ab': ab, 'ur': ur, 'fileh': fileh}
    return render(request, 'admin/ad_Details_file.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_file(request, file_no):
    if 'adminid' not in request.session:
        return redirect('adminlogin')

    obj = fileupload.objects.filter(file_no=file_no).first()
    if not obj:
        messages.error(request, "File not found")
        return redirect('sentfiles')

    if request.method == "POST":
        subject = request.POST.get('subject', '').strip()
        priority = request.POST.get('priority', '').strip()
        department = request.POST.get('department', '').strip()
        description = request.POST.get('description', '').strip()

        if not subject or not priority or not department:
            messages.error(request, "Subject, Priority, and Department cannot be empty.")
            return render(request, 'admin/editfile.html', {'obj': obj})

        obj.subject = subject
        obj.priority = priority
        obj.department = department
        obj.description = description
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

    obj = fileupload.objects.filter(file_no=file_no).first()
    if obj:
        obj.delete()
        messages.success(request, "File Deleted Successfully")
    return redirect('sentfiles')

# ==================== User Views ====================

def userlogin(request):
    saved_username = request.COOKIES.get('remember_user', '')
    return render(request, 'user/userlogin.html', {'saved_username': saved_username})

def userlogcode(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        remember = request.POST.get('remember')

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return redirect('userlogin')

        user = addemp.objects.filter(Q(username=username) | Q(email=username), password=password).first()
        if user:
            if user.status and user.status.lower() == "active":
                request.session['userid'] = user.username
                request.session['name'] = user.name
                
                response = redirect('userdashboard')
                if remember:
                    request.session.set_expiry(1209600)
                    response.set_cookie('remember_user', username, max_age=1209600)
                else:
                    request.session.set_expiry(0)
                    response.delete_cookie('remember_user')
                return response
            else:
                messages.error(request, "Your account is inactive. Please contact administrator.")
                return redirect('userlogin')
        messages.error(request, "Invalid Username or Password")
        return redirect('userlogin')
    return redirect('userlogin')

def forgot_password(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not username or not new_password or not confirm_password:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'user/forgot_password.html')

        if len(new_password) < 4:
            messages.error(request, "Password must be at least 4 characters long.")
            return render(request, 'user/forgot_password.html')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match. Please try again.")
            return render(request, 'user/forgot_password.html')

        user = addemp.objects.filter(Q(username=username) | Q(email=username)).first()
        if user:
            user.password = new_password
            user.save()
            login.objects.filter(username=user.username).update(password=new_password)
            messages.success(request, "Password reset successfully! Please login with your new password.")
            return redirect('userlogin')
        else:
            messages.error(request, "No account found with this email/username.")
            return render(request, 'user/forgot_password.html')

    return render(request, 'user/forgot_password.html')      

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userdashboard(request):
    if 'userid' not in request.session:
        return redirect('userlogin')

    username = request.session.get('userid')
    my_files = fileupload.objects.filter(create_user=username).count()
    received_files = fileupload.objects.filter(current_user=username).count()
    sent_files = File_History.objects.filter(current_user=username).count()
    pending_files = fileupload.objects.filter(current_user=username, status__iexact="Pending").count()

    recent_history = File_History.objects.filter(
        Q(current_user=username) | Q(forwarded_user=username)
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
    return render(request, 'user/userlayout.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userlogout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('userlogin')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ur_upload_files(request):
    if 'userid' not in request.session:
        return redirect('userlogin')

    userid = request.session.get('userid')
    dp = adddepartment.objects.all()
    em = addemp.objects.all()

    if request.method == "POST":
        subject = request.POST.get('subject', '').strip()
        priority = request.POST.get('priority', 'Medium').strip()
        department = request.POST.get('department', '').strip()
        current_user = request.POST.get('current_user', '').strip()
        description = request.POST.get('description', '').strip()
        custom_file_no = request.POST.get('file_no', '').strip()

        if not subject or not priority or not department or not current_user:
            messages.error(request, "Please fill in all required file details (Subject, Priority, Department, Assign User).")
            return redirect('ur_upload_files')

        if custom_file_no:
            if fileupload.objects.filter(file_no__iexact=custom_file_no).exists():
                messages.error(request, f"File number {custom_file_no} already exists. Please choose a different number.")
                return redirect('ur_upload_files')
            file_no = custom_file_no
        else:
            all_files = fileupload.objects.all()
            max_num = 0
            for f in all_files:
                nums = re.findall(r'\d+', f.file_no)
                if nums:
                    num = int(nums[-1])
                    if num > max_num:
                        max_num = num
            file_no = f"FIL{max_num + 1:03d}"

        status = "Forwarded"
        create_at = timezone.now().date()

        fhs = File_History(
            File_no=file_no,
            current_user=userid,
            forwarded_user=current_user,
            remark=description,
            action=status,
            create_at=create_at
        )
        fhs.save()

        fileupload.objects.create(
            file_no=file_no,
            subject=subject,
            create_user=userid,
            priority=priority,
            department=department,
            current_user=current_user,
            file=request.FILES.get('file'),
            description=description,
            create_at=timezone.now().time(),
            status=status
        )

        messages.success(request, "File Created Successfully")
        return redirect('ur_upload_files')

    con = {'dp': dp, 'em': em}
    return render(request, 'user/ur_uploadfiles.html', con)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ur_receivedfiles(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    sid = request.session.get('userid')
    ab = fileupload.objects.filter(current_user=sid)
    return render(request, 'user/ur_receivedfiles.html', {'ab': ab, 'sid': sid})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ur_sentfile(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    sid = request.session.get('userid')
    ab = fileupload.objects.filter(create_user=sid)
    return render(request, 'user/ur_sentfile.html', {'ab': ab})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def pendingfile(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    sid = request.session.get('userid')
    ab = fileupload.objects.filter(current_user=sid, status__iexact='Pending')
    return render(request, 'user/pendingfile.html', {'ab': ab})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ur_allfiles(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    sid = request.session.get('userid')
    ab = fileupload.objects.filter(create_user=sid)
    return render(request, 'user/ur_allfiles.html', {'ab': ab})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def trackfile(request):
    if 'userid' not in request.session:
        return redirect('userlogin')

    search = request.GET.get('search', '').strip()
    ab = fileupload.objects.all()
    if search:
        ab = ab.filter(
            Q(file_no__icontains=search) |
            Q(subject__icontains=search) |
            Q(create_user__icontains=search) |
            Q(current_user__icontains=search)
        )

    return render(request, 'user/trackfile.html', {'ab': ab})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Details_file(request, file_no):
    if 'userid' not in request.session:
        return redirect('userlogin')

    sn = request.session.get('userid')
    ur = addemp.objects.all()
    fileh = File_History.objects.filter(File_no=file_no).order_by('-id')
    ab = fileupload.objects.filter(file_no=file_no).first()

    if not ab:
        messages.error(request, "File not found")
        return redirect('ur_allfiles')

    can_close = (ab.create_user == sn)

    if request.method == "POST":
        action = request.POST.get('action', '').strip()
        forwarded_user = request.POST.get('forwarded_user', '').strip()
        remark = request.POST.get('remark', '').strip()
        create_at = timezone.now().date()

        if not action:
            messages.error(request, "Please select an action.")
            return redirect('Details_file', file_no=file_no)

        if action.lower() in ['forward', 'forwarded'] and not forwarded_user:
            messages.error(request, "Please select a user to forward the file.")
            return redirect('Details_file', file_no=file_no)

        if action.lower() in ['close', 'closed']:
            if not can_close:
                messages.error(request, "Only the creator of this file or Admin can close it.")
                return redirect('Details_file', file_no=file_no)
            ab.status = 'Closed'
            ab.current_user = sn
        else:
            ab.current_user = forwarded_user if forwarded_user else ab.current_user
            ab.status = action.capitalize() if action else ab.status
        ab.save()

        fh = File_History(
            File_no=ab.file_no,
            current_user=sn,
            action=ab.status,
            forwarded_user=forwarded_user if forwarded_user else sn,
            remark=remark,
            create_at=create_at
        )
        fh.save()
        messages.success(request, "File action updated successfully")
        return redirect('ur_receivedfiles')

    context = {'ab': ab, 'ur': ur, 'fileh': fileh, 'can_close': can_close}
    return render(request, 'user/Details_file.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def us_showfile(request):
    if 'userid' not in request.session:
        return redirect('userlogin')
    sid = request.session.get('userid')
    ab = fileupload.objects.filter(current_user=sid)
    return render(request, 'user/us_showfile.html', {'ab': ab})