from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

from apps.core.models import CafeSetting, OpeningHour
from .forms import ContactInquiryForm


class ContactView(View):
    """Contact page handling inquiries and presenting contact/location info."""

    def get(self, request):
        cafe_settings = CafeSetting.objects.filter(is_active=True).first()
        opening_hours = OpeningHour.objects.filter(is_active=True).order_by('display_order', 'id')
        form = ContactInquiryForm()

        context = {
            'page_title': 'Contact & Location',
            'cafe_settings': cafe_settings,
            'opening_hours': opening_hours,
            'form': form,
            'request': request,
        }
        return render(request, 'contact/contact.html', context)

    def post(self, request):
        cafe_settings = CafeSetting.objects.filter(is_active=True).first()
        opening_hours = OpeningHour.objects.filter(is_active=True).order_by('display_order', 'id')
        form = ContactInquiryForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thank you! Your message has been received. Our team will get back to you shortly."
            )
            return redirect('contact:index')
        else:
            messages.error(
                request,
                "There was an error in your submission. Please check the fields below."
            )

        context = {
            'page_title': 'Contact & Location',
            'cafe_settings': cafe_settings,
            'opening_hours': opening_hours,
            'form': form,
            'request': request,
        }
        return render(request, 'contact/contact.html', context)

