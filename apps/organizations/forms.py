from django import forms

from apps.organizations.models import Membership, Organization

COUNTRY_CHOICES = [
    ("", "Select country…"),
    ("US", "United States"),
    ("GB", "United Kingdom"),
    ("CA", "Canada"),
    ("AU", "Australia"),
    ("IN", "India"),
    ("DE", "Germany"),
    ("FR", "France"),
    ("JP", "Japan"),
    ("SG", "Singapore"),
    ("AE", "United Arab Emirates"),
    ("NL", "Netherlands"),
    ("SE", "Sweden"),
    ("NO", "Norway"),
    ("DK", "Denmark"),
    ("FI", "Finland"),
    ("CH", "Switzerland"),
    ("AT", "Austria"),
    ("BE", "Belgium"),
    ("BR", "Brazil"),
    ("MX", "Mexico"),
    ("ZA", "South Africa"),
    ("NG", "Nigeria"),
    ("KE", "Kenya"),
    ("PH", "Philippines"),
    ("MY", "Malaysia"),
    ("ID", "Indonesia"),
    ("PK", "Pakistan"),
    ("NZ", "New Zealand"),
    ("IE", "Ireland"),
    ("IL", "Israel"),
    ("TR", "Turkey"),
    ("CN", "China"),
    ("KR", "South Korea"),
    ("TH", "Thailand"),
    ("VN", "Vietnam"),
    ("AR", "Argentina"),
    ("CO", "Colombia"),
    ("CL", "Chile"),
    ("PL", "Poland"),
    ("ES", "Spain"),
    ("IT", "Italy"),
    ("PT", "Portugal"),
    ("RU", "Russia"),
    ("OTHER", "Other"),
]

_FI = "form-input"
_TA = "form-input h-24 resize-none"
_SEL = "form-input"


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name", "logo"]
        widgets = {
            "name": forms.TextInput(attrs={"class": _FI, "placeholder": "Acme Corp"}),
        }


class OnboardingOrgForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name", "industry", "company_size", "website", "description"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": _FI,
                "placeholder": "Acme Inc.",
                "autocomplete": "organization",
            }),
            "industry": forms.Select(attrs={"class": _SEL}),
            "company_size": forms.Select(attrs={"class": _SEL}),
            "website": forms.URLInput(attrs={
                "class": _FI,
                "placeholder": "https://yourcompany.com",
                "autocomplete": "url",
            }),
            "description": forms.Textarea(attrs={
                "class": _TA,
                "placeholder": "Briefly describe what your company does…",
                "rows": 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["industry"].required = False
        self.fields["company_size"].required = False
        self.fields["website"].required = False
        self.fields["description"].required = False
        # Prepend blank choice for select fields
        self.fields["industry"].choices = [("", "Select industry…")] + list(Organization.INDUSTRY_CHOICES)
        self.fields["company_size"].choices = [("", "Select size…")] + list(Organization.SIZE_CHOICES)


class OnboardingContactForm(forms.ModelForm):
    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": _SEL}),
    )

    class Meta:
        model = Organization
        fields = [
            "phone", "support_email",
            "address_line1", "address_line2",
            "city", "state", "postal_code", "country",
            "registration_number",
        ]
        widgets = {
            "phone": forms.TextInput(attrs={
                "class": _FI, "placeholder": "+1 (555) 000-0000", "autocomplete": "tel",
            }),
            "support_email": forms.EmailInput(attrs={
                "class": _FI, "placeholder": "support@yourcompany.com", "autocomplete": "email",
            }),
            "address_line1": forms.TextInput(attrs={
                "class": _FI, "placeholder": "123 Main Street", "autocomplete": "address-line1",
            }),
            "address_line2": forms.TextInput(attrs={
                "class": _FI, "placeholder": "Suite 400", "autocomplete": "address-line2",
            }),
            "city": forms.TextInput(attrs={
                "class": _FI, "placeholder": "San Francisco", "autocomplete": "address-level2",
            }),
            "state": forms.TextInput(attrs={
                "class": _FI, "placeholder": "California", "autocomplete": "address-level1",
            }),
            "postal_code": forms.TextInput(attrs={
                "class": _FI, "placeholder": "94107", "autocomplete": "postal-code",
            }),
            "registration_number": forms.TextInput(attrs={
                "class": _FI, "placeholder": "Optional — e.g. EIN, VAT, or Company #",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].required = False


class OnboardingProfileForm(forms.Form):
    first_name = forms.CharField(
        max_length=150, required=False, label="First name",
        widget=forms.TextInput(attrs={
            "class": _FI, "placeholder": "Jane", "autocomplete": "given-name",
        }),
    )
    last_name = forms.CharField(
        max_length=150, required=False, label="Last name",
        widget=forms.TextInput(attrs={
            "class": _FI, "placeholder": "Smith", "autocomplete": "family-name",
        }),
    )
    job_title = forms.CharField(
        max_length=100, required=False, label="Job title",
        widget=forms.TextInput(attrs={
            "class": _FI, "placeholder": "CTO, Product Manager, Developer…",
            "autocomplete": "organization-title",
        }),
    )


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
