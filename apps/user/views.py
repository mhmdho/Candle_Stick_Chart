from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from apps.user.tasks import sms77_otp
from apps.user.utils import OTP
from .models import CustomUser
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import User2FASerializer, UserPhoneVerifySerializer, MyTokenObtainPairSerializer, RegisterSerializer
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
    Generates an otp and takes the otp to verify user phone number.
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
        cache.set(customer.phone, str(otp.totp), timeout=otp.interval)
        sms77_otp(customer.phone,
                    cache.get(customer.phone),
                    otp.expire_at
                    )
        return Response({"Verify Code": cache.get(customer.phone),
                        "Expire at": otp.expire_at},
                         status=status.HTTP_201_CREATED)
        
    def put(self, request, *args, **kwargs):
        super().put(request, *args, **kwargs)
        customer = get_object_or_404(CustomUser, id=self.request.user.id)
        if customer.is_phone_verified:
            return Response({"Message": "Your phone has been verified before"},
                            status=status.HTTP_200_OK)
        if cache.get(customer.phone) == self.request.data['otp']:
            customer.is_phone_verified = True
            customer.save()
            return Response({"Verified": customer.is_phone_verified},
                            status=status.HTTP_202_ACCEPTED)
        return Response({"Error": "Wrong OTP or expired"},
                        status=status.HTTP_400_BAD_REQUEST)


class User2FA(generics.RetrieveUpdateAPIView):
    """
    Generates a QRcode for google authenticator.
    """
    http_method_names = ['get', 'put']
    permission_classes = (IsAuthenticated,)
    serializer_class = User2FASerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)

    def get(self, request, *args, **kwargs):   
        super().get(request, *args, **kwargs)
        customer = get_object_or_404(CustomUser, id=self.request.user.id)
        if customer.is_2FA_enabled:
            return Response({"Message": "Your Google authenticater has been set before"},
                            status=status.HTTP_200_OK)
        otp = OTP(customer.phone)
        otp.get_qrcode(customer.email)
        customer.is_2FA_enabled = True
        customer.save()   
        return Response({"Verify Code": customer.is_2FA_enabled,
                        "Expire at": otp.expire_at,
                        "QR": otp.get_qrcode(customer.email)},
                         status=status.HTTP_201_CREATED)
        
    def put(self, request, *args, **kwargs):
        super().put(request, *args, **kwargs)
        customer = get_object_or_404(CustomUser, id=self.request.user.id)
        if not customer.is_2FA_enabled:
            return Response({"Message": "Your google authenticater is not active"},
                            status=status.HTTP_400_BAD_REQUEST)
        otp = OTP(customer.phone)
        if str(otp.totp) == self.request.data['otp']:
            return Response({"Verified": True},
                            status=status.HTTP_202_ACCEPTED)
        return Response({"Error": "Wrong OTP or expired"},
                        status=status.HTTP_400_BAD_REQUEST)
