"""
Project Name: Wealth Projection & FIRE Calculator
Goal: Financial Independence & Wealth Building
Description: A comprehensive tool to project wealth growth over time using compound interest, 
             including FIRE (Financial Independence, Retire Early) number calculation.
Author: Sivanesh
Date: 2026-03-16
"""

import math
from typing import Dict, List, Optional

class WealthProjector:
    def __init__(
        self,
        initial_investment: float,
        monthly_contribution: float,
        annual_return_rate: float,
        years: int,
        inflation_rate: float = 0.03
    ):
        """
        Initialize the wealth projector.
        
        Args:
            initial_investment: Starting capital ($)
            monthly_contribution: Amount added every month ($)
            annual_return_rate: Expected annual return (as a decimal, e.g., 0.07 for 7%)
            years: Projection horizon (years)
            inflation_rate: Expected inflation rate (default 3%)
        """
        self.initial_investment = initial_investment
        self.monthly_contribution = monthly_contribution
        self.annual_return_rate = annual_return_rate
        self.years = years
        self.inflation_rate = inflation_rate
        self.results = []

    def calculate(self) -> List[Dict]:
        """
        Calculate year-by-year wealth growth.
        """
        current_balance = self.initial_investment
        total_contributed = self.initial_investment
        
        monthly_rate = (1 + self.annual_return_rate) ** (1/12) - 1
        
        for year in range(0, self.years + 1):
            real_value = current_balance / ((1 + self.inflation_rate) ** year)
            
            self.results.append({
                "year": year,
                "nominal_balance": round(current_balance, 2),
                "real_balance": round(real_value, 2),
                "total_contributed": round(total_contributed, 2),
                "interest_earned": round(current_balance - total_contributed, 2)
            })
            
            # Update for next year
            for _ in range(12):
                current_balance = (current_balance + self.monthly_contribution) * (1 + monthly_rate)
                total_contributed += self.monthly_contribution
                
        return self.results

    def calculate_fire_number(self, annual_expenses: float, withdrawal_rate: float = 0.04) -> float:
        """
        Calculate the FIRE number based on the 4% rule (default).
        """
        return annual_expenses / withdrawal_rate

    def years_to_fire(self, fire_number: float) -> Optional[int]:
        """
        Estimate years until the FIRE number is reached.
        """
        for entry in self.results:
            if entry["real_balance"] >= fire_number:
                return entry["year"]
        return None

def display_results(projector: WealthProjector, annual_expenses: float):
    """
    Format and display the projection results in the terminal.
    """
    results = projector.calculate()
    fire_num = projector.calculate_fire_number(annual_expenses)
    years_to_fire = projector.years_to_fire(fire_num)

    print("\n" + "="*60)
    print(" WEALTH PROJECTION & FIRE CALCULATOR ".center(60, "="))
    print("="*60)
    print(f"Initial Investment:  ${projector.initial_investment:,.2f}")
    print(f"Monthly Contribution: ${projector.monthly_contribution:,.2f}")
    print(f"Annual Return Rate:   {projector.annual_return_rate*100:.1f}%")
    print(f"Inflation Rate:       {projector.inflation_rate*100:.1f}%")
    print(f"Projection Horizon:   {projector.years} years")
    print("-" * 60)
    print(f"Target FIRE Number:   ${fire_num:,.2f} (based on ${annual_expenses:,.2f} expenses)")
    
    if years_to_fire is not None:
        print(f"Estimated Time to FIRE: {years_to_fire} years")
    else:
        print("FIRE target not reached within projection horizon.")
    print("-" * 60)
    
    # Table Header
    header = f"{'Year':<6} | {'Nominal Balance':<18} | {'Real Balance (Adj)':<18} | {'Interest':<12}"
    print(header)
    print("-" * len(header))
    
    # Sample results (every 5 years to keep it clean)
    for i, res in enumerate(results):
        if i % 5 == 0 or i == projector.years:
            print(f"{res['year']:<6} | ${res['nominal_balance']:>17,.2f} | ${res['real_balance']:>17,.2f} | ${res['interest_earned']:>11,.2f}")

    print("-" * 60)
    
    # ASCII Chart (Simple representation of Real Balance growth)
    print("\nReal Balance Growth (Progressive Scale):")
    max_val = results[-1]['real_balance']
    for i, res in enumerate(results):
        if i % 5 == 0 or i == projector.years:
            bar_len = int((res['real_balance'] / max_val) * 40) if max_val > 0 else 0
            print(f"Year {res['year']:>2}: {'#' * bar_len}")

    print("="*60 + "\n")

if __name__ == "__main__":
    # Example Scenario: 
    # Starting with $10k, adding $1k/month, 8% returns, for 30 years.
    # Annual expenses of $40k.
    
    my_projector = WealthProjector(
        initial_investment=10000,
        monthly_contribution=2000,
        annual_return_rate=0.08,
        years=30
    )
    
    display_results(my_projector, annual_expenses=48000)
