from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.


class CustomerMaster(models.Model):
    Customer_Id = models.CharField(unique=True, max_length=20, null=True)
    Agent_Id = models.CharField(unique=True, max_length=20, null=True)
    Customer_Name = models.CharField(max_length=50)
    Phone_No = models.BigIntegerField()
    Status = models.IntegerField(default=1)


class CustomerDetails(models.Model):
    Customer_Id = models.CharField(unique=True, max_length=20, null=True)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=False)
    Agent_Id = models.CharField(unique=True, max_length=20, null=True)
    Customer_Name = models.CharField(max_length=50)
    Phone_No = models.BigIntegerField()
    Alt_Phone = models.BigIntegerField(null=True)
    Email = models.EmailField(max_length=100, null=True)
    Address = models.CharField(max_length=150, null=True)
    Type = models.CharField(null=True, max_length=10)
    Added_By = models.CharField(null=True, max_length=50)
    Status = models.IntegerField(default=1)


class MaterialMaster(models.Model):
    Material_Id = models.CharField(primary_key=True, max_length=15)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=False)
    Added_By = models.CharField(null=True, max_length=50)
    Material_Name = models.CharField(max_length=50)
    Material_Make = models.CharField(max_length=50)
    Material_Size_In_Meters = models.FloatField()
    Material_Size_In_Feet = models.FloatField()
    Additional_Info = models.CharField(max_length=50)
    Status = models.IntegerField(default=1)


class InwardMaster(models.Model):
    S_No = models.IntegerField(unique=True)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=False)
    Added_By = models.CharField(null=True, max_length=50)
    Inward_Id = models.CharField(primary_key=True, max_length=15)
    Material_Id = models.CharField(max_length=15)
    Material_Name = models.CharField(null=True, max_length=50)
    Vendor_Name = models.CharField(max_length=50)
    Vendor_Mobile = models.BigIntegerField()
    Vendor_GST = models.CharField(max_length=20)
    Invoice_Cost = models.IntegerField()
    Invoice_Quantity = models.IntegerField()
    Batch_No = models.CharField(max_length=50)
    Batch_Id = models.CharField(max_length=15)
    Additional_Info = models.CharField(max_length=50)
    Status = models.IntegerField(default=1)


class OutwardMaster(models.Model):
    Outward_Id = models.CharField(max_length=15)
    Inward_Id = models.CharField(max_length=15, null=True)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=False)
    Material_Id = models.CharField(max_length=15)
    Material_Name = models.CharField(max_length=15)
    Used_By = models.CharField(max_length=15)
    Outward_Quantity = models.IntegerField()
    Batch_Id = models.CharField(max_length=15)
    Batch_No = models.CharField(max_length=50)
    Additional_Info = models.CharField(max_length=50)


class ProductMaster(models.Model):
    Product_Id = models.CharField(primary_key=True, max_length=15)
    Date = models.DateField(null=True, blank=True)
    Added_By = models.CharField(max_length=50, blank=True, null=True)
    Product_Name = models.CharField(max_length=50)
    GST = models.CharField(max_length=10)
    HSN_Code = models.CharField(max_length=15)
    Status = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.Product_Id:
            last_product = ProductMaster.objects.order_by(
                '-Product_Id').first()
            if last_product and last_product.Product_Id.startswith("PROD"):
                # Extract the numeric part
                last_id = int(last_product.Product_Id[4:])
                self.Product_Id = f"PROD{last_id + 1:04d}"
            else:
                self.Product_Id = "PROD0001"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.Product_Name


class CategoriesMaster(models.Model):
    Categories_Id = models.CharField(primary_key=True, max_length=15)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=False)
    Added_By = models.CharField(null=True, max_length=50)
    Categories_Name = models.CharField(max_length=50)
    Product_Name = models.CharField(max_length=50)
    Size = models.CharField(max_length=15, default="None")
    Sub_Categories = models.CharField(null=True, max_length=50)
    Status = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.Categories_Id:
            last_categories = CategoriesMaster.objects.order_by(
                '-Categories_Id').first()
            if last_categories:
                # Extract the numeric part
                last_id = int(last_categories.Categories_Id[3:])
                self.Categories_Id = f"CAT{last_id + 1:04d}"
            else:
                self.Categories_Id = "CAT0001"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.Categories_Name


class CostMaster(models.Model):
    Cost_Id = models.CharField(primary_key=True, max_length=15)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=False)
    Added_By = models.CharField(null=True, max_length=50)
    Product_Name = models.CharField(max_length=50)
    Category_Name = models.CharField(max_length=50)
    Sub_Category = models.CharField(null=True, max_length=50)
    Size = models.CharField(null=True, max_length=15, default="None")
    Length = models.IntegerField(null=True)
    Height = models.IntegerField(null=True)
    Cost_Per_Unit_Status = models.IntegerField(default=0)
    Cost_Per_Unit = models.IntegerField(default=0)
    Cost_Per_Sqft_Status = models.IntegerField(default=0)
    Cost_Per_Sqft = models.IntegerField(default=0)
    Fixed_Cost_Status = models.IntegerField(default=0)
    Fixed_Cost = models.FloatField(default=0)
    Cost_for_Agent = models.FloatField(null=True)
    Selling_Cost = models.FloatField(null=True)
    Status = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.Cost_Id:
            last_product = CostMaster.objects.order_by('-Cost_Id').first()
            if last_product:
                # Extract the numeric part
                last_id = int(last_product.Cost_Id[4:])
                self.Cost_Id = f"COST{last_id + 1:04d}"
            else:
                self.Cost_Id = "COST0001"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.Product_Name


class BillingMaster(models.Model):
    S_No = models.IntegerField(null=True)
    Bill_Id = models.CharField(primary_key=True, max_length=15)
    Customer_Id = models.CharField(max_length=15)
    Agent_Id = models.CharField(max_length=15, null=True)
    Type = models.CharField(null=True, max_length=15)
    Customer_Name = models.CharField(max_length=50)
    Phone_No = models.BigIntegerField()
    Grand_Total = models.IntegerField()
    Grand_Total_With_Gst = models.IntegerField()

    Paid_Amount = models.IntegerField(default=0)
    Pending_Amount = models.IntegerField(default=0)
    Fully_Paid = models.IntegerField(default=0)
    Partialy_Paid = models.IntegerField(default=0)
    Not_Paid = models.IntegerField(default=1)
    Force_Paid = models.IntegerField(default=0)
    Added_By = models.CharField(null=True, max_length=50)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=False)

    Status = models.IntegerField(default=1)

    def __str__(self):
        return self.Bill_Id


class BillingDetails(models.Model):
    Bill_Id = models.ForeignKey(
        "ssdapp.BillingMaster",
        on_delete=models.CASCADE)
    Item_Id = models.CharField(null=True, max_length=15)
    Customer_Id = models.CharField(max_length=15)
    Agent_Id = models.CharField(max_length=15, null=True)
    Type = models.CharField(null=True, max_length=15)
    Customer_Name = models.CharField(max_length=50)
    Phone_No = models.BigIntegerField()
    Product_Name = models.CharField(max_length=50)
    Custom_Product = models.CharField(max_length=50)
    Category_Name = models.CharField(max_length=50)
    Sub_Category = models.CharField(null=True, max_length=50)
    Length = models.FloatField(default=0)
    Height = models.FloatField(default=0)
    Total_Sqft = models.FloatField(null=True)
    Quantity = models.IntegerField(default=0)
    Cost_Per_Sqft = models.FloatField(default=0)
    Difference_Amount = models.IntegerField(null=True)
    Modified_Cost = models.IntegerField(null=True)
    Actual_Cost = models.FloatField(null=True)
    GST = models.CharField(max_length=15)
    HSN_Code = models.CharField(max_length=15)
    Total_Cost = models.CharField(max_length=15)
    Final_Total_Cost = models.CharField(null=True, max_length=15)
    Total_Cost_With_Gst = models.CharField(max_length=15)
    Final_Total_Cost_With_Gst = models.CharField(max_length=15, null=True)
    Remarks = models.CharField(null=True, max_length=50)
    Size = models.CharField(null=True, max_length=15)
    Added_By = models.CharField(null=True, max_length=50)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=False)
    Additional_Charges = models.FloatField(null=True)
    Status = models.IntegerField(default=1)

    def __str__(self):
        return self.Bill_Id


class QuoteMaster(models.Model):
    Quote_Id = models.CharField(primary_key=True, max_length=15)
    S_No = models.IntegerField(null=True)
    Customer_Id = models.CharField(max_length=15)
    Agent_Id = models.CharField(max_length=15, null=True)
    Type = models.CharField(null=True, max_length=15)
    Customer_Name = models.CharField(max_length=50)
    Phone_No = models.BigIntegerField()
    Grand_Total = models.IntegerField()
    Grand_Total_With_Gst = models.IntegerField()

    Added_By = models.CharField(null=True, max_length=50)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=False)
    Status = models.IntegerField(default=1)

    def __str__(self):
        return self.Quote_Id


class QuoteDetails(models.Model):
    Quote_Id = models.ForeignKey(
        "ssdapp.QuoteMaster",
        on_delete=models.CASCADE)
    Item_Id = models.CharField(null=True, max_length=15)
    Customer_Id = models.CharField(max_length=15)
    Agent_Id = models.CharField(max_length=15, null=True)
    Type = models.CharField(null=True, max_length=15)
    Customer_Name = models.CharField(max_length=50)
    Phone_No = models.BigIntegerField()
    Product_Name = models.CharField(max_length=50)
    Category_Name = models.CharField(max_length=50)
    Sub_Category = models.CharField(null=True, max_length=50)
    Length = models.FloatField(default=0)
    Height = models.FloatField(default=0)
    Total_Sqft = models.FloatField(null=True)
    Quantity = models.IntegerField(default=0)
    Cost_Per_Sqft = models.FloatField(default=0)
    Difference_Amount = models.IntegerField(null=True)
    Modified_Cost = models.IntegerField(null=True)
    Actual_Cost = models.FloatField(null=True)
    GST = models.CharField(max_length=15, null=True)
    HSN_Code = models.CharField(max_length=15, null=True)
    Total_Cost = models.CharField(max_length=15)
    Final_Total_Cost = models.CharField(null=True, max_length=15)
    Total_Cost_With_Gst = models.CharField(max_length=15)
    Final_Total_Cost_With_Gst = models.CharField(max_length=15, null=True)
    Remarks = models.CharField(null=True, max_length=50)
    Size = models.CharField(null=True, max_length=15)
    Added_By = models.CharField(null=True, max_length=50)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=False)
    Additional_Charges = models.FloatField(null=True)
    Status = models.IntegerField(default=1)

    def __str__(self):
        return self.Quote_Id


class EstimateMaster(models.Model):
    Estimation_Id = models.CharField(primary_key=True, max_length=50)
    Customer_Id = models.CharField(max_length=50)
    Agent_Id = models.CharField(max_length=50, null=True)
    Type = models.CharField(null=True, max_length=50)
    Customer_Name = models.CharField(max_length=50)
    Phone_No = models.BigIntegerField()
    Grand_Total = models.IntegerField()
    Date = models.DateField(null=True, auto_now=False, auto_now_add=False)
    Added_By = models.CharField(null=True, max_length=50)
    Status = models.IntegerField(default=1)

    def __str__(self):
        return self.Estimation_Id


class EstimateDetails(models.Model):
    Estimation_Id = models.ForeignKey(
        "ssdapp.EstimateMaster",
        on_delete=models.CASCADE)
    Item_Id = models.CharField(null=True, max_length=50)
    Customer_Id = models.CharField(max_length=50)
    Agent_Id = models.CharField(max_length=50, null=True)
    Type = models.CharField(null=True, max_length=50)
    Customer_Name = models.CharField(max_length=50)
    Phone_No = models.BigIntegerField()
    Product_Name = models.CharField(max_length=50)
    Custom_Product = models.CharField(max_length=50)
    Category_Name = models.CharField(max_length=50)
    Sub_Category = models.CharField(null=True, max_length=50)
    Length = models.FloatField(default=0)
    Height = models.FloatField(default=0)
    Total_Sqft = models.FloatField(null=True)
    Quantity = models.IntegerField(default=0)
    Cost_Per_Sqft = models.FloatField(default=0)
    Difference_Amount = models.IntegerField(null=True)
    Modified_Cost = models.IntegerField(null=True)
    Actual_Cost = models.FloatField(null=True)
    Total_Cost = models.CharField(max_length=50)
    Final_Total_Cost = models.CharField(max_length=50, null=True)
    Remarks = models.CharField(null=True, max_length=50)
    Size = models.CharField(null=True, max_length=50)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=False)
    Added_By = models.CharField(null=True, max_length=50)
    Status = models.IntegerField(default=1)

    def __str__(self):
        return self.Estimation_Id


class Employee(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='employee')
    emp_id = models.CharField(max_length=20, unique=True)
    phone = models.BigIntegerField(unique=True)
    DOJ = models.DateField(null=True)
    aadhar = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=50, null=True)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=False)
    Added_By = models.CharField(null=True, max_length=50)
    # Add related_name to avoid conflicts with auth.User
    groups = models.ManyToManyField(
        Group, related_name="employee_groups", blank=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name="employee_permissions", blank=True)


class Payment_Master(models.Model):
    Payment_Id = models.CharField(max_length=50, primary_key=True)
    Bill_Id = models.CharField(default="BILL0001", max_length=50)
    Grand_Total = models.IntegerField(default=0)
    Paid_Amount = models.IntegerField(default=0)
    Pending_Amount = models.IntegerField(default=0)
    Added_By = models.CharField(null=True, max_length=50)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=True)


class Payment_Details(models.Model):
    Payment_Id = models.ForeignKey(
        "ssdapp.Payment_Master",
        on_delete=models.CASCADE)
    Customer_Id = models.CharField(null=True, max_length=50)
    Customer_Name = models.CharField(null=True, max_length=50)
    Phone_Number = models.BigIntegerField(null=True)
    Grand_Total = models.IntegerField(default=0)
    Payment_Date = models.DateField(auto_now=True, auto_now_add=False)
    Paid_Amount = models.IntegerField(default=0)
    Pending_Amount = models.IntegerField(default=0)
    Payment_Mode = models.CharField(max_length=50)
    Utr_Or_Reason = models.CharField(max_length=50)
    Mobile_No = models.CharField(max_length=50)
    Bill_Id = models.CharField(default="BILL0001", max_length=50)
    Added_By = models.CharField(null=True, max_length=50)
    Date = models.DateField(null=True, auto_now=False, auto_now_add=True)


class Cash_Book_Master(models.Model):
    S_No = models.IntegerField()
    Expenses_Id = models.CharField(primary_key=True, max_length=50)
    Date_Time = models.DateTimeField(auto_now=True, auto_now_add=False)
    Date = models.DateField(auto_now=True, auto_now_add=False)
    Cash_In = models.FloatField(default=1500.00)
    Cash_Out = models.FloatField(default=0)
    Balance = models.FloatField(default=0)


class Cash_Book_Details(models.Model):
    Expenses_Id = models.ForeignKey(
        "ssdapp.Cash_Book_Master",
        on_delete=models.CASCADE)
    Date = models.DateTimeField(auto_now=True, auto_now_add=False)
    Expenses = models.CharField(max_length=50)
    Expenses_Category = models.CharField(max_length=50)
    Out_Mode = models.CharField(null=True, max_length=50)
    Amount = models.FloatField(null=True)
    Note = models.CharField(max_length=50)


class Expense_Category(models.Model):
    Category = models.CharField(max_length=50, null=True)
    Expense_Name = models.CharField(max_length=50)
