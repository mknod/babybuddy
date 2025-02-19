# Generated by Django 3.2.5 on 2021-07-26 22:38

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_child_slug'),
    ]

    operations = [
        migrations.CreateModel(
            name='Music',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('artist', models.CharField(max_length=255, verbose_name='Artist')),
                ('song', models.CharField(max_length=255, verbose_name='Song')),
                ('liked_song', models.BooleanField(default=True, verbose_name='Liked Song')),
                ('time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date')),
                ('child', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='music', to='core.child', verbose_name='Child')),
            ],
            options={
                'verbose_name': 'Music',
                'verbose_name_plural': 'Music',
                'ordering': ['-time'],
                'default_permissions': ('view', 'add', 'change', 'delete'),
            },
        ),
    ]
