from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.views.generic import TemplateView


class AboutPageView(TemplateView):
    template_name = "pages/about.html"


class RulesPageView(TemplateView):
    template_name = "pages/rules.html"


def custom_403(request, reason=""):
    return render(request, "pages/403csrf.html", status=403)


def custom_404(request, exception):
    return render(request, "pages/404.html", status=404)


def custom_500(request):
    return render(request, "pages/500.html", status=500)


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(to="blog:index")
    else:
        form = UserCreationForm()
    return render(
        request, "registration/registration_form.html", {"form": form}
    )
