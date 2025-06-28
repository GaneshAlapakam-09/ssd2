from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .decorators import admin_branch_required

from ssdapp.models import Employee,BillingMaster,Payment_Master

# for graph data
from django.db.models import Sum
from django.db.models.functions import TruncDay
from django.utils import timezone
from collections import OrderedDict
import calendar

# Create your views here.


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        upperuser=username.upper()
        password = request.POST['password']
        user = authenticate(username=upperuser, password=password)
        if user is not None:
            if user.Office_Branch == 'main':
                login(request, user)
                return redirect('ssdapp:dashboard')
            elif user.Office_Branch == 'branch_one':
                login(request, user)
                return redirect('branch_one:dashboard')
            elif user.Office_Branch == 'admin':
                login(request, user)
                return redirect('mainapp:graph')
        else:
            messages.info(request, "username and password not match")
            return redirect('mainapp:signin')
    return render(request, 'pages.signin.html')
