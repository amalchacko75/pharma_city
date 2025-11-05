from django.urls import path

from billing.views import InvoiceDrugExtractView

urlpatterns = [
    path('upload/', InvoiceDrugExtractView.as_view(), name='bill-upload'),
]
