from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Payment, Batch
from datetime import date

# Create your views here.


@login_required
def home(request):
    profile = UserProfile.objects.get(user=request.user)
    is_subscription_active = profile.is_subscription_active
    batch = profile.batch
    return render(
        request,
        "home.html",
        {
            "profile": profile,
            "is_subscription_active": is_subscription_active,
        },
    )


def payment(request):
    if (
        request.session.get("payment_stage")
        and request.session["payment_stage"] == "otp"
    ):
        return redirect("/payment/otp")
    if request.method == "POST":
        card_number = request.POST["card_number"]
        card_holder_name = request.POST["card_name"]
        card_expiry = request.POST["card_expiry"]
        card_cvv = request.POST["card_cvv"]
        batch = request.POST["batch"]
        batch = Batch.objects.get(id=batch)
        user = User.objects.get(username=request.user)
        payment = Payment(
            user=user,
            card_number=card_number,
            card_holder_name=card_holder_name,
            card_expiry=card_expiry,
            card_cvv=card_cvv,
            batch=batch,
        )
        payment.save()
        request.session["payment_id"] = payment.payment_id
        request.session["payment_stage"] = "otp"
        return redirect("/payment/otp")
    batches = Batch.objects.all()
    return render(request, "payment.html", {"batches": batches})


def otp(request):
    if request.method == "POST":
        otp = request.POST["otp"]
        if otp == "123456":
            payment_id = request.session["payment_id"]
            payment = Payment.objects.get(payment_id=payment_id)
            payment.is_completed = True
            payment.save()
            user = User.objects.get(username=request.user)
            profile = UserProfile.objects.get(user=user)
            profile.subscribe(batch=payment.batch)
            del request.session["payment_id"]
            del request.session["payment_stage"]
            messages.success(request, "Payment successful")
            return redirect("/")
        else:
            messages.error(request, "Invalid OTP")
            return redirect("/payment/otp")
    return render(request, "otp.html")


def login(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "You have successfully logged in")
            if request.GET.get("next"):
                return redirect(request.GET.get("next"))
            return redirect("/")
        else:
            messages.error(request, "Invalid username or password")
            return render(
                request,
                "login.html",
            )
    return render(request, "login.html")


@login_required
def logout(request):
    auth_logout(request)
    messages.success(request, "You have successfully logged out")
    return redirect("/")


def register(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        username = request.POST["username"]
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, "register.html")

        password = request.POST["password"]
        password2 = request.POST["password2"]
        if password != password2:
            messages.error(request, "Passwords do not match")
            return render(request, "register.html")

        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        phone = request.POST["phone"]
        date_of_birth = request.POST["date_of_birth"]
        # convert date_of_birth to date object
        date_of_birth = date_of_birth.split("-")
        date_of_birth = date(
            int(date_of_birth[0]), int(date_of_birth[1]), int(date_of_birth[2])
        )
        # calculate age
        today = date.today()
        age = (
            today.year
            - date_of_birth.year
            - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        )
        print(age)
        if age < 18 or age > 65:
            messages.error(request, "You must be in the age range of 18 to 65")
            return render(request, "register.html")

        user = User.objects.create_user(
            username, email, password, first_name=first_name, last_name=last_name
        )
        user.save()

        profile = UserProfile(
            user=user,
            phone=phone,
            date_of_birth=date_of_birth,
        )
        profile.save()
        messages.success(request, "You have successfully registered")
        return redirect("/accounts/login/")
    return render(request, "register.html")
