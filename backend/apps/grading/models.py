from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import TimeStampedModel, UUIDModel
from apps.test_catalog.models import Test


class ScoringBandMapping(UUIDModel, TimeStampedModel):
    class SectionType(models.TextChoices):
        LISTENING = 'listening', 'Listening'
        READING = 'reading', 'Reading'
        WRITING = 'writing', 'Writing'
        SPEAKING = 'speaking', 'Speaking'

    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True, blank=True, related_name='scoring_band_mappings')
    section_type = models.CharField(max_length=16, choices=SectionType.choices)
    raw_score_min = models.DecimalField(max_digits=6, decimal_places=2)
    raw_score_max = models.DecimalField(max_digits=6, decimal_places=2)
    band_score = models.DecimalField(max_digits=3, decimal_places=2)
    is_default = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['section_type', 'raw_score_min']

    def clean(self):
        if self.raw_score_min >= self.raw_score_max:
            raise ValidationError({'raw_score_max': 'raw_score_max must be greater than raw_score_min.'})

        overlapping = ScoringBandMapping.objects.filter(
            section_type=self.section_type,
            test=self.test,
        ).exclude(pk=self.pk)

        for mapping in overlapping:
            if self.raw_score_min < mapping.raw_score_max and self.raw_score_max > mapping.raw_score_min:
                raise ValidationError('Scoring band ranges must not overlap for the same test and section type.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.section_type}: {self.raw_score_min}-{self.raw_score_max} => {self.band_score}'
