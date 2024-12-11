from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('object_detection/', include('object_detection.urls')),  # Маршруты из вашего приложения
]


