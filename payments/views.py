from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from django.utils import  timezone
from django.contrib import messages

from app.models import Company
from .forms import PaymeCardForm, PaymeVerifyForm
from .payme_utils import Payme
from .models import PaymentAmount, PaymeToken

@login_required
def payme(request):

    need_to_pay = None
    amount = PaymentAmount.objects.last().amount
    if request.user.company.payment_expire_date:
        initial = True
        if request.user.company.payment_expire_date <= timezone.localtime(timezone.now()):
            need_to_pay = True
        else:
            need_to_pay = False
    else:
        initial = False
    
    form = PaymeCardForm()
    if request.method == 'POST':
        form = PaymeCardForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            card_number, expire = cleaned_data['card_number'], cleaned_data['expire']
            payme = Payme()

            response = payme.create_cards(card_number,
                                        expire=expire,
                                        save=False)
            try:
                token = response['result']['card']['token']
            except:
                return HttpResponse(f'Error: {response}')
            res = payme.cards_get_verify_code(token)
            print(res)
            PaymeToken.objects.filter(company=request.user.company).delete()
            token = PaymeToken.objects.create(company=request.user.company, token=token)
            messages.success(request, f'Tasdiqlash kodi {res["result"]["phone"]}ga yuborildi')
            return redirect('payme_verify')
        
    context = {'form': form, "need_to_pay": need_to_pay, "amount": amount, "initial": initial}
    return render(request, 'backoffice/pages/payments/index.html', context)


@login_required
def payme_verify(request):
    if request.user.company.payment_expire_date:
        if request.user.company.payment_expire_date <= timezone.localtime(timezone.now()):
            need_to_pay = True
        else:
            need_to_pay = False
    else:
        need_to_pay = True
    
    form = PaymeVerifyForm()
    if request.method == 'POST':
        form = PaymeVerifyForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            code = cleaned_data['code']
            payme = Payme()
            token = PaymeToken.objects.filter(company=request.user.company).last()
            if not token:
                messages.warning(request, 'Sizga sms jo\'natilmagan!')
                return redirect('payme_verify')
            token = token.token
            verify = payme.cards_verify(code=str(code), token=token)

            if "error" in verify:
                return render(request, 'backoffice/pages/payments/payme_verify.html', {"error": verify, "need_to_pay": need_to_pay, "form": form})

            token = verify['result']['card']['token']
            amount = PaymentAmount.objects.last().amount
            result = payme.create_transaction(
                token, request.user.id, amount * 100)
            if "error" in result:
                return render(request, 'backoffice/pages/payments/payme_verify.html', {"error": result["error"], "need_to_pay": need_to_pay, "form": form})
            
            company: Company = request.user.company
            company.payment_expire_date = timezone.localtime(timezone.now()) + timezone.timedelta(days=365)
            company.save()
            PaymeToken.objects.all().delete()
            messages.success(request, 'To\'lov muvaffaqiyatli amalga oshirildi!')
            return redirect('payme')

    context = {'form': form, "need_to_pay": need_to_pay}
    return render(request, 'backoffice/pages/payments/payme_verify.html', context)