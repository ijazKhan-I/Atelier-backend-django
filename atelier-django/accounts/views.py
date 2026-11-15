from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

UserModel = get_user_model()


def user_payload(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }


def jwt_for_user(user) -> str:
    return str(RefreshToken.for_user(user).access_token)


class LocalLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = (request.data.get("identifier") or "").strip()
        password = request.data.get("password") or ""

        if not identifier or not password:
            return Response(
                {"error": {"message": "Identifier and password are required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = None
        if "@" in identifier:
            try:
                matched = UserModel.objects.get(email__iexact=identifier)
                user = authenticate(username=matched.username, password=password)
            except UserModel.DoesNotExist:
                user = None
        if user is None:
            user = authenticate(username=identifier, password=password)

        if user is None:
            return Response(
                {"error": {"message": "Invalid identifier or password."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"jwt": jwt_for_user(user), "user": user_payload(user)})


class LocalRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password") or ""

        if not username or not email or not password:
            return Response(
                {"error": {"message": "Username, email and password are required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if UserModel.objects.filter(username__iexact=username).exists():
            return Response(
                {"error": {"message": "Username already taken."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if UserModel.objects.filter(email__iexact=email).exists():
            return Response(
                {"error": {"message": "Email already registered."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = UserModel.objects.create_user(username=username, email=email, password=password)
        return Response(
            {"jwt": jwt_for_user(user), "user": user_payload(user)},
            status=status.HTTP_201_CREATED,
        )
