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

data = sheet.get_all_values()

if len(data) <= 1:
    raise Exception("No data found in sheet")

headers = [h.strip() for h in data[0]]
rows = data[1:]

df = pd.DataFrame(rows, columns=headers)

# =========================
# 🧹 CLEAN DATA (CRITICAL)
# =========================

# Remove completely empty rows
df = df.dropna(how="all")

# Strip spaces from all string cells
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Convert types
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Drop rows with no amount
df = df.dropna(subset=["Amount"])

# Normalize text
df["Category"] = df["Category"].str.capitalize()
df["Segment"] = df["Segment"].str.capitalize()

# =========================
# 🧪 DEBUG (IMPORTANT)
# =========================
print("ROWS AFTER CLEANING:", len(df))
print("CATEGORY:", df["Category"].unique())
print("SEGMENT:", df["Segment"].unique())

# =========================
# 💰 CALCULATIONS (FINAL)
# =========================

income = df.loc[df["Category"] == "Income", "Amount"].sum()
expenses = df.loc[df["Category"] == "Expense", "Amount"].sum()
savings = df.loc[df["Segment"] == "Savings", "Amount"].sum()

top_spending = (
    df[df["Category"] == "Expense"]
    .groupby("Segment")["Amount"]
    .sum()
    .sort_values(ascending=False)
)

# =========================
# 🧠 SMART INSIGHTS
# =========================
def generate_insight():
    if income == 0:
        return "No income recorded."

    insight = ""

    if expenses > income:
        insight += "⚠️ You are overspending.<br>"
    else:
        insight += "✅ Your spending is under control.<br>"

    if savings > 0:
        insight += f"💰 You saved ₦{savings:,.0f}.<br>"
    else:
        insight += "⚠️ No savings recorded.<br>"

    if not top_spending.empty:
        top = top_spending.idxmax()
        insight += f"📊 Highest spending: {top}.<br>"
        insight += "💡 Try reducing this category."

    return insight

insight = generate_insight()

# =========================
# 📧 EMAIL DESIGN (MODERN)
# =========================
html_content = f"""
<div style="font-family:Arial; max-width:600px; margin:auto; padding:20px;">
    
    <h2 style="color:#111;">📊 Monthly Finance Report</h2>

    <hr>

    <p><b>💰 Income:</b> ₦{income:,.0f}</p>
    <p><b>💸 Expenses:</b> ₦{expenses:,.0f}</p>
    <p><b>🏦 Savings:</b> ₦{savings:,.0f}</p>

    <h3>📈 Top Spending</h3>
    <ul>
        {''.join([f"<li>{k}: ₦{v:,.0f}</li>" for k, v in top_spending.head(3).items()])}
    </ul>

    <div style="background:#f4f6f8; padding:15px; border-radius:8px;">
        <h3>🧠 Insights</h3>
        <p>{insight}</p>
    </div>

    <hr>
    <p style="font-size:12px; color:gray;">Sent by Finance AI Bot</p>
</div>
"""

# =========================
# 📤 SEND EMAIL
# =========================
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENTS = os.getenv("RECIPIENTS")

if not EMAIL or not EMAIL_PASSWORD or not RECIPIENTS:
    raise Exception("Missing email environment variables")

recipients = [r.strip() for r in RECIPIENTS.split(",")]

msg = MIMEMultipart("alternative")
msg["Subject"] = "📊 Monthly Finance Report"
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
    print("❌ Email failed:", e)
