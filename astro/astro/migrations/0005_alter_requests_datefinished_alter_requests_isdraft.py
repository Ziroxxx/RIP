# Generated by Django 5.1 on 2024-09-12 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('astro', '0004_alter_planets_constellations_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requests',
            name='dateFinished',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='requests',
            name='isDraft',
            field=models.BooleanField(default=True),
        ),
    ]