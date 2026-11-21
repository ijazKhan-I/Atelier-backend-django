from django.db.models import FileField
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


def _file_fields(instance):
    for field in instance._meta.fields:
        if isinstance(field, FileField):
            yield field.name, getattr(instance, field.name, None)


@receiver(post_delete)
def delete_files_on_model_delete(sender, instance, **kwargs):
    """Remove stored files when a model row with FileField is deleted."""
    if sender._meta.app_label == "mediafiles":
        return
    for _name, file_field in _file_fields(instance):
        if file_field:
            file_field.delete(save=False)


@receiver(pre_save)
def delete_old_file_on_change(sender, instance, **kwargs):
    """Replace uploads: drop the previous stored file when the path changes."""
    if sender._meta.app_label == "mediafiles" or not instance.pk:
        return
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    for field_name, new_file in _file_fields(instance):
        old_file = getattr(old, field_name, None)
        if old_file and old_file.name and old_file != new_file:
            old_file.delete(save=False)
