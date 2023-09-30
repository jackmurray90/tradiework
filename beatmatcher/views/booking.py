from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.urls import reverse
from beatmatcher.models import Booking
from beatmatcher.translations import tr
from beatmatcher.util import random_128_bit_string
from datetime import datetime


class NewBookingView(View):
    def get(self, request, lang, dj_username):
        if lang not in tr:
            raise Http404

        # Ensure DJ profile exists
        user = User.objects.filter(username=dj_username).first()
        if not user:
            raise Http404
        try:
            dj = user.dj
        except User.dj.RelatedObjectDoesNotExist:
            raise Http404

        # Instantiate a booking with no parameters.
        booking = Booking()

        # Render the form
        return render(
            request, "new-booking.html", {"tr": tr[lang], "dj": dj, "booking": booking}
        )

    def post(self, request, lang, dj_username):
        if lang not in tr:
            raise Http404

        # Ensure DJ profile exists
        user = User.objects.filter(username=dj_username).first()
        if not user:
            raise Http404
        try:
            dj = user.dj
        except User.dj.RelatedObjectDoesNotExist:
            raise Http404

        # Set the fields from the request
        booking = Booking()
        booking.user = user
        booking.contact_name = request.POST["contact-name"]
        booking.phone_number = request.POST["phone-number"]
        booking.email = request.POST["email"]
        booking.address = request.POST["address"]
        booking.set_time = request.POST["set-time"]
        booking.hours = request.POST["hours"]
        booking.other_information = request.POST["other-information"]
        booking.rate = dj.rate
        booking.status = "pending"
        booking.code = random_128_bit_string()

        ### Validate fields

        errors = {}

        # Contact name
        if not booking.contact_name:
            errors["contact_name"] = tr[lang]["Contactnameisrequired"]
        elif len(booking.contact_name) > 200:
            errors["contact_name"] = tr[lang]["Contactnameistoolong_text"]

        # Phone number
        if not booking.phone_number or len(booking.phone_number) > 200:
            errors["phone_number"] = tr[lang]["Invalidphonenumber"]

        # Address
        if not booking.address:
            errors["address"] = tr[lang]["Addressisrequired"]
        elif len(booking.address) > 200:
            errors["address"] = tr[lang]["Addressistoolong_text"]

        # Email
        if not booking.email or len(booking.email) > 254:
            errors["email"] = tr[lang]["Invalidemailaddress"]

        # Set time
        try:
            booking.set_time = datetime.strptime(booking.set_time, "%Y-%m-%d %H:%M")
        except:
            errors["set_time"] = tr[lang]["Invalidsettime"]

        # Hours
        try:
            booking.hours = int(booking.hours)
        except:
            errors["hours"] = tr[lang]["Bookinghoursmustbeaninteger"]

        # In the case of any errors, re-render the form:
        if errors:
            return render(
                request,
                "new-booking.html",
                {"tr": tr[lang], "dj": dj, "booking": booking, "errors": errors},
            )

        # Save the booking request
        booking.save()

        # Generate the email
        plaintext = get_template(f"new-booking-email-{lang}.txt")
        html = get_template(f"new-booking-email-{lang}.html")
        subject = tr[lang]["NewbookingonBeatmatcher"]
        from_email = "no-reply@beatmatcher.org"
        to = user.email
        text_content = plaintext.render(
            {
                "url": request.build_absolute_uri(
                    reverse(
                        "account", kwargs={"lang": user.settings.language}
                    )
                )
            }
        )
        html_content = html.render(
            {
                "url": request.build_absolute_uri(
                    reverse(
                        "account", kwargs={"lang": user.settings.language}
                    )
                )
            }
        )

        # Create the email message with the content and send it
        message = EmailMultiAlternatives(subject, text_content, from_email, [to])
        message.attach_alternative(html_content, "text/html")
        message.send()

        return redirect("booking", lang=lang, code=booking.code)


class BookingView(View):
    def get(self, request, lang, code):
        if lang not in tr:
            raise Http404

        # Ensure Booking exists
        booking = Booking.objects.filter(code=code).first()
        if not booking:
            raise Http404

        return render(request, "booking.html", {"tr": tr[lang], "booking": booking})
