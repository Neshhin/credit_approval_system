from decimal import Decimal
import math

def calculate_monthly_installment(loan_amount, annual_interest_rate, tenure_months):
    """
    Calculate EMI using compound interest formula.
    EMI = P × r × (1 + r)^n / ((1 + r)^n - 1)
    where:
    P = Principal loan amount
    r = Monthly interest rate (annual rate / 12 / 100)
    n = Number of months (tenure)
    """
    if annual_interest_rate == 0:
        return Decimal(loan_amount) / Decimal(tenure_months)
    
    P = Decimal(loan_amount)
    r = Decimal(annual_interest_rate) / Decimal(12) / Decimal(100)
    n = Decimal(tenure_months)
    
    # Calculate (1 + r)^n
    one_plus_r_power_n = (1 + r) ** n
    
    # EMI formula
    emi = P * r * one_plus_r_power_n / (one_plus_r_power_n - 1)
    
    return round(emi, 2)


def round_to_nearest_lakh(amount):
    """Round amount to nearest lakh (100,000)"""
    return round(Decimal(amount) / Decimal(100000)) * Decimal(100000)
