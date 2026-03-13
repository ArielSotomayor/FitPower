import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(to_email: str, code: str):

    sender_email = "fitpowerpro48@gmail.com"
    sender_password = "ucjr rbuh zarx cimc"  # ⚠ no dejes esto expuesto

    message = MIMEMultipart("alternative")
    message["Subject"] = "Código de verificación - FitPower Pro"
    message["From"] = sender_email
    message["To"] = to_email

    html_content = f"""
    <html>
        <body style="font-family: Arial; text-align:center;">
            <h2>Bienvenido a FitPower Pro 💪</h2>
            <p>Tu código de verificación es:</p>
            <h1 style="color:#28a745; letter-spacing:5px;">{code}</h1>
            <p>Este código expira en 10 minutos.</p>
        </body>
    </html>
    """

    message.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())

        