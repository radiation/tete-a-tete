# Generated by Django 4.2.8 on 2024-06-22 21:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0001_initial"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="userdigest",
            options={
                "verbose_name": "User Digest",
                "verbose_name_plural": "User Digests",
            },
        ),
        migrations.AlterField(
            model_name="userdigest",
            name="send_time",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to="common.eventtime",
                verbose_name="Send Time",
            ),
        ),
        migrations.AlterField(
            model_name="userpreferences",
            name="working_days",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (0, "Monday"),
                    (1, "Tuesday"),
                    (2, "Wednesday"),
                    (3, "Thursday"),
                    (4, "Friday"),
                    (5, "Saturday"),
                    (6, "Sunday"),
                ],
                null=True,
            ),
        ),
    ]
