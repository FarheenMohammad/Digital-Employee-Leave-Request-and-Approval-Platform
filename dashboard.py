from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
import datetime
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse
from employee.forms import EmployeeCreateForm
from leave.models import Leave
from employee.models import *
from leave.forms import LeaveCreationForm


def dashboard(request):
    dataset = dict()
    user = request.user

    if not user.is_authenticated:
        return redirect('accounts:login')

    employees = Employee.objects.all()
    leaves = Leave.objects.all_pending_leaves()
    staff_leaves = Leave.objects.filter(user=user)

    dataset['employees'] = employees
    dataset['leaves'] = leaves
    dataset['staff_leaves'] = staff_leaves
    dataset['title'] = 'summary'

    return render(request, 'dashboard/dashboard_index.html', dataset)


def dashboard_employees(request):
    if not (request.user.is_authenticated and request.user.is_superuser and request.user.is_staff):
        return redirect('/')

    dataset = dict()
    departments = Department.objects.all()
    employees = Employee.objects.all()

    query = request.GET.get('search')
    if query:
        employees = employees.filter(
            Q(firstname__icontains=query) |
            Q(lastname__icontains=query)
        )

    paginator = Paginator(employees, 10)
    page = request.GET.get('page')
    employees_paginated = paginator.get_page(page)

    dataset['departments'] = departments
    dataset['employees'] = employees_paginated

    return render(request, 'dashboard/employee_app.html', dataset)


def dashboard_employees_create(request):
    if not (request.user.is_authenticated and request.user.is_superuser and request.user.is_staff):
        return redirect('/')

    if request.method == 'POST':
        form = EmployeeCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user_id = request.POST.get('user')
            assigned_user = User.objects.get(id=user_id)

            # Prevent duplicate
            if Employee.objects.filter(user=assigned_user).exists():
                messages.error(request, 'Trying to create duplicate employee with a single user account.',
                               extra_tags='alert alert-warning alert-dismissible show')
                return redirect("dashboard:employeecreate")

            instance = form.save(commit=False)
            instance.user = assigned_user

            instance.title = request.POST.get('title')
            instance.image = request.FILES.get('image')
            instance.firstname = request.POST.get('firstname')
            instance.lastname = request.POST.get('lastname')
            instance.othername = request.POST.get('othername')
            instance.birthday = request.POST.get('birthday')

            role_id = request.POST.get('role')
            role_instance = Role.objects.get(id=role_id)
            instance.role = role_instance

            instance.startdate = request.POST.get('startdate')
            instance.employeetype = request.POST.get('employeetype')
            instance.employeeid = request.POST.get('employeeid')
            instance.dateissued = request.POST.get('dateissued')

            instance.save()
            return redirect("dashboard:employees")

    else:
        form = EmployeeCreateForm()

    dataset = {
        'form': form,
        'title': 'Register Employee'
    }
    return render(request, 'dashboard/employee_create.html', dataset)


def employee_edit_data(request, id):
    if not (request.user.is_authenticated and request.user.is_superuser and request.user.is_staff):
        return redirect('/')

    employee = get_object_or_404(Employee, id=id)

    if request.method == "POST":
        form = EmployeeCreateForm(request.POST, request.FILES, instance=employee)

        if form.is_valid():
            instance = form.save(commit=False)

            user_id = request.POST.get('user')
            assigned_user = User.objects.get(id=user_id)
            instance.user = assigned_user

            instance.image = request.FILES.get("image")
            instance.firstname = request.POST.get('firstname')
            instance.lastname = request.POST.get('lastname')
            instance.othername = request.POST.get('othername')
            instance.birthday = request.POST.get('birthday')

            religion_id = request.POST.get('religion')
            instance.religion = Religion.objects.get(id=religion_id)

            nationality_id = request.POST.get('nationality')
            instance.nationality = Nationality.objects.get(id=nationality_id)

            department_id = request.POST.get('department')
            instance.department = Department.objects.get(id=department_id)

            instance.hometown = request.POST.get('hometown')
            instance.region = request.POST.get('region')
            instance.residence = request.POST.get('residence')
            instance.address = request.POST.get('address')
            instance.education = request.POST.get('education')
            instance.lastwork = request.POST.get('lastwork')
            instance.position = request.POST.get('position')
            instance.ssnitnumber = request.POST.get('ssnitnumber')
            instance.tinnumber = request.POST.get('tinnumber')

            role_id = request.POST.get('role')
            instance.role = Role.objects.get(id=role_id)

            instance.startdate = request.POST.get('startdate')
            instance.employeetype = request.POST.get('employeetype')
            instance.employeeid = request.POST.get('employeeid')
            instance.dateissued = request.POST.get('dateissued')

            instance.updated = datetime.datetime.now()
            instance.save()

            messages.success(request, 'Employee data updated successfully.')
            return redirect('dashboard:employees')
    else:
        form = EmployeeCreateForm(instance=employee)

    dataset = {
        'form': form,
        'employee': employee,
        'title': 'Edit Employee'
    }
    return render(request, 'dashboard/employee_edit.html', dataset)
