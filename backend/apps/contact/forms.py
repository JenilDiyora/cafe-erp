import re
from django import forms
from .models import ContactInquiry


class ContactInquiryForm(forms.ModelForm):
    """Customer contact inquiry form with validation and styled widgets."""

    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name *',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email Address *',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number (Optional)'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'How can we help you? *',
                'required': 'required'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter a valid name (at least 2 characters).")
        return name

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 5:
            raise forms.ValidationError("Please provide a descriptive message (at least 5 characters).")
        return message

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            # Allow digits, spaces, plus, hyphens, parentheses
            if not re.match(r'^[+\d\s\-\(\)]{7,20}$', phone):
                raise forms.ValidationError("Please enter a valid phone number.")
        return phone

