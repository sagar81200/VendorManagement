from django.db import models
from django.db.models import Count, Avg, ExpressionWrapper, F, DurationField
from datetime import timezone
from django.db.models import Avg, ExpressionWrapper, F, Sum, DurationField
from django.db.models.functions import ExtractSecond

class Vendor(models.Model):
    name = models.CharField(max_length=100)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=20, unique=True)
    on_time_delivery_rate = models.FloatField(default=0)
    quality_rating_avg = models.FloatField(default=0)
    average_response_time = models.FloatField(default=0)
    fulfillment_rate = models.FloatField(default=0)
    
    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=20, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='purchase_orders')
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, default='pending')
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.calculate_performance_metrics()

    def calculate_performance_metrics(self):
        # On-Time Delivery Rate
        if self.status == 'completed':
            completed_orders_count = PurchaseOrder.objects.filter(vendor=self.vendor, status='completed').count()
            on_time_delivered_count = PurchaseOrder.objects.filter(vendor=self.vendor, status='completed', delivery_date__lte=timezone.now()).count()
            self.vendor.on_time_delivery_rate = on_time_delivered_count / completed_orders_count if completed_orders_count != 0 else 0

        # Quality Rating Average
        completed_orders = PurchaseOrder.objects.filter(vendor=self.vendor, status='completed', quality_rating__isnull=False)
        self.vendor.quality_rating_avg = completed_orders.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0

        # Average Response Time
        if self.acknowledgment_date:
            response_times = PurchaseOrder.objects.filter(vendor=self.vendor, acknowledgment_date__isnull=False).annotate(response_time=ExpressionWrapper(F('acknowledgment_date') - F('issue_date'), output_field=DurationField()))
            total_response_count = response_times.count()

            # Calculate total response time in seconds
            total_response_time_seconds = sum(response_time.total_seconds() for response_time in response_times.values_list('response_time', flat=True))

            # Calculate average response time in seconds
            average_response_time_seconds = total_response_time_seconds / total_response_count if total_response_count != 0 else 0
            self.vendor.average_response_time = average_response_time_seconds

        # Fulfilment Rate
        fulfilled_orders_count = PurchaseOrder.objects.filter(vendor=self.vendor, status='completed').count()
        total_orders_count = PurchaseOrder.objects.filter(vendor=self.vendor).count()
        self.vendor.fulfillment_rate = fulfilled_orders_count / total_orders_count if total_orders_count != 0 else 0

        self.vendor.save()

class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()
