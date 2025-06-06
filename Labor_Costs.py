#Import the libraries
import pandas as pd
import numpy as np
import math
from scipy import stats
import os


#1. Personnel Costs (without Sunday surcharges!)


# Source monthly salary: GAV Swissport Zürich (CHF) https://luftverkehr.vpod.ch/downloads/gav/swissport-zuerich/gesamtarbeitsvertrag-gav-monatslohn-ab-1.1.2016.pdf
monthly_salary = 4524
months_per_year = 13  # incl. 13th monthly salary
weeks_per_year = 52
working_hours_per_week = 39

# Calculation of hourly wage
hourly_wage = (monthly_salary * months_per_year) / (weeks_per_year * working_hours_per_week)

# Employer cost surcharge (incl. social contributions etc.) according to https://www.postfinance.ch/de/blog/business-blog/wie-sie-personalkosten-richtig-kalkulieren.html
employer_surcharge = 1.2
personnel_cost_per_hour = hourly_wage * employer_surcharge

# Operating hours Zurich Airport in hours per year (05:45 - 22:45) https://www.flughafen-zuerich.ch/de/unternehmen/magazin/2025/politik_betriebszeiten

operating_hours_per_day = 22.45 - 5.45
days_per_year = 365
operating_hours_per_year = operating_hours_per_day * days_per_year

# Number of TUGs (can be adjusted)
number_of_tugs = 1  # example value

# Total personnel costs per year
annual_personnel_costs = number_of_tugs * personnel_cost_per_hour * operating_hours_per_year

# Output
print("=== Personnel Cost Overview ===")
print(f"Hourly wage (gross): {hourly_wage:.2f} CHF")
print(f"Employer personnel cost per hour: {personnel_cost_per_hour:.2f} CHF")
print(f"Operating hours per year: {operating_hours_per_year:.0f} h")
print(f"Annual personnel costs for {number_of_tugs} TUG(s): {annual_personnel_costs:,.2f} CHF")