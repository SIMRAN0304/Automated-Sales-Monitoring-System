
from flask import Flask, render_template
import pandas as pd
import smtplib
import ssl
import os
import json

from email.message import EmailMessage
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

THRESHOLD = 500
ALERT_FILE = "alerted_dates.json"


def send_email_alert(date, sales):

    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("APP_PASSWORD", "").replace(" ", "")
    manager = os.getenv("MANAGER_EMAIL")

    if not sender or not password or not manager:
        print("Email credentials are missing in .env")
        return False

    message = EmailMessage()

    message["Subject"] = f"Low Sales Alert - {date}"
    message["From"] = sender
    message["To"] = manager

    message.set_content(
        f"""
Dear Manager,

A low sales alert has been generated.

Date: {date}
Daily Sales: €{sales:.2f}
Minimum Sales Target: €{THRESHOLD}

Please review the sales performance.

Automated Sales Monitoring System
        """
    )

    try:
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            "smtp.gmail.com", 465, context=context
        ) as server:

            server.login(sender, password)
            server.send_message(message)

        print(f"Email alert successfully sent for {date}")
        return True

    except Exception as error:
        print(f"Email sending failed: {error}")
        return False


def check_and_send_alerts(daily_sales):

    if os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, "r") as file:
            sent_dates = json.load(file)
    else:
        sent_dates = []

    for _, row in daily_sales.iterrows():

        date = row["date"]
        sales = row["revenue"]

        if sales < THRESHOLD and date not in sent_dates:

            success = send_email_alert(date, sales)

            if success:
                sent_dates.append(date)

    with open(ALERT_FILE, "w") as file:
        json.dump(sent_dates, file)


@app.route("/")
def dashboard():

    df = pd.read_csv("sales_data.csv")

    df["revenue"] = df["quantity"] * df["unit_price"]

    daily_sales = (
        df.groupby("date")["revenue"]
        .sum()
        .reset_index()
    )

    daily_sales["status"] = daily_sales["revenue"].apply(
        lambda sales: "LOW SALES ALERT"
        if sales < THRESHOLD else "NORMAL"
    )

    # Check and send email alerts
    check_and_send_alerts(daily_sales)

    total_orders = len(df)
    total_revenue = df["revenue"].sum()
    alert_count = (daily_sales["revenue"] < THRESHOLD).sum()

    return render_template(
        "dashboard.html",
        sales=daily_sales.to_dict("records"),
        total_orders=total_orders,
        total_revenue=total_revenue,
        alert_count=alert_count
    )


if __name__ == "__main__":
    app.run(debug=True)
