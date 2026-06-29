from django.urls import path

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("verify-email/sent/", views.VerifyEmailSentView.as_view(), name="verify_email_sent"),
    path("verify-email/<uidb64>/<token>/", views.VerifyEmailView.as_view(), name="verify_email"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/delete/", views.DeleteAccountView.as_view(), name="delete_account"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("profile/change-password/", views.ChangePasswordRedirectView.as_view(), name="change_password"),
]
