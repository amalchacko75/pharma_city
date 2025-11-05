from billing.serializer import InvoiceExtractSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class InvoiceDrugExtractView(APIView):
    """
    POST /api/invoice/extract-drugs/
    Upload an invoice and return matched/unmatched drug names.
    """

    def post(self, request):
        serializer = InvoiceExtractSerializer(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
