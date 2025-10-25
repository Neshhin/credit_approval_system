from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import date
from dateutil.relativedelta import relativedelta

from .models import Customer, Loan
from .serializers import (
    CustomerRegistrationSerializer,
    CustomerResponseSerializer,
    LoanEligibilityRequestSerializer,
    LoanEligibilityResponseSerializer,
    CreateLoanRequestSerializer,
    CreateLoanResponseSerializer,
    LoanDetailSerializer,
    CustomerLoanSerializer
)
from .services import LoanEligibilityChecker, calculate_monthly_installment, round_to_nearest_lakh


@api_view(['POST'])
def register_customer(request):
    """Register a new customer"""
    serializer = CustomerRegistrationSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Calculate approved limit
    monthly_salary = data['monthly_income']
    approved_limit = round_to_nearest_lakh(monthly_salary * 36)
    
    # Create customer
    customer = Customer.objects.create(
        first_name=data['first_name'],
        last_name=data['last_name'],
        age=data['age'],
        phone_number=data['phone_number'],
        monthly_salary=monthly_salary,
        approved_limit=approved_limit,
        current_debt=0
    )
    
    response_serializer = CustomerResponseSerializer(customer)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def check_eligibility(request):
    """Check loan eligibility for a customer"""
    serializer = LoanEligibilityRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Get customer
    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check eligibility
    checker = LoanEligibilityChecker(
        customer=customer,
        loan_amount=data['loan_amount'],
        interest_rate=data['interest_rate'],
        tenure=data['tenure']
    )
    
    result = checker.check_eligibility()
    
    response_serializer = LoanEligibilityResponseSerializer(data=result)
    response_serializer.is_valid()
    
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_loan(request):
    """Create a new loan"""
    serializer = CreateLoanRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Get customer
    try:
        customer = Customer.objects.get(customer_id=data['customer_id'])
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check eligibility
    checker = LoanEligibilityChecker(
        customer=customer,
        loan_amount=data['loan_amount'],
        interest_rate=data['interest_rate'],
        tenure=data['tenure']
    )
    
    eligibility_result = checker.check_eligibility()
    
    if not eligibility_result['approval']:
        response_data = {
            'loan_id': None,
            'customer_id': customer.customer_id,
            'loan_approved': False,
            'message': 'Loan not approved based on credit score or EMI-to-salary ratio',
            'monthly_installment': eligibility_result['monthly_installment']
        }
        response_serializer = CreateLoanResponseSerializer(data=response_data)
        response_serializer.is_valid()
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    # Create loan
    start_date = date.today()
    end_date = start_date + relativedelta(months=data['tenure'])
    
    loan = Loan.objects.create(
        customer=customer,
        loan_amount=data['loan_amount'],
        tenure=data['tenure'],
        interest_rate=eligibility_result['corrected_interest_rate'],
        monthly_repayment=eligibility_result['monthly_installment'],
        emis_paid_on_time=0,
        start_date=start_date,
        end_date=end_date,
        is_active=True
    )
    
    # Update customer's current debt
    customer.current_debt += data['loan_amount']
    customer.save()
    
    response_data = {
        'loan_id': loan.loan_id,
        'customer_id': customer.customer_id,
        'loan_approved': True,
        'message': 'Loan approved successfully',
        'monthly_installment': float(loan.monthly_repayment)
    }
    
    response_serializer = CreateLoanResponseSerializer(data=response_data)
    response_serializer.is_valid()
    
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def view_loan(request, loan_id):
    """View details of a specific loan"""
    loan = get_object_or_404(Loan, loan_id=loan_id)
    serializer = LoanDetailSerializer(loan)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    """View all loans for a specific customer"""
    customer = get_object_or_404(Customer, customer_id=customer_id)
    loans = Loan.objects.filter(customer=customer, is_active=True)
    serializer = CustomerLoanSerializer(loans, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
