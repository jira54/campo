import pyotp
import qrcode
import io
import base64

def generate_otp_secret():
    """Generates a random base32 secret."""
    return pyotp.random_base32()

def get_totp_uri(email, secret, issuer_name="CampoPawa"):
    """Generates the provisioning URI for a TOTP secret."""
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer_name)

def generate_qr_base64(uri):
    """Generates a QR code image as a base64 string from a URI."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def verify_otp(secret, token):
    """Verifies a TOTP token against a secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(token)
