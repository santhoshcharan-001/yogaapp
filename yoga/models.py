from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.


class Batch(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["start_time"]
        verbose_name = "Batch"
        verbose_name_plural = "Batches"

    def __str__(self):
        return (
            self.start_time.strftime("%I:%M %p")
            + " - "
            + self.end_time.strftime("%I:%M %p")
        )


class Payment(models.Model):
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.IntegerField(default=500)
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    card_number = models.CharField(max_length=16, null=True, blank=True)
    card_holder_name = models.CharField(max_length=100, null=True, blank=True)
    card_expiry = models.CharField(max_length=5, null=True, blank=True)
    card_cvv = models.CharField(max_length=3, null=True, blank=True)

    def __str__(self):
        return self.payment_id

    def save(self, *args, **kwargs):
        if self.payment_id is None or self.payment_id == "":
            epoch = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            self.payment_id = "ORDER_" + str(self.user.id) + epoch
        super(Payment, self).save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, null=True, blank=True)
    subscribed = models.BooleanField(default=False)
    subscription_start_date = models.DateField(null=True, blank=True)
    subscription_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    def subscribe(self, batch):
        if batch:
            self.batch = batch
        self.subscribed = True
        self.subscription_start_date = datetime.date.today()
        self.subscription_end_date = datetime.date.today() + datetime.timedelta(days=29)
        self.save()

    @property
    def is_subscription_active(self):
        if self.subscribed and self.subscription_end_date < datetime.date.today():
            self.subscribed = False
            self.save()
        return self.subscribed
