from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Profile, User
from apps.grading.models import ScoringBandMapping
from apps.questions.models import CorrectAnswerRule, Question, QuestionGroup
from apps.test_catalog.models import AudioAsset, Passage, Section, Test


class Command(BaseCommand):
    help = 'Seed the original BandUp demo test and demo users.'

    MOCK_TEST_SLUG = 'mock-test-1'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            dest='no_input',
            help='Accepted for CI and Docker compatibility; sample data is recreated automatically.',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('BandUp Sample Data Seeder'))
        self.stdout.write(self.style.NOTICE('=========================='))

        with transaction.atomic():
            self._clean_sample_data()
            admin, student = self._create_demo_users()
            test = self._create_test(admin)
            reading = self._seed_reading(test)
            listening = self._seed_listening(test)
            self._seed_writing(test)
            self._seed_speaking(test)
            self._seed_scoring_mappings(test)

        self.stdout.write('')
        self.stdout.write(self.style.NOTICE('=========================='))
        self.stdout.write(self.style.SUCCESS('Seed complete!'))
        self.stdout.write('')
        self.stdout.write('Test credentials:')
        self.stdout.write('  Admin:   admin@bandup.test / Admin123!')
        self.stdout.write('  Student: student@bandup.test / Student123!')
        self.stdout.write('')
        self.stdout.write('Visit http://localhost:3000 to start the mock test.')
        self.stdout.write(
            self.style.NOTICE(
                f'Seeded {reading.question_groups.count()} reading group(s) and '
                f'{listening.question_groups.count()} listening group(s).'
            )
        )

    def _clean_sample_data(self):
        deleted, _ = Test.objects.filter(slug=self.MOCK_TEST_SLUG).delete()
        self.stdout.write(self.style.NOTICE('[1/6] Cleaning existing sample data...'))
        self.stdout.write(self.style.SUCCESS(f'      Done ({deleted} object(s) removed)'))

    def _create_demo_users(self):
        admin, _ = User.objects.update_or_create(
            email='admin@bandup.test',
            defaults={
                'username': 'admin',
                'role': User.Role.SUPERADMIN,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'email_verified': True,
            },
        )
        admin.set_password('Admin123!')
        admin.save(update_fields=['username', 'role', 'is_staff', 'is_superuser', 'is_active', 'email_verified', 'password'])

        student, _ = User.objects.update_or_create(
            email='student@bandup.test',
            defaults={
                'username': 'student',
                'role': User.Role.STUDENT,
                'is_staff': False,
                'is_superuser': False,
                'is_active': True,
                'email_verified': True,
            },
        )
        student.set_password('Student123!')
        student.save(update_fields=['username', 'role', 'is_staff', 'is_superuser', 'is_active', 'email_verified', 'password'])
        Profile.objects.update_or_create(
            user=student,
            defaults={
                'target_band': '7.5',
                'country': 'Bangladesh',
                'language_preference': Profile.LanguagePreference.EN,
            },
        )

        self.stdout.write(self.style.NOTICE('[2/6] Creating demo users...'))
        self.stdout.write(self.style.SUCCESS('      Created or updated admin@bandup.test, student@bandup.test'))
        return admin, student

    def _create_test(self, admin):
        test = Test.objects.create(
            title='BandUp Original Mock Test 1',
            slug=self.MOCK_TEST_SLUG,
            description='A complete original IELTS-style practice test covering all four modules.',
            module_type=Test.ModuleType.ACADEMIC,
            attempt_limit=0,
            strict_exam_mode=True,
            allow_practice_replay=True,
            is_published=True,
            is_featured=True,
            created_by=admin,
            updated_by=admin,
            default_section_order=['reading', 'listening', 'writing', 'speaking'],
        )
        self.stdout.write(self.style.NOTICE('[3/6] Creating sample test & sections...'))
        self.stdout.write(self.style.SUCCESS(f'      "{test.title}"'))
        return test

    def _seed_reading(self, test):
        section = Section.objects.create(
            test=test,
            title='Reading',
            section_type=Section.SectionType.READING,
            duration_seconds=3600,
            order=1,
            instruction_text='Read the passage and answer all questions.',
            is_published=True,
        )
        passage = Passage.objects.create(
            section=section,
            title='The Evolution of Urban Transportation',
            body_text=(
                'At the beginning of the nineteenth century, moving through a city was a slow and social affair. '
                'Horse-drawn carriages shared narrow streets with carts, pedestrians, and livestock. In 1829, '
                'George Shillibeer introduced one of London\'s first regular omnibus services, carrying passengers '
                'between Paddington and Bank for a modest fare. The service established a pattern that later '
                'transport planners would repeat: fixed routes, scheduled departures, and a shared vehicle.\n\n'
                'The next major change occurred below the surface. London opened the world\'s first underground '
                'railway in 1863, linking Paddington with Farringdon. Its steam locomotives were smoky and noisy, '
                'yet the line moved about 38,000 passengers on its first day. Other cities soon studied the idea. '
                'In 1890, electric trains replaced steam on London\'s City and South London Railway, making tunnels '
                'cleaner and allowing deeper routes to be built.\n\n'
                'Electricity also transformed street travel. The first electric tram in this account began operating '
                'in Berlin in 1881, demonstrated by engineer Werner von Siemens. By 1900, electric trams served '
                'more than 30 European cities, and the average commuter could travel several kilometres farther '
                'from the city centre than a generation earlier. The change was not simply technological: reliable '
                'tram routes encouraged factories and apartment buildings to spread along their corridors.\n\n'
                'Buses and private cars then competed for the same urban space. After 1950, car ownership rose '
                'rapidly in many European cities, but it did not rise evenly. Historian Mara Voss estimates that '
                'Copenhagen had 75 cars per 1,000 residents in 1955, while Paris had 128. Congestion, noise, and '
                'dirty air led some governments to build ring roads, pedestrian zones, and dedicated bus lanes. '
                'These measures reduced some pressure without ending the appeal of personal travel.\n\n'
                'Today, transport policy is turning once again toward shared and electric mobility. Battery buses, '
                'tram extensions, and app-based bicycles allow a single journey to combine several modes. In 2023, '
                'the fictional Metrovale transport authority reported that electric vehicles made 42 percent of '
                'its public-transport trips, up from 9 percent in 2014. The modern challenge is therefore familiar: '
                'designing a network that is affordable, dependable, and able to grow without making city life less '
                'pleasant.'
            ),
            source_note='Original BandUp sample content.',
            license_note='Created for BandUp demonstration and testing.',
            is_original_sample=True,
        )
        group = QuestionGroup.objects.create(
            section=section,
            title='Reading Questions 1-5',
            instruction='For questions 1-2, choose True, False, or Not Given. For questions 3-4, choose one answer. For question 5, write the year.',
            passage=passage,
            order=1,
            is_required=True,
        )
        questions = [
            (Question.QuestionType.TRUE_FALSE_NOT_GIVEN, 'The first electric tram was introduced in Berlin in 1881.', ['True', 'False', 'Not Given'], {'answer': 'True'}, {'accepted_answers': ['true']}),
            (Question.QuestionType.TRUE_FALSE_NOT_GIVEN, 'Private car ownership declined sharply after 1950 in most European cities.', ['True', 'False', 'Not Given'], {'answer': 'False'}, {'accepted_answers': ['false']}),
            (Question.QuestionType.MCQ_SINGLE, 'What is the main idea of paragraph 3?', ['A. Electric travel changed cities as well as vehicles.', 'B. Steam trains were safer than electric trains.', 'C. Berlin had the largest tram network in Europe.', 'D. Engineers stopped developing underground railways.'], {'answer': 'A'}, {}),
            (Question.QuestionType.MCQ_SINGLE, 'In paragraph 5, what does "turning once again toward shared and electric mobility" mean?', ['A. Returning to horse-drawn transport.', 'B. Giving greater attention to collective and electrically powered travel.', 'C. Making all journeys longer.', 'D. Removing public transport from city centres.'], {'answer': 'B'}, {}),
            (Question.QuestionType.SHORT_ANSWER, 'According to the passage, what year did the first subway system open?', [], {'answer': '1863'}, {'accepted_answers': ['1863'], 'max_words': 1}),
        ]
        self._create_questions(group, questions)
        self.stdout.write(self.style.NOTICE('[4/6] Seeding Reading section (5 questions)...'))
        self.stdout.write(self.style.SUCCESS('      Done'))
        return section

    def _seed_listening(self, test):
        section = Section.objects.create(
            test=test,
            title='Listening',
            section_type=Section.SectionType.LISTENING,
            duration_seconds=1800,
            order=2,
            instruction_text='Listen to the accommodation enquiry and answer the questions.',
            is_published=True,
        )
        audio = AudioAsset.objects.create(
            section=section,
            title='Section 1 - Accommodation Enquiry',
            audio_file='audio_assets/sample-accommodation-enquiry.mp3',
            duration_seconds=180,
            transcript=(
                'Officer: Good morning, Riverside Student Homes. How can I help?\n'
                'Student: I am starting at Metrovale College and need a room from the autumn term.\n'
                'Officer: We have a furnished room near the north campus. What is the best number to reach you on?\n'
                'Student: It is 07700 900123.\n'
                'Officer: Thank you. The monthly rent is 475 pounds, but we have a smaller room for students whose budget is 450 pounds.\n'
                'Student: That would be ideal. I would prefer the quiet Riverside area rather than the city centre.\n'
                'Officer: Riverside is popular because it is close to the cycle path. When would you like to move in?\n'
                'Student: On 15 October, if possible.\n'
                'Officer: I will reserve a viewing for Thursday and email the details this afternoon.'
            ),
            mime_type='audio/mpeg',
            storage_provider='local',
            original_license='Original BandUp sample transcript; audio placeholder.',
            playback_policy={'allow_replay': False, 'allow_seek': False, 'max_play_count': 1, 'lock_answers_after_end': True},
        )
        group = QuestionGroup.objects.create(
            section=section,
            title='Listening Questions 1-4',
            instruction='Complete the form or choose the correct answer.',
            audio_asset=audio,
            order=1,
            is_required=True,
        )
        questions = [
            (Question.QuestionType.FILL_BLANK, "What is the student's phone number?", [], {'answer': '07700 900123'}, {'accepted_answers': ['07700900123', '07700-900123']}),
            (Question.QuestionType.FILL_BLANK, 'What is the student\'s monthly rent budget?', [], {'answer': '£450'}, {'accepted_answers': ['450', '£450', '450 pounds', '450 pound'], 'max_words': 2}),
            (Question.QuestionType.MCQ_SINGLE, 'Which area does the student prefer?', ['A. Riverside', 'B. The city centre', 'C. The north campus', 'D. Paddington'], {'answer': 'A'}, {}),
            (Question.QuestionType.FILL_BLANK, 'When would the student like to move in?', [], {'answer': '15 October'}, {'accepted_answers': ['15 october', '15th october', 'october 15'], 'max_words': 2}),
        ]
        self._create_questions(group, questions)
        map_data = {
            'title': 'Map of the town centre',
            'north': True,
            'spots': [
                {'letter': 'A', 'x': 18, 'y': 25}, {'letter': 'B', 'x': 39, 'y': 20},
                {'letter': 'C', 'x': 63, 'y': 25}, {'letter': 'D', 'x': 82, 'y': 40},
                {'letter': 'E', 'x': 72, 'y': 68}, {'letter': 'F', 'x': 48, 'y': 78},
                {'letter': 'G', 'x': 25, 'y': 68}, {'letter': 'H', 'x': 12, 'y': 47},
            ],
        }
        map_group = QuestionGroup.objects.create(
            section=section,
            title='Listening Questions 5-7: Map Labelling',
            instruction='Look at the map and choose the letter for each place.',
            audio_asset=audio,
            order=2,
            is_required=True,
        )
        for order, (prompt, answer) in enumerate([
            ('The library is at letter ___', 'C'),
            ('The post office is at letter ___', 'F'),
            ('The car park is at letter ___', 'H'),
        ], 5):
            question = Question.objects.create(
                question_group=map_group,
                type=Question.QuestionType.MAP_LABEL,
                prompt=prompt,
                order=order,
                points=1,
                options_json=map_data,
                correct_answer_json={'answer': answer},
                validation_rules_json={'allowed_letters': list('ABCDEFGH')},
                difficulty='bandup-original',
                tags=['sample', 'listening', 'map'],
            )
            CorrectAnswerRule.objects.create(
                question=question,
                rule_type=CorrectAnswerRule.RuleType.EXACT,
                value={'answer': answer},
            )
        return section

    def _seed_writing(self, test):
        section = Section.objects.create(
            test=test,
            title='Writing',
            section_type=Section.SectionType.WRITING,
            duration_seconds=3600,
            order=3,
            instruction_text='Complete both writing tasks. Task 1 should take about 20 minutes and Task 2 about 40 minutes.',
            is_published=True,
        )
        task_group = QuestionGroup.objects.create(section=section, title='Writing Tasks', instruction='Write your answers in the spaces provided.', order=1, is_required=True)
        self._create_questions(task_group, [
            (Question.QuestionType.WRITING_PROMPT, 'The chart below shows electricity consumption in a typical UK household across four seasons. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.', {'chart_type': 'line', 'title': 'Seasonal household electricity consumption', 'x_label': 'Season', 'y_label': 'Consumption (kWh)', 'series': [{'name': '2019', 'data': [{'label': 'Winter', 'value': 3200}, {'label': 'Spring', 'value': 2500}, {'label': 'Summer', 'value': 1800}, {'label': 'Autumn', 'value': 2700}]}, {'name': '2024', 'data': [{'label': 'Winter', 'value': 2900}, {'label': 'Spring', 'value': 2300}, {'label': 'Summer', 'value': 1700}, {'label': 'Autumn', 'value': 2450}]}]}, {'min_words': 150, 'task_number': 1}, {'min_words': 150}),
            (Question.QuestionType.WRITING_PROMPT, 'Some people believe that artificial intelligence will eventually replace most human jobs, while others argue it will create new opportunities. Discuss both views and give your own opinion.', [], {'min_words': 250, 'task_number': 2}, {'min_words': 250}),
        ])
        return section

    def _seed_speaking(self, test):
        section = Section.objects.create(
            test=test,
            title='Speaking',
            section_type=Section.SectionType.SPEAKING,
            duration_seconds=840,
            order=4,
            instruction_text='Respond to each prompt. Preparation and recording times are shown for each part.',
            is_published=True,
        )
        prompts = [
            ('Speaking Part 1', "Let's talk about where you live. Can you describe your hometown or neighborhood?", 30, 60),
            ('Speaking Part 2', 'Cue card: Describe a memorable journey you have taken. You should say: where you went, how you traveled, why you went on the journey, and explain why it was memorable.', 60, 120),
            ('Speaking Part 3', 'How has modern transportation changed the way people live and work in your country?', 10, 90),
        ]
        for order, (title, prompt, prep_seconds, recording_seconds) in enumerate(prompts, 1):
            group = QuestionGroup.objects.create(section=section, title=title, instruction=f'Prepare for {prep_seconds} seconds, then speak for up to {recording_seconds} seconds.', order=order, is_required=True)
            self._create_questions(group, [(Question.QuestionType.SPEAKING_PROMPT, prompt, [], {'prep_seconds': prep_seconds, 'recording_seconds': recording_seconds}, {'prep_seconds': prep_seconds, 'recording_seconds': recording_seconds})])
        self.stdout.write(self.style.NOTICE('[5/6] Seeding Listening/Writing/Speaking...'))
        self.stdout.write(self.style.SUCCESS('      Done'))
        return section

    def _seed_scoring_mappings(self, test):
        mappings = {
            Section.SectionType.READING: [(0, 0.5, 4.0), (0.5, 1.5, 5.0), (1.5, 2.5, 6.0), (2.5, 3.5, 7.0), (3.5, 4.5, 8.0), (4.5, 5.5, 9.0)],
            Section.SectionType.LISTENING: [(0, 0.5, 4.0), (0.5, 1.5, 5.0), (1.5, 2.5, 6.0), (2.5, 3.5, 7.5), (3.5, 4.5, 9.0)],
        }
        for section_type, ranges in mappings.items():
            for raw_score_min, raw_score_max, band_score in ranges:
                ScoringBandMapping.objects.create(
                    test=test,
                    section_type=section_type,
                    raw_score_min=raw_score_min,
                    raw_score_max=raw_score_max,
                    band_score=band_score,
                    is_default=False,
                    description=f'BandUp Original Mock Test 1 {section_type} conversion.',
                )
        self.stdout.write(self.style.NOTICE('[6/6] Setting up scoring mappings...'))
        self.stdout.write(self.style.SUCCESS('      Done'))

    @staticmethod
    def _create_questions(group, question_data):
        for order, (question_type, prompt, options, correct_answer, validation_rules) in enumerate(question_data, 1):
            Question.objects.create(
                question_group=group,
                type=question_type,
                prompt=prompt,
                order=order,
                points=1,
                options_json=options,
                correct_answer_json=correct_answer,
                validation_rules_json=validation_rules,
                difficulty='bandup-original',
                tags=['sample', group.section.section_type],
            )