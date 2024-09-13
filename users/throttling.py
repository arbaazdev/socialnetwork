from rest_framework.throttling import UserRateThrottle

class FriendRequestThrottle(UserRateThrottle):
    """
    Throttle class to limit the number of friend requests a user can send per minute.
    """
    scope = 'friend_requests'
