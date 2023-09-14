from django.db import models
from django.conf import settings

# Create your models here.

class Axiom(models.Model):
    name = models.CharField(max_length=200)
    content = models.CharField(max_length=200)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Axiom: {self.name}"

class Argument(models.Model):
    name = models.CharField(max_length=200)
    content = models.CharField(max_length=200)
    axiom = models.ForeignKey(Axiom, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Argument: {self.name}"

    def is_valid(self):
        return True

    def is_sound(self):
        return False

class Premise(models.Model):
    name = models.CharField(max_length=200)
    content = models.CharField(max_length=200)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def is_true(self):
        # maybe by voting? over threshold? but with evidence somehow
        return True

class Conclusion(models.Model):
    name = models.CharField(max_length=200)
    content = models.CharField(max_length=200)
    premises = models.ManyToManyField(Premise)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"Conclusion: {self.name}"
    
    # check if all premises are true, make conclusion true
    @property
    def is_true(self):
        if self.premise.is_true:
            return True
