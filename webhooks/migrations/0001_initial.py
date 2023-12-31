# Generated by Django 4.2 on 2023-10-27 07:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Webhook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('url', models.URLField(max_length=2048, unique=True)),
                ('secret', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('status', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webhook_owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'url')},
            },
        ),
        migrations.CreateModel(
            name='WebhookEvents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('event', models.CharField(choices=[], max_length=200)),
                ('webhook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webhooks.webhook')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
