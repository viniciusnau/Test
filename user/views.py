import json
import os

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Person, Task
from .serializers import PersonSerializer, TaskSerializer
from .services import GoogleRawLoginFlowService, create_user, handle_person_serializer


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
            if not person_data:
                return JsonResponse(
                    {"error": "Missing person data"}, status=status.HTTP_400_BAD_REQUEST
                )

            user = create_user(person_data)
            return handle_person_serializer(user, person_data)

        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST
            )
        except KeyError as e:
            return JsonResponse(
                {"error": f"Missing key: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse(
        {"message": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST
    )


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        person = get_object_or_404(Person, user=self.request.user)
        if obj.person != person:
            raise PermissionDenied("You do not have permission to perform this action.")
        return obj

    def perform_update(self, serializer):
        person = get_object_or_404(Person, user=self.request.user)
        if serializer.instance.person != person:
            raise PermissionDenied("You do not have permission to perform this action.")
        serializer.save()

    def perform_destroy(self, instance):
        person = get_object_or_404(Person, user=self.request.user)
        if instance.person != person:
            raise PermissionDenied("You do not have permission to perform this action.")
        instance.delete()


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["title", "due_date", "is_completed"]
    search_fields = ["title"]
    ordering_fields = ["due_date"]

    def get_queryset(self):
        person = get_object_or_404(Person, user=self.request.user)
        return Task.objects.filter(person=person)

    def perform_create(self, serializer):
        person = get_object_or_404(Person, user=self.request.user)
        serializer.save(person=person)


class MeView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PersonSerializer
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        person = get_object_or_404(Person, user=self.request.user)
        person_serializer = self.serializer_class(person)
        tasks = Task.objects.filter(person=person).order_by("-created_at")

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(tasks, request)
        tasks_serializer = TaskSerializer(result_page, many=True)

        data = {
            "me": person_serializer.data,
            "tasks": tasks_serializer.data,
        }

        return paginator.get_paginated_response(data)
