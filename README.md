# 📊 AI Monthly Finance Report Bot

<P>An automated system that reads financial data from Google Sheets, analyzes spending and savings patterns, and sends a beautifully formatted monthly report via email.</P>

## 🚀 Features
- 📥 Reads data from Google Sheets
- 📊 Calculates: Total Income, Total Expenses, Total Savings (from Segment column)
- 📈 Identifies top spending categories
- 🧠 Generates smart financial insights
- 📧 Sends a styled email report
- ⏰ Fully automated using GitHub Actions (monthly)

## 📊 Google Sheet Format
<p>Your sheet must follow this structure:</p>

- Date
- Category
- Segment
- Amount
<P>⚠️ Important Rules </P>
Amount must be numeric (no currency symbols)

## 🔐 Setup Google Sheets API
1. Go to Google Cloud Console
2. Create a project
3. Enable Google Sheets API
4. Create a Service Account
5. Download JSON credentials

## 🔑 Share Your Sheet
Share your Google Sheet with:your-service-account@project.iam.gserviceaccount.com
Permission: Viewer

## 🔐 Environment Variables (GitHub Secrets)
Set the following in your repository secrets:
- GOOGLE_CREDENTIALS = {your JSON content}
- EMAIL = your_email@gmail.com
- EMAIL_PASSWORD = your_app_password
- RECIPIENTS = email1@gmail.com,email2@gmail.com

## 🧠 Key Logic
Financial Calculations: 
- income = df[df["Segment"] == "Income"]["Amount"].sum()
- expenses = df[df["Segment"] == "Expense"]["Amount"].sum()
- savings = df[df["Segment"] == "Savings"]["Amount"].sum()
- Top Spending
top_spending = (
    df[df["Segment"] == "Expense"]
    .groupby("Category")["Amount"]
    .sum()
    .sort_values(ascending=False)
)

## Smart Insights
- Detects overspending
- Highlights saving behavior
- Identifies highest expense category
- Provides actionable recommendations

## ⏰ Automation (GitHub Actions)
Runs monthly

## 💡 Example Output
📊 Monthly Finance Report
<p>
Income: ₦150,000
Expenses: ₦110,000
Savings: ₦20,000
</p>
<p>🧠 Insights: </p>

- ✅ You are spending within your income
- 💰 You saved ₦20,000
- 📊 Highest spending: Food
- 💡 Reduce spending in this category

## 💼 Use Case
This project demonstrates:
- Data analysis with Python & Pandas
- API integration (Google Sheets)
- Automation (GitHub Actions)
- Email systems (SMTP)
- Real-world AI/data product thinking

## 👨‍💻 Author
**Isaiah Akinlabi** 🧠
