from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AnonRateThrottle(AnonRateThrottle):
    rate = "100/hour"


class UserRateThrottle(UserRateThrottle):
    rate = "1000/hour"


class OrgRateThrottle(UserRateThrottle):
    scope = "org"
    rate = "5000/hour"
