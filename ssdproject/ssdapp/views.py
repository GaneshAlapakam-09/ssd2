import traceback
from django.shortcuts import render,redirect, get_object_or_404
from django.urls import reverse
from .models import Cash_Book_Details, CustomerMaster,CustomerDetails, Expense_Category,MaterialMaster,InwardMaster,ProductMaster,CategoriesMaster,CostMaster,BillingMaster,QuoteMaster, EstimateMaster, BillingDetails, QuoteDetails, EstimateDetails, Payment_Master, Payment_Details,Cash_Book_Master, Employee, OutwardMaster
from django.contrib import messages

from django.http import HttpResponse
from weasyprint import HTML


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from django.contrib.auth.hashers import make_password

from django.contrib.auth.decorators import login_required, user_passes_test

from django.contrib.auth import authenticate,login,logout

from datetime import datetime,date,timedelta
from django.utils.timezone import now
from zoneinfo import ZoneInfo

import os
from django.core.files.storage import default_storage
# from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt


import qrcode
import io
import base64

from django.db.models import F

# Create your views here.

       
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'
def is_employee(user):
    return user.is_authenticated and user.role == 'employee'



def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username,password = password)
        if user is not None:
            login(request,user)
            return redirect('dashboard')
        else:
            messages.info(request,"username and password not match")
            return redirect('signin')
    return render(request,'pages.signin.html')

@login_required(login_url='signin')
def dashboard(request):
    return render(request,'index.html')



@login_required(login_url='signin')
def addCustomer(request):
    if request.method == 'POST':
        type_radio = request.POST['customer_type']
        name = request.POST['name']
        phone = request.POST['phone']
        altPhone = request.POST['alt_phone'].strip() or 000  # Set to None if empty
        email = request.POST['email'].strip() or 'None'        # Set to None if empty
        address = request.POST['address'].strip() or 'None'    # Set to None if empty

        last_customer = CustomerMaster.objects.filter(Customer_Id__isnull=False).order_by('-Customer_Id').first()
        if last_customer:
            last_id = int(last_customer.Customer_Id[4:])  # Extract the numeric part
            new_id = f"SSDC{last_id + 1:04d}"
        else:
            new_id = "SSDC0001"

        last_Agent = CustomerMaster.objects.filter(Agent_Id__isnull=False).order_by('-Agent_Id').first()
        
        if last_Agent:
            last_id = int(last_Agent.Agent_Id[4:])  # Extract the numeric part
            new_agent_id = f"SSDA{last_id + 1:04d}"
        else:
            new_agent_id = "SSDA0001"

        if type_radio == "customer" :
            CustomerMaster.objects.create(Customer_Id = new_id, Customer_Name = name.upper(), Phone_No = phone)
            CustomerDetails.objects.create(Customer_Id = new_id, Customer_Name = name.upper(), Phone_No = phone, Alt_Phone = altPhone, Email = email, Address = address,Type = type_radio)
        elif type_radio == "agent" :
            CustomerMaster.objects.create(Agent_Id = new_agent_id, Customer_Name = name.upper(), Phone_No = phone)
            CustomerDetails.objects.create(Agent_Id = new_agent_id, Customer_Name = name.upper(), Phone_No = phone, Alt_Phone = altPhone, Email = email, Address = address,Type = type_radio)

        return redirect('listcustomer')
 
    last_customer = CustomerMaster.objects.filter(Customer_Id__isnull=False).order_by('-Customer_Id').first()
    if last_customer:
        last_id = int(last_customer.Customer_Id[4:])  # Extract the numeric part
        new_id = f"SSDC{last_id + 1:04d}"
    else:
        new_id = "SSDC0001"

    last_Agent =  CustomerMaster.objects.filter(Agent_Id__isnull=False).order_by('-Agent_Id').first()
    if last_Agent:
        last_id = int(last_Agent.Agent_Id[4:])  # Extract the numeric part
        new_agent_id = f"SSDA{last_id + 1:04d}"
    else:
        new_agent_id = "SSDA0001"
    
    phone = CustomerDetails.objects.filter(Status = 1)
    context = {'data':new_id, 'data2':new_agent_id, 'phone': phone}

    return render(request,'add_customer.html',context)

@login_required(login_url='signin')
def listCustomer(request):
    data = CustomerDetails.objects.filter(Status = 1)
    context = {'data':data}
    return render(request,'list_customer.html',context)

@login_required(login_url='signin')
def customerDetail(request,id):
    if id.startswith("SSDC"):
        data = CustomerDetails.objects.filter(Customer_Id = id , Status =1)
    elif id.startswith("SSDA"):
        data = CustomerDetails.objects.filter(Agent_Id = id , Status =1)
    context = {'data':data}
    return render(request,'customer_details.html',context)


@login_required(login_url='signin')
def editCustomer(request,id):
    if request.method == 'POST':
        if request.method == 'POST':
            customerId = request.POST['customer_id']
            name = request.POST['name']
            phone = request.POST['phone']
            altPhone = request.POST['alt_phone']
            email = request.POST['email']
            address = request.POST['address']
            if id.startswith("SSDC"):
                CustomerDetails.objects.filter(Customer_Id=customerId).update(Customer_Name = name,Phone_No = phone, Alt_Phone = altPhone, Email = email, Address = address)
            elif id.startswith("SSDA"):
                CustomerDetails.objects.filter(Agent_Id=customerId).update(Customer_Name = name,Phone_No = phone, Alt_Phone = altPhone, Email = email, Address = address)
            
            return redirect('listcustomer')

    if id.startswith("SSDC"):
        data = CustomerDetails.objects.filter(Customer_Id = id , Status =1)
    elif id.startswith("SSDA"):
        data = CustomerDetails.objects.filter(Agent_Id = id , Status =1)
    context = {'data':data}
    return render(request,'edit_customer.html',context)
@login_required(login_url='signin')
def deleteCustomer(request,id):
    if id.startswith("SSDC"):
        existing_customer = BillingMaster.objects.filter(Customer_Id = id)
        if not existing_customer:
            CustomerDetails.objects.filter(Customer_Id = id).update(Status = 0)
            CustomerMaster.objects.filter(Customer_Id = id).update(Status = 0)
        else:
            messages.info(request,"This Custromer have Transactions With Us")
            return redirect('listcustomer')

    elif id.startswith("SSDA"):
        existing_agent = BillingMaster.objects.filter(Agent_Id = id)
        if not existing_agent:
            CustomerDetails.objects.filter(Agent_Id = id).update(Status = 0)
            CustomerMaster.objects.filter(Agent_Id = id).update(Status = 0)
        else:
            messages.info(request,"This Agent have Transactions With Us")
            return redirect('listcustomer')

    return redirect('listcustomer')

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def addMaterial(request):
    if request.method == "POST":
        material_name = request.POST['name']
        date =  request.POST['date']
        material_make = request.POST['material_make']
        material_size_in_meters = request.POST['material_size_in_meter']
        material_size_in_feet = request.POST['material_size_in_feet']
        additional_info = request.POST['additiona_info']
        # Generate Material_Id starting with jremp0001 and display in back-end
        last_material = MaterialMaster.objects.order_by('-Material_Id').first()
        if last_material:
            last_id = int(last_material.Material_Id[3:])  # Extract the numeric part
            new_id = f"MAT{last_id + 1:04d}"
        else:
            new_id = "MAT0001"
        context = {'data':new_id}
        MaterialMaster.objects.create(Material_Id = new_id,Date = date, Material_Name = material_name.upper(), Material_Make = material_make.upper(), Material_Size_In_Meters = material_size_in_meters, Material_Size_In_Feet = material_size_in_feet, Additional_Info = additional_info)
        return redirect('listmaterial')
        


    # Generate Material_Id starting with jremp0001 and display in front-end 
    last_material = MaterialMaster.objects.order_by('-Material_Id').first()
    if last_material:
        last_id = int(last_material.Material_Id[3:])  # Extract the numeric part
        new_id = f"MAT{last_id + 1:04d}"
    else:
        new_id = "MAT0001"
    context = {'data':new_id}
    return render(request,'add_material.html',context)

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def listMaterial(request):
    data = MaterialMaster.objects.filter(Status = 1)
    context = {'data':data}
    return render(request,'list_material.html',context)

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def editMaterial(request,id):
    if request.method == "POST":
        material_name = request.POST['name']
        date =  request.POST['date']
        material_make = request.POST['material_make']
        material_size_in_meters = request.POST['material_size_in_meter']
        material_size_in_feet = request.POST['material_size_in_feet']
        additional_info = request.POST['additiona_info']
        MaterialMaster.objects.filter(Material_Id = id).update(Material_Name = material_name.upper(), Date = date, Material_Make = material_make.upper(), Material_Size_In_Meters = material_size_in_meters, Material_Size_In_Feet = material_size_in_feet, Additional_Info = additional_info)
        return redirect('listmaterial')
    data = MaterialMaster.objects.filter(Material_Id = id , Status =1)
    context = {'data':data}
    return render(request,'edit_material.html',context)

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def materialDetails(request,id):
    data = MaterialMaster.objects.filter(Material_Id = id , Status =1)
    context = {'data':data}
    return render(request,'material_details.html',context)

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def deleteMaterial(request,id):
    MaterialMaster.objects.filter(Material_Id = id).update(Status = 0)
    return redirect('listmaterial')


@login_required(login_url='signin')
def select_material(request):
    if request.method == 'POST':
        material_id = request.POST['material_id']
        date =  request.POST['date']
        vendor_name = request.POST['vendor_name']
        vendor_phone = request.POST['vendor_phone']
        vendor_gst = request.POST['vendor_gst']
        invoice_cost = request.POST['invoice_cost']
        invoice_quantity = request.POST['invoice_quantity']
        batch_no = request.POST['batch_no']
        additional_info = request.POST['additional_info']
        name = MaterialMaster.objects.get(Material_Id = material_id)

        last_Sno = InwardMaster.objects.last()  # Get the last entry

        if last_Sno:  
            new_sno = last_Sno.S_No + 1  # Assuming 'Sno' is the integer field storing serial numbers
        else:
            new_sno = 1  # Start from 1 if no records exist


        # Generate Inward_Id starting with INW0001 and store in back-end 
        last_inward = InwardMaster.objects.order_by('-Inward_Id').first()
        if last_inward:
            last_id = int(last_inward.Inward_Id[3:])  # Extract the numeric part
            new_inw_id = f"INW{last_id + 1:04d}"
        else:
            new_inw_id = "INW0001"

        # Generate Batch_Id starting with BAT0001 and store in back-end 
        last_batch = InwardMaster.objects.order_by('-Batch_Id').first()
        if last_batch:
            last_id = int(last_batch.Batch_Id[3:])  # Extract the numeric part
            new_bat_id = f"BAT{last_id + 1:04d}"
        else:
            new_bat_id = "BAT0001"


        Material = MaterialMaster.objects.filter(Material_Id = material_id, Status = 1)
        if Material:
            InwardMaster.objects.create(S_No = new_sno, Inward_Id = new_inw_id, Material_Id = material_id, Material_Name = name.Material_Name, Date = date, Vendor_Name = vendor_name.upper(), Vendor_Mobile = vendor_phone, Vendor_GST = vendor_gst.upper(), Invoice_Cost = invoice_cost, Invoice_Quantity = invoice_quantity, Batch_No = batch_no.upper(), Batch_Id = new_bat_id, Additional_Info = additional_info)
        else:
            messages.info(request,"Material Id Not Available")
            return redirect('select_material')
        return redirect('listinward')

    
    mat_id = MaterialMaster.objects.filter(Status =1)

    # Generate Inward_Id starting with INW0001 and display in front-end 
    last_inward = InwardMaster.objects.order_by('-Inward_Id').first()
    if last_inward:
        last_id = int(last_inward.Inward_Id[3:])  # Extract the numeric part
        new_inw_id = f"INW{last_id + 1:04d}"
    else:
        new_inw_id = "INW0001"

    # Generate Batch_Id starting with BAT0001 and display in front-end 
    last_batch = InwardMaster.objects.order_by('-Batch_Id').first()
    if last_batch:
        last_id = int(last_batch.Batch_Id[3:])  # Extract the numeric part
        new_bat_id = f"BAT{last_id + 1:04d}"
    else:
        new_bat_id = "BAT0001"

    context = {'mat_id':mat_id,'inw_id':new_inw_id,'bat_id':new_bat_id}
    
    return render(request,'select_inward.html', context)



@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def addInward(request, id):
    if request.method == 'POST':
        material_id = request.POST['material_id']
        date =  request.POST['date']
        vendor_name = request.POST['vendor_name']
        vendor_phone = request.POST['vendor_phone']
        vendor_gst = request.POST['vendor_gst']
        invoice_cost = request.POST['invoice_cost']
        invoice_quantity = request.POST['invoice_quantity']
        batch_no = request.POST['batch_no']
        additional_info = request.POST['additional_info']
        name = MaterialMaster.objects.get(Material_Id = material_id)

        last_Sno = InwardMaster.objects.last()  # Get the last entry

        if last_Sno:  
            new_sno = last_Sno.S_No + 1  # Assuming 'Sno' is the integer field storing serial numbers
        else:
            new_sno = 1  # Start from 1 if no records exist


        # Generate Inward_Id starting with INW0001 and store in back-end 
        last_inward = InwardMaster.objects.order_by('-Inward_Id').first()
        if last_inward:
            last_id = int(last_inward.Inward_Id[3:])  # Extract the numeric part
            new_inw_id = f"INW{last_id + 1:04d}"
        else:
            new_inw_id = "INW0001"

        # Generate Batch_Id starting with BAT0001 and store in back-end 
        last_batch = InwardMaster.objects.order_by('-Batch_Id').first()
        if last_batch:
            last_id = int(last_batch.Batch_Id[3:])  # Extract the numeric part
            new_bat_id = f"BAT{last_id + 1:04d}"
        else:
            new_bat_id = "BAT0001"


        Material = MaterialMaster.objects.filter(Material_Id = material_id, Status = 1)
        if Material:
            InwardMaster.objects.create(S_No = new_sno, Inward_Id = new_inw_id, Material_Id = material_id,Material_Name = name.Material_Name, Date = date, Vendor_Name = vendor_name.upper(), Vendor_Mobile = vendor_phone, Vendor_GST = vendor_gst.upper(), Invoice_Cost = invoice_cost, Invoice_Quantity = invoice_quantity, Batch_No = batch_no.upper(), Batch_Id = new_bat_id, Additional_Info = additional_info)
        else:
            messages.info(request,"Material Id Not Available")
        return redirect('listinward')

    
    mat_id = MaterialMaster.objects.filter(Material_Id = id , Status =1)

    # Generate Inward_Id starting with INW0001 and display in front-end 
    last_inward = InwardMaster.objects.order_by('-Inward_Id').first()
    if last_inward:
        last_id = int(last_inward.Inward_Id[3:])  # Extract the numeric part
        new_inw_id = f"INW{last_id + 1:04d}"
    else:
        new_inw_id = "INW0001"

    # Generate Batch_Id starting with BAT0001 and display in front-end 
    last_batch = InwardMaster.objects.order_by('-Batch_Id').first()
    if last_batch:
        last_id = int(last_batch.Batch_Id[3:])  # Extract the numeric part
        new_bat_id = f"BAT{last_id + 1:04d}"
    else:
        new_bat_id = "BAT0001"

    context = {'mat_id':mat_id,'inw_id':new_inw_id,'bat_id':new_bat_id}
    
    return render(request,'add_inward.html', context)

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def listInward(request):
    data = InwardMaster.objects.filter(Status = 1)
    context = {'data':data}
    return render(request,'list_inward.html',context)

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def inwardDetails(request,id):
    data = InwardMaster.objects.filter(Inward_Id = id , Status =1)
    context = {'data':data}
    return render(request,'inward_details.html',context)



@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def deleteInward(request,id):
    InwardMaster.objects.filter(Inward_Id = id).update(Status = 0)
    return redirect('listinward')




@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def add_outward(request,id):
    if request.method == "POST":
        material_id = request.POST['material_id']
        material_name = request.POST['material_name']
        available_quantity = request.POST['available_quantity']
        batch_id = request.POST['batch_id']
        batch_no = request.POST['batch_no']
        date = request.POST['date']
        outward_quantity = int(request.POST['outward_quantity'])
        additional_info = request.POST['additional_info']

        # Generate Outward_Id starting with INW0001 and display in front-end 
        last_outward = OutwardMaster.objects.order_by('-Outward_Id').first()
        if last_outward:
            last_id = int(last_outward.Outward_Id[3:])  # Extract the numeric part
            new_out_id = f"OUT{last_id + 1:04d}"
        else:
            new_out_id = "OUT0001"
        OutwardMaster.objects.create(
            Outward_Id = new_out_id,
            Inward_Id = id,
            Date = date,
            Material_Id = material_id,
            Material_Name = material_name,
            Used_By = request.user.username,
            Outward_Quantity = outward_quantity,
            Batch_Id = batch_id,
            Batch_No = batch_no.upper(),
            Additional_Info = additional_info
        )
        inwa = InwardMaster.objects.get(Inward_Id = id)
        balance_quantity = inwa.Invoice_Quantity - outward_quantity
        InwardMaster.objects.filter(Inward_Id = id).update(Invoice_Quantity = balance_quantity)

        return redirect('listoutward')
        


    data = InwardMaster.objects.filter(Inward_Id = id, Status = 1)

    # Generate Outward_Id starting with INW0001 and display in front-end 
    last_outward = OutwardMaster.objects.order_by('-Outward_Id').first()
    if last_outward:
        last_id = int(last_outward.Outward_Id[3:])  # Extract the numeric part
        new_out_id = f"OUT{last_id + 1:04d}"
    else:
        new_out_id = "OUT0001"
    context = {'new_out_id':new_out_id,'data':data}
    return render(request,'add_outward.html', context)

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def list_outward(request):
    data = OutwardMaster.objects.all()
    context = {'data':data}
    return render(request,'list_outward.html',context)




def city_autocomplete(request):
    return render(request, 'invoice.html')
    data = CustomerDetails.objects.filter(Status = 1)
    context = {'data':data}
    # Invoice.objects.create(invoice_number = 1, customer_name = "Test", date = "25-10-2001", total_amount = 1000)

    return render(request,'auto_complete.html', context)







@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def addProduct(request):
 
    if request.method == 'POST':
        name = request.POST['name']
        date = request.POST['date']
        gst = request.POST['gst']
        hsn = request.POST['hsn']
        last_product = ProductMaster.objects.order_by('-Product_Id').first()
        if last_product:
            last_id = int(last_product.Product_Id[4:])  # Extract the numeric part
            new_id = f"PROD{last_id + 1:04d}"
        else:
            new_id = "PROD0001"

        ProductMaster.objects.create(Product_Id = new_id ,Date = date, Product_Name = name.upper(), GST = gst, HSN_Code = hsn.upper())

        return redirect('addproduct')
    
    last_product = ProductMaster.objects.order_by('-Product_Id').first()
    if last_product:
        last_id = int(last_product.Product_Id[4:])  # Extract the numeric part
        new_id = f"PROD{last_id + 1:04d}"
    else:
        new_id = "PROD0001"
    
    context = {'data':new_id}

    return render(request,'add_product.html',context)

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def editProduct(request,id):
    if request.method == 'POST':
        name = request.POST['name']
        date = request.POST['date']
        gst = request.POST['gst']
        hsn = request.POST['hsn']

        ProductMaster.objects.filter(Product_Id=id).update(Date = date, Product_Name = name.upper(), GST = gst, HSN_Code = hsn.upper())

        return redirect('listproduct')

    data = ProductMaster.objects.get(Product_Id = id)
    context = {'data':data}

    return render(request,'edit_product.html',context)


@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def deleteProduct(request,id):
    existing_product = ProductMaster.objects.get(Product_Id = id)
    if existing_product:
        ProductMaster.objects.filter(Product_Id = id).update(Status = 0)
        CategoriesMaster.objects.filter(Product_Name = existing_product.Product_Name).update(Status = 0)
        CostMaster.objects.filter(Product_Name = existing_product.Product_Name).update(Status = 0)
    return redirect('listproduct')

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def listProduct(request):
    data = ProductMaster.objects.filter(Status = 1)
    context = {'data':data}
    return render(request,'list_product.html',context)





@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def addCategories(request):
    if request.method == 'POST':
        product_name = request.POST['product_name']
        category_name = request.POST['category_name']
        sub_category = request.POST['sub_category']
        
        last_categories = CategoriesMaster.objects.order_by('-Categories_Id').first()
        if last_categories:
            last_id = int(last_categories.Categories_Id[3:])  # Extract the numeric part
            new_id = f"CAT{last_id + 1:04d}"
        else:
            new_id = "CAT0001"
            
        CategoriesMaster.objects.create(Categories_Id = new_id, Product_Name = product_name, Categories_Name = category_name.upper(), Sub_Categories = sub_category.upper())

        return redirect('addcategories')

    last_categories = CategoriesMaster.objects.order_by('-Categories_Id').first()
    if last_categories:
        last_id = int(last_categories.Categories_Id[3:])  # Extract the numeric part
        new_id = f"CAT{last_id + 1:04d}"
    else:
        new_id = "CAT0001"

    products = ProductMaster.objects.filter(Status = 1)
    
    context = {'data':new_id, 'products':products}

    return render(request,'add_categories.html',context)



@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def editCategories(request,id):
    if request.method == 'POST':
        product_name = request.POST['product_name']
        category_name = request.POST['category_name']
        sub_category = request.POST['sub_category']
        
        CategoriesMaster.objects.filter(Categories_Id=id).update(Product_Name = product_name, Categories_Name = category_name.upper(), Sub_Categories = sub_category.upper())

        return redirect('listcategories')
    data = CategoriesMaster.objects.get(Categories_Id = id)
    
    context = {'data':data}

    return render(request,'edit_categories.html',context)

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def listCategories(request):
    data = CategoriesMaster.objects.filter(Status = 1)
    context = {'data':data}
    return render(request,'list_categories.html',context)




@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def add_Cost(request):
    if request.method == "POST":
        product_name = request.POST['product_name']
        date = request.POST['date']
        category_name = request.POST['category_name']
        sub_category = request.POST['sub_category']
        cost_for_agent = request.POST['cost_for_agent']
        cost = request.POST['cost']
        length = request.POST['length']
        height = request.POST['height']
        cost_calculate =  request.POST['cost_calculate']
        rate =  request.POST['rate']
        

        selling_cost = request.POST['selling_cost']

        last_product = CostMaster.objects.order_by('-Cost_Id').first()
        if last_product:
            last_id = int(last_product.Cost_Id[4:])  # Extract the numeric part
            new_id = f"COST{last_id + 1:04d}"
        else:
            new_id = "COST0001"

        if cost_calculate == "Unit Cost":
            CostMaster.objects.create(Cost_Id = new_id, Product_Name = product_name, Date = date, Category_Name = category_name, Sub_Category = sub_category, Fixed_Cost = cost, Cost_for_Agent = cost_for_agent, Selling_Cost = selling_cost, Cost_Per_Unit_Status = 1 )
            return redirect('addcost')
        elif cost_calculate == "Size Cost" and rate == "Sqft Rate":
            CostMaster.objects.create(Cost_Id = new_id, Product_Name = product_name, Date = date, Category_Name = category_name, Sub_Category = sub_category, Fixed_Cost = cost,Length = length, Height = height, Cost_for_Agent = cost_for_agent, Selling_Cost = selling_cost, Cost_Per_Sqft_Status = 1 )
            return redirect('addcost')
        elif cost_calculate == "Size Cost" and rate == "Fixed Rate":
            CostMaster.objects.create(Cost_Id = new_id, Product_Name = product_name , Date = date, Category_Name = category_name, Sub_Category = sub_category,Length = length, Height = height, Fixed_Cost = cost,Fixed_Cost_Status = 1, Cost_for_Agent = cost_for_agent, Selling_Cost = selling_cost )
            return redirect('addcost')

    last_product = CostMaster.objects.order_by('-Cost_Id').first()
    if last_product:
        last_id = int(last_product.Cost_Id[4:])  # Extract the numeric part
        new_id = f"COST{last_id + 1:04d}"
    else:
        new_id = "COST0001"

    category = CategoriesMaster.objects.filter(Status = 1)
    products = ProductMaster.objects.filter(Status = 1)
        
    context = {'data':new_id, 'category':category, 'products':products}


    return render(request,'add_cost4.html',context)

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def editCost(request,id):
    if request.method == "POST":
        product_name = request.POST['product_name']
        date = request.POST['date']
        category_name = request.POST['category_name']
        sub_category = request.POST['sub_category']
        cost_for_agent = request.POST['cost_for_agent']
        cost = request.POST['cost']
        selling_cost = request.POST['selling_cost']
        

        CostMaster.objects.filter(Cost_Id = id).update(Cost_Id = id, Product_Name = product_name ,Date = date, Category_Name = category_name, Sub_Category = sub_category, Fixed_Cost = cost, Cost_for_Agent = cost_for_agent, Selling_Cost = selling_cost )
        return redirect('listcost')
    

    data = CostMaster.objects.get(Cost_Id = id)

    context = {'data':data}


    return render(request,'edit_cost.html',context)

   

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def listCost(request):
    data = CostMaster.objects.filter(Status =1)
    context = {'data':data}
    return render(request,'list_cost.html',context)

@login_required(login_url='signin')
def bill(request):
    # for adding multiple form entry in db 
    if request.method == "POST":
        try:
            # Parse JSON data
            data = json.loads(request.body)
            entries = data.get("entries", [])
            # Save each entry into the database
            for entry in entries:
                last_bill = BillingMaster.objects.order_by('-S_No').first()
                if last_bill:
                    last_id = int(last_bill.Bill_Id[4:])  # Extract the numeric part
                    new_id = f"BILL{last_id + 1:04d}"
                    last_s_no = last_bill.S_No
                    s_no = last_s_no + 1
                else:
                    new_id = "BILL0001"
                    s_no = 1

                detail_id = BillingMaster.objects.create(
                    S_No = s_no,
                    Bill_Id= new_id,
                    Customer_Id= data.get("customer_id" , "None") ,
                    Agent_Id = data.get("agent_id" , "None"),
                    Type = "Agent" if data.get("agent_id") else "Customer",
                    Customer_Name=data.get("customer_name") if data.get("customer_name") else data.get("agent_name"),
                    Phone_No=data.get("customer_phone") if data.get("customer_phone") else data.get("agent_phone"),
                    Date = data.get("bill_date"),
                    Grand_Total = int(data.get("grand_total", 0)) if data.get("grand_total") not in [None, "", "None"] else 0,
                    Grand_Total_With_Gst = 0,
                    Added_By = request.user.username,
                    Pending_Amount = int(data.get("grand_total", 0)) if data.get("grand_total") not in [None, "", "None"] else 0,
                )
               

                break

            

            for entry in entries:
                last_bill = BillingDetails.objects.order_by('-Item_Id').first()
                if last_bill:
                    last_id = int(last_bill.Item_Id[12:])  # Extract the numeric part
                    new_id = f"ITM{last_id + 1:01d}-{detail_id}"
                else:
                    new_id = f"ITM1-{detail_id}"

                specification = entry.get("product", "NONE") if entry.get("product") not in [None, "", "None"] else "NONE"
                splitted_spec = specification.split(",")

                costs = entry.get("cost", "NONE") if entry.get("cost") not in [None, "", "None"] else "NONE"
                charge = entry.get("charges", 0) if entry.get("charges") not in [None, "", 0] else 0
                
                manual_amount = 0
              
                

                dimetions = entry.get("dimension")
                dimention_parts = dimetions.split("X")
                length , height = float(dimention_parts[0].strip()), float(dimention_parts[1].split("=")[0].strip())


                whatsData = BillingDetails.objects.create(
                    Bill_Id= detail_id,
                    Date = data.get("bill_date"),
                    Item_Id= new_id,
                    Added_By = request.user.username,
                    Customer_Id= data.get("customer_id" , "None") ,
                    Agent_Id = data.get("agent_id" , "None"),
                    Customer_Name=data.get("customer_name") if data.get("customer_name") else data.get("agent_name"),
                    Phone_No=data.get("customer_phone") if data.get("customer_phone") else data.get("agent_phone"),
                    Product_Name=splitted_spec[0] ,
                    Custom_Product=entry.get("custom", "NONE") if entry.get("custom") not in [None, "", "None"] else "NONE",
                    Category_Name=splitted_spec[1],
                    Sub_Category=splitted_spec[2],
                    Size = entry.get("size", "NONE") if entry.get("size") not in [None, "", "None"] else "NONE",
                    Length= length,
                    Height = height,
                    Total_Sqft = float(entry.get("total_sqft", 0) if entry.get("total_sqft") not in [None, "", "None"] else 0),
                    Quantity=int(entry.get("quantity", 0)),  # Convert to int (default 0 if missing)
                    Cost_Per_Sqft= float(entry.get("cost_per_sqft", 0)),
                    Actual_Cost = float(costs) - float(charge),
                    Modified_Cost = manual_amount,
                    GST=float(entry.get("gst", 0)) if entry.get("gst") not in [None, "", "None"] else 0,  # Convert to float (default 0 if missing)
                    HSN_Code=entry.get("hsn", "NONE") if entry.get("hsn") not in [None, "", "None"] else "NONE",
                    Total_Cost = float(costs) - float(charge),  # Convert to float
                    Total_Cost_With_Gst=float(entry.get("total_with_gst", 0)),  # Convert to float
                    Remarks = entry.get("remarks", "NONE") if entry.get("remarks") not in [None, "", "None"] else "NONE",
                    Additional_Charges = entry.get("charges", 0) if entry.get("charges") not in [None, "", 0] else 0,
                    Difference_Amount = int(float(entry.get("cost", "NONE"))) if entry.get("cost") not in [None, "", "None"] else 0
                )

            
            return redirect("listbill")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            traceback.print_exc()  # This prints the full error traceback in the console
            return JsonResponse({"error": str(e)}, status=500)

    last_bill = BillingMaster.objects.order_by('-S_No').first()
    if last_bill:
        last_id = int(last_bill.Bill_Id[4:])  # Extract the numeric part
        new_id = f"BILL{last_id + 1:04d}"
    else:
        new_id = "BILL0001"

    data = CustomerDetails.objects.filter(Status = 1,Type = 'customer')
    data3 = CustomerDetails.objects.filter(Status = 1, Type = 'agent')
    data2 = BillingMaster.objects.all()
    category = CategoriesMaster.objects.filter(Status = 1)
    products = ProductMaster.objects.filter(Status = 1)
    cos = CostMaster.objects.filter(Status = 1)
        
    context = {'new_id':new_id, 'category':category, 'products':products, 'data': data,'data2': data2,'data3':data3, 'cos': cos, 'new_id': new_id }

    
    return render(request,'bill3.html',context)


@login_required(login_url='signin')
def select_bill(request,id):
    whatsData = BillingMaster.objects.get(Bill_Id = id)
    # Store WhatsApp URL in session to use after redirect
    whatsapp_url = send_whatsapp_message(whatsData)
    request.session['whatsapp_url'] = whatsapp_url
    return redirect(service_success)

@login_required(login_url='signin')
def send_whatsapp_message(data):
    phone = str(data.Phone_No)
    name = data.Customer_Name

    
    # message = f"Hello {name},\n\n Bill Id : {data.Bill_Id}\n Bill Amount : ₹ {data.Grand_Total}\n Piad Amount : ₹ {data.Paid_Amount}\n Balance : ₹ {data.Pending_Amount}\n\n Thank You For Reaching Us.\n Regards ' SSDIGITAL '\n For More Informantion\n +91 9629932649"
    message = f"Hello {name},\n\n" \
          f"Bill Id : {data.Bill_Id}\n" \
          f"Bill Amount : ₹ {data.Grand_Total}\n" \
          f"Paid Amount : ₹ {data.Paid_Amount}\n" \
          f"Balance : *₹ {data.Pending_Amount}*\n\n" \
          f"Thank You For Reaching Us.\n" \
          f"Regards ' SSDIGITAL '\n" \
          f"For More Information\n" \
          f"+91 9629932649"

    # Format phone number (ensure it starts with country code)
    if not phone.startswith("+"):
        phone = "+91" + phone  # Add country code (India: +91) if missing
    
    # URL encode the message
    from urllib.parse import quote
    encoded_message = quote(message)
    
    return f"https://wa.me/{phone}?text={encoded_message}"

@login_required(login_url='signin')
def service_success(request):
    # Get WhatsApp URL from session
    whatsapp_url = request.session.pop('whatsapp_url', None)
    context = {'whatsapp_url': whatsapp_url}
    return render(request, 'service_success.html', context)




@login_required(login_url='signin')
def listBill(request):
    data = BillingMaster.objects.filter(Status =1).order_by("-Bill_Id")
    context = {'data':data}
    return render(request,'list_bill.html',context)

@login_required(login_url='signin')
def outstanding(request):
    data = BillingMaster.objects.exclude(Pending_Amount = 0)
    context = {'data':data}
    return render(request,'list_bill.html',context)


@login_required(login_url='signin')
def billDetails(request,id):
    data = BillingDetails.objects.filter(Bill_Id = id , Status =1)
    data2 = BillingMaster.objects.get(Bill_Id = id , Status =1)
    context = {'data':data, 'data2':data2}
    return render(request,'bill_details.html',context)




@login_required(login_url='signin')
def quote(request):
    # for adding multiple form entry in db 
    if request.method == "POST":
        try:
            # Parse JSON data
            data = json.loads(request.body)
            entries = data.get("entries", [])
            # Save each entry into the database
            for entry in entries:
                last_bill = QuoteMaster.objects.order_by('-S_No').first()
                if last_bill:
                    last_id = int(last_bill.Quote_Id[4:])  # Extract the numeric part
                    new_id = f"QUOT{last_id + 1:04d}"
                    last_s_no = last_bill.S_No
                    s_no = last_s_no + 1
                else:
                    new_id = "QUOT0001"
                    s_no = 1

                detail_id = QuoteMaster.objects.create(
                    S_No = s_no,
                    Quote_Id= new_id,
                    Customer_Id= data.get("customer_id" , "None") ,
                    Agent_Id = data.get("agent_id" , "None"),
                    Type = "Agent" if data.get("agent_id") else "Customer",
                    Customer_Name=data.get("customer_name") if data.get("customer_name") else data.get("agent_name"),
                    Phone_No=data.get("customer_phone") if data.get("customer_phone") else data.get("agent_phone"),
                    Date = data.get("bill_date"),
                    Grand_Total = int(data.get("grand_total", 0)) if data.get("grand_total") not in [None, "", "None"] else 0,
                    Grand_Total_With_Gst = 0,
                    Added_By = request.user.username,
                )
               

                break

            

            for entry in entries:
                last_quote = QuoteDetails.objects.order_by('-Item_Id').first()
                if last_quote:
                    last_id = int(last_quote.Item_Id[12:])  # Extract the numeric part
                    new_id = f"ITM{last_id + 1:01d}-{detail_id}"
                else:
                    new_id = f"ITM1-{detail_id}"

                specification = entry.get("product", "NONE") if entry.get("product") not in [None, "", "None"] else "NONE"
                splitted_spec = specification.split(",")

                costs = entry.get("cost", "NONE") if entry.get("cost") not in [None, "", "None"] else "NONE"
                charge = entry.get("charges", 0) if entry.get("charges") not in [None, "", 0] else 0
                
                manual_amount = 0
              
                

                dimetions = entry.get("dimension")
                dimention_parts = dimetions.split("X")
                length , height = float(dimention_parts[0].strip()), float(dimention_parts[1].split("=")[0].strip())


                whatsData = QuoteDetails.objects.create(
                    Quote_Id= detail_id,
                    Date = data.get("bill_date"),
                    Item_Id= new_id,
                    Added_By = request.user.username,
                    Customer_Id= data.get("customer_id" , "None") ,
                    Agent_Id = data.get("agent_id" , "None"),
                    Customer_Name=data.get("customer_name") if data.get("customer_name") else data.get("agent_name"),
                    Phone_No=data.get("customer_phone") if data.get("customer_phone") else data.get("agent_phone"),
                    Product_Name=splitted_spec[0] ,
                    Category_Name=splitted_spec[1],
                    Sub_Category=splitted_spec[2],
                    Size = entry.get("size", "NONE") if entry.get("size") not in [None, "", "None"] else "NONE",
                    Length= length,
                    Height = height,
                    Total_Sqft = float(entry.get("total_sqft", 0) if entry.get("total_sqft") not in [None, "", "None"] else 0),
                    Quantity=int(entry.get("quantity", 0)),  # Convert to int (default 0 if missing)
                    Cost_Per_Sqft= float(entry.get("cost_per_sqft", 0)),
                    Actual_Cost = float(costs) - float(charge),
                    Modified_Cost = manual_amount,
                    GST=float(entry.get("gst", 0)) if entry.get("gst") not in [None, "", "None"] else 0,  # Convert to float (default 0 if missing)
                    HSN_Code=entry.get("hsn", "NONE") if entry.get("hsn") not in [None, "", "None"] else "NONE",
                    Total_Cost = float(costs) - float(charge),  # Convert to float
                    Total_Cost_With_Gst=float(entry.get("total_with_gst", 0)),  # Convert to float
                    Remarks = entry.get("remarks", "NONE") if entry.get("remarks") not in [None, "", "None"] else "NONE",
                    Additional_Charges = entry.get("charges", 0) if entry.get("charges") not in [None, "", 0] else 0,
                    Difference_Amount = int(float(entry.get("cost", "NONE"))) if entry.get("cost") not in [None, "", "None"] else 0
                )

            
            return redirect("listquote")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            traceback.print_exc()  # This prints the full error traceback in the console
            return JsonResponse({"error": str(e)}, status=500)

    last_quote = QuoteMaster.objects.order_by('-S_No').first()
    if last_quote:
        last_id = int(last_quote.Bill_Id[4:])  # Extract the numeric part
        new_id = f"BILL{last_id + 1:04d}"
    else:
        new_id = "BILL0001"

    data = CustomerDetails.objects.filter(Status = 1,Type = 'customer')
    data3 = CustomerDetails.objects.filter(Status = 1, Type = 'agent')
    data2 = BillingMaster.objects.all()
    category = CategoriesMaster.objects.filter(Status = 1)
    products = ProductMaster.objects.filter(Status = 1)
    cos = CostMaster.objects.filter(Status = 1)
        
    context = {'new_id':new_id, 'category':category, 'products':products, 'data': data,'data2': data2,'data3':data3, 'cos': cos, 'new_id': new_id }

    
    return render(request,'bill3.html',context)

@login_required(login_url='signin')
def listQuote(request):
    data = QuoteMaster.objects.filter(Status =1)
    context = {'data':data}
    return render(request,'list_quote.html',context)

@login_required(login_url='signin')
def quoteDetails(request,id):
    data = QuoteDetails.objects.filter(Quote_Id = id , Status =1)
    data2 = QuoteMaster.objects.get(Quote_Id = id , Status =1)
    context = {'data':data, 'data2':data2}
    return render(request,'quote_details.html',context)


@login_required(login_url='signin')
def bill_quotation(request,id):
    data = QuoteMaster.objects.filter(Quote_Id = id)
    data2 = QuoteDetails.objects.filter(Quote_Id = id)
    last_bill = BillingMaster.objects.order_by('-S_No').first()
    if last_bill:
        last_id = int(last_bill.Bill_Id[4:])  # Extract the numeric part
        new_id = f"BILL{last_id + 1:04d}"
        last_s_no = last_bill.S_No
        s_no = last_s_no + 1
    else:
        new_id = "BILL0001"
        s_no = 1

    for item in data:
        generate_bill = BillingMaster.objects.create(
            S_No = s_no,
            Bill_Id = new_id,
            Customer_Id = item.Customer_Id,
            Agent_Id = item.Agent_Id,
            Customer_Name = item.Customer_Name,
            Phone_No = item.Phone_No,
            Grand_Total = item.Grand_Total,
            Grand_Total_With_Gst = item.Grand_Total_With_Gst,
            Pending_Amount = item.Grand_Total,
            Added_By = request.user.username,
            Date = item.Date
        )
        break

    for item in data2:
        last_bill = BillingDetails.objects.order_by('-Item_Id').first()
        if last_bill:
            last_id = int(last_bill.Item_Id[12:])  # Extract the numeric part
            new_id = f"ITM{last_id + 1:01d}-{generate_bill}"
        else:
            new_id = f"ITM1-{generate_bill}"
        BillingDetails.objects.create(
            Bill_Id= generate_bill,
            Date = item.Date,
            Item_Id= new_id,
            Added_By = request.user.username,
            Customer_Id= item.Customer_Id,
            Agent_Id = item.Agent_Id,
            Customer_Name = item.Customer_Name,
            Phone_No = item.Phone_No,
            Product_Name= item.Product_Name ,
            Custom_Product= "N/A",
            Category_Name=item.Category_Name,
            Sub_Category = item.Sub_Category,
            Size = item.Size,
            Length = item.Length,
            Height = item.Height,
            Total_Sqft = item.Total_Sqft,
            Quantity = item.Quantity,
            Cost_Per_Sqft = item.Cost_Per_Sqft,
            Actual_Cost = item.Actual_Cost,
            GST = '00',  
            HSN_Code = "00",
            Total_Cost = item.Total_Cost,
            Total_Cost_With_Gst = "00",  
            Remarks = item.Remarks,
            Additional_Charges = item.Additional_Charges,
            Difference_Amount = item.Difference_Amount
        )
    return redirect('listbill')

@login_required(login_url='signin')
def estimate(request):

    # for adding multiple form entry in db 
    if request.method == "POST":
        try:
            # Parse JSON data
            data = json.loads(request.body)
            entries = data.get("entries", [])
            # Save each entry into the database
            for entry in entries:
                last_bill = EstimateMaster.objects.order_by('-Estimation_Id').first()
                if last_bill:
                    last_id = int(last_bill.Estimation_Id[4:])  # Extract the numeric part
                    new_id = f"ESTM{last_id + 1:04d}"
                else:
                    new_id = "ESTM0001"
                detail_id = EstimateMaster.objects.create(
                    Estimation_Id= new_id,
                    Customer_Id=data.get("customer_id"),
                    Customer_Name=data.get("customer_name"),
                    Phone_No=data.get("customer_phone"),
                    Grand_Total = int(data.get("grand_total", 0)) if data.get("grand_total") not in [None, "", "None"] else 0,
                    # Grand_Total_With_Gst = int(data.get("grand_total_with_gst", 0)) if data.get("grand_total_with_gst") not in [None, "", "None"] else 0,
                )
                break
            for entry in entries:
                last_bill = EstimateDetails.objects.order_by('-Item_Id').first()
                if last_bill:
                    last_id = int(last_bill.Item_Id[12:])  # Extract the numeric part
                    new_id = f"ITM{last_id + 1:01d}-{detail_id}"
                else:
                    new_id = f"ITM1-{detail_id}"
                EstimateDetails.objects.create(
                    Estimation_Id = detail_id,
                    Item_Id= new_id,
                    Customer_Id=data.get("customer_id"),
                    Customer_Name=data.get("customer_name"),
                    Phone_No=data.get("customer_phone"),
                    Product_Name=entry.get("product", "NONE") if entry.get("product") not in [None, "", "None"] else "NONE",
                    Custom_Product=entry.get("custom", "NONE") if entry.get("custom") not in [None, "", "None"] else "NONE",
                    Category_Name=entry.get("category", "NONE") if entry.get("category") not in [None, "", "None"] else "NONE",
                    Sub_Category=entry.get("sub_category", "NONE") if entry.get("sub_category") not in [None, "", "None"] else "NONE",
                    Length=int(entry.get("length", 0)) if entry.get("length") not in [None, "", "None"] else 0,
                    Height=int(entry.get("width", 0)) if entry.get("width") not in [None, "", "None"] else 0,
                    Total_Sqft=int(entry.get("total_sqft", 0)) if entry.get("total_sqft") not in [None, "", "None"] else 0,
                    Quantity=int(entry.get("quantity", 0)),  # Convert to int (default 0 if missing)
                    Cost_Per_Sqft=float(entry.get("cost", 0)) if entry.get("cost") not in [None, "", "None"] else 0,  # Convert to float (default 0 if missing)
                    # GST=float(entry.get("gst", 0)) if entry.get("gst") not in [None, "", "None"] else 0,  # Convert to float (default 0 if missing)
                    # HSN_Code=entry.get("hsn", "NONE") if entry.get("hsn") not in [None, "", "None"] else "NONE",
                    Total_Cost=float(entry.get("total", 0)),  # Convert to float
                    # Total_Cost_With_Gst=float(entry.get("total_with_gst", 0))  # Convert to float
                )
            return redirect("listestimate")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            traceback.print_exc()  # This prints the full error traceback in the console
            return JsonResponse({"error": str(e)}, status=500)
  
    return redirect('bill')

@login_required(login_url='signin')
def listEstimate(request):
    data = EstimateMaster.objects.filter(Status =1)
    context = {'data':data}
    return render(request,'list_estimate.html',context)
@login_required(login_url='signin')
def estimateDetails(request,id):
    data = EstimateDetails.objects.filter(Estimation_Id = id , Status =1)
    data2 = EstimateMaster.objects.get(Estimation_Id = id , Status =1)
    context = {'data':data, 'data2':data2}
    return render(request,'estimate_details.html',context)






@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def add_employee(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # emp_id = request.POST['emp_id']
        name = request.POST['name']
        phone = request.POST['phone']
        DOJ = request.POST['DOJ']
        aadhar = request.POST['aadhar']
        email = request.POST['email']
        role = request.POST['role']
        address = request.POST['address']

        last_emp = Employee.objects.order_by('-emp_id').first()
        if last_emp:
            last_emp = int(last_emp.emp_id[3:])  # Extract the numeric part
            new_id = f"EMP{last_emp + 1:04d}"
        else:
            new_id = "EMP0001"

        # Create employee user
        user = Employee.objects.create(
            username=username.upper(),
            password=make_password(password),  # Hashing the password
            emp_id=new_id,
            first_name=name.upper(),  # Django default field
            phone=phone,
            DOJ=DOJ,
            aadhar=aadhar,
            email=email,
            address=address,
            role=role  # Default role as Employee
        )
        messages.info(request,"employee added")
        return redirect('addemployee')  # Redirect after successful creation
    last_emp = Employee.objects.order_by('-emp_id').first()
    if last_emp:
        last_emp = int(last_emp.emp_id[3:])  # Extract the numeric part
        new_id = f"EMP{last_emp + 1:04d}"
    else:
        new_id = "EMP0001"
    data2 = Employee.objects.all()
    context = {'data':new_id,'data2':data2}

    return render(request, 'add_employee.html', context)

@login_required(login_url='signin')
@user_passes_test(is_admin)  # Only admin can add employees
def list_employee(request):
    data = Employee.objects.all()
    context = {'data':data}
 
   
    return render(request,'list_employee.html',context)

@login_required(login_url='signin')
def invoice(request,id):
    splitted_billId = id.split("-")
    billId = splitted_billId[0]
    upi_id = "ssenterprisesabu@okhdfcbank"    
    if id.startswith("BILL"):
        data = BillingDetails.objects.filter(Bill_Id = billId , Status =1)
        data2 = BillingMaster.objects.get(Bill_Id = billId , Status =1)
        if data2.Customer_Id:
            data3 = CustomerDetails.objects.get(Customer_Id = data2.Customer_Id)
        else:
            data3 = CustomerDetails.objects.get(Agent_Id = data2.Agent_Id)
        data4 = Payment_Master.objects.filter(Payment_Id=id)
        data5 = Payment_Details.objects.filter(Payment_Id=id)
        current_date = datetime.today()

        if data4:
            for item in data4:
                amount = item.Pending_Amount
        else:
            amount = data2.Grand_Total

        upi_link = f"upi://pay?pa={upi_id}&pn=Payee&am={amount}&cu=INR"

        # Generate QR code
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(upi_link)
        qr.make(fit=True)
        
        # Convert QR to image
        img = qr.make_image(fill="black", back_color="white").resize((400, 400))

        # Convert image to Base64 to embed in HTML
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()



        context = {'data':data, 'data2':data2,'data3':data3,'current_date':current_date,'data4':data4,'billId':billId,'invoice_no':id,'data5':data5,'qr_base64': qr_base64}
        return render(request,'invoice.html',context)
    elif id.startswith("ESTM"):
        data = EstimateDetails.objects.filter(Estimation_Id = id , Status =1)
        data2 = EstimateMaster.objects.get(Estimation_Id = id , Status =1)
        data3 = CustomerDetails.objects.get(Customer_Id = data2.Customer_Id)
        current_date=datetime.today()
        context = {'data':data, 'data2':data2,'data3':data3,'current_date':current_date}
        return render(request,'invoive_no_gst.html',context)
    elif id.startswith("QUOT"):
        data = BillingDetails.objects.filter(Bill_Id = billId , Status =1)
        data2 = BillingMaster.objects.get(Bill_Id = billId , Status =1)
        if data2.Customer_Id:
            data3 = CustomerDetails.objects.get(Customer_Id = data2.Customer_Id)
        else:
            data3 = CustomerDetails.objects.get(Agent_Id = data2.Agent_Id)
        data4 = Payment_Master.objects.filter(Payment_Id=id)
        data5 = Payment_Details.objects.filter(Payment_Id=id)
        current_date = datetime.today()

        if data4:
            for item in data4:
                amount = item.Pending_Amount
        else:
            amount = data2.Grand_Total

        upi_link = f"upi://pay?pa={upi_id}&pn=Payee&am={amount}&cu=INR"

        # Generate QR code
        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(upi_link)
        qr.make(fit=True)
        
        # Convert QR to image
        img = qr.make_image(fill="black", back_color="white").resize((400, 400))

        # Convert image to Base64 to embed in HTML
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()



        context = {'data':data, 'data2':data2,'data3':data3,'current_date':current_date,'data4':data4,'billId':billId,'invoice_no':id,'data5':data5,'qr_base64': qr_base64}
        return render(request,'invoice.html',context)
    return redirect('bill')


@login_required(login_url='signin')
def signout(request):
    logout(request)
    return redirect("signin")


@login_required(login_url='signin')
def add_payment(request, id):
    # Cash_Book_Master.objects.all().delete()
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Load request data once
            table_data = data.get("tableData", [])
            last_pay = Payment_Master.objects.filter(Payment_Id__startswith=id).order_by('-Payment_Id').first()  

            if last_pay:        
                last_id = int(last_pay.Payment_Id[13:])  # Extract the numeric part
                new_pay_id = f"{id}-{last_id + 1:02d}"
            else:
                new_pay_id = f"{id}"

            customer = BillingMaster.objects.get(Bill_Id = id.split("-")[0])
            if customer.Customer_Id:
                customer_id = customer.Customer_Id
                customer_name = customer.Customer_Name
                phone_no = customer.Phone_No
            else:
                customer_id = customer.Agent_Id
                customer_name = customer.Customer_Name
                phone_no = customer.Phone_No



            paym_id = Payment_Master.objects.create(
                Payment_Id=new_pay_id,
                Bill_Id = id.split("-")[0],
                Grand_Total=int(float(data.get("totalAmount") or 0)),  # Ensure it's never None
                Paid_Amount=int(float((data.get("totalAmount") or 0)) - int(float((data.get("finalPending") or 0)))),
                Pending_Amount=int(float(data.get("finalPending") or 0)), 
                Added_By = request.user.username
                
            )

            BillingMaster.objects.filter(Bill_Id = id.split("-")[0]).update(
                Fully_Paid=1 if data.get("finalPending") == "0.00" else 0,  # Fully paid if no pending amount
                Partialy_Paid=1 if 0 < int(float((data.get("finalPending") or 0))) < int(float((data.get("totalAmount") or 0))) else 0,  # Partial payment
                Not_Paid=1 if (data.get("totalAmount") or 0) == (data.get("finalPending") or 0) else 0,  # Not paid if pending = total
                Paid_Amount = int(float(data.get("totalAmount"))) - int(float(data.get("finalPending"))),
                Pending_Amount = int(float(data.get("finalPending")))
                )
            
            incomming_amount = 0
            for entry in table_data:
                incomming_amount+=int(float(entry.get("amount")))
                Payment_Details.objects.create(
                    Payment_Id=paym_id,
                    Customer_Id = customer_id,
                    Customer_Name = customer_name,
                    Phone_Number = phone_no,
                    Grand_Total=int(float(data.get("totalAmount") or 0)),  # Ensure it's never None
                    Paid_Amount=int(float(entry.get("amount"))),  # Avoid NoneType subtraction
                    Pending_Amount=int(float(entry.get("pending_amount") or 0)),   # Ensure correct pending amount
                    Payment_Mode=entry.get("payment_mode"),
                    Utr_Or_Reason=entry.get("utr_reason"),
                    Mobile_No=entry.get("mobile_number"),
                    Bill_Id = id.split("-")[0],
                    Added_By = request.user.username
                    
                )
                if entry.get("payment_mode") == "MANUAL CLOSE":
                    BillingMaster.objects.filter(Bill_Id = id.split("-")[0]).update(
                    Force_Paid=1 if entry.get("payment_mode") == "MANUAL CLOSE" else 0,  # Set Force_Paid if MANUAL_CLOSE
                    )


            # for updating Cash_Book
            time_now = datetime.now(ZoneInfo("Asia/Kolkata"))
            current_date = time_now.strftime("%Y-%m-%d")
            today_expences = Cash_Book_Master.objects.filter(Date = current_date)
            
            if today_expences:
                for item in today_expences:
                    today_income = item.Cash_In
                Cash_Book_Master.objects.filter(Date = current_date).update(Cash_In = today_income + incomming_amount)
            else:
                last_cash = Cash_Book_Master.objects.order_by('-S_No').first()
                if last_cash:
                    last_id = int(last_cash.Expenses_Id[3:])  # Extract the numeric part
                    new_id = f"EXP{last_id + 1:04d}"
                    last_s_no = last_cash.S_No
                    s_no = last_s_no + 1
                else:
                    new_id = "EXP0001"
                    s_no = 1

                Cash_Book_Master.objects.create(S_No = s_no, Expenses_Id = new_id, Cash_In = 1500 + incomming_amount)

            
            return JsonResponse({"message": "Data received successfully"}, status=200)


        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)  # Use 400 for bad requests
        
    
 

    # Handle GET request (Fetch data for the given Bill_Id)


    last_pay = Payment_Master.objects.filter(Payment_Id__startswith=id).order_by('-Payment_Id').first() 


    if last_pay:
        last_id = int(last_pay.Payment_Id[12:])  # Extract the numeric part
        new_pay_id = f"{id}-PAY{last_id + 1:02d}"
        data= Payment_Master.objects.filter(Payment_Id__startswith=id).last()
    else:
        new_pay_id = f"{id}-PAY01"
        data =  BillingMaster.objects.filter(Bill_Id=id).last()

    
    context = {'data': data,'new_pay_id' : new_pay_id,'bill_id':id}
    return render(request, "add_payment.html", context)

@login_required(login_url='signin')
def list_payment(request,id):
    
    data = Payment_Master.objects.filter(Payment_Id__startswith=id)
    context = {'data':data}
    return render(request,'list_payments.html',context)




@login_required(login_url='signin')
def bill_and_pay(request,id):
    # for adding multiple form entry in db 
    if request.method == "POST":
        try:
            # Parse JSON data
            data = json.loads(request.body)
            entries = data.get("entries", [])
            # Save each entry into the database
            for entry in entries:
                last_bill = BillingMaster.objects.order_by('-S_No').first()
                if last_bill:
                    last_id = int(last_bill.Bill_Id[4:])  # Extract the numeric part
                    new_id = f"BILL{last_id + 1:04d}"
                    last_s_no = last_bill.S_No
                    s_no = last_s_no + 1
                else:
                    new_id = "BILL0001"
                    s_no = 1

                detail_id = BillingMaster.objects.create(
                    S_No = s_no,
                    Bill_Id= new_id,
                    Customer_Id= data.get("customer_id" , "None") ,
                    Agent_Id = data.get("agent_id" , "None"),
                    Type = "Agent" if data.get("agent_id") else "Customer",
                    Customer_Name=data.get("customer_name") if data.get("customer_name") else data.get("agent_name"),
                    Phone_No=data.get("customer_phone") if data.get("customer_phone") else data.get("agent_phone"),
                    Date = data.get("bill_date"),
                    Grand_Total = int(data.get("grand_total", 0)) if data.get("grand_total") not in [None, "", "None"] else 0,
                    Grand_Total_With_Gst = 0,
                    Added_By = request.user.username,
                    Pending_Amount = int(data.get("grand_total", 0)) if data.get("grand_total") not in [None, "", "None"] else 0,
                )
               

                break

            
            incomming_amount = 0
            for entry in entries:
                incomming_amount+=int(float(entry.get("amount")))
                last_bill = BillingDetails.objects.order_by('-Item_Id').first()
                if last_bill:
                    last_id = int(last_bill.Item_Id[12:])  # Extract the numeric part
                    new_id = f"ITM{last_id + 1:01d}-{detail_id}"
                else:
                    new_id = f"ITM1-{detail_id}"

                specification = entry.get("product", "NONE") if entry.get("product") not in [None, "", "None"] else "NONE"
                splitted_spec = specification.split(",")

                costs = entry.get("cost", "NONE") if entry.get("cost") not in [None, "", "None"] else "NONE"
                charge = entry.get("charges", 0) if entry.get("charges") not in [None, "", 0] else 0
                
                manual_amount = 0
              
                

                dimetions = entry.get("dimension")
                dimention_parts = dimetions.split("X")
                length , height = float(dimention_parts[0].strip()), float(dimention_parts[1].split("=")[0].strip())


                whatsData = BillingDetails.objects.create(
                    Bill_Id= detail_id,
                    Date = data.get("bill_date"),
                    Item_Id= new_id,
                    Added_By = request.user.username,
                    Customer_Id= data.get("customer_id" , "None") ,
                    Agent_Id = data.get("agent_id" , "None"),
                    Customer_Name=data.get("customer_name") if data.get("customer_name") else data.get("agent_name"),
                    Phone_No=data.get("customer_phone") if data.get("customer_phone") else data.get("agent_phone"),
                    Product_Name=splitted_spec[0] ,
                    Custom_Product=entry.get("custom", "NONE") if entry.get("custom") not in [None, "", "None"] else "NONE",
                    Category_Name=splitted_spec[1],
                    Sub_Category=splitted_spec[2],
                    Size = entry.get("size", "NONE") if entry.get("size") not in [None, "", "None"] else "NONE",
                    Length= length,
                    Height = height,
                    Total_Sqft = float(entry.get("total_sqft", 0) if entry.get("total_sqft") not in [None, "", "None"] else 0),
                    Quantity=int(entry.get("quantity", 0)),  # Convert to int (default 0 if missing)
                    Cost_Per_Sqft= float(entry.get("cost_per_sqft", 0)),
                    Actual_Cost = float(costs) - float(charge),
                    Modified_Cost = manual_amount,
                    GST=float(entry.get("gst", 0)) if entry.get("gst") not in [None, "", "None"] else 0,  # Convert to float (default 0 if missing)
                    HSN_Code=entry.get("hsn", "NONE") if entry.get("hsn") not in [None, "", "None"] else "NONE",
                    Total_Cost = float(costs) - float(charge),  # Convert to float
                    Total_Cost_With_Gst=float(entry.get("total_with_gst", 0)),  # Convert to float
                    Remarks = entry.get("remarks", "NONE") if entry.get("remarks") not in [None, "", "None"] else "NONE",
                    Additional_Charges = entry.get("charges", 0) if entry.get("charges") not in [None, "", 0] else 0,
                    Difference_Amount = int(float(entry.get("cost", "NONE"))) if entry.get("cost") not in [None, "", "None"] else 0
                )
                            
            
            # for updating Cash_Book
            time_now = datetime.now(ZoneInfo("Asia/Kolkata"))
            current_date = time_now.strftime("%Y-%m-%d")
            today_expences = Cash_Book_Master.objects.filter(Date = current_date)
            
            if today_expences:
                for item in today_expences:
                    today_income = item.Cash_In
                Cash_Book_Master.objects.filter(Date = current_date).update(Cash_In = today_income + incomming_amount)
            else:
                last_cash = Cash_Book_Master.objects.order_by('-S_No').first()
                if last_cash:
                    last_id = int(last_cash.Expenses_Id[3:])  # Extract the numeric part
                    new_id = f"EXP{last_id + 1:04d}"
                    last_s_no = last_cash.S_No
                    s_no = last_s_no + 1
                else:
                    new_id = "EXP0001"
                    s_no = 1

                Cash_Book_Master.objects.create(S_No = s_no, Expenses_Id = new_id, Cash_In = 1500 + incomming_amount)

            
            return redirect("addpayment", id=id)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            traceback.print_exc()  # This prints the full error traceback in the console
            return JsonResponse({"error": str(e)}, status=500)

    last_bill = BillingMaster.objects.order_by('-Bill_Id').first()
    if last_bill:
        last_id = int(last_bill.Bill_Id[4:])  # Extract the numeric part
        new_id = f"BILL{last_id + 1:04d}"
    else:
        new_id = "BILL0001"

    data = CustomerDetails.objects.filter(Status = 1)
    category = CategoriesMaster.objects.filter(Status = 1)
    products = ProductMaster.objects.filter(Status = 1)
    cos = CostMaster.objects.filter(Status = 1)
        
    context = {'new_id':new_id, 'category':category, 'products':products, 'data': data, 'cos': cos, 'new_id': new_id }

    
    return render(request,'bill3.html',context)


@login_required(login_url='signin')
@csrf_exempt
def upload_pdf(request):
    if request.method == "POST" and request.FILES.get("pdf_file"):
        pdf_file = request.FILES["pdf_file"]
        whatsapp_number = request.POST.get("whatsapp_number")

        file_path = os.path.join("media", pdf_file.name)
        file_url = request.build_absolute_uri("/media/" + pdf_file.name)

        with default_storage.open(file_path, "wb") as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        response = send_pdf_whatsapp(whatsapp_number, file_url)
        return JsonResponse(response)

    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required(login_url='signin')
def send_pdf_whatsapp(to_number, pdf_url):
    access_token = "your_access_token"
    phone_number_id = "your_phone_number_id"

    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "document",
        "document": {
            "link": pdf_url,
            "filename": "invoice.pdf"
        }
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()


@login_required(login_url='signin')
def overall_invoice(request,id):
    data = BillingDetails.objects.filter(Bill_Id = id , Status =1)
    data2 = BillingMaster.objects.get(Bill_Id = id , Status =1)
    if data2.Customer_Id:
        data3 = CustomerDetails.objects.get(Customer_Id = data2.Customer_Id)
    else :
        data3 = CustomerDetails.objects.get(Agent_Id = data2.Agent_Id)
    data4 = BillingMaster.objects.filter(Bill_Id=id)
    data5 = Payment_Details.objects.filter(Bill_Id=id)

    time_now = datetime.now(ZoneInfo("Asia/Kolkata"))
    current_date = time_now.strftime("%B %d, %Y, %I:%M %p")

    upi_id = "ssenterprisesabu@okhdfcbank" 

    if data4:
        for item in data4:
            amount = item.Pending_Amount
    else:
        amount = data2.Grand_Total

    upi_link = f"upi://pay?pa={upi_id}&pn=Payee&am={amount}&cu=INR"

    # Generate QR code
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(upi_link)
    qr.make(fit=True)
    
    # Convert QR to image
    img = qr.make_image(fill="black", back_color="white").resize((400, 400))

    # Convert image to Base64 to embed in HTML
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    context = {'data':data, 'data2':data2,'data3':data3,'current_date':current_date,'data4':data4,'billId':id,'invoice_no':id,'data5':data5,'qr_base64': qr_base64}
    return render(request,'overall_invoice.html',context)


@login_required(login_url='signin')
def quote_invoice(request,id):
    data = QuoteDetails.objects.filter(Quote_Id = id , Status =1)
    data2 = QuoteMaster.objects.get(Quote_Id = id , Status =1)


    if data2.Customer_Id:
        data3 = CustomerDetails.objects.get(Customer_Id = data2.Customer_Id)
    else :
        data3 = CustomerDetails.objects.get(Agent_Id = data2.Agent_Id)


    data4 = QuoteMaster.objects.filter(Quote_Id=id)
    data5 = QuoteDetails.objects.filter(Quote_Id=id)

    time_now = datetime.now(ZoneInfo("Asia/Kolkata"))
    current_date = time_now.strftime("%B %d, %Y")

    upi_id = "ssenterprisesabu@okhdfcbank" 

   
    amount = data2.Grand_Total

    upi_link = f"upi://pay?pa={upi_id}&pn=Payee&am={amount}&cu=INR"

    # Generate QR code
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(upi_link)
    qr.make(fit=True)
    
    # Convert QR to image
    img = qr.make_image(fill="black", back_color="white").resize((400, 400))

    # Convert image to Base64 to embed in HTML
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    context = {'data':data, 'data2':data2,'data3':data3,'current_date':current_date,'data4':data4,'billId':id,'invoice_no':id,'data5':data5,'qr_base64': qr_base64}
    return render(request,'quote_invoice.html',context)





@login_required(login_url='signin')
def list_payments_terms(request,id):
    data=Payment_Details.objects.filter(Payment_Id = id)
    context ={'data':data}
    return render(request,'list_payment_terms.html',context)

@login_required(login_url='signin')
def list_all_payments(request):
    data=Payment_Details.objects.all()
    context ={'data':data}
    return render(request,'list_all_payments.html',context)


@login_required(login_url='signin')
def filtered_data(request, filter_type):
    today = now().date()
    # Start and end of the week (Monday - Sunday)
    start_of_week = today - timedelta(days=today.weekday())  # Monday of current week
    end_of_week = start_of_week + timedelta(days=6)  # Sunday of current week

    # Start and end of the month
    start_of_month = today.replace(day=1)
    next_month = start_of_month.replace(day=28) + timedelta(days=4)  # Jump to next month
    end_of_month = next_month.replace(day=1) - timedelta(days=1)  # Get last day of current month

    # Start and end of the year
    start_of_year = today.replace(month=1, day=1)
    end_of_year = today.replace(month=12, day=31)

    # Filtering based on type
    if filter_type == 'today':
        data = Payment_Details.objects.filter(Payment_Date=today)
        data2 = BillingMaster.objects.filter(Date=today).exclude(Grand_Total=F('Pending_Amount'))
        data3 = BillingMaster.objects.filter(Date=today)
        data4 = "Today"
    elif filter_type == 'this_week':
        data = Payment_Details.objects.filter(Payment_Date__range=(start_of_week, end_of_week))
        data2 = BillingMaster.objects.filter(Date__range=(start_of_week, end_of_week)).exclude(Grand_Total=F('Pending_Amount'))
        data3 = BillingMaster.objects.filter(Date__range=(start_of_week, end_of_week))
        data4 = "This Week"
    elif filter_type == 'this_month':
        data = Payment_Details.objects.filter(Payment_Date__range=(start_of_month, end_of_month))
        data2 = BillingMaster.objects.filter(Date__range=(start_of_month, end_of_month)).exclude(Grand_Total=F('Pending_Amount'))
        data3 = BillingMaster.objects.filter(Date__range=(start_of_month, end_of_month))
        data4 = "This Month"
    elif filter_type == 'this_year':
        data = Payment_Details.objects.filter(Payment_Date__range=(start_of_year, end_of_year))
        data2 = BillingMaster.objects.filter(Date__range=(start_of_year, end_of_year)).exclude(Grand_Total=F('Pending_Amount'))
        data3 = BillingMaster.objects.filter(Date__range=(start_of_year, end_of_year))
        data4 = "This Year"
    else:
        data = Payment_Details.objects.all()
        data2 = BillingMaster.objects.exclude(Grand_Total = F('Pending_Amount'))
        data3 = BillingMaster.objects.all()
        data4 = "Overall"
 
    grand_total = 0
    paid_amount = 0
    pending_amount = 0
    for total in data3:
        grand_total += total.Grand_Total
        paid_amount += total.Paid_Amount
        pending_amount += total.Pending_Amount

        

    context = {'data': data,'grand_total': grand_total,'paid_amount':paid_amount,'pending_amount':pending_amount,'data3':data3,'data4':data4}
    return render(request, 'list_all_payments.html', context)



@login_required(login_url='signin')
def bill_payment_details(request,id):
    data = BillingDetails.objects.filter(Bill_Id = id , Status =1)
    data2 = BillingMaster.objects.get(Bill_Id = id , Status =1)
    data3= Payment_Master.objects.filter(Payment_Id__startswith=id)
    context = {'data':data, 'data2':data2, 'data3':data3,'id':id}
    # return render(request,'bill_details.html',context) 
    return render(request,'list_bill_payment.html',context)




@login_required(login_url='signin')
def update_bill(request,id):
    # for adding multiple form entry in db 
    if request.method == "POST":
        try:
            # Parse JSON data
            data = json.loads(request.body)
            entries = data.get("entries", [])

            dat = BillingMaster.objects.filter(Bill_Id=id,Status = 1)
            if dat:
                for bill in dat:
                    existing_total = bill.Grand_Total
                    existing_pending = bill.Pending_Amount
            else:
                type = "none"
                messages.info(request,f"No Existing Bill")
                return redirect('listbill')
            # Save each entry into the database
            for entry in entries:

                bill_master = BillingMaster.objects.get(Bill_Id=id)
                if bill_master.Pending_Amount == 0:
                    BillingMaster.objects.filter(Bill_Id=id).update(Fully_Paid = 0,Partialy_Paid = 1)


                detail_id = BillingMaster.objects.filter(Bill_Id = id).update(
                    Date = data.get("bill_date"),
                    Grand_Total = existing_total + int(data.get("grand_total", 0)) if data.get("grand_total") not in [None, "", "None"] else 0,
                    Grand_Total_With_Gst = 0,
                    Added_By = request.user.username,
                    Pending_Amount = existing_pending + int(data.get("grand_total", 0)) if data.get("grand_total") not in [None, "", "None"] else 0,
                )               
                update_payment_master = Payment_Master.objects.filter(Bill_Id = id).update(
                    Grand_Total = existing_total + int(data.get("grand_total", 0)) if data.get("grand_total") not in [None, "", "None"] else 0,
                    Pending_Amount = existing_pending + int(data.get("grand_total", 0)) if data.get("grand_total") not in [None, "", "None"] else 0,
                )
                update_payment_details = Payment_Details.objects.filter(Bill_Id = id).update(
                    Grand_Total = existing_total + int(data.get("grand_total", 0)) if data.get("grand_total") not in [None, "", "None"] else 0,
                    Pending_Amount = existing_pending + int(data.get("grand_total", 0)) if data.get("grand_total") not in [None, "", "None"] else 0,
                )

                break

            

            for entry in entries:
                last_bill = BillingDetails.objects.order_by('-Item_Id').first()
                if last_bill:
                    last_id = int(last_bill.Item_Id[12:])  # Extract the numeric part
                    new_id = f"ITM{last_id + 1:01d}-{detail_id}"
                else:
                    new_id = f"ITM1-{detail_id}"

                specification = entry.get("product", "NONE") if entry.get("product") not in [None, "", "None"] else "NONE"
                splitted_spec = specification.split(",")

                costs = entry.get("cost", "NONE") if entry.get("cost") not in [None, "", "None"] else "NONE"
                charge = entry.get("charges", 0) if entry.get("charges") not in [None, "", 0] else 0
                
                manual_amount = 0
              
                

                dimetions = entry.get("dimension")
                dimention_parts = dimetions.split("X")
                length , height = float(dimention_parts[0].strip()), float(dimention_parts[1].split("=")[0].strip())
                bill_master = BillingMaster.objects.get(Bill_Id=id)


                whatsData = BillingDetails.objects.create(
                    Bill_Id= bill_master,
                    Date = data.get("bill_date"),
                    Item_Id= new_id,
                    Added_By = request.user.username,
                    Customer_Id= data.get("customer_id" , "None") ,
                    Agent_Id = data.get("agent_id" , "None"),
                    Customer_Name=data.get("customer_name") if data.get("customer_name") else data.get("agent_name"),
                    Phone_No=data.get("customer_phone") if data.get("customer_phone") else data.get("agent_phone"),
                    Product_Name=splitted_spec[0] ,
                    Custom_Product=entry.get("custom", "NONE") if entry.get("custom") not in [None, "", "None"] else "NONE",
                    Category_Name=splitted_spec[1],
                    Sub_Category=splitted_spec[2],
                    Size = entry.get("size", "NONE") if entry.get("size") not in [None, "", "None"] else "NONE",
                    Length= length,
                    Height = height,
                    Total_Sqft = float(entry.get("total_sqft", 0) if entry.get("total_sqft") not in [None, "", "None"] else 0),
                    Quantity=int(entry.get("quantity", 0)),  # Convert to int (default 0 if missing)
                    Cost_Per_Sqft= float(entry.get("cost_per_sqft", 0)),
                    Actual_Cost = float(costs) - float(charge),
                    Modified_Cost = manual_amount,
                    GST=float(entry.get("gst", 0)) if entry.get("gst") not in [None, "", "None"] else 0,  # Convert to float (default 0 if missing)
                    HSN_Code=entry.get("hsn", "NONE") if entry.get("hsn") not in [None, "", "None"] else "NONE",
                    Total_Cost = float(costs) - float(charge),  # Convert to float
                    Total_Cost_With_Gst=float(entry.get("total_with_gst", 0)),  # Convert to float
                    Remarks = entry.get("remarks", "NONE") if entry.get("remarks") not in [None, "", "None"] else "NONE",
                    Additional_Charges = entry.get("charges", 0) if entry.get("charges") not in [None, "", 0] else 0,
                    Difference_Amount = int(float(entry.get("cost", "NONE"))) if entry.get("cost") not in [None, "", "None"] else 0
                )

            
            return redirect("listbill")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            traceback.print_exc()  # This prints the full error traceback in the console
            return JsonResponse({"error": str(e)}, status=500)



    data = CustomerDetails.objects.filter(Status = 1,Type = 'customer')
    data3 = CustomerDetails.objects.filter(Status = 1, Type = 'agent')
    data2 = BillingMaster.objects.all()
    category = CategoriesMaster.objects.filter(Status = 1)
    products = ProductMaster.objects.filter(Status = 1)
    cos = CostMaster.objects.filter(Status = 1)

    
    data4 = BillingMaster.objects.filter(Bill_Id=id,Status = 1)
    if data4:
        for bill in data4:
            if bill.Customer_Id:
                type = "customer"
            elif bill.Agent_Id:
                type = "agent"
    else:
        type = "none"
        messages.info(request,f"No Existing Bill")
        return redirect('listbill')

        
    context = {'new_id':id, 'category':category, 'products':products, 'data': data,'data2': data2,'data3':data3, 'cos': cos,'data4':data4, 'type':type }

    
    return render(request,'update_bill.html',context)



def graph(request):
    return render(request,'index.dashboard.html')

def Cash_Book(request):
    if request.method == 'POST':
        try:
            entries_json = request.POST.get('entries')
            total_amount = int(request.POST.get('total_amount'))
            available_amount = int(request.POST.get('available_amount'))
            category = Expense_Category.objects.all()
            print("===========",entries_json)
            entries = json.loads(entries_json) 

            time_now = datetime.now(ZoneInfo("Asia/Kolkata"))
            current_date = time_now.strftime("%Y-%m-%d")
            id_for_details  = Cash_Book_Master.objects.get(Date = current_date)
            today_expences = Cash_Book_Master.objects.filter(Date = current_date).update(Cash_In = available_amount - total_amount, Cash_Out = id_for_details.Cash_Out + total_amount)

            for entry in entries:
                Cash_Book_Details.objects.create(
                    Expenses_Id = id_for_details,
                    Expenses = entry.get('expense', "N/A"),
                    Expenses_Category = entry.get('category',"N/A"),
                    Out_Mode = entry.get('paymentMode', "N/A"),
                    Amount = entry.get('amount',0),
                    Note = entry.get('remarks',"N/A")
                )
                for item in category:
                    if item.Expense_Name != entry.get('expense', "N/A"):
                        Expense_Category.objects.create(Expense_Name = entry.get('expense', "N/A"))

            return JsonResponse({
                'success': True,
                'message': 'Payments saved successfully',
                'new_available_amount': 'new_available_amount'  # Optional
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    # for updating Cash_Book
    time_now = datetime.now(ZoneInfo("Asia/Kolkata"))
    current_date = time_now.strftime("%Y-%m-%d")
    today_expences = Cash_Book_Master.objects.filter(Date = current_date)
    cash_in_hand = 0

    if today_expences:
        for item in today_expences:
            cash_in_hand += item.Cash_In
    else:
        last_cash = Cash_Book_Master.objects.order_by('-S_No').first()
        if last_cash:
            last_id = int(last_cash.Expenses_Id[3:])  # Extract the numeric part
            new_id = f"EXP{last_id + 1:04d}"
            last_s_no = last_cash.S_No
            s_no = last_s_no + 1
        else:
            new_id = "EXP0001"
            s_no = 1
        Cash_Book_Master.objects.create(S_No = s_no, Expenses_Id = new_id)

        # If there is no income done today 
        today_expences = Cash_Book_Master.objects.filter(Date = current_date)
        if today_expences:
            for item in today_expences:
                cash_in_hand += item.Cash_In

    category = Expense_Category.objects.all()

    context = {'cash_in_hand':cash_in_hand,'category':category}
    
    return render(request,'cash_book.html',context)


def list_cash_book(request):
    data = Cash_Book_Master.objects.all()
    context = {'data':data}
    return render(request,'list_cash_book.html',context)

def expenses_details(request,id):
    data = Cash_Book_Details.objects.filter(Expenses_Id = id)
    context = {'data':data}
    return render(request,'expenses_details.html',context)

def load_cash(request):
    if request.method == "POST":
        time_now = datetime.now(ZoneInfo("Asia/Kolkata"))
        current_date = time_now.strftime("%Y-%m-%d")
        today_expences = Cash_Book_Master.objects.get(Date = current_date)
        loaded_amount = int(request.POST['loaded_amount'])
        Cash_Book_Master.objects.filter(Date = current_date).update(Cash_In = today_expences.Cash_In + loaded_amount)
        return redirect('cashbook')


    # for updating Cash_Book
    time_now = datetime.now(ZoneInfo("Asia/Kolkata"))
    current_date = time_now.strftime("%Y-%m-%d")
    today_expences = Cash_Book_Master.objects.filter(Date = current_date)
    cash_in_hand = 0

    if today_expences:
        for item in today_expences:
            cash_in_hand += item.Cash_In
    else:
        last_cash = Cash_Book_Master.objects.order_by('-S_No').first()
        if last_cash:
            last_id = int(last_cash.Expenses_Id[3:])  # Extract the numeric part
            new_id = f"EXP{last_id + 1:04d}"
            last_s_no = last_cash.S_No
            s_no = last_s_no + 1
        else:
            new_id = "EXP0001"
            s_no = 1
        Cash_Book_Master.objects.create(S_No = s_no, Expenses_Id = new_id)
    context={'cash_in_hand':cash_in_hand}
    return render(request,'load_cash.html',context)


