# Generated by Django 4.2 on 2023-10-30 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webhooks', '0002_alter_webhookevents_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webhookevents',
            name='event',
            field=models.CharField(choices=[('user.create', 'user.create'), ('user.update', 'user.update'), ('user.delete', 'user.delete'), ('test.hook', 'test.hook'), ('webhook.create', 'webhook.create'), ('webhook.update', 'webhook.update'), ('webhook.delete', 'webhook.delete')], max_length=200),
        ),
    ]
