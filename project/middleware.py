from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.utils import timezone
from datetime import  timedelta

from payments.models import FreeTrial


def check_redirect(request):
    if any(i in request.path for i in ['payme', 'register', 'logout', 'login',]):
        pass
    else:
        return redirect('payme')

class MyRedirectMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):    
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            if hasattr(request.user, 'company'):
                company = request.user.company
                free_trial_days = FreeTrial.objects.last().days
                if not company.payment_expire_date:                
                    if company.created_at + timedelta(days=free_trial_days) < timezone.localtime(timezone.now()): 
                        return check_redirect(request)
                else:
                    if company.created_at + timedelta(days=free_trial_days) < timezone.localtime(timezone.now()) and company.payment_expire_date  < timezone.localtime(timezone.now()): 
                        return check_redirect(request)
                    elif company.payment_expire_date  <= timezone.localtime(timezone.now()):
                        return check_redirect(request)
                