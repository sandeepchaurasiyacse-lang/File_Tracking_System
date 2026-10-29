from django.db import migrations

def create_default_data(apps, schema_editor):
    Login = apps.get_model('myapp', 'login')
    AddEmp = apps.get_model('myapp', 'addemp')
    AddDepartment = apps.get_model('myapp', 'adddepartment')

    # 1. Create Default Admin in login table
    admin_login, _ = Login.objects.get_or_create(
        username='admin@gmail.com',
        defaults={'password': 'admin@123', 'role': 'Admin'}
    )
    if admin_login.role != 'Admin' or admin_login.password != 'admin@123':
        admin_login.role = 'Admin'
        admin_login.password = 'admin@123'
        admin_login.save()

    # 2. Create Default Departments
    dep_it, _ = AddDepartment.objects.get_or_create(
        dep_code='DEP-IT',
        defaults={
            'dep_name': 'Information Technology',
            'dep_head': 'Mr. Head IT',
            'dep_email': 'it@ggl.com',
            'dep_number': '0522-123456',
            'status': 'Active',
            'create_at': '10:00:00'
        }
    )
    dep_hr, _ = AddDepartment.objects.get_or_create(
        dep_code='DEP-HR',
        defaults={
            'dep_name': 'Human Resources',
            'dep_head': 'Mrs. Head HR',
            'dep_email': 'hr@ggl.com',
            'dep_number': '0522-654321',
            'status': 'Active',
            'create_at': '10:00:00'
        }
    )

    # 3. Create Default Admin in addemp table
    AddEmp.objects.get_or_create(
        username='admin@gmail.com',
        defaults={
            'name': 'Administrator',
            'email': 'admin@gmail.com',
            'mobile': '9876543210',
            'password': 'admin@123',
            'address': 'GGL Head Office, Vibhuti Khand, Gomti Nagar, Lucknow',
            'department': 'Information Technology',
            'disignation': 'System Administrator',
            'status': 'Active',
            'emp_id': 'EMP001'
        }
    )

    # 4. Create Default Users (Employees)
    AddEmp.objects.get_or_create(
        username='rakesh@gmail.com',
        defaults={
            'name': 'Rakesh Kumar',
            'email': 'rakesh@gmail.com',
            'mobile': '9876543211',
            'password': 'admin@123',
            'address': 'Lucknow, UP',
            'department': 'Information Technology',
            'disignation': 'Senior Engineer',
            'status': 'Active',
            'emp_id': 'EMP002'
        }
    )
    Login.objects.get_or_create(
        username='rakesh@gmail.com',
        defaults={'password': 'admin@123', 'role': 'User'}
    )

    AddEmp.objects.get_or_create(
        username='amit@fms.com',
        defaults={
            'name': 'Amit Verma',
            'email': 'amit@fms.com',
            'mobile': '9876543212',
            'password': 'admin@123',
            'address': 'Agra, UP',
            'department': 'Human Resources',
            'disignation': 'HR Executive',
            'status': 'Active',
            'emp_id': 'EMP003'
        }
    )
    Login.objects.get_or_create(
        username='amit@fms.com',
        defaults={'password': 'admin@123', 'role': 'User'}
    )

def remove_default_data(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0022_alter_adddepartment_dep_code_and_more'),
    ]

    operations = [
        migrations.RunPython(create_default_data, remove_default_data),
    ]
