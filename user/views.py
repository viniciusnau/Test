import os
import random
import string

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework import filters, generics, serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Person
from .serializers import (
    PersonSerializer
)
from .services import GoogleRawLoginFlowService


class PublicApi(APIView):
    authentication_classes = ()
    permission_classes = ()


class GoogleLoginRedirectApi(PublicApi):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleRawLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state

        return redirect(authorization_url)


class GoogleLoginApi(PublicApi):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)
        state = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get("code")
        error = validated_data.get("error")
        state = validated_data.get("state")

        if error is not None:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        if code is None or state is None:
            return Response(
                {"error": "Code and state are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session_state = request.session.get("google_oauth2_state")

        if session_state is None:
            return Response(
                {"error": "CSRF check failed."}, status=status.HTTP_400_BAD_REQUEST
            )

        del request.session["google_oauth2_state"]

        if state != session_state:
            return Response(
                {"error": "CSRF check failed."}, status=status.HTTP_400_BAD_REQUEST
            )

        google_login_flow = GoogleRawLoginFlowService()

        google_tokens = google_login_flow.get_tokens(code=code)

        id_token_decoded = google_tokens.decode_id_token()

        user_email = id_token_decoded["email"]
        user = User.objects.get(email=user_email)
        token, created = Token.objects.get_or_create(user=user)
        api_token = token.key

        if user is None:
            return Response(
                {"error": f"User with email {user_email} is not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        login(request, user)
        url = f"{os.environ.get('GOOGLE_REDIRECT_URL')}{api_token}"

        return redirect(url)


class PersonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsAdminUser]


class PersonListCreateView(generics.ListCreateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsAdminUser]


@csrf_exempt
def register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            person_data = data.get("person")
            password = person_data["password"]
            user = User.objects.create(
                username=person_data["email"],
                email=person_data["email"],
                first_name=person_data["first_name"],
                last_name=person_data["last_name"],
                is_superuser=False,
                is_active=True,
                is_staff=False,
            )
            user.set_password(password)
            user.save()

            if user:
                person_data["user"] = user.id
                person_serializer = PersonSerializer(data=person_data)

                if person_serializer.is_valid():
                    person_serializer.save()

                    return JsonResponse(
                        person_serializer.data, status=status.HTTP_201_CREATED
                    )
                else:
                    user.delete()
                    return JsonResponse(
                        person_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return JsonResponse(
                    {"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({"message": "Invalid request."}, status=400)
