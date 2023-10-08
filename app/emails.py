from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
from app.translation import tr


def send_sign_up_email(request, language, email, code):
    # Load the content
    plaintext = get_template(f"emails/sign-up.txt")
    html = get_template(f"emails/sign-up.html")
    subject = tr("Welcome to %s", language) % settings.SITE_TITLE
    from_email = f"no-reply@{request.get_host()}"
    text_content = plaintext.render({f"language": language, f"url": request.build_absolute_uri(reverse(f"sign-up-verify", kwargs={f"code": code}))})
    html_content = html.render({f"language": language, f"url": request.build_absolute_uri(reverse(f"sign-up-verify", kwargs={f"code": code}))})

    # Create the email message with the content and send it
    message = EmailMultiAlternatives(subject, text_content, from_email, [email])
    message.attach_alternative(html_content, f"text/html")
    message.send()
