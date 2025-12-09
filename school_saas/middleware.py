from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import logout

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Agar user login nahi hai, ya Superuser hai, toh jaane do
        if not request.user.is_authenticated or request.user.is_superuser:
            return self.get_response(request)

        # 2. Agar user ke paas School nahi hai (e.g. naya staff), toh rok do
        if not request.user.school:
            return render(request, 'core/error.html', {'message': "No School Assigned. Contact Admin."})

        # 3. Expiry Date Check Karo
        # Aaj ki date
        today = timezone.now().date()
        school = request.user.school

        # Agar subscription date set hai aur aaj ki date usse badi hai (Expire ho gaya)
        if school.subscription_end_date and today > school.subscription_end_date:
            # Agar user pehle se 'expired' page par nahi hai, toh wahan bhejo
            if request.path != reverse('subscription_expired') and request.path != reverse('logout'):
                return redirect('subscription_expired')

        return self.get_response(request)