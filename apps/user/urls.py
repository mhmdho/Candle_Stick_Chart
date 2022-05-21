from django.urls import path
from .views import MyObtainTokenPairView, UserPhoneVerify, UserRegister


urlpatterns = [
    path('register/', UserRegister.as_view(), name='register_api'),
    path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('customer/phone/verify/', UserPhoneVerify.as_view(), name='phone_verify_api'),

]
