import os
import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# =========================
# 🔐 LOAD GOOGLE CREDENTIALS
# =========================
creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))

scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# =========================
# 📊 LOAD GOOGLE SHEET
# =========================
SHEET_ID = "1Mzybgh1NZ6jOrQHCzmA4ZZNn2BuImAHV9WAD2s4Dq-8"
sheet = client.open_by_key(SHEET_ID).worksheet("Transactions")

all_values = sheet.get_all_values()

if not all_values:
    print("Sheet is empty")
    df = pd.DataFrame()
else:
    headers = all_values[0]
    data_rows = all_values[1:]

    # Fix empty or duplicate headers
    cleaned_headers = []
    seen = {}

    for i, h in enumerate(headers):
        name = h.strip() if h.strip() else f"Unnamed_{i}"

        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0

        cleaned_headers.append(name)

    df = pd.DataFrame(data_rows, columns=cleaned_headers)

    print(df.columns)

    # Clean columns
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# =========================
# 🧹 CLEAN DATA
# =========================
df.columns = df.columns.str.strip()

df["Category"] = df["Category"].astype(str).str.strip().str.title()
df["Segment"] = df["Segment"].astype(str).str.strip().str.title()

df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

df.head()

# Ensure 'Date' column is in datetime format
df["Date"] = pd.to_datetime(df["Date"])

# Filter for the current month (dynamically gets the current month)
current_month_num = pd.Timestamp.now().month
current_month = df[df["Date"].dt.month == current_month_num]

# Display the first few rows of the filtered data to verify
print(f"Data for the current month (Month {current_month_num}):")
print(current_month.head())

income = current_month[current_month["Category"] == "Income"]["Amount"].sum()
expenses = current_month[current_month["Category"] == "Expenses"]["Amount"].sum()

savings = current_month[current_month["Segment"] == "Savings"]["Amount"].sum()

top_spending = (
    current_month[current_month["Category"] == "Expenses"] # Filter for expense transactions based on 'Category'
    .groupby("Segment") # Group by 'Segment' to identify top spending areas within expenses
    ["Amount"].sum()
    .sort_values(ascending=False)
)

# =========================
# 🧠 SMART INSIGHTS
# =========================
def generate_smart_insight():
    insight = ""

    if income == 0:
        return "No income recorded this month."

    if expenses > income:
        insight += "⚠️ Your expenses exceed your income.<br>"
    else:
        insight += "✅ You are spending within your income.<br>"

    if savings > 0:
        insight += f"💰 You saved ₦{savings:,.0f} this month.<br>"
    else:
        insight += "⚠️ No savings recorded.<br>"

    if not top_spending.empty:
        top_category = top_spending.idxmax()
        insight += f"📊 Highest spending: {top_category}.<br>"
        insight += "💡 Try reducing spending in this category."
    else:
        insight += "No expense data available."

    return insight

insight = generate_smart_insight()

# =========================
# 📧 BUILD EMAIL
# =========================
html_content = f"""
<div style="font-family:Arial; padding:20px;">
    <h2>📊 Monthly Finance Report</h2>

    <p><b>Income:</b> ₦{income:,.0f}</p>
    <p><b>Expenses:</b> ₦{expenses:,.0f}</p>
    <p><b>Savings:</b> ₦{savings:,.0f}</p>

    <h3>📈 Top Spending</h3>
    <pre>{top_spending.head(3).to_string()}</pre>

    <div style="background:#f5f7fa; padding:15px; border-radius:8px; margin-top:20px;">
        <h3>🧠 Financial Insights</h3>
        <p>{insight}</p>
    </div>
</div>
"""

# =========================
# 📤 SEND EMAIL
# =========================
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
recipients = os.getenv("RECIPIENTS").split(",")

msg = MIMEMultipart("alternative")
msg["Subject"] = "Monthly Finance Report"
msg["From"] = f"Finance AI Bot <{EMAIL}>"
msg["To"] = ", ".join(recipients)

msg.attach(MIMEText(html_content, "html"))

try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL, EMAIL_PASSWORD)
    server.sendmail(EMAIL, recipients, msg.as_string())
    server.quit()
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Email failed: {e}")
