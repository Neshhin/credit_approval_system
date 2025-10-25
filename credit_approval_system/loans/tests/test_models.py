from django.test import TestCase
from decimal import Decimal
from loans.models import Customer, Loan
from datetime import date

class CustomerModelTest(TestCase):
    def test_customer_creation(self):
        """Test customer model creation"""
        customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=25,
            phone_number="1111111111",
            monthly_salary=Decimal('40000'),
            approved_limit=Decimal('1440000')
        )
        self.assertEqual(str(customer), "Test User (ID: {})".format(customer.customer_id))
    
    def test_approved_limit_calculation(self):
        """Test approved limit calculation"""
        customer = Customer.objects.create(
            first_name="Test",
            last_name="User",
            age=25,
            phone_number="2222222222",
            monthly_salary=Decimal('55000'),
            approved_limit=Decimal('0')
        )
        calculated_limit = customer.calculate_approved_limit()
        # 55000 * 36 = 1,980,000 rounded to nearest lakh = 2,000,000
        self.assertEqual(calculated_limit, Decimal('2000000'))


class LoanModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Loan",
            last_name="Tester",
            age=30,
            phone_number="3333333333",
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000')
        )
    
    def test_loan_creation(self):
        """Test loan model creation"""
        loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('100000'),
            tenure=12,
            interest_rate=Decimal('10'),
            monthly_repayment=Decimal('8791.59'),
            emis_paid_on_time=5,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31)
        )
        self.assertEqual(loan.emis_left(), 7)
    
    def test_emis_left_calculation(self):
        """Test EMIs left calculation"""
        loan = Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('200000'),
            tenure=24,
            interest_rate=Decimal('12'),
            monthly_repayment=Decimal('9414'),
            emis_paid_on_time=10,
            start_date=date(2024, 1, 1),
            end_date=date(2026, 1, 1)
        )
        self.assertEqual(loan.emis_left(), 14)
