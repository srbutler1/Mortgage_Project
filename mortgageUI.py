#%%
import tkinter as tk
import os
import requests

def get_fred_rate(series_id, api_key):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'observations' in data and data['observations']:
            latest_rate = float(data['observations'][-1]['value'])
            return latest_rate
        else:
            raise ValueError("No observations found in the API response.")
    except requests.exceptions.RequestException as err:
        print(f"Request Error: {err}")
        return None

def calculate_monthly_payment(principal, annual_rate, years):
    monthly_rate = annual_rate / 1200
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
        return None, None, None

    loan_amount = home_price * (1 - down_payment / 100)
    monthly_housing_payment = calculate_monthly_payment(loan_amount, base_rate, loan_years)
    total_fronted = (down_payment / 100 * home_price) + (points / 100 * loan_amount)
    adjusted_rate = base_rate - (points / 100) * 0.25

    if credit_score < 650:
        adjusted_rate += 0.5
    if ltv > 80:
        adjusted_rate += 0.2
    if down_payment < 20:
        adjusted_rate += 0.25

    dti = calculate_dti(monthly_housing_payment, other_debts, annual_income)

    if dti > 40:
        adjusted_rate += 0.3
    elif dti > 30:
        adjusted_rate += 0.15

    if assets > 1000000:
        adjusted_rate -= 0.5

    return adjusted_rate, monthly_housing_payment, total_fronted

def submit_form():
    try:
        loan_type = loan_type_var.get()
        home_price = float(home_price_entry.get())
        credit_score = int(credit_score_entry.get())
        ltv = float(ltv_entry.get())
        down_payment = float(down_payment_entry.get())
        annual_income = float(annual_income_entry.get())
        other_debts = float(other_debts_entry.get())
        assets = float(assets_entry.get())
        points = float(points_entry.get())
        api_key = "057ab4271dd220a1c637c41dbb52a60a"
        if not api_key:
            result_label.config(text="API Key is not set in environment.")
            return
        estimated_rate, monthly_payment, total_fronted = calculate_estimated_rate(
            loan_type, credit_score, ltv, down_payment, assets, points, annual_income, other_debts, home_price, api_key)
        if estimated_rate is None:
            result_label.config(text="An error occurred while calculating the estimated rate.")
        else:
            result_label.config(text=f"Estimated Mortgage Rate: {estimated_rate:.2f}%\n"
                                     f"Monthly Mortgage Payment: ${monthly_payment:.2f}\n"
                                     f"Total Dollar Value Fronted: ${total_fronted:.2f}")
    except Exception as e:
        result_label.config(text=f"Error: {str(e)}")

def create_gui():
    global loan_type_var, home_price_entry, credit_score_entry, ltv_entry, down_payment_entry, annual_income_entry, other_debts_entry, assets_entry, points_entry, result_label
    root = tk.Tk()
    root.title("Mortgage Rate Estimator")

    tk.Label(root, text="Loan Type (30 year/15 year):").grid(row=0, column=0)
    loan_type_var = tk.StringVar(value="30 year")
    loan_type_option_menu = tk.OptionMenu(root, loan_type_var, "30 year", "15 year")
    loan_type_option_menu.config(width=20)
    loan_type_option_menu.grid(row=0, column=1)

    tk.Label(root, text="Home Price ($):").grid(row=1, column=0)
    home_price_entry = tk.Entry(root)
    home_price_entry.grid(row=1, column=1)

    tk.Label(root, text="Credit Score:").grid(row=2, column=0)
    credit_score_entry = tk.Entry(root)
    credit_score_entry.grid(row=2, column=1)

    tk.Label(root, text="Loan-to-Value Ratio (%):").grid(row=3, column=0)
    ltv_entry = tk.Entry(root)
    ltv_entry.grid(row=3, column=1)

    tk.Label(root, text="Down Payment (%):").grid(row=4, column=0)
    down_payment_entry = tk.Entry(root)
    down_payment_entry.grid(row=4, column=1)

    tk.Label(root, text="Annual Income ($):").grid(row=5, column=0)
    annual_income_entry = tk.Entry(root)
    annual_income_entry.grid(row=5, column=1)

    tk.Label(root, text="Other Monthly Debts ($):").grid(row=6, column=0)
    other_debts_entry = tk.Entry(root)
    other_debts_entry.grid(row=6, column=1)

    tk.Label(root, text="Assets Transferred ($):").grid(row=7, column=0)
    assets_entry = tk.Entry(root)
    assets_entry.grid(row=7, column=1)

    tk.Label(root, text="Points Paid (% of loan amount):").grid(row=8, column=0)
    points_entry = tk.Entry(root)
    points_entry.grid(row=8, column=1)

    submit_button = tk.Button(root, text="Calculate", command=submit_form)
    submit_button.grid(row=9, column=0, columnspan=2)

    result_label = tk.Label(root, text="")
    result_label.grid(row=10, column=0, columnspan=2)

    root.mainloop()

root = tk.Tk()

create_gui()

tk.Label(root, text="Assets Transferred ($):").grid(row=7, column=0)
assets_entry = tk.Entry(root)
assets_entry.grid(row=7, column=1)

tk.Label(root, text="Points Paid (% of loan amount):").grid(row=8, column=0)
points_entry = tk.Entry(root)
points_entry.grid(row=8, column=1)

submit_button = tk.Button(root, text="Calculate", command=submit_form)
submit_button.grid(row=9, column=0, columnspan=2)

result_label = tk.Label(root, text="")
result_label.grid(row=10, column=0, columnspan=2)

root.mainloop()

if __name__ == "__main__":
    create_gui()
