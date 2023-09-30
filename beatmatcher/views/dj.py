from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from beatmatcher.models import DJ
from beatmatcher.translations import tr
from PIL import Image
from io import BytesIO


class EditDJView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        if not request.user.is_authenticated:
            return redirect("log-in", lang=lang)
        try:
            dj = request.user.dj
        except User.dj.RelatedObjectDoesNotExist:
            dj = DJ()
        return render(request, "edit-dj.html", {"tr": tr[lang], "dj": dj})

    def post(self, request, lang):
        if lang not in tr:
            raise Http404
        if not request.user.is_authenticated:
            return redirect("log-in", lang=lang)
        try:
            dj = request.user.dj
        except User.dj.RelatedObjectDoesNotExist:
            dj = DJ(user=request.user, picture=False)

        # Set the fields from the request
        dj.name = request.POST["name"]
        dj.description = request.POST["description"]
        if "picture" in request.FILES:
            dj.picture = True
        dj.soundcloud_url = request.POST["soundcloud_url"]
        dj.rate = request.POST["rate"] or None

        ### Validate fields

        errors = {}

        # Name
        if len(dj.name) == 0 or len(dj.name) > 200:
            errors["name"] = tr[lang]["Stagenamerequirements_text"]

        # SoundCloud URL
        if dj.soundcloud_url and (not dj.soundcloud_url.startswith("https://soundcloud.com/") or len(dj.soundcloud_url) > 200):
            errors["soundcloud_url"] = tr[lang]["SoundCloudURLrequirements_text"]

        # Rate
        if dj.rate:
            try:
                dj.rate = int(dj.rate)
            except:
                errors["rate"] = tr[lang]["Hourlyratemustbeaninteger"]

        # Picture
        if "picture" in request.FILES:
            image_bytes = request.FILES["picture"].read()
            if len(image_bytes) > 1024*1024*20:
                errors["picture"] = tr[lang]["Pictureistoolarge"]
            try:
                image = Image.open(BytesIO(image_bytes))
                width, height = image.size
                if width < 180 or height < 180:
                    errors["picture"] = tr[lang]["Pictureisnotlargeenough_text"]
            except:
                errors["picture"] = tr[lang]["Invalidpicture"]

        # In the case of any errors, simply re-render the form:
        if errors:
            return render(request, "edit-dj.html", {"tr": tr[lang], "dj": dj, "errors": errors})

        # Save the DJ
        dj.save()

        # Save the uploaded profile picture
        if "picture" in request.FILES:
            image.resize((180,180)).save(f"static/images/djs/{dj.id}.png")

        return redirect("edit-dj-success", lang=lang)


class EditDJSuccessView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        if not request.user.is_authenticated:
            return redirect("log-in", lang=lang)
        return render(request, "edit-dj-success.html", {"tr": tr[lang]})
