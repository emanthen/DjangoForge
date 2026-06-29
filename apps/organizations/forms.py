from django import forms

from apps.organizations.models import Membership, Organization


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name", "logo"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Acme Corp"}),
        }


class InviteMemberForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-input", "placeholder": "colleague@example.com"})
    )
    role = forms.ChoiceField(
        choices=Membership.ROLES,
        initial=Membership.ROLE_MEMBER,
        widget=forms.Select(attrs={"class": "form-input"}),
    )


class TransferOwnershipForm(forms.Form):
    new_owner = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, org=None, current_owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields["new_owner"].queryset = User.objects.filter(
            memberships__org=org
        ).exclude(pk=current_owner.pk)
        self.fields["new_owner"].widget.attrs["class"] = "form-input"
