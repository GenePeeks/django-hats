import re

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from django_hats.bootstrap import Bootstrapper


def migrate_role(old_group, new_role):
    # Get all the users for the old role
    users = old_group.user_set.all()

    # Add the new role first, then remove the old one
    new_role.assign(*users)
    old_group.user_set.remove(*users)


def cleanup_roles():
    roles = Bootstrapper.get_roles()

    # Get stale Roles
    stale_roles = Group.objects.filter(
        name__istartswith=Bootstrapper.prefix
    ).exclude(
        id__in=[role.get_group().id for role in roles]
    ).delete()

    return stale_roles


def synchronize_roles(roles):
    # Ensure the ContentType exists
    ContentType.objects.get_or_create(app_label='roles', model='role')

    # Create all of the new Groups
    for role in roles:
        role.synchronize()


def snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
