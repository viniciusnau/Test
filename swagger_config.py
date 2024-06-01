from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="work",
        default_version="v1",
        description="Hello world",
        terms_of_service="",
        contact=openapi.Contact(email="suporte@email.com"),
        license=openapi.License(name=""),
    ),
    public=True,
)
