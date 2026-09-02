from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('questions', '0001_initial')]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.CharField(
                choices=[
                    ('mcq_single', 'MCQ Single'), ('mcq_multiple', 'MCQ Multiple'),
                    ('true_false_not_given', 'True/False/Not Given'), ('yes_no_not_given', 'Yes/No/Not Given'),
                    ('fill_blank', 'Fill Blank'), ('sentence_completion', 'Sentence Completion'),
                    ('summary_completion', 'Summary Completion'), ('matching_headings', 'Matching Headings'),
                    ('matching_items', 'Matching Items'), ('short_answer', 'Short Answer'),
                    ('writing_prompt', 'Writing Prompt'), ('speaking_prompt', 'Speaking Prompt'),
                    ('map_label', 'Map Label'),
                ],
                max_length=32,
            ),
        ),
    ]
