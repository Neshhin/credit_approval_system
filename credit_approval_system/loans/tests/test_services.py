from django.test import TestCase
from decimal import Decimal
from loans.models import Customer, Loan
from loans.services import CreditScoreCalculator, LoanEligibilityChecker, calculate_monthly_installment
from datetime import date

class LoanCalculatorTest(TestCase):
    def test_calculate_emi_with_interest(self):
        """Test EMI calculation with interest"""
        emi = calculate_monthly_installment(100000, 10, 12)
        self.assertAlmostEqual(float(emi), 8791.59, places=2)
    
    def test_calculate_emi_zero_interest(self):
        """Test EMI calculation with zero interest"""
        emi = calculate_monthly_installment(120000, 0, 12)
        self.assertEqual(float(emi), 10000.00)


class CreditScoreTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            age=30,
            phone_number="1234567890",
            monthly_salary=Decimal('50000'),
            approved_limit=Decimal('1800000'),
            current_debt=Decimal('0')
        )
    
    def test_new_customer_score(self):
        """Test credit score for new customer with no loans"""
        calculator = CreditScoreCalculator(self.customer)
        score = calculator.calculate()
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_score_with_good_payment_history(self):
        """Test credit score with good payment history"""
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('100000'),
            tenure=12,
            interest_rate=Decimal('10'),
            monthly_repayment=Decimal('8791.59'),
            emis_paid_on_time=12,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            is_active=False
        )
        
        calculator = CreditScoreCalculator(self.customer)
        score = calculator.calculate()
        self.assertGreater(score, 50)


class LoanEligibilityTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Jane",
            last_name="Smith",
            age=28,
            phone_number="9876543210",
            monthly_salary=Decimal('60000'),
            approved_limit=Decimal('2160000'),
            current_debt=Decimal('0')
        )
    
    def test_high_credit_score_approval(self):
        """Test loan approval with high credit score"""
        # Create good loan history
        Loan.objects.create(
            customer=self.customer,
            loan_amount=Decimal('50000'),
            tenure=6,
            interest_rate=Decimal('8'),
            monthly_repayment=Decimal('8600'),
            emis_paid_on_time=6,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),
            is_active=False
        )
        
        checker = LoanEligibilityChecker(
            self.customer, 100000, 10, 12
        )
        result = checker.check_eligibility()
        
        self.assertTrue(result['approval'])
    
    def test_emi_salary_ratio_rejection(self):
        """Test loan rejection when EMI exceeds 50% of salary"""
        checker = LoanEligibilityChecker(
            self.customer, 500000, 12, 12
        )
        result = checker.check_eligibility()
        
        # High loan amount should be rejected due to EMI-salary ratio
        self.assertFalse(result['approval'])
