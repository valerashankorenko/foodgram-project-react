# Generated by Django 3.2.3 on 2024-01-18 17:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20240118_1956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(help_text='HEX формат цветового кода (#RRGGBB)', max_length=7, unique=True, validators=[django.core.validators.RegexValidator(regex='^#(?:[0-9a-fA-F]{3}){1,2}$')], verbose_name='Цветовой код'),
        ),
    ]
