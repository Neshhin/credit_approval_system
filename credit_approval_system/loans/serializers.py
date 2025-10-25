from rest_framework import serializers
from .models import Customer, Loan

class CustomerRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField(min_value=18, max_value=100)
    monthly_income = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    phone_number = serializers.CharField(max_length=15)
    
    def validate_phone_number(self, value):
        if Customer.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already registered")
        return value


class CustomerResponseSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    monthly_income = serializers.DecimalField(source='monthly_salary', max_digits=12, decimal_places=2)
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'age', 'monthly_income', 'approved_limit', 'phone_number']
    
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class LoanEligibilityRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0)
    tenure = serializers.IntegerField(min_value=1)


class LoanEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    corrected_interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    tenure = serializers.IntegerField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)


class CreateLoanRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0)
    tenure = serializers.IntegerField(min_value=1)


class CreateLoanResponseSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.DecimalField(max_digits=12, decimal_places=2)


class CustomerDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='customer_id')
    
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'age']


class LoanDetailSerializer(serializers.ModelSerializer):
    customer = CustomerDetailSerializer()
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_amount', 'interest_rate', 'monthly_repayment', 'tenure']


class CustomerLoanSerializer(serializers.ModelSerializer):
    repayments_left = serializers.SerializerMethodField()
    
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_repayment', 'repayments_left']
    
    def get_repayments_left(self, obj):
        return obj.emis_left()
