from django.urls import path

from users.views import UserView, UserToken, UserRevokeToken


urlpatterns = [
    path("token/", UserToken.as_view(), name="token"),
    path("logout/", UserRevokeToken.as_view(), name="revoke-token"),
    path("", UserView.as_view(), name="user")
]