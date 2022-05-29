from CandleStickChart.settings import OTP_SECRET
from datetime import datetime
import onetimepass as otp
import random
import time
import re
import qrcode


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
        rn_token = random.randint(100000,9999999) + my_token
        return str(rn_token)[:6], str(my_token).zfill(6)
    
    @property
    def expire_at(self):
        return datetime.fromtimestamp(self.expire).strftime('%H:%M:%S')

    def get_qrcode(self, email):
        img = qrcode.make(f'otpauth://totp/{email}?secret={self.secret}&\
            algorithm=SHA1&digits={self.digit}&period={self.interval}&issuer=TradingHills')
        return img.show()
