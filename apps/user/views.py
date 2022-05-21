from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from apps.user.utils import OTP
from .models import CustomUser
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserPhoneVerifySerializer, MyTokenObtainPairSerializer, RegisterSerializer
from rest_framework import generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.cache import cache


# Create your views here.


class UserRegister(generics.CreateAPIView):
    """
    Takes a set of informations and register customer.
    """
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response({"Success": "Your registration was successful"}, status=status.HTTP_201_CREATED)


class MyObtainTokenPairView(TokenObtainPairView):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer
    parser_classes = (MultiPartParser, FormParser)


class UserPhoneVerify(generics.RetrieveUpdateAPIView):
    """
    Generates an otp and takes the otp to verify customer phone number.
    """
    http_method_names = ['put', 'get']
    permission_classes = (IsAuthenticated,)
    serializer_class = UserPhoneVerifySerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def get(self, request, *args, **kwargs):   
        super().get(request, *args, **kwargs)
        customer = get_object_or_404(CustomUser, id=self.request.user.id)
        if customer.is_phone_verified:
            return Response({"Message": "Your phone have been verified before"},
                            status=status.HTTP_200_OK)
        otp = OTP(customer.phone)
        cache.set(customer.phone, otp.totp, timeout=otp.interval)

        return Response({"Verify Code": otp.totp,
                        "Expire at": otp.expire_at},
                         status=status.HTTP_201_CREATED)
        
    def put(self, request, *args, **kwargs):
        super().put(request, *args, **kwargs)
        customer = get_object_or_404(CustomUser, id=self.request.user.id)
        if customer.is_phone_verified:
            return Response({"Message": "Your phone have been verified before"},
                            status=status.HTTP_200_OK)
        otp = OTP(customer.phone)
        if cache.get(customer.phone) == self.request.data['otp']:
            customer.is_phone_verified = True
            customer.save()
            return Response({"Verified": customer.is_phone_verified},
                            status=status.HTTP_202_ACCEPTED)
        return Response({"Error": "Wrong OTP or expired"},
                        status=status.HTTP_400_BAD_REQUEST)
