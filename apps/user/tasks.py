from CandleStickChart.settings import SMS77_API_KEY
from sms77api.Sms77api import Sms77api


def sms77_otp(phone, otp, expire):
    api = Sms77api(SMS77_API_KEY)
    message =f"--TradingHills--\
            \nCode: {otp}\
            \nExpire: {expire}"
    return api.sms(phone, message)
