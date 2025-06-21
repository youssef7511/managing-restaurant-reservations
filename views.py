from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import json
from .models import Reservation, Payment
from .serializers import ReservationSerializer, UserSerializer, PaymentSerializer

# Template views - serve the React/HTML templates
def index(request):
    return render(request, 'restaurant/index.html')

def login_page(request):
    if request.user.is_authenticated:
        return redirect('reservations')
    return render(request, 'restaurant/connexion.html')

@login_required(login_url='login_page')
def reservations_page(request):
    return render(request, 'restaurant/mes-reservations.html')

@login_required(login_url='login_page')
def reservation_detail_page(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    return render(request, 'restaurant/reservation-detail.html', {'reservation_id': reservation_id})

@login_required(login_url='login_page')
def payment_page(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    return render(request, 'restaurant/payement.html', {'reservation': reservation})

# Authentication API endpoints
@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('email')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                'status': 'success',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid credentials'
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def user_register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('email')
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Email already registered'
            }, status=400)
        
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        
        # Set first_name based on provided name
        if name:
            names = name.split(' ', 1)
            user.first_name = names[0]
            if len(names) > 1:
                user.last_name = names[1]
            user.save()
        
        # Log the user in
        login(request, user)
        
        return JsonResponse({
            'status': 'success',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.get_full_name()
            }
        })
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@login_required
def user_logout(request):
    logout(request)
    return JsonResponse({'status': 'success'})

# Reservation API endpoints
class ReservationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing reservations
    """
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        This view returns a list of all reservations for the currently authenticated user
        """
        user = self.request.user
        return Reservation.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt  # Only if you are handling CSRF manually (not recommended for production)
def create_reservation(request):
    if request.method == 'POST':
        # handle reservation creation logic here
        return JsonResponse({'status': 'success', 'redirect_url': '/reservations/'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
def reservation_detail(request, pk):
    """
    Retrieve, update or delete a reservation
    """
    try:
        reservation = Reservation.objects.get(pk=pk, user=request.user)
    except Reservation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ReservationSerializer(reservation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Payment API endpoints
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def payment_process(request, reservation_id):
    """
    Process payment for a specific reservation
    """
    try:
        reservation = Reservation.objects.get(pk=reservation_id, user=request.user)
    except Reservation.DoesNotExist:
        return Response({'status': 'error', 'message': 'Reservation not found'}, 
                        status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        # Return reservation details for payment
        serializer = ReservationSerializer(reservation)
        return Response({
            'reservation': serializer.data,
            'payment_required': True,  # This would be determined by your business logic
            'amount': 50.00  # This would be calculated based on reservation details
        })
    
    elif request.method == 'POST':
        # Process payment
        payment_data = {
            'reservation': reservation.id,
            'amount': request.data.get('amount', 50.00),
            'payment_method': request.data.get('payment_method', 'card'),
            'status': 'completed'
        }
        
        serializer = PaymentSerializer(data=payment_data)
        if serializer.is_valid():
            payment = serializer.save(user=request.user)
            
            # Update reservation payment status
            reservation.is_paid = True
            reservation.save()
            
            return Response({
                'status': 'success',
                'message': 'Payment processed successfully',
                'payment': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Create your views here.
