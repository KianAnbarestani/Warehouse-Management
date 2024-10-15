from django.db import models

# This model represents an individual product in the warehouse
class Ware(models.Model):
    # Name of the product, with a constraint that ensures each name is unique
    name = models.CharField(max_length=255, unique=True)
    
    # Cost method can either be 'FIFO' or 'Weighted Mean'
    cost_method = models.CharField(
        max_length=50, 
        choices=[('fifo', 'FIFO'), ('weighted_mean', 'Weighted Mean')]
    )

    # String representation for easier display of ware names
    def __str__(self):
        return self.name


# This model represents a transaction (either input for stock or output for sales)
class Factor(models.Model):
    # Foreign key linking the transaction to a specific ware
    ware = models.ForeignKey(Ware, on_delete=models.CASCADE)
    
    # The number of units affected by the transaction
    quantity = models.IntegerField()

    # Purchase price, relevant only for input transactions (when stock is added)
    # Blank/null allowed because it's not used for output transactions
    purchase_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Total cost for the transaction (used for both input and output)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Type of transaction: either 'input' for adding stock or 'output' for removing stock
    type = models.CharField(
        max_length=10, 
        choices=[('input', 'Input'), ('output', 'Output')]
    )
    
    # Automatically record when the transaction was created
    created_at = models.DateTimeField(auto_now_add=True)

    # String representation to display transaction info easily
    def __str__(self):
        return f"{self.type} - {self.ware.name} - {self.quantity} units"
