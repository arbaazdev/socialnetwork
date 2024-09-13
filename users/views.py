from django.db.models import Q

from rest_framework.authtoken.models import Token
from rest_framework import views, viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .throttling import FriendRequestThrottle

from .models import User, FriendRequest
from .serializers import UserSignupSerializer, UserLoginSerializer, UserSerializer, FriendRequestSerializer


class SignupView(views.APIView):
    """
    API View for user signup. Creates a new user and returns the authentication token.
    
    Permissions:
        - AllowAny: Allows access to unauthenticated users.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handles POST request for user signup.

        Args:
            request (Request): The request object containing user signup data.

        Returns:
            Response: Contains the user data and token if signup is successful.
        """
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    """
    API View for user login. Authenticates the user and returns the authentication token.

    Permissions:
        - AllowAny: Allows access to unauthenticated users.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handles POST request for user login.

        Args:
            request (Request): The request object containing login credentials.

        Returns:
            Response: Contains the user data and token if login is successful.
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSearchViewSet(viewsets.ModelViewSet):
    """
    Viewset for searching users by name or email. Provides list, retrieve, and search actions.

    Permissions:
        - IsAuthenticated: Only authenticated users can access these views.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for users by name or email. Supports pagination.

        Args:
            request (Request): The request object containing the query parameter `q`.

        Returns:
            Response: Paginated response with matched users.
        """
        query = request.query_params.get('q', '')
        if '@' in query:
            users = User.objects.filter(email__iexact=query)
        else:
            users = User.objects.filter(name__icontains=query)

        page = self.paginate_queryset(users)
        if page is not None:
            return self.get_paginated_response(UserSerializer(page, many=True).data)

        return Response(UserSerializer(users, many=True).data)


class FriendRequestViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing friend requests. Allows sending, accepting, rejecting friend requests,
    and listing pending and accepted friends.

    Permissions:
        - IsAuthenticated: Only authenticated users can access these views.
    """

    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        """
        Return throttles based on the action.
        """
        if self.action == 'create':  # Only apply throttle for sending requests
            return [FriendRequestThrottle()]
        return []  # No throttle for other actions


    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        List all pending friend requests received by the authenticated user.

        Args:
            request (Request): The request object.

        Returns:
            Response: List of pending friend requests.
        """
        pending_requests = FriendRequest.objects.filter(to_user=request.user, status=FriendRequest.Status.PENDING)
        return Response(FriendRequestSerializer(pending_requests, many=True).data)

    @action(detail=False, methods=['get'])
    def accepted(self, request):
        """
        List all accepted friends of the authenticated user.

        Args:
            request (Request): The request object.

        Returns:
            Response: List of accepted friends.
        """

        user = request.user

        # Fetch all accepted friend requests related to the user
        sent_requests = FriendRequest.objects.filter(
            from_user=user, status=FriendRequest.Status.ACCEPTED
        ).select_related('to_user')  # Use select_related for efficient lookup

        received_requests = FriendRequest.objects.filter(
            to_user=user, status=FriendRequest.Status.ACCEPTED
        ).select_related('from_user')  # Use select_related for efficient lookup

        # Collect user IDs from the friend requests
        sent_friends_ids = sent_requests.values_list('to_user_id', flat=True)
        received_friends_ids = received_requests.values_list('from_user_id', flat=True)

        # Combine the user IDs and remove duplicates
        friend_ids = set(sent_friends_ids) | set(received_friends_ids)

        # Fetch the users in one query
        friends = User.objects.filter(id__in=friend_ids).distinct()

        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data)
