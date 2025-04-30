from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict

from Insurecow.utils import  convert_non_serializable_fields
from assetservice.models import Asset
from insuranceservice.models import AssetInsurance, InsuranceClaim


class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    model_name = models.CharField(max_length=255)
    instance_id = models.PositiveIntegerField()
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    changes = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_action_display()} {self.model_name} ID {self.instance_id}"


def create_audit_log(user, model_name, instance_id, action, changes=None):
    # Convert any non-serializable fields (Decimal, date, datetime, FieldFile) in the changes dictionary
    changes = convert_non_serializable_fields(changes or {})
    AuditLog.objects.create(
        user=user,
        model_name=model_name,
        instance_id=instance_id,
        action=action,
        changes=changes,
    )

@receiver(post_save, sender=Asset)
@receiver(post_save, sender=AssetInsurance)
@receiver(post_save, sender=InsuranceClaim)
def create_update_audit(sender, instance, created, **kwargs):
    user = getattr(instance, 'updated_by', None) or getattr(instance, 'created_by', None)
    changes = model_to_dict(instance)
    action = 'create' if created else 'update'
    # Convert non-serializable fields (Decimal, date, datetime, FieldFile) before logging
    changes = convert_non_serializable_fields(changes)
    create_audit_log(user, sender.__name__, instance.pk, action, changes)

@receiver(post_delete, sender=Asset)
@receiver(post_delete, sender=AssetInsurance)
@receiver(post_delete, sender=InsuranceClaim)
def delete_audit(sender, instance, **kwargs):
    user = getattr(instance, 'updated_by', None) or getattr(instance, 'created_by', None)
    changes = model_to_dict(instance)
    # Convert non-serializable fields (Decimal, date, datetime, FieldFile) before logging
    changes = convert_non_serializable_fields(changes)
    create_audit_log(user, sender.__name__, instance.pk, 'delete', changes)
