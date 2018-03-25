# Generated by Django 2.0.3 on 2018-03-25 07:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ighelper', '0019_auto_20180325_0026'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramUserCounter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('likes_count', models.PositiveIntegerField(default=0)),
                ('instagram_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instagram_user_counters', to='ighelper.InstagramUser')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instagram_user_counters', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-likes_count'],
            },
        ),
    ]
