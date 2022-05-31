from django.urls import path
from .views import MyObtainTokenPairView, User2FA, UserEmailVerify, UserPhoneVerify, UserRegister


urlpatterns = [
    path('register/', UserRegister.as_view(), name='register_api'),
    path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('phone/verify/', UserPhoneVerify.as_view(), name='phone_verify_api'),
    path('email/verify/', UserEmailVerify.as_view(), name='email_verify_api'),
    path('2FA/', User2FA.as_view(), name='2FA_api'),

]
