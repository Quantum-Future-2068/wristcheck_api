from django.contrib.auth import authenticate
from django.contrib.auth.models import User
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
    }

    @action(methods=['POST'], detail=False, url_path='login', url_name='login')
    def login(self, request, *args, **kwargs):
        """Login with username and password and return a token

        :param request: { "username": "admin", "password": "admin" }
        :param args:
        :param kwargs:
        :return: {"token": "token"}
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
