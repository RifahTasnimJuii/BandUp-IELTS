# listening/migrations/0002_add_answers_field.py
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('listening', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlisteningattempt',
            name='answers',
            field=models.JSONField(default=dict, blank=True),
        ),
    ]
