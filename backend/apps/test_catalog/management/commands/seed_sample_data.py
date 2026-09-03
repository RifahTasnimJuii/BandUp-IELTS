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
            reading = self._seed_reading_expanded(test)
            listening = self._seed_listening_expanded(test)
            self._seed_writing(test)
            self._seed_speaking(test)
            self._seed_scoring_mappings(test)
            test_two = self._create_test_two(admin)
            self._seed_reading_two(test_two)
            self._seed_listening_two(test_two)
            self._seed_writing_two(test_two)
            self._seed_speaking_two(test_two)
            self._seed_scoring_mappings(test_two)

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
        deleted, _ = Test.objects.filter(slug__in=[self.MOCK_TEST_SLUG, 'mock-test-2']).delete()
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

    def _create_test_two(self, admin):
        return Test.objects.create(title='BandUp Original Mock Test 2', slug='mock-test-2', description='A second original IELTS-style practice test with fresh content.', module_type=Test.ModuleType.ACADEMIC, attempt_limit=0, strict_exam_mode=True, allow_practice_replay=True, is_published=True, is_featured=False, created_by=admin, updated_by=admin, default_section_order=['reading', 'listening', 'writing', 'speaking'])

    def _seed_reading_two(self, test):
        section = Section.objects.create(test=test, title='Reading', section_type=Section.SectionType.READING, duration_seconds=3600, order=1, instruction_text='Read three new passages and answer all 40 questions.', is_published=True)
        texts = [
            ('The Secret Life of Trees', 'Trees exchange resources through fungal partners beneath the soil. A mature tree may shade seedlings, slow water loss, and release chemical signals when insects attack. Researchers studying forest plots have found that roots overlap more than older diagrams suggested. This does not mean a forest is a single organism, but it does show that competition and cooperation can occur together.\n\nYoung trees often survive in shadow because older neighbours alter the soil and shelter them from wind. Fungal threads carry minerals toward roots and receive sugars in return. The partnership changes with drought, season, and species. Some trees reduce their own growth while supporting nearby relatives; other results are less predictable. Scientists therefore distinguish observed transfer from claims about intention.\n\nForest managers now use these findings when planning restoration. A mixed canopy can protect soil better than a row of identical trees, and fallen branches create habitat for insects and fungi. Yet connected roots can also spread disease. The secret life below ground is consequently a network of opportunities and risks rather than a simple story of generosity.'),
            ('Ancient Roman Engineering', 'Roman engineers built roads, bridges, aqueducts, and harbours by combining practical surveying with durable materials. Their roads followed military and commercial priorities, but local geography still shaped every route. Surveyors used sighting instruments to establish gradients, while labourers prepared foundations that could drain after heavy rain. A straight road was an achievement only when it remained usable.\n\nAqueducts carried water over long distances using a carefully controlled slope. Arches allowed channels to cross valleys, although many sections ran underground. Maintenance crews removed sediment and repaired leaks. Concrete made from volcanic ash could harden in damp conditions, which helped harbour structures survive waves. The recipe varied according to available stone and ash.\n\nRoman construction depended on organisation as much as invention. Officials secured materials, contractors managed teams, and towns paid for repairs. Some monuments survive because their design was strong; others survive because later communities reused them. Engineering history must therefore consider labour, administration, and adaptation as well as celebrated structures.'),
            ('The Psychology of Memory', 'Memory is not a filing cabinet that stores an event unchanged. It is a reconstruction influenced by attention, emotion, later information, and the questions asked during recall. People can remember the central meaning of a conversation while losing its exact wording. Confidence may increase when a memory is repeated, even if repetition does not make every detail accurate.\n\nAttention determines what enters the system in the first place. Divided attention produces gaps, and stress can narrow focus toward a threatening feature. Sleep helps consolidate some learning, but it does not guarantee a perfect record. Retrieval itself can strengthen a useful pathway while also allowing errors to become familiar.\n\nGood study strategies use retrieval practice, spacing, and meaningful links. A learner who tests themselves after a delay usually builds more durable access than one who only rereads notes. However, memory has a social dimension too: discussion can add useful context or introduce confident misinformation. The practical lesson is to value evidence and revision rather than treating vividness as proof.'),
        ]
        for index, (title, body) in enumerate(texts):
            passage = Passage.objects.create(section=section, title=title, body_text=body, source_note='Original BandUp sample content.', license_note='Created for BandUp demonstration and testing.', is_original_sample=True)
            group = QuestionGroup.objects.create(section=section, title=f'Passage {index + 1} Questions', instruction='Answer using this passage only.', passage=passage, order=index + 1, is_required=True)
            total = 13 if index < 2 else 14
            question_data = []
            for number in range(1, total + 1):
                if index == 0 and number <= 5:
                    question_data.append((Question.QuestionType.TRUE_FALSE_NOT_GIVEN, f'Tree passage statement {number} is supported by the text.', ['True', 'False', 'Not Given'], {'answer': 'True'}, {'accepted_answers': ['true']}))
                elif index == 1 and number <= 4:
                    question_data.append((Question.QuestionType.MATCHING_HEADINGS, f'Choose a heading for paragraph {number}.', ['A. Practical networks', 'B. Materials and maintenance', 'C. Organised construction', 'D. Soil research'], {'answer': 'A'}, {'accepted_answers': ['a']}))
                elif index == 2 and number <= 6:
                    question_data.append((Question.QuestionType.YES_NO_NOT_GIVEN, f'Memory statement {number} agrees with the passage.', ['Yes', 'No', 'Not Given'], {'answer': 'Yes'}, {'accepted_answers': ['yes']}))
                else:
                    question_data.append((Question.QuestionType.MCQ_SINGLE, f'What does the passage emphasise in question {number}?', ['A. Cooperation and evidence', 'B. Competition alone', 'C. A vanished technology', 'D. An unsupported claim'], {'answer': 'A'}, {}))
            self._create_questions(group, question_data)

    def _seed_listening_two(self, test):
        section = Section.objects.create(test=test, title='Listening', section_type=Section.SectionType.LISTENING, duration_seconds=1800, order=2, instruction_text='Listen to four new parts and answer 40 questions.', is_published=True)
        scripts = [(f'Part {index} - Mock Test Two', f'Part {index}. This original announcement gives details for Mock Test Two. The key number is {index * 17}, the appointment is on {index + 4} October, and the meeting place is room {index}05.') for index in range(1, 5)]
        audio = AudioAsset.objects.create(section=section, title='Four-part listening test 2', audio_file='audio_assets/sample-listening-two-placeholder.mp3', duration_seconds=1500, transcript='\n\n'.join(f'{title}. {script}' for title, script in scripts), mime_type='audio/mpeg', is_active=True, playback_policy={'allow_replay': False, 'allow_seek': False})
        for index, (title, script) in enumerate(scripts, 1):
            group = QuestionGroup.objects.create(section=section, title=title, instruction='Complete the notes using the recording.', audio_asset=audio, order=index, is_required=True)
            self._create_questions(group, [(Question.QuestionType.FILL_BLANK, f'Part {index} detail {number}: write the key number.', [], {'answer': str(index * 17)}, {'accepted_answers': [str(index * 17)]}) for number in range(1, 11)])

    def _seed_writing_two(self, test):
        section = Section.objects.create(test=test, title='Writing', section_type=Section.SectionType.WRITING, duration_seconds=3600, order=3, instruction_text='Complete both writing tasks.', is_published=True)
        group = QuestionGroup.objects.create(section=section, title='Writing Tasks', instruction='Write both responses.', order=1, is_required=True)
        self._create_questions(group, [(Question.QuestionType.WRITING_PROMPT, 'The bar chart shows internet users by region. Summarise the main features and make comparisons where relevant.', {'chart_type': 'bar', 'title': 'Internet users by region', 'x_label': 'Region', 'y_label': 'Users (millions)', 'series': [{'name': '2025', 'data': [{'label': 'Asia', 'value': 2900}, {'label': 'Europe', 'value': 750}, {'label': 'Africa', 'value': 600}]}]}, {'task_number': 1, 'answer': ''}, {'min_words': 150}), (Question.QuestionType.WRITING_PROMPT, 'Some people believe remote work improves modern employment, while others think offices are essential. Discuss both views and give your opinion.', [], {'task_number': 2, 'answer': ''}, {'min_words': 250})])

    def _seed_speaking_two(self, test):
        section = Section.objects.create(test=test, title='Speaking', section_type=Section.SectionType.SPEAKING, duration_seconds=840, order=4, instruction_text='Respond to each new speaking prompt.', is_published=True)
        for order, prompt in enumerate(['What do you enjoy about your neighbourhood?', 'Describe a useful skill you learned.', 'How should cities prepare for future work?'], 1):
            group = QuestionGroup.objects.create(section=section, title=f'Speaking Part {order}', instruction='Answer the examiner.', order=order, is_required=True)
            self._create_questions(group, [(Question.QuestionType.SPEAKING_PROMPT, prompt, [], {'prep_seconds': 60 if order == 2 else 0, 'recording_seconds': 120 if order == 2 else 60}, {'prep_seconds': 60 if order == 2 else 0, 'recording_seconds': 120 if order == 2 else 60})])

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

    def _seed_reading_expanded(self, test):
        section = Section.objects.create(test=test, title='Reading', section_type=Section.SectionType.READING, duration_seconds=3600, order=1, instruction_text='Read each passage and answer all 40 questions.', is_published=True)
        passages = [
            ('The History of Lighthouses', '''Before electronic navigation, a light on a dangerous shore was both a practical guide and a public promise. Early coastal communities burned fires on hills, but these flames were unreliable: wind scattered them, rain extinguished them, and a fire high above a harbour could be mistaken for a star. The first organised lighthouse projects therefore combined a raised structure, a protected flame, and a keeper who understood the local sea.

In the ancient Mediterranean, sailors relied on prominent towers as much as on their fires. The Pharos of Alexandria, completed during the third century BCE, became famous because its height made the harbour entrance visible from far offshore. Its designers used mirrors or polished metal to strengthen the daylight signal, although later descriptions probably exaggerate the distance at which the night fire could be seen. The tower also demonstrated that navigation was a civic responsibility rather than merely a private service for merchants.

For many centuries, European lights remained small and local. Monasteries, harbour authorities, and wealthy traders sometimes maintained beacons, but there was no common design. A tower that worked in a sheltered bay could fail on an exposed headland. Fires fuelled by wood or coal produced smoke as well as light, and keepers had to carry heavy fuel up narrow stairs. As shipping increased, the cost of an unmarked reef became more obvious to governments and insurers.

The eighteenth century brought a technical change through better lamps and reflectors. In Britain, engineer John Smeaton rebuilt the Eddystone Lighthouse after earlier structures had been destroyed by storms. His third tower, completed in 1759, used interlocking stone blocks and a curved profile that spread the force of waves. Smeaton did not invent the lighthouse, but he showed that a building could be engineered as a single structure rather than assembled as a pile of masonry.

Light itself also became more controlled. The French engineer Augustin-Jean Fresnel developed a stepped lens that bent and concentrated rays without requiring a huge solid piece of glass. First installed in 1823, the lens allowed a comparatively modest lamp to produce a powerful beam. Rotating screens then created a recognisable pattern of flashes, so sailors could identify one station from another. This was an important shift from simply seeing a light to reading a signal.

The keeper remained central even as machinery improved. A keeper trimmed wicks, polished lenses, recorded weather, helped shipwreck survivors, and reported defects. Remote stations could be isolated for weeks, and families often lived in the same compound. Automation gradually replaced these routines during the twentieth century. Electricity, radio beacons, radar, and satellite positioning reduced the need for a permanent resident, although many stations continued to operate as visual warnings.

Modern navigation rarely depends on a lighthouse alone. Digital charts can show a vessel its position, while radar detects hazards in darkness or fog. Yet coastal lights have not become meaningless. They provide an independent reference when electronics fail, help small boats near harbour entrances, and preserve a shared vocabulary of maritime marks. Their history is therefore not a simple story of obsolete technology; it is a record of engineering, public investment, and the continuing value of visible landmarks.

Preservation has added another chapter. Former stations are now museums, weather observatories, holiday cottages, and research bases. Conservationists must decide whether to restore a tower to an earlier appearance or preserve evidence of later repairs. Salt, wind, and rising maintenance costs make both choices difficult. Local communities often support restoration because a lighthouse can anchor a regional identity and attract visitors, but tourism cannot replace the safety function of an operating light. The best projects therefore separate public access from the lantern and keep modern equipment working alongside historic fabric.'''),
            ('Bee Communication and the Waggle Dance', '''A honeybee colony behaves like a distributed community. No single bee directs every task, yet thousands of individuals coordinate nest building, feeding, guarding, and foraging. Much of this coordination depends on contact, scent, vibration, and a remarkable movement performed by returning foragers. The movement is commonly called the waggle dance because its central phase involves a short run during which the bee shakes its abdomen from side to side.

A forager begins the dance after discovering a useful source of nectar or pollen. Other bees gather around it in a dark area of the hive and touch its body with their antennae. The dancer runs in a straight line, turns in a semicircle, and repeats the route. The direction of the straight run represents the direction of the food in relation to the sun. If the run points upward on the vertical comb, the food lies toward the sun; an angle to the left or right represents the same angle away from the sun in the outside world.

Distance is communicated by the duration of the waggle run and by the effort required to return. A distant source generally produces a longer run, although temperature, wind, and the quality of the route can alter the relationship. Bees do not announce a distance in metres. Instead, their nervous systems combine several clues, creating an estimate that is useful enough for the colony to decide whether a journey is worthwhile.

The message is not a perfect map. The sun moves across the sky, so the dancer must compensate for its changing position. Bees can also navigate using the pattern of polarised light when clouds hide the sun. Experienced foragers appear to adjust their signals, while young bees learn the meaning of the dance through repeated observation. This learning helps explain why the behaviour is both inherited and flexible rather than a fixed mechanical routine.

Recruitment depends on economics as well as geometry. A rich patch of flowers attracts more dancers than a poor patch, and vigorous dances persuade more bees to investigate. The colony can therefore shift its workforce between locations without a central supervisor. If a source dries up, dances become less frequent and attention moves elsewhere. Scent carried on the dancer may provide an additional clue about the flower species, allowing recruits to recognise the target when they leave the hive.

Researchers once assumed that every detail of the dance was interpreted literally. More recent work suggests that bees use the information probabilistically. Recruits may visit the indicated area rather than fly directly to a single flower, and they combine the dance with landscape memory, odour, and the position of landmarks. In this view, the dance is a compact recommendation whose usefulness comes from narrowing a search, not from transmitting coordinates with human precision.

The waggle dance has become a model for studying collective intelligence. It shows how simple signals can produce adaptable decisions when many individuals contribute partial information. It also warns against describing animal communication as either language or noise. Bee signals have structure, consequences, and social context, but they operate within the limits of a bee's senses and needs. Their sophistication lies in the colony's decision-making system, where local actions create a coordinated response.

The dance also changes with the colony's surroundings. A crowded flower patch may cause many bees to return at once, forcing observers to distinguish overlapping signals. Temperature affects how long a forager can fly, and wind can make a distant source less attractive than its measured distance suggests. Beekeepers sometimes move hives beside crops and observe recruitment, but an artificial setting cannot reproduce every woodland or meadow. Studies are consequently compared across seasons and landscapes. This caution matters because communication is useful precisely when it remains responsive to conditions rather than following a rigid code.'''),
            ('The Rise of Vertical Farming', '''Vertical farming places crops in stacked layers inside buildings, often using hydroponic or aeroponic systems instead of soil. The idea grew from controlled-environment agriculture, but recent versions add efficient LEDs, sensors, automated handling, and data analysis. Supporters present the method as a way to produce fresh food near cities while reducing pressure on land. Its success, however, depends on energy, crop choice, labour, and the economics of construction.

Traditional farms receive free sunlight and rely on soil to store water and nutrients. An indoor farm replaces these services with equipment. Plants grow in channels or trays, and a nutrient solution circulates around their roots. Sensors measure acidity, temperature, humidity, and electrical conductivity. Software can adjust the light schedule or irrigation within minutes. Because the environment is enclosed, growers can also limit insects and reduce the need for broad pesticide treatments.

The strongest early business case has involved leafy greens and herbs. Lettuce, basil, and similar crops grow quickly, remain relatively short, and can be harvested close to the customer. Cereals and tree fruit are much more difficult because they require more space or longer growing periods. A building may produce many harvests of a small crop, but its shelves cannot automatically make every crop profitable. Product selection is therefore a technical decision and a marketing decision.

Water efficiency is one of the most frequently cited advantages. Recirculating systems can deliver moisture directly to roots, while evaporation is collected or controlled. Some facilities claim dramatic savings compared with open-field production, but comparisons depend on the baseline. A greenhouse, a carefully irrigated outdoor farm, and a dry field do not use water in the same way. Transport distance and refrigeration also affect the total environmental account.

Electricity is the central limitation. Artificial light, pumps, ventilation, cooling, and climate control operate throughout the year. If the power comes from a carbon-intensive grid, a local indoor crop may have a larger climate footprint than an outdoor crop shipped from a favourable region. Renewable electricity can improve the balance, but batteries, building materials, and replacement equipment have their own costs. A vertical farm is not automatically sustainable simply because it is located in a city.

Automation may reduce repetitive work, yet it does not eliminate skilled labour. Someone must diagnose plant stress, maintain sensors, plan nutrient recipes, and manage disease risks. Operators also need reliable supply chains for seeds, lighting components, and replacement pumps. A short power interruption can damage a crop that has no access to natural light. Redundancy and monitoring are therefore part of production, not optional extras.

The most plausible future is a mixed food system. Indoor farms may supply fragile greens to dense urban markets, while open fields continue to grow staple crops and orchards. Research is exploring better light spectra, renewable heat, and crops with higher nutritional value. The important question is not whether vertical farming will replace agriculture. It is whether particular buildings can use resources efficiently enough to provide a useful service that conventional farms cannot provide nearby.

Location changes the calculation further. A warehouse beside a restaurant district may save time and packaging, whereas a remote facility may gain little from being indoors. Waste heat from factories or data centres could warm growing rooms, and treated urban water might be recirculated rather than discharged. Planning authorities must still consider noise, fire safety, traffic, and the cost of converting old buildings. Consumers may value a local harvest, but they will not necessarily pay enough to cover an expensive system. Vertical farming will therefore be judged less by its novelty than by whether its daily operation fits a particular place.'''),
        ]
        counts = [13, 13, 14]
        for passage_index, ((title, body), count) in enumerate(zip(passages, counts), 1):
            passage = Passage.objects.create(section=section, title=title, body_text=body, source_note='Original BandUp sample content.', license_note='Created for BandUp demonstration and testing.', is_original_sample=True)
            group = QuestionGroup.objects.create(section=section, title=f'Passage {passage_index} Questions', instruction='Answer using the passage only.', passage=passage, order=passage_index, is_required=True)
            questions = []
            if passage_index == 1:
                questions += [(Question.QuestionType.TRUE_FALSE_NOT_GIVEN, prompt, ['True', 'False', 'Not Given'], {'answer': answer}, {'accepted_answers': [answer.lower()]}) for prompt, answer in [('The Pharos was completed during the third century BCE.', 'True'), ('The first lighthouse fires used electricity.', 'Not Given'), ('Smeaton completed his third Eddystone tower in 1759.', 'True'), ('Fresnel invented the first lighthouse.', 'False'), ('Modern navigation never uses visual landmarks.', 'False')]]
                questions += [(Question.QuestionType.MCQ_SINGLE, prompt, options, {'answer': answer}, {}) for prompt, options, answer in [('What did Smeaton demonstrate?', ['A. A curved stone structure could resist waves.', 'B. Coal was safer than oil.', 'C. Mirrors were unnecessary.', 'D. Radio replaced radar.'], 'A'), ('What did the Fresnel lens improve?', ['A. Fuel transport', 'B. Light concentration', 'C. Harbour depth', 'D. Weather recording'], 'B'), ('Why were flashing patterns useful?', ['A. They identified stations.', 'B. They predicted storms.', 'C. They measured tides.', 'D. They called keepers.'], 'A'), ('Which service did keepers provide?', ['A. They designed satellites.', 'B. They maintained equipment and helped survivors.', 'C. They sold cargo.', 'D. They mapped continents.'], 'B')]]
                questions += [(Question.QuestionType.SENTENCE_COMPLETION, prompt, [], {'answer': answer}, {'accepted_answers': [answer.lower()], 'max_words': 2}) for prompt, answer in [('The Pharos used polished metal or ______ to strengthen daylight signals.', 'mirrors'), ('Smeaton used interlocking ______ blocks.', 'stone'), ('A Fresnel lens created a powerful ______.', 'beam'), ('Radio beacons and ______ reduced the need for keepers.', 'radar')]]
            elif passage_index == 2:
                headings = ['i The limits of a perfect map', 'ii A colony without a manager', 'iii Signals in a dark room', 'iv How distance is estimated', 'v An inherited but flexible skill', 'vi Economic choices in the hive', 'vii A modern research controversy', 'viii The first farming bees']
                questions += [(Question.QuestionType.MATCHING_HEADINGS, f'Choose the best heading for paragraph {number}.', headings, {'answer': answer}, {'accepted_answers': [answer]}) for number, answer in [(1, 'ii'), (2, 'iii'), (3, 'iv'), (4, 'v')]]
                features = ['waggle duration', 'sun angle', 'flower scent', 'polarised light', 'dance frequency']
                questions += [(Question.QuestionType.MATCHING_ITEMS, f'Which feature helps with {prompt}?', features, {'answer': answer}, {'accepted_answers': [answer]}) for prompt, answer in [('estimating distance', 'waggle duration'), ('finding direction', 'sun angle'), ('recognising flower species', 'flower scent'), ('navigation when clouds hide the sun', 'polarised light'), ('showing that a source is rich', 'dance frequency')]]
                bank = ['coordinates', 'probabilistically', 'search', 'landmarks']
                questions += [(Question.QuestionType.SUMMARY_COMPLETION, prompt, bank, {'answer': answer}, {'accepted_answers': [answer], 'max_words': 1}) for prompt, answer in [('The dance is best understood as a recommendation rather than exact ______.', 'coordinates'), ('Recruits interpret signals ______.', 'probabilistically'), ('The message narrows a ______ area.', 'search'), ('Bees combine signals with memories of ______.', 'landmarks')]]
            else:
                questions += [(Question.QuestionType.YES_NO_NOT_GIVEN, prompt, ['Yes', 'No', 'Not Given'], {'answer': answer}, {'accepted_answers': [answer.lower()]}) for prompt, answer in [('Vertical farming uses stacked growing layers.', 'Yes'), ('All crops are equally suitable for indoor production.', 'No'), ('Traditional farms pay for sunlight.', 'Not Given'), ('Indoor farms always use less water than greenhouses.', 'Not Given'), ('Electricity is a major limitation.', 'Yes'), ('Automation removes the need for skilled workers.', 'No')]]
                questions += [(Question.QuestionType.MCQ_SINGLE, prompt, options, {'answer': answer}, {}) for prompt, options, answer in [('Which crops are an early business focus?', ['A. Leafy greens and herbs', 'B. Wheat and rice', 'C. Tree fruit', 'D. Timber'], 'A'), ('What do sensors measure?', ['A. Ocean tides', 'B. Acidity and humidity', 'C. Road traffic', 'D. Wind direction'], 'B'), ('What can renewable electricity improve?', ['A. The environmental balance', 'B. Crop height', 'C. Soil depth', 'D. Fruit colour'], 'A'), ('What future does the passage consider most plausible?', ['A. Indoor farms replace all fields.', 'B. A mixed food system.', 'C. Cities stop eating greens.', 'D. Farms abandon technology.'], 'B')]]
                questions += [(Question.QuestionType.SHORT_ANSWER, prompt, [], {'answer': answer}, {'accepted_answers': [answer.lower()], 'max_words': 3}) for prompt, answer in [('What circulates around plant roots?', 'nutrient solution'), ('What kind of crops may indoor farms supply to cities?', 'fragile greens'), ('What can damage a crop during an interruption?', 'power failure'), ('What must operators diagnose?', 'plant stress')]]
            self._create_questions(group, questions)
        self.stdout.write(self.style.NOTICE('[4/6] Seeding Reading section (40 questions)...'))
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

    def _seed_listening_expanded(self, test):
        section = Section.objects.create(test=test, title='Listening', section_type=Section.SectionType.LISTENING, duration_seconds=1800, order=2, instruction_text='Listen once to all four parts and answer 40 questions.', is_published=True)
        scripts = [
            ('Part 1 - Gym Membership Booking', 'Receptionist: Good morning, Northgate Fitness. Caller: I would like to join. Receptionist: Please give me your name. Caller: Maya Rahman, R-A-H-M-A-N. Receptionist: Your phone number? Caller: 07700 246810. Receptionist: The monthly price is 32 pounds, or 28 pounds for students. Caller: I am a student. Receptionist: Your membership begins on 6 September. The swimming pool opens at 6:30, and the gym opens at 6. Caller: I would like an induction on Tuesday. Receptionist: That is 10 September at 5 pm.'),
            ('Part 2 - Museum Opening Announcement', 'Welcome to the new Harbour Museum. The main entrance is beside the clock tower at map letter B. The cafe is at letter D, opposite the entrance. The accessible lift is at letter F. The model boat gallery is at letter H, beside the river. The shop is at letter E. The museum opens to the public on Saturday 14 June. Adults pay 8 pounds, children enter for 4 pounds, and members enter free. The first guided tour starts at 11:15.'),
            ('Part 3 - Student Project Discussion', 'Tutor: How is the river project progressing? Lina: Our survey had  eighty participants. Omar: I analysed the water samples, while Lina interviewed residents. Tutor: The introduction needs a clearer definition of pollution. Lina: We will add one tomorrow. Omar: Could we move the presentation to Thursday? Tutor: Friday is available at 2 pm. Lina: We also need three photographs and a map. Tutor: Use the library archive for the historical photograph. Omar: I will prepare the conclusion, and Lina will design the slides.'),
            ('Part 4 - Sleep Science Lecture', 'Today we examine sleep science. Adults usually need between seven and nine hours. During stage two, body temperature falls and heart rate slows. Deep sleep supports physical repair. REM sleep is associated with vivid dreams and memory processing. Light exposure in the evening can delay melatonin release. Researchers recommend a regular wake time rather than simply sleeping late at weekends. Caffeine has a half-life of about five hours, so afternoon coffee may affect night sleep. Short naps can improve alertness, but long late naps may reduce sleep pressure.'),
        ]
        audio = AudioAsset.objects.create(section=section, title='Four-part listening test', audio_file='audio_assets/sample-listening-placeholder.mp3', duration_seconds=1500, transcript='\n\n'.join(f'{title}. {script}' for title, script in scripts), mime_type='audio/mpeg', storage_provider='local', original_license='Original BandUp sample transcript; audio placeholder.', playback_policy={'allow_replay': False, 'allow_seek': False, 'max_play_count': 1, 'lock_answers_after_end': True})
        for part, (title, script) in enumerate(scripts, 1):
            group = QuestionGroup.objects.create(section=section, title=title, instruction='Complete the notes or choose the correct answer.', audio_asset=audio, order=part, is_required=True)
            if part == 1:
                data = [(Question.QuestionType.FILL_BLANK, prompt, [], {'answer': answer}, {'accepted_answers': [answer.lower()], 'max_words': 3}) for prompt, answer in [('Member name: Maya ______', 'Rahman'), ('Telephone: 07700 ______', '246810'), ('Student monthly price: ______ pounds', '28'), ('Membership starts: ______ September', '6'), ('Induction: Tuesday at ______ pm', '5')]]
                data += [(Question.QuestionType.MCQ_SINGLE, prompt, options, {'answer': answer}, {}) for prompt, options, answer in [('When does the gym open?', ['A. 5:00', 'B. 6:00', 'C. 6:30', 'D. 10:00'], 'B'), ('Who receives the lower price?', ['A. Visitors', 'B. Staff', 'C. Students', 'D. Children'], 'C'), ('What does the caller want?', ['A. An induction', 'B. A refund', 'C. A lesson', 'D. A locker'], 'A'), ('How much is the standard monthly fee?', ['A. 24 pounds', 'B. 28 pounds', 'C. 32 pounds', 'D. 38 pounds'], 'C'), ('Which spelling is given?', ['A. Rahman', 'B. Raman', 'C. Rehman', 'D. Rayman'], 'A')]]
            elif part == 2:
                map_data = {'title': 'Harbour Museum', 'north': True, 'spots': [{'letter': letter, 'x': 12 + index * 11, 'y': 25 + (index % 3) * 18} for index, letter in enumerate('ABCDEFGH')]}
                data = [(Question.QuestionType.MAP_LABEL, f'{place} is at letter ___', [], {'answer': answer}, {'allowed_letters': list('ABCDEFGH')}) for place, answer in [('main entrance', 'B'), ('cafe', 'D'), ('accessible lift', 'F'), ('model boat gallery', 'H'), ('shop', 'E')]]
                data = [(kind, prompt, map_data if kind == Question.QuestionType.MAP_LABEL else options, answer, rules) for kind, prompt, options, answer, rules in data]
                data += [(Question.QuestionType.MCQ_SINGLE, prompt, options, {'answer': answer}, {}) for prompt, options, answer in [('When does the museum open?', ['A. Friday', 'B. Saturday', 'C. Sunday', 'D. Monday'], 'B'), ('What is the adult fee?', ['A. 4 pounds', 'B. 6 pounds', 'C. 8 pounds', 'D. 14 pounds'], 'C'), ('Who enters free?', ['A. Children', 'B. Members', 'C. Tourists', 'D. Students'], 'B'), ('When is the first tour?', ['A. 10:15', 'B. 11:15', 'C. 12:15', 'D. 2:00'], 'B'), ('Where is the cafe?', ['A. Beside the river', 'B. Opposite the entrance', 'C. Beside the shop', 'D. In the tower'], 'B')]]
            elif part == 3:
                data = [(Question.QuestionType.MCQ_SINGLE, prompt, options, {'answer': answer}, {}) for prompt, options, answer in [('How many people joined the survey?', ['A. 18', 'B. 40', 'C. 80', 'D. 180'], 'C'), ('Who analysed water samples?', ['A. Lina', 'B. Omar', 'C. The tutor', 'D. Residents'], 'B'), ('What needs clearer definition?', ['A. The conclusion', 'B. The map', 'C. Pollution', 'D. The slides'], 'C'), ('When might the presentation occur?', ['A. Monday', 'B. Tuesday', 'C. Thursday', 'D. Sunday'], 'C'), ('What will Lina design?', ['A. Slides', 'B. A conclusion', 'C. Samples', 'D. An archive'], 'A')]]
                data += [(Question.QuestionType.MATCHING_ITEMS, prompt, ['Lina', 'Omar', 'Tutor'], {'answer': answer}, {'accepted_answers': [answer.lower()]}) for prompt, answer in [('Will prepare the conclusion', 'Omar'), ('Will design the slides', 'Lina'), ('Provided the archive suggestion', 'Tutor'), ('Interviewed residents', 'Lina'), ('Analysed water samples', 'Omar')]]
            else:
                data = [(Question.QuestionType.SENTENCE_COMPLETION, prompt, [], {'answer': answer}, {'accepted_answers': [answer.lower()], 'max_words': 3}) for prompt, answer in [('Adults usually need seven to ______ hours.', 'nine'), ('During stage two, body ______ falls.', 'temperature'), ('Deep sleep supports physical ______.', 'repair'), ('REM sleep helps with memory ______.', 'processing'), ('Evening light can delay ______ release.', 'melatonin')]]
                data += [(Question.QuestionType.MCQ_SINGLE, prompt, options, {'answer': answer}, {}) for prompt, options, answer in [('What do researchers recommend?', ['A. A regular wake time', 'B. Sleeping late', 'C. Long naps', 'D. No routine'], 'A'), ('How long is caffeine half-life?', ['A. 2 hours', 'B. 5 hours', 'C. 7 hours', 'D. 9 hours'], 'B'), ('What can short naps improve?', ['A. Appetite', 'B. Alertness', 'C. Temperature', 'D. Dreams'], 'B'), ('What may reduce sleep pressure?', ['A. Early exercise', 'B. Long late naps', 'C. Water', 'D. Morning light'], 'B'), ('What is linked with vivid dreams?', ['A. REM sleep', 'B. Stage one', 'C. Deep sleep', 'D. Wake time'], 'A')]]
            self._create_questions(group, data)
        self.stdout.write(self.style.NOTICE('[5/6] Seeding Listening section (40 questions)...'))
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
            Section.SectionType.READING: [(0, 8, 4.0), (8, 13, 4.5), (13, 18, 5.0), (18, 23, 5.5), (23, 26, 6.0), (26, 29, 6.5), (29, 32, 7.0), (32, 34, 7.5), (34, 36, 8.0), (36, 39, 8.5), (39, 41, 9.0)],
            Section.SectionType.LISTENING: [(0, 8, 4.0), (8, 13, 4.5), (13, 18, 5.0), (18, 23, 5.5), (23, 26, 6.0), (26, 29, 6.5), (29, 32, 7.0), (32, 34, 7.5), (34, 36, 8.0), (36, 39, 8.5), (39, 41, 9.0)],
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
            question = Question.objects.create(
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
            answer = correct_answer.get('answer', '') if isinstance(correct_answer, dict) else correct_answer
            accepted = validation_rules.get('accepted_answers') if isinstance(validation_rules, dict) else None
            CorrectAnswerRule.objects.create(question=question, rule_type=CorrectAnswerRule.RuleType.ACCEPTED_VARIANTS if accepted else CorrectAnswerRule.RuleType.EXACT, accepted_answers=accepted or [], value={'answer': answer}, max_words=validation_rules.get('max_words') if isinstance(validation_rules, dict) else None, case_sensitive=False)