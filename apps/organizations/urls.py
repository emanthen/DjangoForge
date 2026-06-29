from django.urls import path

from apps.organizations import views

app_name = "organizations"

urlpatterns = [
    path("orgs/create/", views.CreateOrgView.as_view(), name="create"),
    path("orgs/switch/<slug:slug>/", views.OrgSwitchView.as_view(), name="switch"),
    path("orgs/settings/", views.OrgSettingsView.as_view(), name="settings"),
    path("orgs/members/", views.MemberListView.as_view(), name="members"),
    path("orgs/members/invite/", views.InviteMemberView.as_view(), name="invite"),
    path("orgs/members/<uuid:membership_id>/remove/", views.RemoveMemberView.as_view(), name="remove_member"),
    path("orgs/members/<uuid:membership_id>/role/", views.ChangeMemberRoleView.as_view(), name="change_role"),
    path("orgs/invitations/<str:token>/accept/", views.AcceptInvitationView.as_view(), name="accept_invitation"),
    path("orgs/transfer/", views.TransferOwnershipView.as_view(), name="transfer_ownership"),
]
