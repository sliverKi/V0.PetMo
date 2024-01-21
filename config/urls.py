
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="PetMo backend API",
        default_version="v2",
        description="https://github.com/sliverKi/PetMo",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],

)
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v2/users/",include("users.urls")),
    path("api/v2/pets/", include("pets.urls")),
    path("api/v2/posts/", include("posts.urls")),
    path("api/v2/categories/", include("categories.urls")),
    path("api/v2/auths/", include("auths.urls")),
    path("api/v2/bookmarks/", include("bookmarks.urls")),
    path("api/v2/likes/", include("likes.urls")),
    path("api/v2/images/", include("images.urls")),
    path("api/v2/address/", include("addresses.urls")),
    path("api/v2/search/", include("search.urls")),
    path(
        "swagger/", 
        schema_view.with_ui("swagger", cache_timeout=0), 
        name="schema-swagger-ui",
        ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
        ),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns +=[
        path('__debug__/', include(debug_toolbar.urls)),
    ]
