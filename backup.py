import os
import datetime
import subprocess
import smtplib
from email.message import EmailMessage
import gzip

# -----------------------------
# DB CONFIG
# -----------------------------
DB_NAME = "ssdproject_db"
DB_USER = "ssduser"
DB_PASSWORD = "$DrOK8laryvF"
DB_HOST = "localhost"
DB_PORT = "3306"

# -----------------------------
# EMAIL CONFIG
# -----------------------------
EMAIL_SENDER = "technical.jrtechnologies@gmail.com"
EMAIL_PASSWORD = "iyxn jsmz cibl yzkk"
EMAIL_RECEIVER = "technical.jrtechnologies@gmail.com"

# -----------------------------
# FILE NAME
# -----------------------------
today = datetime.datetime.now().strftime("%Y-%m-%d")
sql_file = f"{DB_NAME}_{today}.sql"
gz_file = f"{sql_file}.gz"

# -----------------------------
# STEP 1: BACKUP DATABASE
# -----------------------------
try:
    env = os.environ.copy()
    env["MYSQL_PWD"] = DB_PASSWORD  # secure way

    with open(sql_file, "w") as f:
        subprocess.run(
            [
                "mysqldump",
                "-h", DB_HOST,
                "-P", DB_PORT,
                "-u", DB_USER,
                DB_NAME
            ],
            stdout=f,
            check=True,
            env=env
        )

    print("Backup created")

except Exception as e:
    print("Backup failed:", e)
    exit()

# -----------------------------
# STEP 2: COMPRESS FILE
# -----------------------------
try:
    with open(sql_file, "rb") as f_in:
        with gzip.open(gz_file, "wb") as f_out:
            f_out.writelines(f_in)

    os.remove(sql_file)
    print("Compressed to .gz")

except Exception as e:
    print("Compression failed:", e)

# -----------------------------
# STEP 3: SEND EMAIL
# -----------------------------
try:
    msg = EmailMessage()
    msg["Subject"] = f"DB Backup - {today}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg.set_content("Database backup attached.")

    with open(gz_file, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="gzip",
            filename=gz_file
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print("Email sent")

except Exception as e:
    print("Email failed:", e)

# -----------------------------
# OPTIONAL CLEANUP
# -----------------------------
# os.remove(gz_file)