# Generated by Django 3.2.8 on 2022-02-04 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='employee_info',
            fields=[
                ('idx', models.AutoField(primary_key=True, serialize=False)),
                ('emp_name', models.CharField(max_length=10)),
                ('use_yn', models.CharField(max_length=10)),
                ('start_dt', models.DateTimeField()),
                ('end_dt', models.DateTimeField()),
            ],
        ),
    ]
