from django.db import migrations

def create_guest_user(apps, schema_editor):
    CustomUser = apps.get_model('user_auth_app', 'CustomUser')
    if not CustomUser.objects.filter(email="guest@guest.com").exists():
        guest_user = CustomUser(
            username="guest",
            email="guest@guest.com",
            emblem="G",
            color="#091931",
            is_guest=True
        )
        guest_user.set_unusable_password()
        guest_user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('user_auth_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_guest_user),
    ]