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
from django.core.mail import send_mail
from CandleStickChart.settings import DEAFULT_EMAIL_USER


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
            return Response({"Message": "Your phone has been verified before"},
                            status=status.HTTP_200_OK)
        otp = OTP(customer.phone)
        cache.set(customer.phone, otp.totp[0], timeout=otp.interval_phone)
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
        return Response({"Google Authenticator set:": customer.is_2FA_enabled},
                         status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        super().put(request, *args, **kwargs)
        customer = get_object_or_404(CustomUser, id=self.request.user.id)
        if not customer.is_2FA_enabled:
            return Response({"Message": "Your google authenticater is not active"},
                            status=status.HTTP_400_BAD_REQUEST)
        otp = OTP(customer.phone)
        if otp.totp[1] == self.request.data['otp']:
            return Response({"Verified": True},
                            status=status.HTTP_202_ACCEPTED)
        return Response({"Error": "Wrong OTP or expired"},
                        status=status.HTTP_400_BAD_REQUEST)


class UserEmailVerify(generics.RetrieveUpdateAPIView):
    """
    Generates an otp and takes the otp to verify user email.
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
        if customer.is_email_verified:
            return Response({"Message": "Your email has been verified before"},
                            status=status.HTTP_200_OK)
        otp = OTP(customer.email)
        cache.set(customer.email, otp.totp[0], timeout=otp.interval_phone)
        msg_t = f'[TradingHills] Verification Code: {cache.get(customer.email)}'
        msg_c = f'\n\nConfirm Your Email \
                \n\nWelcome to TradingHills! \
                \nHere is your Email confirmation code: \
                \n \
                \n{cache.get(customer.email)} \
                \n(Expire at: {otp.expire_at}) \
                \n \
                \nTradingHills Developer Team \
                \nThis is an automated message, please do not reply.'
        send_mail(msg_t,
                msg_c,
                DEAFULT_EMAIL_USER,
                [customer.email],
                fail_silently=False
                )
        return Response({"Verify Code": cache.get(customer.email),
                        "Expire at": otp.expire_at},
                         status=status.HTTP_201_CREATED)
        
    def put(self, request, *args, **kwargs):
        super().put(request, *args, **kwargs)
        customer = get_object_or_404(CustomUser, id=self.request.user.id)
        if customer.is_email_verified:
            return Response({"Message": "Your email has been verified before"},
                            status=status.HTTP_200_OK)
        if cache.get(customer.email) == self.request.data['otp']:
            customer.is_email_verified = True
            customer.save()
            return Response({"Verified": customer.is_email_verified},
                            status=status.HTTP_202_ACCEPTED)
        return Response({"Error": "Wrong OTP or expired"},
                        status=status.HTTP_400_BAD_REQUEST)
