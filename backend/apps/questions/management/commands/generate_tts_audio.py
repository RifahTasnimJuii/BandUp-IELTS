import asyncio
import os
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.questions.models import Question
from apps.test_catalog.models import AudioAsset, Test


class Command(BaseCommand):
    help = 'Generate examiner audio for Listening parts and Speaking prompts.'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Regenerate existing MP3 files.')
        parser.add_argument('--slug', default='mock-test-1', help='Test slug to process.')

    def handle(self, *args, **options):
        test = Test.objects.filter(slug=options['slug']).first()
        if not test:
            self.stdout.write(self.style.WARNING(f'No test found for slug {options["slug"]}.'))
            return
        output_dir = Path(settings.MEDIA_ROOT) / 'tts'
        output_dir.mkdir(parents=True, exist_ok=True)
        engine = self._build_engine()
        prefix = '' if options['slug'] == 'mock-test-1' else f'{options["slug"]}_'
        jobs = []
        listening = test.sections.filter(section_type='listening').first()
        audio_assets = list(listening.audio_assets.filter(is_active=True).order_by('title')) if listening else []
        audio = audio_assets[0] if audio_assets else None
        source_transcript = '\n\n'.join(asset.transcript for asset in audio_assets if asset.transcript) if len(audio_assets) > 1 else (audio.transcript if audio else '')
        for index, script in enumerate(self._split_parts(source_transcript), 1):
            part_audio = audio if index == 1 else None
            if listening and index > 1:
                from apps.test_catalog.models import AudioAsset
                part_audio, _ = AudioAsset.objects.get_or_create(section=listening, title=f'Listening Part {index}', defaults={'audio_file': 'audio_assets/placeholder.mp3', 'duration_seconds': 0, 'transcript': script, 'mime_type': 'audio/mpeg', 'is_active': True, 'playback_policy': {'allow_replay': False, 'allow_seek': False}})
            if part_audio:
                part_audio.title = f'Listening Part {index}'
                part_audio.transcript = script
                part_audio.save(update_fields=['title', 'transcript', 'updated_at'])
            jobs.append((f'{prefix}listening_part_{index}.mp3', script, part_audio, None))
        speaking_questions = Question.objects.filter(
            question_group__section__test=test,
            type=Question.QuestionType.SPEAKING_PROMPT,
        ).select_related('question_group').order_by('question_group__order', 'order')
        for question in speaking_questions:
            filename = f'speaking_part{question.question_group.order}_question{question.order}.mp3'
            jobs.append((f'{prefix}{filename}', question.prompt, None, question))
        speaking = test.sections.filter(section_type='speaking').first()
        transitions = [
            ('speaking_greeting.mp3', "Hello. My name is Alex. I'll be your examiner today. Can you tell me your full name?"),
            ('speaking_part2_intro.mp3', "Now I'll give you a topic. You have one minute to prepare, and then you should speak for up to two minutes."),
            ('speaking_part2_begin.mp3', 'You may begin.'),
            ('speaking_part3_intro.mp3', "Now let's discuss this topic in more detail."),
        ]
        for filename, text in transitions:
            asset = AudioAsset.objects.filter(section=speaking, title=filename[:-4]).first() if speaking else None
            if speaking and asset is None:
                asset = AudioAsset.objects.create(section=speaking, title=filename[:-4], audio_file='audio_assets/placeholder.mp3', transcript=text, mime_type='audio/mpeg', is_active=True)
            jobs.append((f'{prefix}{filename}', text, asset, None))

        rows = []
        for filename, text, audio_asset, question in jobs:
            destination = output_dir / filename
            if destination.exists() and not options['force']:
                self._attach(destination, audio_asset, question)
                rows.append((filename, destination.stat().st_size, 'existing'))
                continue
            if engine is None:
                rows.append((filename, 0, 'skipped'))
                continue
            try:
                engine.generate(text, destination)
                self._attach(destination, audio_asset, question)
                rows.append((filename, destination.stat().st_size, engine.name))
            except Exception as error:
                self.stdout.write(self.style.WARNING(f'Skipped {filename}: {error}'))
                rows.append((filename, 0, 'skipped'))

        self.stdout.write('')
        self.stdout.write(f'{"File":<48} {"Size":>12}  Engine')
        self.stdout.write('-' * 72)
        for filename, size, used_engine in rows:
            self.stdout.write(f'{filename:<48} {size:>10} B  {used_engine}')
        self.stdout.write(f'Generated/attached: {sum(1 for _, _, used_engine in rows if used_engine != "skipped")}; skipped: {sum(1 for _, _, used_engine in rows if used_engine == "skipped")}')

    @staticmethod
    def _split_parts(transcript):
        if not transcript:
            return []
        parts = re.split(r'(?=Part\s+[1-4]\s*[-:])', transcript, flags=re.IGNORECASE)
        return [part.strip() for part in parts if part.strip()][:4]

    @staticmethod
    def _attach(path, audio_asset, question):
        relative_name = f'tts/{path.name}'
        if audio_asset:
            audio_asset.audio_file.name = relative_name
            audio_asset.mime_type = 'audio/mpeg'
            audio_asset.storage_provider = 'local'
            audio_asset.save(update_fields=['audio_file', 'mime_type', 'storage_provider', 'updated_at'])
        if question:
            question.prompt_audio_file.name = relative_name
            question.save(update_fields=['prompt_audio_file', 'updated_at'])

    @staticmethod
    def _build_engine():
        api_key = getattr(settings, 'OPENAI_API_KEY', '') or os.getenv('OPENAI_API_KEY', '')
        if api_key:
            try:
                from openai import OpenAI
                return OpenAIEngine(OpenAI(api_key=api_key))
            except Exception:
                pass
        try:
            import edge_tts
            return EdgeTTSEngine(edge_tts)
        except Exception:
            return None


class OpenAIEngine:
    name = 'openai-tts-1-nova'

    def __init__(self, client):
        self.client = client

    def generate(self, text, destination):
        response = self.client.audio.speech.create(model='tts-1', voice='nova', input=text, response_format='mp3')
        response.stream_to_file(str(destination))


class EdgeTTSEngine:
    name = 'edge-tts-AriaNeural'

    def __init__(self, module):
        self.module = module

    def generate(self, text, destination):
        async def render():
            try:
                await self.module.Communicate(text, 'en-US-AriaNeural').save(str(destination))
            except Exception:
                await self.module.Communicate(text, 'en-US-JennyNeural').save(str(destination))
        asyncio.run(render())
