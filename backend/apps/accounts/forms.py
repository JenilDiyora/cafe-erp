"""Authentication and account forms with Bootstrap styling."""
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import CustomerProfile


class RegistrationForm(forms.ModelForm):
    """Customer registration form."""
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name', 'autocomplete': 'given-name'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name', 'autocomplete': 'family-name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com', 'autocomplete': 'email'})
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number', 'autocomplete': 'tel'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create strong password', 'autocomplete': 'new-password'}),
        min_length=6
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password', 'autocomplete': 'new-password'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip().replace(' ', '').replace('-', '')
        if not phone.isdigit() or len(phone) < 10:
            raise ValidationError("Please provide a valid 10-digit phone number.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class LoginForm(forms.Form):
    """Customer login form by email or username."""
    email_or_username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email address or username', 'autocomplete': 'username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Your password', 'autocomplete': 'current-password'})
    )


class OTPVerifyForm(forms.Form):
    """6-digit OTP verification form."""
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center fw-bold fs-3 letter-spacing-lg',
            'placeholder': '••••••',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'inputmode': 'numeric',
            'autocomplete': 'one-time-code',
            'autofocus': 'autofocus'
        })
    )

    def clean_otp_code(self):
        code = self.cleaned_data.get('otp_code', '').strip()
        if not code.isdigit() or len(code) != 6:
            raise ValidationError("Please enter a valid 6-digit number.")
        return code


class ForgotPasswordForm(forms.Form):
    """Form to initiate password reset via OTP."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Registered email address', 'autocomplete': 'email'})
    )


class ResetPasswordForm(forms.Form):
    """Form to complete password reset using OTP."""
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center fw-bold fs-4',
            'placeholder': '6-digit OTP',
            'maxlength': '6',
            'inputmode': 'numeric'
        })
    )
    new_password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New password', 'autocomplete': 'new-password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password', 'autocomplete': 'new-password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class CustomerProfileForm(forms.ModelForm):
    """Form to edit name and phone in customer profile."""
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

