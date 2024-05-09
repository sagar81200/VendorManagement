from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Vendor, PurchaseOrder
from .serializers import VendorSerializer, PurchaseOrderSerializer, VendorPerformanceSerializer

class VendorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class VendorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    
class VendorPerformanceAPIView(APIView):
    serializer_class = VendorPerformanceSerializer

    def get(self, request, vendor_id):
        try:
            vendor = Vendor.objects.prefetch_related('purchase_orders').get(id=vendor_id)
        except Vendor.DoesNotExist:
            return Response({"message": "Vendor does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(vendor)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AcknowledgePurchaseOrder(APIView):
    def post(self, request, po_id):
        try:
            purchase_order = PurchaseOrder.objects.get(pk=po_id)
        except PurchaseOrder.DoesNotExist:
            return Response({"message": "Purchase order does not exist"}, status=status.HTTP_404_NOT_FOUND)

        purchase_order.acknowledgment_date = timezone.now()
        purchase_order.save()

        return Response({"message": "Purchase order acknowledged successfully"}, status=status.HTTP_200_OK)

class PurchaseOrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class PurchaseOrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
