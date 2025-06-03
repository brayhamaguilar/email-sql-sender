import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# Step 1: Connect to the database
conn = mysql.connector.connect(
    host="fdb1030.awardspace.net",
    user="4629818_jbpainting",
    password="Brayham@2025",
    database="4629818_jbpainting"
)
cursor = conn.cursor()

# Step 2: Get entries submitted in the last 5 minutes
now = datetime.utcnow()
five_min_ago = now - timedelta(minutes=5)

def fetch_and_format(table_name, fields):
    query = f"SELECT {', '.join(fields)} FROM {table_name} WHERE submitted_at >= %s"
    cursor.execute(query, (five_min_ago,))
    rows = cursor.fetchall()
    if not rows:
        return ""
    df = pd.DataFrame(rows, columns=fields)
    return f"<h2>New entries in '{table_name}'</h2>" + df.to_html(index=False, escape=False)

# Table fields
contact_fields = ["id", "name", "phone", "email_address", "message", "submitted_at"]
quote_fields = ["id", "full_name", "email", "phone_number", "project_postcode", "file_name", "submitted_at"]

# Step 3: Format HTML for both tables
contact_html = fetch_and_format("contact_form", contact_fields)
quote_html = fetch_and_format("quote_requests", quote_fields)

# Step 4: Send email if there's new data
if contact_html or quote_html:
    sender_email = "brayhamaguilar@pythonanywhere.com"
    receiver_email = "mouhcine.amelhay55@gmail.com"

    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "New Submissions from Website"

    full_html = contact_html + "<br><br>" + quote_html
    msg.attach(MIMEText(full_html, "html"))

    with smtplib.SMTP("smtp.pythonanywhere.com", 587) as server:
        server.login(os.environ.get('PYTHONANYWHERE_USERNAME'), '')  # No password needed
        server.send_message(msg)

# Step 5: Clean up
cursor.close()
conn.close()
