# Generated by Django 4.2.16 on 2024-12-11 16:37

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StateMaster',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('state_name', models.CharField(max_length=100, unique=True)),
                ('state_code', models.CharField(max_length=10, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('flag', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='state_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='state_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'State Master',
                'verbose_name_plural': 'State Masters',
                'db_table': 'state_master',
            },
        ),
        migrations.CreateModel(
            name='RegionMaster',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('region_name', models.CharField(max_length=100, unique=True)),
                ('region_code', models.CharField(blank=True, max_length=10, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='Region code must be alphanumeric and between 3 to 10 characters long.', regex='^[A-Z0-9]{3,10}$')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('flag', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='region_created_by', to=settings.AUTH_USER_MODEL)),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='regions', to='company.statemaster')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='region_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Region Master',
                'verbose_name_plural': 'Region Masters',
                'db_table': 'region_master',
            },
        ),
        migrations.CreateModel(
            name='FinancialYears',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('year_name', models.CharField(max_length=9, unique=True, validators=[django.core.validators.RegexValidator(message='Year name must be in the format YYYY-YY.', regex='^\\d{4}-\\d{2}$')])),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('description', models.TextField(blank=True, null=True)),
                ('is_current', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('flag', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='financial_years_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='financial_years_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Financial Year',
                'verbose_name_plural': 'Financial Years',
                'db_table': 'financial_years',
            },
        ),
        migrations.CreateModel(
            name='CompanyMaster',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('company_name', models.CharField(max_length=255)),
                ('company_logo', models.ImageField(blank=True, null=True, upload_to='company_logos/')),
                ('slogan', models.CharField(blank=True, max_length=255, null=True)),
                ('register_number', models.CharField(max_length=100, unique=True, validators=[django.core.validators.RegexValidator(message='Register number must be alphanumeric and uppercase.', regex='^[A-Z0-9]+$')])),
                ('GST_number', models.CharField(max_length=15, unique=True, validators=[django.core.validators.RegexValidator(message='Invalid GST number format.', regex='^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}[Z]{1}[A-Z0-9]{1}$')])),
                ('INA_number', models.CharField(max_length=20, unique=True)),
                ('pan_no',models.CharField(blank=True, max_length=10, null=True, validators=[django.core.validators.RegexValidator('^[A-Z]{5}[0-9]{4}[A-Z]$', 'Invalid PAN format')])),
                ('email_id', models.TextField()),
                ('contact_number', models.TextField()),
                ('address', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('flag', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Company Master',
                'verbose_name_plural': 'Company Masters',
                'db_table': 'company_master',
            },
        ),
    ]