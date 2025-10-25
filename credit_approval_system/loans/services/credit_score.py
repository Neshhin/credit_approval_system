from decimal import Decimal
from datetime import datetime, date
from django.db.models import Sum, Q
from loans.models import Loan

class CreditScoreCalculator:
    def __init__(self, customer):
        self.customer = customer
        self.score = 0
        
    def calculate(self):
        """Calculate credit score based on various factors (out of 100)"""
        # If sum of current loans > approved limit, credit score = 0
        if self._check_exceeds_limit():
            return 0
        
        score = 0
        
        # Component 1: Past loans paid on time (40 points)
        score += self._score_payment_history()
        
        # Component 2: Number of loans taken (20 points)
        score += self._score_number_of_loans()
        
        # Component 3: Loan activity in current year (20 points)
        score += self._score_current_year_activity()
        
        # Component 4: Loan approved volume (20 points)
        score += self._score_loan_volume()
        
        return min(100, max(0, score))
    
    def _check_exceeds_limit(self):
        """Check if sum of current EMIs exceeds approved limit"""
        current_loans = Loan.objects.filter(
            customer=self.customer,
            is_active=True
        )
        
        total_loan_amount = current_loans.aggregate(
            total=Sum('loan_amount')
        )['total'] or Decimal(0)
        
        return total_loan_amount > self.customer.approved_limit
    
    def _score_payment_history(self):
        """Score based on EMIs paid on time vs total EMIs"""
        loans = Loan.objects.filter(customer=self.customer)
        
        if not loans.exists():
            return 20  # New customer gets average score
        
        total_emis = sum(loan.tenure for loan in loans)
        emis_paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
        
        if total_emis == 0:
            return 20
        
        payment_ratio = emis_paid_on_time / total_emis
        return round(payment_ratio * 40)
    
    def _score_number_of_loans(self):
        """Score based on number of loans"""
        loan_count = Loan.objects.filter(customer=self.customer).count()
        
        if loan_count == 0:
            return 10
        elif loan_count <= 3:
            return 20
        elif loan_count <= 6:
            return 15
        else:
            return 10  # Too many loans
    
    def _score_current_year_activity(self):
        """Score based on loan activity in current year"""
        current_year = datetime.now().year
        
        current_year_loans = Loan.objects.filter(
            customer=self.customer,
            start_date__year=current_year
        )
        
        count = current_year_loans.count()
        
        if count == 0:
            return 5
        elif count <= 2:
            return 20
        elif count <= 4:
            return 15
        else:
            return 10
    
    def _score_loan_volume(self):
        """Score based on total loan volume vs approved limit"""
        total_loan_amount = Loan.objects.filter(
            customer=self.customer
        ).aggregate(total=Sum('loan_amount'))['total'] or Decimal(0)
        
        if self.customer.approved_limit == 0:
            return 10
        
        volume_ratio = total_loan_amount / self.customer.approved_limit
        
        if volume_ratio < Decimal('0.5'):
            return 20
        elif volume_ratio < Decimal('1.0'):
            return 15
        elif volume_ratio < Decimal('2.0'):
            return 10
        else:
            return 5
