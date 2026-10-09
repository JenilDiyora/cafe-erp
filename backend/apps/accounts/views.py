"""Customer accounts, registration, OTP verification, and profile views."""
from datetime import timedelta
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.conf import settings

from apps.notifications.emails import send_otp_email
from .models import CustomerProfile, EmailOTP
from .forms import (
    RegistrationForm,
    LoginForm,
    OTPVerifyForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    CustomerProfileForm
)


class RegisterView(View):
    """Customer registration and OTP generation view."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        form = RegistrationForm()
        return render(request, 'accounts/register.html', {
            'form': form,
            'page_title': 'Create Customer Account',
            'next_url': request.GET.get('next', ''),
        })

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')

        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password'])
            user.is_active = False  # Inactive until email OTP is verified
            user.save()

            # Create CustomerProfile
            CustomerProfile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                is_email_verified=False
            )

            # Generate and dispatch 6-digit OTP
            otp_obj = EmailOTP.generate_otp(email=user.email, user=user, purpose='REGISTER')
            send_otp_email(to_email=user.email, otp_code=otp_obj.otp_code, purpose="Account Verification")

            # Store in session for verification step
            request.session['pending_user_id'] = user.id
            request.session['pending_email'] = user.email
            request.session['otp_last_sent'] = timezone.now().isoformat()
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                request.session['auth_next_url'] = next_url

            messages.success(
                request,
                f"We sent a 6-digit verification code to {user.email}. Please enter it below to activate your account."
            )
            if settings.DEBUG and not getattr(settings, 'EMAIL_HOST_PASSWORD', ''):
                messages.info(
                    request,
                    f"🔑 [Dev Mode] Gmail App Password not yet configured in .env. Your OTP code is: {otp_obj.otp_code}"
                )
            return redirect('accounts:verify_otp')

        return render(request, 'accounts/register.html', {
            'form': form,
            'page_title': 'Create Customer Account',
            'next_url': request.POST.get('next', ''),
        })


class VerifyOTPView(View):
    """Verify 6-digit OTP to activate customer account."""

    def get(self, request):
        email = request.session.get('pending_email')
        if not email:
            messages.warning(request, "No pending verification session found. Please register or log in.")
            return redirect('accounts:register')

        form = OTPVerifyForm()
        return render(request, 'accounts/verify_otp.html', {
            'form': form,
            'email': email,
            'page_title': 'Verify Your Email OTP',
        })

    def post(self, request):
        email = request.session.get('pending_email')
        user_id = request.session.get('pending_user_id')
        if not email or not user_id:
            messages.error(request, "Session expired. Please register again.")
            return redirect('accounts:register')

        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['otp_code']

            # Find latest un-used OTP for this email
            otp_record = EmailOTP.objects.filter(
                email=email,
                purpose='REGISTER',
                is_used=False
            ).order_by('-created_at').first()

            if not otp_record or not otp_record.is_valid():
                messages.error(request, "OTP has expired or exceeded maximum attempts. Please request a new code.")
                return redirect('accounts:verify_otp')

            if otp_record.otp_code != entered_code:
                otp_record.attempts += 1
                otp_record.save(update_fields=['attempts'])
                remaining = max(0, 5 - otp_record.attempts)
                messages.error(request, f"Incorrect OTP code. {remaining} attempt(s) remaining.")
                return render(request, 'accounts/verify_otp.html', {'form': form, 'email': email})

            # Valid OTP!
            otp_record.is_used = True
            otp_record.save(update_fields=['is_used'])

            # Activate User
            try:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save(update_fields=['is_active'])

                profile, _ = CustomerProfile.objects.get_or_create(user=user)
                profile.is_email_verified = True
                profile.save(update_fields=['is_email_verified'])

                # Log the user in
                auth_login(request, user)

                # Clear pending session keys
                request.session.pop('pending_user_id', None)
                request.session.pop('pending_email', None)

                # Migrate guest cart if exists
                try:
                    from apps.cart.models import Cart
                    Cart.merge_guest_cart(request, user)
                except Exception:
                    pass

                messages.success(request, f"Welcome to Mitra Cafe, {user.first_name or user.username}! Your account is activated.")

                # Table context or next redirect
                next_url = request.session.pop('auth_next_url', None)
                if request.session.get('table_token'):
                    table_num = request.session.get('table_number', '')
                    messages.info(request, f"🪑 Dine-in session active at Table {table_num}.")
                    return redirect('menu:list')

                return redirect(next_url if next_url else 'core:home')
            except User.DoesNotExist:
                messages.error(request, "User account not found.")
                return redirect('accounts:register')

        return render(request, 'accounts/verify_otp.html', {'form': form, 'email': email})


class ResendOTPView(View):
    """Resend a new 6-digit OTP with 60-second cooldown."""

    def post(self, request):
        email = request.session.get('pending_email')
        user_id = request.session.get('pending_user_id')
        if not email or not user_id:
            messages.error(request, "Session expired. Please register again.")
            return redirect('accounts:register')

        last_sent_str = request.session.get('otp_last_sent')
        if last_sent_str:
            try:
                last_sent = timezone.datetime.fromisoformat(last_sent_str)
                if timezone.now() - last_sent < timedelta(seconds=60):
                    wait_seconds = 60 - int((timezone.now() - last_sent).total_seconds())
                    messages.warning(request, f"Please wait {wait_seconds} seconds before requesting a new OTP.")
                    return redirect('accounts:verify_otp')
            except Exception:
                pass

        try:
            user = User.objects.get(id=user_id)
            otp_obj = EmailOTP.generate_otp(email=email, user=user, purpose='REGISTER')
            send_otp_email(to_email=email, otp_code=otp_obj.otp_code, purpose="Account Verification")
            request.session['otp_last_sent'] = timezone.now().isoformat()
            messages.success(request, f"A new OTP has been sent to {email}.")
            if settings.DEBUG and not getattr(settings, 'EMAIL_HOST_PASSWORD', ''):
                messages.info(
                    request,
                    f"🔑 [Dev Mode] Your new OTP verification code is: {otp_obj.otp_code}"
                )
        except User.DoesNotExist:
            messages.error(request, "User account not found.")

        return redirect('accounts:verify_otp')


class LoginView(View):
    """Customer login view with table and redirect preservation."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        form = LoginForm()
        return render(request, 'accounts/login.html', {
            'form': form,
            'page_title': 'Customer Login',
            'next_url': request.GET.get('next', ''),
        })

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')

        form = LoginForm(request.POST)
        if form.is_valid():
            email_or_user = form.cleaned_data['email_or_username'].strip()
            password = form.cleaned_data['password']

            # Find user by email or username
            user_obj = User.objects.filter(email__iexact=email_or_user).first()
            if not user_obj:
                user_obj = User.objects.filter(username__iexact=email_or_user).first()

            if user_obj:
                # If account is not active, prompt OTP verification
                if not user_obj.is_active:
                    otp_obj = EmailOTP.generate_otp(email=user_obj.email, user=user_obj, purpose='REGISTER')
                    send_otp_email(to_email=user_obj.email, otp_code=otp_obj.otp_code, purpose="Account Activation")
                    request.session['pending_user_id'] = user_obj.id
                    request.session['pending_email'] = user_obj.email
                    request.session['otp_last_sent'] = timezone.now().isoformat()
                    messages.warning(request, "Your account is not verified yet. We sent a new OTP to your email.")
                    if settings.DEBUG and not getattr(settings, 'EMAIL_HOST_PASSWORD', ''):
                        messages.info(
                            request,
                            f"🔑 [Dev Mode] Gmail App Password not yet configured in .env. Your OTP code is: {otp_obj.otp_code}"
                        )
                    return redirect('accounts:verify_otp')

                # Authenticate
                user = authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    auth_login(request, user)

                    # Merge guest cart to authenticated user
                    try:
                        from apps.cart.models import Cart
                        Cart.merge_guest_cart(request, user)
                    except Exception:
                        pass

                    messages.success(request, f"Welcome back, {user.first_name or user.username}!")

                    next_url = request.POST.get('next') or request.GET.get('next')
                    if request.session.get('table_token'):
                        table_num = request.session.get('table_number', '')
                        messages.info(request, f"🪑 Dine-in active at Table {table_num}.")
                        if not next_url:
                            return redirect('menu:list')

                    return redirect(next_url if next_url else 'core:home')

            messages.error(request, "Invalid email/username or password. Please try again.")

        return render(request, 'accounts/login.html', {
            'form': form,
            'page_title': 'Customer Login',
            'next_url': request.POST.get('next', ''),
        })


class LogoutView(View):
    """Customer logout view."""

    def get(self, request):
        auth_logout(request)
        messages.info(request, "You have been logged out. See you again soon!")
        return redirect('core:home')

    def post(self, request):
        auth_logout(request)
        messages.info(request, "You have been logged out. See you again soon!")
        return redirect('core:home')


class ForgotPasswordView(View):
    """Initiate password reset via 6-digit OTP."""

    def get(self, request):
        form = ForgotPasswordForm()
        return render(request, 'accounts/forgot_password.html', {'form': form, 'page_title': 'Forgot Password'})

    def post(self, request):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            user = User.objects.filter(email__iexact=email).first()
            if user:
                otp_obj = EmailOTP.generate_otp(email=email, user=user, purpose='RESET_PASSWORD')
                send_otp_email(to_email=email, otp_code=otp_obj.otp_code, purpose="Password Reset")
                request.session['reset_email'] = email
                messages.success(request, f"A 6-digit reset code has been sent to {email}.")
                if settings.DEBUG and not getattr(settings, 'EMAIL_HOST_PASSWORD', ''):
                    messages.info(
                        request,
                        f"🔑 [Dev Mode] Gmail App Password not yet configured in .env. Your password reset OTP is: {otp_obj.otp_code}"
                    )
                return redirect('accounts:reset_password')
            else:
                messages.error(request, "No account was found with that email address.")

        return render(request, 'accounts/forgot_password.html', {'form': form, 'page_title': 'Forgot Password'})


class ResetPasswordView(View):
    """Complete password reset using OTP."""

    def get(self, request):
        email = request.session.get('reset_email')
        if not email:
            messages.warning(request, "Please enter your email to request a reset code.")
            return redirect('accounts:forgot_password')
        form = ResetPasswordForm()
        return render(request, 'accounts/reset_password.html', {'form': form, 'email': email, 'page_title': 'Reset Password'})

    def post(self, request):
        email = request.session.get('reset_email')
        if not email:
            messages.error(request, "Session expired. Please request password reset again.")
            return redirect('accounts:forgot_password')

        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            new_password = form.cleaned_data['new_password']

            otp_record = EmailOTP.objects.filter(
                email=email,
                purpose='RESET_PASSWORD',
                is_used=False
            ).order_by('-created_at').first()

            if not otp_record or not otp_record.is_valid():
                messages.error(request, "Reset code is invalid or has expired.")
                return redirect('accounts:forgot_password')

            if otp_record.otp_code != otp_code:
                otp_record.attempts += 1
                otp_record.save(update_fields=['attempts'])
                messages.error(request, "Incorrect OTP code. Please check your email.")
                return render(request, 'accounts/reset_password.html', {'form': form, 'email': email})

            # Valid OTP: reset password
            otp_record.is_used = True
            otp_record.save(update_fields=['is_used'])

            user = User.objects.filter(email__iexact=email).first()
            if user:
                user.set_password(new_password)
                user.is_active = True
                user.save()
                request.session.pop('reset_email', None)
                messages.success(request, "Your password has been reset successfully! Please log in.")
                return redirect('accounts:login')

        return render(request, 'accounts/reset_password.html', {'form': form, 'email': email, 'page_title': 'Reset Password'})


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    """Customer Profile view showing stats, details, and allowing updates."""

    def get(self, request):
        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
        form = CustomerProfileForm(instance=request.user, initial={'phone': profile.phone})

        # Fetch recent customer orders & reservations
        recent_orders = request.user.orders.all().order_by('-created_at')[:5] if hasattr(request.user, 'orders') else []
        recent_reservations = request.user.reservations.all().order_by('-created_at')[:5] if hasattr(request.user, 'reservations') else []

        context = {
            'form': form,
            'profile': profile,
            'recent_orders': recent_orders,
            'recent_reservations': recent_reservations,
            'page_title': 'My Customer Profile',
        }
        return render(request, 'accounts/profile.html', context)

    def post(self, request):
        profile, _ = CustomerProfile.objects.get_or_create(user=request.user)
        form = CustomerProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            profile.phone = form.cleaned_data['phone']
            profile.save(update_fields=['phone'])
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')

        context = {
            'form': form,
            'profile': profile,
            'page_title': 'My Customer Profile',
        }
        return render(request, 'accounts/profile.html', context)

