from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AdminRegisterForm, RequestMoneyForm, SendMoneyForm
from .models import Account, PaymentRequest, PaymentTransaction


def admin_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_superuser)(view_func))


@login_required
def send_money(request):
    message = None

    if request.method == 'POST':
        form = SendMoneyForm(request.POST)
        if form.is_valid():
            recipient_username = form.cleaned_data['recipient_username']
            amount = form.cleaned_data['amount']

            recipient = User.objects.filter(username=recipient_username).first()

            if recipient is None:
                message = "Recipient does not exist."
            elif recipient == request.user:
                message = "You cannot send money to yourself."
            elif amount <= 0:
                message = "Amount must be greater than zero."
            else:
                message = run_payment(request.user, recipient, amount)
    else:
        form = SendMoneyForm()

    return render(request, 'payapp/send_money.html', {'form': form, 'message': message})


def run_payment(sender_user, recipient_user, amount):
    try:
        with transaction.atomic():
            sender_account = Account.objects.select_for_update().get(user=sender_user)
            recipient_account = Account.objects.select_for_update().get(user=recipient_user)

            if sender_account.balance < amount:
                return "Insufficient funds."

            sender_account.balance -= amount
            recipient_account.balance += amount
            sender_account.save()
            recipient_account.save()

            PaymentTransaction.objects.create(
                sender=sender_user,
                recipient=recipient_user,
                amount=amount,
            )
            return "Payment successful."
    except Account.DoesNotExist:
        return "One of the accounts does not exist."


@login_required
def request_money(request):
    message = None

    if request.method == 'POST':
        form = RequestMoneyForm(request.POST)
        if form.is_valid():
            requested_from_username = form.cleaned_data['requested_from_username']
            amount = form.cleaned_data['amount']
            requested_from = User.objects.filter(username=requested_from_username).first()

            if requested_from is None:
                message = "Requested user does not exist."
            elif requested_from == request.user:
                message = "You cannot request money from yourself."
            elif amount <= 0:
                message = "Amount must be greater than zero."
            else:
                PaymentRequest.objects.create(
                    requester=request.user,
                    requested_from=requested_from,
                    amount=amount,
                    status='Pending',
                )
                message = "Payment request created successfully."
    else:
        form = RequestMoneyForm()

    return render(request, 'payapp/request_money.html', {'form': form, 'message': message})


@login_required
@require_POST
def pay_request(request, request_id):
    req = get_object_or_404(PaymentRequest, id=request_id, requested_from=request.user)

    if req.status != 'Pending':
        messages.info(request, "That request has already been handled.")
        return redirect('transaction_history')

    try:
        with transaction.atomic():
            payer_account = Account.objects.select_for_update().get(user=request.user)
            requester_account = Account.objects.select_for_update().get(user=req.requester)

            if payer_account.balance < req.amount:
                messages.error(request, "Insufficient funds to pay this request.")
                return redirect('transaction_history')

            payer_account.balance -= req.amount
            requester_account.balance += req.amount
            payer_account.save()
            requester_account.save()

            PaymentTransaction.objects.create(
                sender=request.user,
                recipient=req.requester,
                amount=req.amount,
            )

            req.status = 'Paid'
            req.save()
            messages.success(request, "Request paid successfully.")
    except Account.DoesNotExist:
        messages.error(request, "One of the accounts could not be found.")

    return redirect('transaction_history')


@login_required
@require_POST
def reject_request(request, request_id):
    req = get_object_or_404(PaymentRequest, id=request_id, requested_from=request.user)
    if req.status == 'Pending':
        req.status = 'Rejected'
        req.save()
        messages.info(request, "Request rejected.")
    return redirect('transaction_history')


@login_required
def transaction_history(request):
    return render(request, 'payapp/transaction_history.html', {
        'sent_transactions': PaymentTransaction.objects.filter(sender=request.user).order_by('-created_at'),
        'received_transactions': PaymentTransaction.objects.filter(recipient=request.user).order_by('-created_at'),
        'sent_requests': PaymentRequest.objects.filter(requester=request.user).order_by('-created_at'),
        'received_requests': PaymentRequest.objects.filter(requested_from=request.user).order_by('-created_at'),
    })


@admin_required
def admin_accounts(request):
    accounts = Account.objects.select_related('user').all().order_by('user__username')
    return render(request, 'payapp/admin_accounts.html', {'accounts': accounts})


@admin_required
def admin_transactions(request):
    transactions = PaymentTransaction.objects.select_related('sender', 'recipient').all().order_by('-created_at')
    return render(request, 'payapp/admin_transactions.html', {'transactions': transactions})


@admin_required
def admin_create_admin(request):
    message = None

    if request.method == 'POST':
        form = AdminRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            message = "New admin created successfully."
    else:
        form = AdminRegisterForm()

    return render(request, 'payapp/admin_create_admin.html', {'form': form, 'message': message})
