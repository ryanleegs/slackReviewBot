from django.db import models


class Name(models.Model):
    idx = models.AutoField(primary_key=True)
    emp_name = models.CharField(max_length=10)
    use_yn = models.CharField(max_length=10)
    start_dt = models.DateTimeField()
    end_dt = models.DateTimeField()

    def __str__(self):
        return self.emp_name
