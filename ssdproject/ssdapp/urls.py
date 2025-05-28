from django.urls import path
from ssdapp import views

urlpatterns = [
    path('addcustomer/',views.addCustomer,name='addcustomer'),
    path('listcustomer/',views.listCustomer,name='listcustomer'),
    path('customerdetails/<str:id>/',views.customerDetail,name='customerdetails'),
    path('editcustomer/<str:id>/',views.editCustomer,name='editcustomer'),
    path('deletecustomer/<str:id>/',views.deleteCustomer,name='deletecustomer'),
    path('addmaterial/',views.addMaterial,name='addmaterial'),
    path('listmaterial/',views.listMaterial,name='listmaterial'),
    path('editmaterial/<str:id>/',views.editMaterial,name='editmaterial'),
    path('materialdetails/<str:id>/',views.materialDetails,name='materialdetails'),
    path('deletematerial/<str:id>/',views.deleteMaterial,name='deletematerial'),
    path('addinward/<str:id>/',views.addInward,name='addinward'),
    path('listinward/',views.listInward,name='listinward'),
    path('inwarddetails/<str:id>/',views.inwardDetails,name='inwarddetails'),
    path('deleteinward/<str:id>/',views.deleteInward,name='deleteinward'),
    path('addproduct/',views.addProduct,name='addproduct'),
    path('listproduct/',views.listProduct,name='listproduct'),
    path('editproduct/<str:id>/',views.editProduct,name='editProduct'),
    path('deleteProduct/<str:id>/',views.deleteProduct,name='deleteProduct'),
    path('addcategories/',views.addCategories,name='addcategories'),
    path('listcategories/',views.listCategories,name='listcategories'),
    path('editCategories/<str:id>/',views.editCategories,name='editCategories'),
    path('addcost/',views.add_Cost,name='addcost'),
    path('listcost/',views.listCost,name='listcost'),
    path('bill/',views.bill,name='bill'),
    path('quote/',views.quote,name='quote'),
    path('estimate/',views.estimate,name='estimate'),
    path('listbill/',views.listBill,name='listbill'),
    path('outstanding/',views.outstanding,name='outstanding'),
    path('listquote/',views.listQuote,name='listquote'),
    path('listestimate/',views.listEstimate,name='listestimate'),
    path('billdetails/<str:id>/',views.billDetails,name='billdetails'),
    path('quotedetails/<str:id>/',views.quoteDetails,name='quotedetails'),
    path('estimatedetails/<str:id>/',views.estimateDetails,name='estimatedetails'),
    path('addemployee/', views.add_employee, name='addemployee'),
    path('listemployee/', views.list_employee, name='listemployee'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('invoice/<str:id>/', views.invoice, name='invoice'),
    path('quote_invoice/<str:id>/', views.quote_invoice, name='quote_invoice'),
    path('bill_quotation/<str:id>/', views.bill_quotation, name='bill_quotation'),
    path('', views.dashboard, name='dashboard'),
    path('addpayment/<str:id>/', views.add_payment, name='addpayment'),
    path('listpayment/<str:id>/', views.list_payment, name='listpayment'),
    path('bill_and_pay/<str:id>/', views.bill_and_pay, name='bill_and_pay'),

     path('upload_pdf/', views.upload_pdf, name='upload_pdf'),

    path('overallinvoice/<str:id>/', views.overall_invoice, name='overallinvoice'),
    path('paymentterms/<str:id>/', views.list_payments_terms, name='paymentterms'),
    path('listallpayments/', views.list_all_payments, name='listallpayments'),
    path('data/<str:filter_type>/', views.filtered_data, name='filtered_data'),
    path('listbilldetails/<str:id>/', views.bill_payment_details, name='bill_payment_details'),

    path('service-success/', views.service_success, name='service_success'),
    path('whatsapp/<str:id>/',views.select_bill,name='whatsapp'),

    path('add_inward/',views.select_material,name='select_material'),
    path('addoutward/<str:id>/',views.add_outward,name='addoutward'),
    path('listoutward/',views.list_outward,name='listoutward'),

    path('editcost/<str:id>/',views.editCost,name='editcost'),
    path('update_bill/<str:id>/',views.update_bill,name='update_bill'),

    path('graph/',views.graph,name='graph'),

    path('cashbook/',views.Cash_Book,name="cashbook"),
    path('listcashbook/',views.list_cash_book,name="listcashbook"),
    path('loadcash/',views.load_cash,name="loadcash"),
    path('detailexpenses/<str:id>',views.expenses_details,name="detailexpenses"),

]


