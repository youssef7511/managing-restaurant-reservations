from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Reservation, Payment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [
            'id', 'reservation_number', 'date', 'time', 'guests', 
            'zone', 'occasion', 'special_requests', 'status', 
            'is_paid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reservation_number', 'is_paid', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Add formatted zone value
        if instance.zone == 'vip':
            representation['zone_display'] = 'Zone VIP'
        elif instance.zone == 'familiale':
            representation['zone_display'] = 'Zone familiale'
        elif instance.zone == 'couple':
            representation['zone_display'] = 'Zone couple'
        
        # Add formatted occasion value if it exists
        if instance.occasion:
            if instance.occasion == 'birthday':
                representation['occasion_display'] = 'Anniversaire'
            elif instance.occasion == 'anniversary':
                representation['occasion_display'] = 'Anniversaire de mariage'
            elif instance.occasion == 'business':
                representation['occasion_display'] = 'Repas d\'affaires'
            elif instance.occasion == 'other':
                representation['occasion_display'] = 'Autre'
        
        # Add within_24_hours flag
        representation['within_24_hours'] = instance.is_within_24_hours()
        
        return representation


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'reservation', 'amount', 'payment_method', 
            'status', 'transaction_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Add formatted payment method
        if instance.payment_method == 'card':
            representation['payment_method_display'] = 'Carte de crédit'
        elif instance.payment_method == 'paypal':
            representation['payment_method_display'] = 'PayPal'
        elif instance.payment_method == 'onsite':
            representation['payment_method_display'] = 'Sur place'
        
        # Add formatted status
        if instance.status == 'pending':
            representation['status_display'] = 'En attente'
        elif instance.status == 'completed':
            representation['status_display'] = 'Complété'
        elif instance.status == 'failed':
            representation['status_display'] = 'Échoué'
        elif instance.status == 'refunded':
            representation['status_display'] = 'Remboursé'
        
        return representation