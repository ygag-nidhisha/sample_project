import json

from django.contrib.auth.models import User
from oauth2_provider.views.mixins import OAuthLibMixin
from oauth2_provider.contrib.rest_framework.permissions import TokenHasScope
from rest_framework import generics, views, status
from rest_framework.response import Response


from .serializers import UserSerializer

class UserView(generics.ListAPIView):
    permission_classes = [TokenHasScope]
    required_scopes = ['read']
    queryset=User.objects.all()
    serializer_class = UserSerializer


class UserToken(OAuthLibMixin, views.APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        _, _, body, status_code = self.create_token_response(request)
        return Response(json.loads(body) if body  else body, status=status_code)


class UserRevokeToken(OAuthLibMixin, views.APIView):
    def post(self, request, *args, **kwargs):
        _, _, body, status_code = self.create_revocation_response(request)
        return Response(json.loads(body) if body else {"message": "Logout Successful"} if status_code==status.HTTP_200_OK else {"error": "Some error occured"}, status=status_code)
