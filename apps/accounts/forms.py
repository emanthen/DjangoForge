from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "••••••••"}),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "••••••••"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Jane"}),
            "last_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Doe"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "jane@example.com"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-input", "placeholder": "jane@example.com", "autofocus": True}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "••••••••"}),
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "avatar"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input"}),
            "last_name": forms.TextInput(attrs={"class": "form-input"}),
        }


class DeleteAccountForm(forms.Form):
    confirm = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "DELETE"}),
        help_text='Type "DELETE" to confirm account deletion.',
    )

    def clean_confirm(self):
        if self.cleaned_data["confirm"] != "DELETE":
            raise forms.ValidationError('Please type "DELETE" to confirm.')
        return self.cleaned_data["confirm"]
