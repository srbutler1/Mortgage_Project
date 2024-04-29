import requests
import os

def get_fred_rate(series_id, api_key):
    if series_id == "MORTGAGE30US":
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id=MORTGAGE30US&api_key=057ab4271dd220a1c637c41dbb52a60a&file_type=json"
    else:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id=MORTGAGE15US&api_key=057ab4271dd220a1c637c41dbb52a60a&file_type=json"
    try:
        response = requests.get(url, timeout=10)  # Adjust timeout as needed
        response.raise_for_status()  # This will raise an exception for HTTP errors
        data = response.json()
        
        if 'observations' in data and data['observations']:
            latest_rate = float(data['observations'][-1]['value'])
            return latest_rate
        else:
            raise ValueError("No observations found in the API response.")

    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Error:", err)
    return None  # This will return None if any error occurs



def calculate_monthly_payment(principal, annual_rate, years):
    monthly_rate = annual_rate / 1200  # Convert annual rate percentage to monthly and decimal
    months = years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    return payment

def calculate_dti(monthly_housing_payment, other_debts, annual_income):
    monthly_income = annual_income / 12
    total_monthly_debts = monthly_housing_payment + other_debts
    dti = (total_monthly_debts / monthly_income) * 100
    return dti

def calculate_estimated_rate(loan_type, credit_score, ltv, down_payment, assets, points, annual_income, other_debts, home_price, api_key):
    if loan_type == "30 year":
        series_id = "MORTGAGE30US"
        loan_years = 30
    else:
        series_id = "MORTGAGE15US"
        loan_years = 15

    base_rate = get_fred_rate(series_id, api_key)
    if base_rate is None:
        print("Failed to retrieve the base rate. Please try again later.")
        return None, None, None # Return None for all values if base rate is not available
    
    # Loan calculations
    loan_amount = home_price * (1 - down_payment / 100)
    monthly_housing_payment = calculate_monthly_payment(loan_amount, base_rate, loan_years)
    
    # Calculate total fronted value
    total_fronted = (down_payment / 100 * home_price) + (points / 100 * home_price)
    
    # Adjust rate based on points
    rate_adjustment_from_points = (points / 100) * 0.25
    base_rate -= rate_adjustment_from_points
    
    # Adjustments based on inputs
    if credit_score < 650:
        base_rate += 0.5
    if ltv > 80:
        base_rate += 0.2
    if down_payment < 20:
        base_rate += 0.25
    
    # Calculate DTI
    dti = calculate_dti(monthly_housing_payment, other_debts, annual_income)
    
    # DTI-based adjustments
    if dti > 40:
        base_rate += 0.3
    elif dti > 30:
        base_rate += 0.15
    
    # Assets transferred and points paid adjustments
    if assets > 1000000:
        base_rate -= 0.5
    
    return base_rate, monthly_housing_payment, total_fronted

def main():
    api_key = os.getenv('057ab4271dd220a1c637c41dbb52a60a')
    print("Welcome to the Mortgage Rate Estimator")
    loan_type = input("Enter the type of loan (30 year/15 year): ")
    home_price = float(input("Enter the sticker price of the home ($): "))
    credit_score = int(input("Enter your credit score: "))
    ltv = float(input("Enter your Loan-to-Value ratio (%): "))
    down_payment = float(input("Enter down payment percentage (%): "))
    annual_income = float(input("Enter your annual income ($): "))
    other_debts = float(input("Enter your other monthly debts ($): "))
    assets = float(input("Enter amount of assets transferred ($): "))
    points = float(input("Enter the amount paid in points (% of loan amount): "))
    
    estimated_rate, monthly_payment, total_fronted = calculate_estimated_rate(loan_type, credit_score, ltv, down_payment, assets, points, annual_income, other_debts, home_price, api_key)
    if estimated_rate is None:
        print("An error occurred while calculating the estimated rate.")
    else:
        print(f"Estimated Mortgage Rate: {estimated_rate}%")
        print(f"Monthly Mortgage Payment: ${monthly_payment:.2f}")
        print(f"Total Dollar Value Fronted: ${total_fronted:.2f}")

if __name__ == "__main__":
    main()
