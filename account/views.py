from decouple import config
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites import requests
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from account.serializer import UserSerializer
from wristcheck_api.permission import GetPermissionByModelActionMixin, IsOwnerOrAdminUser


class UserViewSet(GetPermissionByModelActionMixin, viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (
        SessionAuthentication,
        TokenAuthentication
    )
    permission_classes = [IsAuthenticated]
    permission_classes_map = {
        'list': [IsAdminUser],
        'retrieve': [IsOwnerOrAdminUser],
        'profile': [IsAuthenticated]
    }

    @action(methods=['POST'], detail=False)
    def login(self, request, *args, **kwargs):
        """Login with username and password and return a token

        :param request: { "username": "admin", "password": "admin" }
        :return: {"token": "token string"}
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['POST'], detail=False)
    def wechat_mini_login(self, request, *args, **kwargs):
        """wechat mini login

        :param request: { "code": "code" }
        :return: {"token": "token string"}
        """
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)
        wechat_data = requests.get(
            config('WECHAT_MINI_GET_SESSION_KEY_URL'),
            {
                "appid": config('WECHAT_MINI_APPID'),
                "secret": config('WECHAT_MINI_SECRET'),
                "js_code": code,
                "grant_type": "authorization_code",
            },
        ).json()
        open_id = wechat_data.get('openid')
        if not open_id:
            return Response({'error': 'WeChat authentication failed'}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(open_id=open_id, defaults={
            'open_id': open_id,
            'nickname': wechat_data.get('nickname', ''),
            'avatar_url': wechat_data.get('avatar_url', '')
        })

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

    @action(methods=['GET'], detail=False)
    def profile(self, request):
        """Get user profile when authenticated

        :param request:
        :return: json, example: {"id": 1, "username": "admin"}
        """
        instance = User.objects.filter(id=request.user.id).first()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)