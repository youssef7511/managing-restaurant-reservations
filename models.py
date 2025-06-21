from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Reservation(models.Model):
    """
    Model for restaurant reservations
    """
    ZONE_CHOICES = [
        ('vip', 'Zone VIP'),
        ('familiale', 'Zone familiale'),
        ('couple', 'Zone couple'),
    ]
    
    OCCASION_CHOICES = [
        ('birthday', 'Anniversaire'),
        ('anniversary', 'Anniversaire de mariage'),
        ('business', 'Repas d\'affaires'),
        ('other', 'Autre'),
    ]
    
    TABLE_CHOICES = [
        ('T1', 'Table 1'),
        ('T2', 'Table 2'),
        ('T3', 'Table 3'),
        ('T4', 'Table 4'),
        ('T5', 'Table 5'),
        ('T6', 'Table 6'),
        ('T7', 'Table 7'),
        ('T8', 'Table 8'),
        ('T9', 'Table 9'),
        ('T10', 'Table 10'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
        ('completed', 'Terminée'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    reservation_number = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=100, default='')
    email = models.EmailField(default='')
    phone = models.CharField(max_length=20, default='')
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    number_of_guests = models.IntegerField(default=1)
    zone = models.CharField(max_length=20, choices=ZONE_CHOICES, default='familiale')
    occasion = models.CharField(max_length=20, choices=OCCASION_CHOICES, blank=True, null=True)
    special_requests = models.TextField(blank=True, null=True)
    table = models.CharField(max_length=10, choices=TABLE_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Réservation #{self.id} - {self.name} - {self.date}"
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    def get_zone_display(self):
        return dict(self.ZONE_CHOICES).get(self.zone, self.zone)
    
    def get_occasion_display(self):
        return dict(self.OCCASION_CHOICES).get(self.occasion, self.occasion) if self.occasion else None
    
    def get_table_display(self):
        return dict(self.TABLE_CHOICES).get(self.table, self.table) if self.table else None
    
    def save(self, *args, **kwargs):
        if not self.reservation_number:
            # Generate a unique reservation number
            last_reservation = Reservation.objects.order_by('-id').first()
            reservation_id = 1
            if last_reservation:
                reservation_id = last_reservation.id + 1
            self.reservation_number = f"RES-{reservation_id:05d}"
        super().save(*args, **kwargs)
    
    def is_within_24_hours(self):
        """
        Check if the reservation is within 24 hours
        """
        reservation_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        now = timezone.now()
        time_diff = reservation_datetime - now
        return time_diff.total_seconds() < 86400  # 24 hours in seconds


class Payment(models.Model):
    """
    Model for reservation payments
    """
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Carte de crédit'),
        ('paypal', 'PayPal'),
        ('onsite', 'Sur place'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment for reservation {self.reservation.reservation_number}"
# Create your models here.
