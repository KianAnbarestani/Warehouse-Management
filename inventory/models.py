from django.db import models

class Ware(models.Model):
    name = models.CharField(max_length=255)
    cost_method = models.CharField(max_length=50, choices=[('fifo', 'FIFO'), ('weighted_mean', 'Weighted Mean')])

    def __str__(self):
        return self.name

class Factor(models.Model):
    ware = models.ForeignKey(Ware, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Only for input
    total_cost = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=10, choices=[('input', 'Input'), ('output', 'Output')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.ware.name} - {self.quantity}"
