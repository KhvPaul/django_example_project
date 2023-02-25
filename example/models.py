from django.db import models

# Create your models here.


class Image(models.Model):
    name = models.CharField("image name", max_length=200)
    image = models.ImageField("image", upload_to="images")

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField("name", max_length=255)

    def __str__(self):
        return self.name
