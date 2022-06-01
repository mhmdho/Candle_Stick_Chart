from CandleStickChart.settings import OTP_SECRET
from datetime import datetime
import onetimepass as otp
import random
import time
import re
import qrcode
from CandleStickChart.settings import DEAFULT_EMAIL_USER
from django.core.mail import EmailMultiAlternatives


class OTP:
    """
    Generate otp based on user phone number.
    """
    def __init__(self, phone):
        self.secret = re.sub(r'[^a-zA-Z2-7]', '',
                        phone + OTP_SECRET)[:16]
        self.digit = 6
        self.interval = 30
        self.interval_phone = 180
        self.verified = False

    @property
    def totp(self):
        my_token = otp.get_totp(self.secret, token_length=self.digit,
                                interval_length=self.interval)
        self.expire = time.time() + self.interval_phone
        rn_token = random.randint(0,9999999) + my_token
        return str(rn_token).zfill(7)[1:7], str(my_token).zfill(6)
    
    @property
    def expire_at(self):
        return datetime.fromtimestamp(self.expire).strftime('%H:%M:%S')

    def get_qrcode(self, email):
        img = qrcode.make(f'otpauth://totp/{email}?secret={self.secret}&\
            algorithm=SHA1&digits={self.digit}&period={self.interval}&issuer=TradingHills')
        return img.show()


class MailVerification:
    """
    Render html email and send verification email to user.
    """
    def __init__(self, email, otp):
        self.sender = DEAFULT_EMAIL_USER
        self.reciever = [email]
        self.otp = otp

    @property
    def email_subject(self):
        subject = f'[TradingHills] Verification Code: {self.otp[3]}*****'
        return subject

    @property
    def email_text(self):
        text = f'\n\nConfirm Your Email \
            \n\nWelcome to TradingHills! \
            \nHere is your Email confirmation code: \
            \n \
            \n{self.otp} \
            \n(Expire in 3 minutes) \
            \n \
            \nTradingHills Development Team \
            \nThis is an automated message, please do not reply.'
        return text

    @property
    def email_html(self):
        url = "https://tradinghills.com/PyTHC/logo.png"
        logo = f'<div style="text-align:center;"> \
                    <img src={url} height="70"> \
                </div>' 
        title = '<br><h2>Confirm Your Email</h2><br>'
        content =f'Welcome to TradingHills! \
                <br><br> \
                Here is your Email confirmation code: \
                <br><br> \
                <hr> \
                <div style="text-align:center;"> \
                    <div style="font-size:34px;color:#324a5e;">{self.otp}</div> \
                    <hr> \
                    <i> \
                        (This code will expire in 3 minutes). \
                        Please do not disclose it to anyone (including TradingHills staff) \
                    </i> \
                <hr> \
                </div> \
                <p style="color:#a3a6b3"> \
                    <br> \
                    TradingHills Development Team \
                    <br> \
                    This is an automated message, please do not reply.\
                </p><br>'
        return logo + title + content

    def email_send(self):
        msg = EmailMultiAlternatives(self.email_subject, self.email_text, self.sender, self.reciever)
        msg.attach_alternative(self.email_html, "text/html")
        msg.send()
