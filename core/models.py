from django.db import models

class DataEntry(models.Model):
    name = models.CharField(max_length=100)  # Example: Name of data entry
    value = models.FloatField()  # Example: Numeric data value
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"{self.name}: {self.value}"
