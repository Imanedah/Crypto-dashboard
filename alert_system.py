import smtplib
from email.mime.text import MIMEText

def send_email_alert(subject, body, to_email):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "tonemail@gmail.com"
    msg['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login("tonemail@gmail.com", "TON_MOT_DE_PASSE")
        server.send_message(msg)

# Exemple
# send_email_alert("Alerte BTC", "Bitcoin est en dessous de 20 000 EUR", "destinataire@gmail.com")
