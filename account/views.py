from decouple import config
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites import requests
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular import openapi
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from account.models import Social
from account.serializer import UserSerializer
from drf.pagination import CustomPagination
from wristcheck_api.constants import DEFAULT_PAGE_SIZE, DEFAULT_MAX_PAGE_SIZE
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
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['username', 'email', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email']
    ordering_fields = ['date_joined', 'last_login']
    ordering = ['-last_login']

    from drf_spectacular.utils import extend_schema, OpenApiParameter
    from rest_framework.filters import OrderingFilter

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                description='Which field to use when ordering the results.',
                enum=['date_joined', 'last_login'],
                required=False
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                description=f'Number of results to return per page. Maximum value is {DEFAULT_MAX_PAGE_SIZE}.',
                required=False,
                default=DEFAULT_PAGE_SIZE,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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

        social = Social.objects.filter(open_id=open_id).first()
        if not social:
            user = User.objects.create(username=wechat_data.get('nickname', ''))
            Social.objects.create(open_id=open_id, defaults={
                'user': user,
                'open_id': open_id,
                'nickname': wechat_data.get('nickname', ''),
                'avatar_url': wechat_data.get('avatar_url', '')
            })
        else:
            user = social.user

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