from CandleStickChart.settings import OTP_SECRET
from datetime import datetime
import onetimepass as otp
import random
import time
import re


class OTP:
    """
    Generate otp based on user phone number.
    """
    def __init__(self, phone):     
        self.secret = phone + OTP_SECRET
        self.digit = 6
        self.interval = 120
        self.verified = False

    @property
    def totp(self):
        my_secret = re.sub(r'[^a-zA-Z2-7]', '', self.secret)[:16]
        my_token = otp.get_totp(my_secret, token_length=self.digit,
                                interval_length=self.interval)
        self.expire = time.time() + self.interval
        rn_token = random.randint(10000,9999999) + my_token
        return rn_token
    
    @property
    def expire_at(self):
        return datetime.fromtimestamp(self.expire).strftime('%H:%M:%S')
