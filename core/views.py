import json
import re
import secrets

from django.contrib import admin
from django.contrib.auth import get_user_model, login
from django.conf import settings
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import FirstAdminAccountForm


@csrf_exempt
@require_POST
def local_session_heartbeat(request):
    expected_token = getattr(settings, "SESSION_HEARTBEAT_TOKEN", "")
    provided_token = request.headers.get("X-MSContable-Session", "")
    payload = {}
    if request.content_type == "application/json":
        try:
            payload = json.loads(request.body or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return HttpResponse(status=400)
        if not isinstance(payload, dict):
            return HttpResponse(status=400)
        provided_token = provided_token or payload.get("token", "")

    if not isinstance(provided_token, str) or not expected_token or not secrets.compare_digest(provided_token, expected_token):
        return HttpResponse(status=403)

    tab_id = request.headers.get("X-MSContable-Tab", "") or payload.get("tab_id", "")
    if not isinstance(tab_id, str) or not re.fullmatch(r"[0-9a-f]{32}", tab_id):
        return HttpResponse(status=400)

    heartbeat_file = settings.SESSION_HEARTBEAT_DIR / f"{tab_id}.active"
    try:
        if request.headers.get("X-MSContable-Closed") == "1" or payload.get("closed") is True:
            heartbeat_file.unlink(missing_ok=True)
        else:
            heartbeat_file.parent.mkdir(parents=True, exist_ok=True)
            heartbeat_file.touch()
    except OSError:
        return HttpResponse(status=503)

    return HttpResponse(status=204)


def first_run(request):
    user_model = get_user_model()

    if user_model.objects.filter(is_superuser=True).exists():
        return redirect("admin:index")

    form_data = request.POST if request.method == "POST" else None
    form = FirstAdminAccountForm(form_data)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                if user_model.objects.filter(is_superuser=True).exists():
                    return redirect("admin:index")

                user = form.save(commit=False)
                user.is_staff = True
                user.is_superuser = True
                user.save()
        except IntegrityError:
            form.add_error(None, "No se pudo crear la cuenta. Probá con otro usuario.")
        else:
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            request.session.set_expiry(
                None if form.cleaned_data["remember_session"] else 0
            )
            return redirect("admin:index")

    if request.method == "POST":
        for field in form:
            if field.errors:
                described_by = [f"first-run-error-{field.name}"]
                if field.help_text:
                    described_by.append(f"first-run-help-{field.name}")
                field.field.widget.attrs.update(
                    {
                        "aria-invalid": "true",
                        "aria-describedby": " ".join(described_by),
                    }
                )

    context = admin.site.each_context(request)
    context.update({"form": form, "title": "Crear cuenta"})
    return render(request, "admin/first_run.html", context)


def admin_login(request):
    user_model = get_user_model()

    if not user_model.objects.filter(is_superuser=True).exists():
        return redirect("first-run")

    if request.method == "GET" and request.GET.get("next") == reverse("admin:index"):
        return redirect("admin-login")

    response = admin.site.login(request)
    if request.method == "POST" and response.status_code == 302:
        request.session.set_expiry(
            None if request.POST.get("remember_session") else 0
        )
    return response
