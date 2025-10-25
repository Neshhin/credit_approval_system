from django.contrib import admin
from .models import Customer, Loan

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'first_name', 'last_name', 'phone_number', 'monthly_salary', 'approved_limit']
    search_fields = ['first_name', 'last_name', 'phone_number']
    list_filter = ['created_at']

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_id', 'customer', 'loan_amount', 'tenure', 'interest_rate', 'is_active', 'start_date']
    search_fields = ['loan_id', 'customer__first_name', 'customer__last_name']
    list_filter = ['is_active', 'start_date', 'end_date']
    raw_id_fields = ['customer']
