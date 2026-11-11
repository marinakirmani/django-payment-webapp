from django.urls import path, include

urlpatterns = [
    path('webapps2026/', include('register.urls')),
    path('webapps2026/payapp/', include('payapp.urls')),
    path('webapps2026/conversion/', include('conversion.urls')),
]
