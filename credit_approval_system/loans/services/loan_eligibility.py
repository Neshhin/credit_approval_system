from decimal import Decimal
from .credit_score import CreditScoreCalculator
from .loan_calculator import calculate_monthly_installment
from loans.models import Loan

class LoanEligibilityChecker:
    def __init__(self, customer, loan_amount, interest_rate, tenure):
        self.customer = customer
        self.loan_amount = Decimal(loan_amount)
        self.interest_rate = Decimal(interest_rate)
        self.tenure = int(tenure)
        self.credit_score = 0
        self.corrected_interest_rate = self.interest_rate
        self.approval = False
        self.monthly_installment = Decimal(0)
        
    def check_eligibility(self):
        """Main method to check loan eligibility"""
        # Calculate credit score
        calculator = CreditScoreCalculator(self.customer)
        self.credit_score = calculator.calculate()
        
        # Check if EMIs exceed 50% of salary
        if self._check_emi_salary_ratio():
            self.approval = False
            self.corrected_interest_rate = self.interest_rate
            self.monthly_installment = calculate_monthly_installment(
                self.loan_amount, self.interest_rate, self.tenure
            )
            return self._get_result()
        
        # Determine approval and corrected interest rate based on credit score
        if self.credit_score > 50:
            self.approval = True
            self.corrected_interest_rate = self.interest_rate
        elif 30 < self.credit_score <= 50:
            if self.interest_rate >= 12:
                self.approval = True
                self.corrected_interest_rate = self.interest_rate
            else:
                self.approval = True
                self.corrected_interest_rate = Decimal('12.0')
        elif 10 < self.credit_score <= 30:
            if self.interest_rate >= 16:
                self.approval = True
                self.corrected_interest_rate = self.interest_rate
            else:
                self.approval = True
                self.corrected_interest_rate = Decimal('16.0')
        else:  # credit_score <= 10
            self.approval = False
            self.corrected_interest_rate = self.interest_rate
        
        # Calculate monthly installment with corrected rate
        self.monthly_installment = calculate_monthly_installment(
            self.loan_amount, self.corrected_interest_rate, self.tenure
        )
        
        return self._get_result()
    
    def _check_emi_salary_ratio(self):
        """Check if sum of all current EMIs > 50% of monthly salary"""
        current_emis = Loan.objects.filter(
            customer=self.customer,
            is_active=True
        )
        
        total_current_emi = sum(loan.monthly_repayment for loan in current_emis)
        new_emi = calculate_monthly_installment(
            self.loan_amount, self.interest_rate, self.tenure
        )
        
        total_emi = total_current_emi + new_emi
        max_allowed_emi = self.customer.monthly_salary * Decimal('0.5')
        
        return total_emi > max_allowed_emi
    
    def _get_result(self):
        """Return eligibility result as dictionary"""
        return {
            'customer_id': self.customer.customer_id,
            'approval': self.approval,
            'interest_rate': float(self.interest_rate),
            'corrected_interest_rate': float(self.corrected_interest_rate),
            'tenure': self.tenure,
            'monthly_installment': float(self.monthly_installment)
        }
