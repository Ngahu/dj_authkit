from django.shortcuts import redirect
from django.views.generic import FormView
from django.contrib import messages
from django.http import Http404
from .forms import AcceptInvitationForm
from .services import AccountInvitationService
from .models import AccountInvitation
from .exceptions import (
    InvitationExpiredError,
    InvitationAlreadyAcceptedError,
    InvitationNotFoundError,
)
from django.urls import reverse_lazy


class AcceptInvitationView(FormView):
    template_name = "account_invitations/accept_invitation.html"
    form_class = AcceptInvitationForm
    success_url = reverse_lazy("dashboard/login/")
    service_class = AccountInvitationService
    extra_context = {
        "title": "Accept Invitation",
        "invalid": False,
        "error_message": None,
    }

    # ------------------------------------------
    # Retrieve invitation or raise 404
    # ------------------------------------------
    def get_invitation(self):
        token = self.kwargs.get("token")
        try:
            return AccountInvitation.objects.get(token=token)
        except AccountInvitation.DoesNotExist:
            raise Http404("Invitation not found")
        except Exception:
            raise Http404("Invalid or unknown invitation.")

    def dispatch(self, request, *args, **kwargs):
        self.invitation = self.get_invitation()

        # Invalid cases → message + redirect back to same view

        # if not self.invitation.is_valid:
        #     # return redirect(request.path)
        #     self.extra_context.update(
        #         {
        #             "invalid": True,
        #             "error_message": "This invitation link is invalid. Please request a new one.",
        #         }
        #     )

        # elif self.invitation.is_expired:
        #     messages.error(
        #         request, "This invitation has expired. Please request a new one."
        #     )
        #     self.extra_context.update({"invalid": True})

        # elif self.invitation.is_accepted:
        #     self.extra_context.update(
        #         {
        #             "invalid": True,
        #             "error_message": "This invitation has already been used. Please request a new one.",
        #         }
        #     )

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        invitation = self.get_invitation()
        if not invitation.is_valid:
            # return redirect(request.path)
            self.extra_context.update(
                {
                    "invalid": True,
                    "error_message": "This invitation link is invalid. Please request a new one.",
                }
            )

        elif invitation.is_expired:
            messages.error(
                request, "This invitation has expired. Please request a new one."
            )
            self.extra_context.update({"invalid": True})

        elif invitation.is_accepted:
            self.extra_context.update(
                {
                    "invalid": True,
                    "error_message": "This invitation has already been used. Please request a new one.",
                }
            )

        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["invitation"] = self.invitation
        return ctx

    def form_valid(self, form):
        service = self.service_class()

        try:
            user = service.accept_invitation(
                token=self.invitation.token,
                password=form.cleaned_data["password"],
            )

            print(user, "user")

        except InvitationExpiredError:
            messages.error(
                self.request, "This invitation has expired. Please request a new one."
            )
            return redirect(self.request.path)

        except InvitationAlreadyAcceptedError:
            messages.error(
                self.request,
                "This invitation has already been used. Please request a new one.",
            )
            return redirect(self.request.path)

        except InvitationNotFoundError:
            raise Http404("Invitation not found.")

        # return self.render_to_response(self.get_context_data(form=form))

        # # Success
        # login(self.request, user)
        messages.success(self.request, "Your account has been created successfully!")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        print("invalid form")
        print(form.errors, "errors")
        return self.render_to_response(self.get_context_data(form=form))
