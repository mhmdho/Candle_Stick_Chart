from django.urls import path
from .views import MyObtainTokenPairView, UserRegister


urlpatterns = [
    path('register/', UserRegister.as_view(), name='register_url'),
    path('login/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
]
