# Generated by Django 4.2.16 on 2024-12-11 16:37

import branches.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BranchMaster',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('branch_name', models.CharField(max_length=255, unique=True)),
                ('branch_code', models.CharField(max_length=20, unique=True, validators=[django.core.validators.RegexValidator(message='Branch code must be alphanumeric and uppercase.', regex='^[A-Z0-9]+$')])),
                ('email_id', models.EmailField(max_length=255, unique=True, validators=[django.core.validators.EmailValidator])),
                ('booking_contact', models.TextField()),
                ('delivery_contact', models.TextField()),
                ('address', models.TextField(blank=True, null=True)),
                ('pincode', models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(message='Pincode must be a 6-digit number.', regex='^\\d{6}$')])),
                ('latitude', models.FloatField(blank=True, default=0.0, null=True, validators=[django.core.validators.RegexValidator(message='Latitude must be a valid float value between -90 and 90.', regex='^-?([0-8]?[0-9]|90)\\.([0-9]{1,15})$')])),
                ('longitude', models.FloatField(blank=True, default=0.0, null=True, validators=[django.core.validators.RegexValidator(message='Longitude must be a valid float value between -180 and 180.', regex='^-?((1[0-7][0-9])|([0-9]{1,2}))\\.([0-9]{1,15})$')])),
                ('branch_weekly_off', models.CharField(blank=True, help_text="Enter valid days of the week (e.g., 'Monday, Tuesday').", max_length=100, validators=[branches.models.validate_weekly_off_days])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('flag', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='branch_created_by', to=settings.AUTH_USER_MODEL)),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branches', to='company.regionmaster')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='branch_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Branch Master',
                'verbose_name_plural': 'Branch Masters',
                'db_table': 'branch_master',
            },
        ),
        migrations.CreateModel(
            name='EmployeeType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('type_name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('flag', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='employee_type_created_by', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_type_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Employee Type',
                'verbose_name_plural': 'Employee Types',
                'db_table': 'employee_type',
            },
        ),
        migrations.CreateModel(
            name='EmployeeMaster',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('contact_no', models.TextField()),
                ('email_id', models.TextField()),
                ('address', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('flag', models.BooleanField(default=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='branches.branchmaster')),
                ('created_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='employee_created_by', to=settings.AUTH_USER_MODEL)),
                ('employee_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='branches.employeetype')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_updated_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Employee Master',
                'verbose_name_plural': 'Employee Masters',
                'db_table': 'employee_master',
            },
        ),
    ]
