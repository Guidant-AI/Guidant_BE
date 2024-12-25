import pyotp
import requests

mailgun_api_key = "cfc669704a3c4157e3a7c6152b1e5db1-0920befd-35cc31a4"
mailgun_domain = "sandboxbaf9f5f429ce4ef08d7882fc92250f72.mailgun.org"
def send_otp_email(email: str, otp: str) -> dict:
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
            auth=("api", mailgun_api_key),
            data={
                "from": f"OTP Service <mailgun@{mailgun_domain}>",
                "to": [email],
                "subject": "Your OTP Code",
                "text": f"Your OTP code is: {otp}\n\nThis code is valid for the next 5 minutes."
            }
        )
        if response.status_code == 200:
            return {"status": "success", "message": "OTP sent successfully"}
        else:
            return {"status": "failure", "message": response.text}
    except Exception as e:
        return {"status": "failure", "message": str(e)}

# Function to generate OTP
def generate_otp(secret: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.now()

def validate_otp(otp_secret: str, otp: str) -> bool:
    totp = pyotp.TOTP(otp_secret)
    print(f"Validating OTP: {otp}, Generated OTP: {totp.now()}, Secret: {otp_secret}")
    return totp.verify(otp)
