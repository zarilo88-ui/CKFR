from django.db import migrations


GROUPS = ["Admin", "SuperAdmin", "Membre"]


def rename_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    # Rename the legacy English member group if it exists.
    try:
        legacy_member = Group.objects.get(name="Member")
    except Group.DoesNotExist:
        pass
    else:
        legacy_member.name = "Membre"
        legacy_member.save(update_fields=["name"])

    for name in GROUPS:
        Group.objects.get_or_create(name=name)


def revert_group_changes(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    try:
        member = Group.objects.get(name="Membre")
    except Group.DoesNotExist:
        return
    member.name = "Member"
    member.save(update_fields=["name"])


class Migration(migrations.Migration):

    dependencies = [
        ("ops", "0007_operation"),
    ]

    operations = [
        migrations.RunPython(rename_groups, revert_group_changes),
    ]