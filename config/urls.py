"""
URL configuration for CASE CLOSED project.
"""
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "CASE CLOSED — Detective Bureau Admin"
admin.site.site_title = "Bureau Admin Portal"
admin.site.index_title = "Case Management & Operative Oversight"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('investigations.urls')),
]
