from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)])
    phone_number = models.CharField(max_length=15, unique=True)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=12, decimal_places=2)
    current_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['customer_id']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.customer_id})"
    
    def calculate_approved_limit(self):
        """Calculate approved limit as 36 * monthly_salary rounded to nearest lakh"""
        limit = self.monthly_salary * 36
        # Round to nearest lakh (100,000)
        rounded_limit = round(limit / 100000) * 100000
        return rounded_limit


class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.IntegerField(help_text="Loan tenure in months")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2)
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'loans'
        indexes = [
            models.Index(fields=['customer', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"Loan {self.loan_id} - Customer {self.customer.customer_id}"
    
    def emis_left(self):
        """Calculate remaining EMIs"""
        return max(0, self.tenure - self.emis_paid_on_time)
    
    def total_amount_paid(self):
        """Calculate total amount paid so far"""
        return self.monthly_repayment * self.emis_paid_on_time
    
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        return self.loan_amount - self.total_amount_paid()
