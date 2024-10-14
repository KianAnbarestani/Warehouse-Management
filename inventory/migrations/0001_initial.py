# Generated by Django 4.2 on 2024-10-14 21:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ware",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "cost_method",
                    models.CharField(
                        choices=[("fifo", "FIFO"), ("weighted_mean", "Weighted Mean")],
                        max_length=50,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Factor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.IntegerField()),
                (
                    "purchase_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("total_cost", models.DecimalField(decimal_places=2, max_digits=15)),
                (
                    "type",
                    models.CharField(
                        choices=[("input", "Input"), ("output", "Output")],
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "ware",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="inventory.ware"
                    ),
                ),
            ],
        ),
    ]