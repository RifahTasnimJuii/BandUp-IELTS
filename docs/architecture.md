# BandUp IELTS Architecture

## Overview

BandUp IELTS is an IELTS-style mock test platform built as a production-ready monorepo. It supports Listening, Reading, Writing, and Speaking practice with server-authoritative timing, async AI evaluation, admin-managed content, analytics, and secure exam workflows.

This architecture document consolidates the approved Phase 1 specification, including monorepo structure, backend apps, frontend routes, data models, API design, real-time integrations, Celery tasks, admin capabilities, security, and product rules.

---

## Monorepo Structure

```
/
├── backend/
├── frontend/
├── docker/
├── docs/
├── scripts/
├── README.md
├── .env.example
└── docker-compose.yml
```

### Directory purposes

- `backend/`: Python/Django backend scaffold, apps, configuration, and requirements.
- `frontend/`: Next.js App Router scaffold, TypeScript configuration, and frontend assets.
- `docker/`: service container build files and local environment artifacts.
- `docs/`: architecture, API, data model, deployment, and security documentation.
- `scripts/`: helper scripts for setup, seeding, local startup, and testing.
- `README.md`: monorepo overview and developer guidance.
- `.env.example`: environment variable template for local and production setups.
- `docker-compose.yml`: local development container orchestration.

---

## Backend App Structure

Backend apps are organized to separate domain responsibilities and avoid naming collisions.

- `accounts`
- `common`
- `test_catalog`
- `questions`
- `attempts`
- `exam_engine`
- `listening`
- `reading`
- `writing`
- `speaking`
- `grading`
- `ai_evaluation`
- `analytics`
- `admin_dashboard`

### App responsibilities

- `accounts`: authentication, registration, JWT, OAuth, profiles, consent.
- `common`: shared models, utilities, permissions, mixins.
- `test_catalog`: test definitions, metadata, publication, section sequences.
- `questions`: question bank, answer options, validation rules.
- `attempts`: exam and practice attempt lifecycle, autosave, responses.
- `exam_engine`: timing, state machine, violation detection, heartbeat.
- `listening`, `reading`, `writing`, `speaking`: module-specific content and interaction logic.
- `grading`: scoring, band mapping, results aggregation.
- `ai_evaluation`: async writing/speaking evaluation orchestration and validation.
- `analytics`: user metrics, leaderboards, progress insights.
- `admin_dashboard`: admin CRUD, import/export, content management.

---

## Frontend Route Map

### Public Routes

- `/`
- `/tests`
- `/tests/[slug]`
- `/login`
- `/register`
- `/forgot-password`
- `/privacy-policy`
- `/terms`

### User Routes

- `/dashboard`
- `/exam/[attemptId]`
- `/exam/[attemptId]/instructions`
- `/results/[attemptId]`
- `/results/[attemptId]/review`
- `/analytics`
- `/practice`
- `/profile`
- `/settings`
- `/leaderboard`

### Admin Routes

- `/admin-dashboard`
- `/admin-dashboard/tests`
- `/admin-dashboard/tests/[id]`
- `/admin-dashboard/tests/[id]/builder`
- `/admin-dashboard/questions`
- `/admin-dashboard/passages`
- `/admin-dashboard/audio`
- `/admin-dashboard/users`
- `/admin-dashboard/attempts`
- `/admin-dashboard/attempts/[id]`
- `/admin-dashboard/evaluations`
- `/admin-dashboard/violations`
- `/admin-dashboard/analytics`
- `/admin-dashboard/import-export`

### SEO Rules

- Public pages should use SSR/SSG where appropriate.
- Include meta tags, Open Graph tags, `sitemap.xml`, and `robots.txt`.
- Protect exam pages and any private pages with `noindex`.

---

## Database Model Summary

### UUID Primary Key Policy

All primary domain models use UUID primary keys unless there is a strong technical reason not to.

### User

Fields:
- `id` UUID PK
- `email` unique
- `username` unique
- `password`
- `full_name` optional
- `role` enum: `student`, `content_editor`, `admin`, `superadmin`
- `auth_provider` enum: `email`, `google`
- `email_verified`
- `is_active`
- `is_staff`
- `is_superuser`
- `date_joined`
- `last_login`

Relationships:
- `Profile`
- `AuditLog`
- `Attempt`
- `AIEvaluation`

### Profile

Fields:
- `id` UUID PK
- `user` one-to-one
- `target_band` decimal optional
- `country` optional
- `language_preference` enum: `en`, `bn`
- `timezone`
- `dark_mode` boolean
- `leaderboard_opt_in` boolean default `false`
- `exam_instructions_acknowledged` boolean default `false`
- `streak_count` integer default `0`
- `last_practice_at` datetime optional
- `avatar_url`
- `bio`
- `speaking_audio_consent` boolean default `false`
- `created_at`
- `updated_at`

### Test

Fields:
- `id` UUID PK
- `slug` unique
- `title`
- `description`
- `instructions`
- `module_type` enum: `academic`, `general`, `both`
- `attempt_limit` integer nullable
- `strict_exam_mode` boolean
- `allow_practice_replay` boolean
- `copy_protection_enabled` boolean
- `default_section_order` JSON
- `is_published`
- `is_featured`
- `published_at`
- `scoring_config` JSON
- `created_by` FK
- `updated_by` FK
- `created_at`
- `updated_at`

Notes:
- `mode` is a recommendation only; actual attempt mode is decided by `Attempt.mode`.

### Section

Fields:
- `id` UUID PK
- `test` FK
- `title`
- `section_type` enum: `listening`, `reading`, `writing`, `speaking`
- `duration_seconds`
- `extra_transfer_time_seconds` nullable
- `instruction_text`
- `order`
- `is_locked_by_default`
- `is_published`
- `created_at`
- `updated_at`

Constraints:
- unique on `test + section_type + order`

### Passage

Fields:
- `id` UUID PK
- `section` FK
- `title`
- `body_text`
- `source_note`
- `license_note`
- `is_original_sample`
- `is_copyable_default` boolean default `true`
- `word_count`
- `order`
- `created_at`
- `updated_at`

Rules:
- passages are text-based and selectable/copyable by default
- no image-based passages
- only original or properly licensed content

### AudioAsset

Fields:
- `id` UUID PK
- `section` FK optional
- `title`
- `audio_file` or `storage_key`
- `duration_seconds`
- `transcript` optional
- `mime_type`
- `storage_provider`
- `signed_url_expires_at`
- `original_license`
- `is_active`
- `playback_policy` JSON
- `created_at`
- `updated_at`

Playback policy fields:
- `allow_replay`
- `allow_seek`
- `max_play_count`
- `lock_answers_after_end`

Defaults for listening exam:
- replay disabled
- seek disabled or restricted
- answers lock after end

### QuestionGroup

Fields:
- `id` UUID PK
- `section` FK
- `title`
- `instruction`
- `passage` FK optional
- `audio_asset` FK optional
- `order`
- `is_required`
- `created_at`
- `updated_at`

Notes:
- does not force a single question type
- groups can contain multiple question types

### Question

Fields:
- `id` UUID PK
- `question_group` FK
- `type` enum: `mcq_single`, `mcq_multiple`, `true_false_not_given`, `yes_no_not_given`, `fill_blank`, `sentence_completion`, `summary_completion`, `matching_headings`, `matching_items`, `short_answer`, `writing_prompt`, `speaking_prompt`
- `prompt`
- `instruction`
- `order`
- `points`
- `options_json` JSON
- `correct_answer_json` JSON admin-only
- `validation_rules_json` JSON
- `explanation` optional
- `difficulty` optional
- `tags` optional
- `is_active`
- `created_at`
- `updated_at`

Security:
- `correct_answer_json` must never be exposed to exam users before submission

Speaking question metadata may include:
- `part_number`
- `prep_seconds`
- `max_recording_seconds`
- `min_recording_seconds`

Writing question metadata may include:
- `task_number`
- `min_words`
- `recommended_minutes`

### AnswerOption

Fields:
- `id` UUID PK
- `question` FK
- `text`
- `order`
- `explanation`
- `metadata` JSON

Notes:
- preferred approach is to remove `is_correct`
- correctness stored in `CorrectAnswerRule`
- if `is_correct` remains, it is admin-only and never serialized for exam users

### CorrectAnswerRule

Fields:
- `id` UUID PK
- `question` FK
- `rule_type` enum: `exact`, `accepted_variants`, `contains`, `regex`, `keyword_set`, `numeric_tolerance`, `date_variants`, `matching_pairs`, `manual_review`, `semantic`
- `accepted_answers` JSON array
- `value` text or JSON
- `case_sensitive` boolean
- `trim_whitespace` boolean
- `ignore_punctuation` boolean
- `max_words` nullable
- `min_words` nullable
- `partial_credit` boolean
- `points_override`
- `metadata` JSON
- `is_active`
- `priority` optional
- `created_by` FK
- `updated_by` FK
- `created_at`
- `updated_at`

Validation:
- rule_type must match question type
- accepted_answers must be valid JSON arrays when applicable
- regex rules must compile
- matching rules require valid pair structures
- numeric tolerance rules require valid metadata
- manual_review rules do not auto-grade

Indexes:
- `question`
- `rule_type`

### ScoringBandMapping

Fields:
- `id` UUID PK
- `test` FK nullable
- `section_type` enum: `listening`, `reading`, `writing`, `speaking`
- `raw_score_min`
- `raw_score_max`
- `band_score` decimal max_digits=3, decimal_places=2
- `is_default`
- `description`
- `created_at`
- `updated_at`

Rules:
- raw score ranges for the same `test` and `section_type` must not overlap
- `test` null indicates global default mapping
- test-specific mappings override global defaults
- band_score must range 0.0 to 9.0
- support half bands like 6.5, 7.0, 7.5

### Attempt

Fields:
- `id` UUID PK
- `user` FK
- `test` FK
- `mode` enum: `practice`, `exam`
- `state` enum: `created`, `in_progress`, `submitted`, `expired`, `evaluating`, `completed`, `failed`
- `started_at`
- `expires_at`
- `submitted_at`
- `ended_at`
- `current_section` FK optional
- `attempt_number`
- `last_heartbeat_at`
- `server_start_time`
- `client_timezone`
- `locale`
- `device_info` JSON
- `violation_count`
- `is_auto_submitted`
- `is_review_allowed`
- `overall_band` decimal optional
- `listening_band` decimal nullable
- `reading_band` decimal nullable
- `writing_band` decimal nullable
- `speaking_band` decimal nullable
- `audit_reason`
- `created_at`
- `updated_at`

Indexes:
- `user`
- `test`
- `state`
- `expires_at`
- `created_at`

Rules:
- `Test.attempt_limit = 1` blocks duplicate active or submitted attempts unless admin overrides
- exam mode attempts cannot pause unless explicitly configured
- practice mode may allow pause/resume if permitted
- `expires_at` is server-generated
- `server_start_time` is authoritative for timer sync

### AttemptSectionState

Fields:
- `id` UUID PK
- `attempt` FK
- `section` FK
- `state` enum: `pending`, `active`, `completed`, `skipped`, `locked`
- `started_at`
- `ends_at`
- `completed_at`
- `remaining_seconds`
- `duration_seconds`
- `raw_score` nullable
- `band_score` nullable
- `is_locked`
- `autosave_timestamp`
- `created_at`
- `updated_at`

Constraints:
- unique `attempt + section`

### AnswerResponse

Fields:
- `id` UUID PK
- `attempt` FK
- `question` FK
- `value_json` JSON
- `answer_text` optional
- `selected_options` optional
- `is_flagged`
- `is_cleared`
- `is_locked`
- `locked_at`
- `submitted_at`
- `updated_at`
- `metadata` JSON

Constraints:
- unique `attempt + question`

Notes:
- objective answers are stored in `AnswerResponse`
- writing answers are stored in `WritingSubmission`
- speaking responses are stored in `SpeakingAudioSubmission`

### WritingSubmission

Fields:
- `id` UUID PK
- `attempt` FK
- `question` FK
- `task_number` enum: `1`, `2`
- `prompt`
- `answer_text`
- `word_count`
- `below_min_word_warning` boolean
- `submitted_at`
- `evaluation_status` enum: `pending`, `in_progress`, `completed`, `failed`, `pending_human_review`
- `band_score` decimal
- `criteria_scores` JSON
- `ai_feedback` text
- `strengths` JSON
- `weaknesses` JSON
- `improvement_suggestions` JSON
- `model_name`
- `prompt_version`
- `token_usage` integer optional
- `estimated_cost` decimal optional
- `latency_ms` optional
- `manual_override_score`
- `manual_feedback`
- `created_at`
- `updated_at`

Constraints:
- unique `attempt + question`
- fallback unique logic on `attempt + task_number` if question is optional

Rules:
- word count is calculated server-side
- below-minimum word count produces a warning by default
- writing evaluation is asynchronous
- AI failure moves submission to `pending_human_review`

### SpeakingAudioSubmission

Fields:
- `id` UUID PK
- `attempt` FK
- `question` FK
- `part_number` enum: `1`, `2`, `3`
- `prompt` text snapshot
- `storage_key`
- `audio_file_url_method` enum: `signed_url`, `private_media`
- `duration_seconds`
- `mime_type`
- `uploaded_at`
- `prep_seconds_allowed` optional
- `prep_seconds_used` optional
- `recording_started_at` optional
- `recording_ended_at` optional
- `transcript` text nullable
- `transcription_status` enum: `pending`, `in_progress`, `completed`, `failed`
- `evaluation_status` enum: `pending`, `in_progress`, `completed`, `failed`, `pending_human_review`
- `band_score` decimal nullable, max_digits=3, decimal_places=2
- `criteria_scores` JSON
- `ai_feedback` text
- `strengths` JSON
- `weaknesses` JSON
- `improvement_suggestions` JSON
- `model_name`
- `prompt_version`
- `token_usage` integer optional
- `estimated_cost` decimal optional
- `latency_ms` optional
- `manual_override_score` decimal optional
- `manual_feedback` text optional
- `consent_given` boolean
- `created_at`
- `updated_at`

Criteria schema example:
```json
{
  "fluency_coherence": 6.5,
  "lexical_resource": 6.5,
  "grammar": 6.5,
  "pronunciation": 6.5
}
```

### AIEvaluation

Fields:
- `id` UUID PK
- `writing_submission` FK nullable
- `speaking_submission` FK nullable
- `status` enum: `pending`, `started`, `completed`, `failed`, `pending_human_review`
- `provider`
- `model_name`
- `prompt_version`
- `request_payload` JSON
- `response_payload` JSON
- `score` decimal nullable
- `criteria_scores` JSON
- `feedback` text
- `strengths` JSON optional
- `weaknesses` JSON optional
- `improvement_suggestions` JSON optional
- `error_message`
- `retry_count`
- `token_usage` integer optional
- `estimated_cost` decimal optional
- `latency_ms` optional
- `started_at`
- `completed_at`
- `created_at`
- `updated_at`

Constraints:
- exactly one of `writing_submission` or `speaking_submission` must be set

Rules:
- validate AI output before saving
- retry once if invalid
- fallback to `pending_human_review` if still invalid
- AI failure must not crash the attempt

### ExamViolationEvent

Fields:
- `id` UUID PK
- `attempt` FK
- `violation_type` enum: `tab_switch`, `visibility_hidden`, `fullscreen_exit`, `copy_attempt`, `paste_attempt`, `multiple_tabs`, `network_disconnect`, `no_heartbeat`, `audio_playback_error`, `manual_review`
- `details` text
- `metadata` JSON
- `severity` enum: `warning`, `critical`
- `auto_action_taken` enum: `none`, `warning_shown`, `attempt_locked`, `auto_submitted`
- `created_at`
- `resolved_at`

Rules:
- log violations server-side
- admin configures warning thresholds
- repeated critical violations may auto-submit
- the platform avoids proctoring claims

### DailyPracticeActivity

Fields:
- `id` UUID PK
- `user` FK
- `date`
- `practice_minutes`
- `sections_completed`
- `tests_started`
- `tests_completed`
- `questions_answered`
- `average_band` decimal nullable
- `score_progress` JSON
- `created_at`
- `updated_at`

Constraints:
- unique `user + date`

### LeaderboardEntry

Fields:
- `id` UUID PK
- `user` FK
- `period` enum: `weekly`, `monthly`, `all_time`
- `score_type` enum: `overall_band`, `practice_points`
- `rank`
- `band_score` decimal nullable
- `score` decimal optional
- `completed_tests`
- `last_active_at`
- `computed_at`

Rules:
- include only users with `Profile.leaderboard_opt_in = true`
- do not expose email or sensitive data
- support privacy-safe display

### AuditLog

Fields:
- `id` UUID PK
- `actor` FK optional
- `user` FK optional
- `action` enum: `register`, `login`, `logout`, `password_reset_requested`, `password_reset_completed`, `attempt_start`, `attempt_submit`, `attempt_auto_submit`, `attempt_expired`, `violation_logged`, `admin_create`, `admin_update`, `admin_delete`, `content_publish`, `content_unpublish`, `ai_evaluation_started`, `ai_evaluation_completed`, `ai_evaluation_failed`, `ai_evaluation_retry`, `permission_change`, `user_role_change`
- `target_type`
- `target_id`
- `details` JSON
- `ip_address`
- `user_agent`
- `created_at`

---

## Exam State Machine

States:
- `created`
- `in_progress`
- `submitted`
- `expired`
- `evaluating`
- `completed`
- `failed`

---

## API Endpoint Plan

### Auth
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/auth/logout/`
- `POST /api/auth/password-reset/`
- `POST /api/auth/password-reset-confirm/`
- `GET /api/auth/me/`
- `PATCH /api/auth/me/`
- `POST /api/auth/google-oauth/`

### Profile
- `GET /api/profile/`
- `PATCH /api/profile/`
- `GET /api/profile/preferences/`
- `PATCH /api/profile/preferences/`
- `PATCH /api/profile/consent/`

### Tests
- `GET /api/tests/`
- `GET /api/tests/{slug}/`
- `GET /api/tests/{slug}/sections/`
- `GET /api/tests/{slug}/preview/`
- `POST /api/tests/{slug}/start-attempt/`

### Attempts
- `GET /api/attempts/{attemptId}/`
- `GET /api/attempts/{attemptId}/state/`
- `POST /api/attempts/{attemptId}/heartbeat/`
- `POST /api/attempts/{attemptId}/autosave/`
- `POST /api/attempts/{attemptId}/violations/`
- `POST /api/attempts/{attemptId}/submit/`

### Results
- `GET /api/results/{attemptId}/`
- `GET /api/results/{attemptId}/feedback/`
- `GET /api/results/{attemptId}/review/`

### Speaking
- `POST /api/attempts/{attemptId}/speaking/consent/`
- `POST /api/attempts/{attemptId}/speaking/upload-init/`
- `POST /api/attempts/{attemptId}/speaking/upload/`
- `POST /api/attempts/{attemptId}/speaking/upload-complete/`
- `GET /api/attempts/{attemptId}/speaking/{submissionId}/`
- `GET /api/attempts/{attemptId}/speaking/{submissionId}/status/`

### Writing
- `POST /api/attempts/{attemptId}/writing/submit/`
- `GET /api/attempts/{attemptId}/writing/{submissionId}/status/`

### Listening Audio
- `GET /api/attempts/{attemptId}/listening/audio/{audioId}/signed-url/`

### Analytics
- `GET /api/analytics/dashboard/`
- `GET /api/analytics/score-trend/`
- `GET /api/analytics/weak-areas/`
- `GET /api/analytics/question-type-accuracy/`
- `GET /api/analytics/practice-history/`
- `GET /api/analytics/streak/`
- `GET /api/analytics/leaderboard/`

### Admin CRUD and Actions
- `GET /api/admin/tests/`
- `POST /api/admin/tests/`
- `PATCH /api/admin/tests/{id}/`
- `DELETE /api/admin/tests/{id}/`
- `GET /api/admin/sections/`
- `POST /api/admin/sections/`
- `PATCH /api/admin/sections/{id}/`
- `DELETE /api/admin/sections/{id}/`
- `GET /api/admin/passages/`
- `POST /api/admin/passages/`
- `PATCH /api/admin/passages/{id}/`
- `DELETE /api/admin/passages/{id}/`
- `GET /api/admin/audio-assets/`
- `POST /api/admin/audio-assets/`
- `PATCH /api/admin/audio-assets/{id}/`
- `DELETE /api/admin/audio-assets/{id}/`
- `GET /api/admin/question-groups/`
- `POST /api/admin/question-groups/`
- `PATCH /api/admin/question-groups/{id}/`
- `DELETE /api/admin/question-groups/{id}/`
- `GET /api/admin/questions/`
- `POST /api/admin/questions/`
- `PATCH /api/admin/questions/{id}/`
- `DELETE /api/admin/questions/{id}/`
- `GET /api/admin/answer-options/`
- `POST /api/admin/answer-options/`
- `PATCH /api/admin/answer-options/{id}/`
- `DELETE /api/admin/answer-options/{id}/`
- `GET /api/admin/correct-answer-rules/`
- `POST /api/admin/correct-answer-rules/`
- `PATCH /api/admin/correct-answer-rules/{id}/`
- `DELETE /api/admin/correct-answer-rules/{id}/`
- `GET /api/admin/scoring-band-mappings/`
- `POST /api/admin/scoring-band-mappings/`
- `PATCH /api/admin/scoring-band-mappings/{id}/`
- `DELETE /api/admin/scoring-band-mappings/{id}/`
- `GET /api/admin/users/`
- `POST /api/admin/users/`
- `PATCH /api/admin/users/{id}/`
- `DELETE /api/admin/users/{id}/`
- `GET /api/admin/attempts/`
- `PATCH /api/admin/attempts/{id}/`
- `DELETE /api/admin/attempts/{id}/`
- `GET /api/admin/ai-evaluations/`
- `PATCH /api/admin/ai-evaluations/{id}/`
- `DELETE /api/admin/ai-evaluations/{id}/`
- `GET /api/admin/violations/`
- `GET /api/admin/leaderboard-entries/`
- `GET /api/admin/import-export/templates/`
- `POST /api/admin/import-export/import/`
- `GET /api/admin/import-export/export/`
- `POST /api/admin/evaluations/{evaluationId}/retry/`
- `POST /api/admin/attempts/{attemptId}/regrade/`
- `POST /api/admin/tests/{testId}/publish/`
- `POST /api/admin/tests/{testId}/unpublish/`

### Admin Analytics
- `GET /api/admin/analytics/overview/`
- `GET /api/admin/analytics/user-activity/`
- `GET /api/admin/analytics/test-performance/`
- `GET /api/admin/analytics/question-difficulty/`
- `GET /api/admin/analytics/ai-failures/`
- `GET /api/admin/analytics/violations/`

---

## WebSocket Plan

### Connection
- authenticated connection required
- JWT or session auth middleware
- attempt-specific group: `attempt_{attempt_id}`
- verify attempt ownership before joining
- fallback polling if WebSocket unavailable

### Events
- `timer_sync`
- `heartbeat`
- `autosave_ack`
- `violation_warning`
- `attempt_locked`
- `section_state_change`
- `evaluation_update`
- `result_ready`

### Payload shapes

`timer_sync`:
- `server_timestamp`
- `remaining_seconds`
- `attempt_state`

`evaluation_update`:
- `attempt_id`
- `submission_type`
- `submission_id`
- `status`
- `progress` optional

---

## Celery Tasks

- `auto_submit_expired_attempts`
- `evaluate_writing_submission`
- `transcribe_speaking_audio`
- `evaluate_speaking_submission`
- `retry_failed_ai_evaluation`
- `generate_leaderboard_snapshots`
- `generate_daily_analytics`
- `generate_analytics_suggestions`
- `cleanup_expired_signed_urls` optional
- `send_transactional_email` optional

Rules:
- AI tasks validate JSON output
- retry once if output invalid
- fallback to `pending_human_review`
- auto-submit expired attempts
- tasks should be idempotent where possible

---

## Admin Capabilities

- manage tests
- manage sections
- manage passages
- manage audio assets
- manage question groups
- manage questions
- manage answer options
- manage correct answer rules
- manage scoring band mappings
- manage users
- manage attempts
- manage AI evaluations
- manage violations
- manage leaderboard entries
- import/export content
- view analytics
- retry evaluations
- regrade attempts
- publish/unpublish tests

---

## Security Rules

- correct answers never exposed before submission
- server-authoritative timing
- attempt ownership checks
- prevent IDOR
- signed audio URLs
- file upload validation
- upload size and MIME limits
- rate limit auth endpoints
- rate limit attempt start
- rate limit autosave
- rate limit speaking upload
- rate limit AI evaluation triggers
- JWT refresh rotation
- httpOnly secure cookies if cookie auth used
- CSRF protection if cookie auth used
- strict CORS
- admin action logging
- no secrets in frontend
- no unnecessary personal data sent to AI
- speaking audio requires consent
- only original/licensed content allowed
- no copyrighted Cambridge IELTS content

---

## Product Rules

- listening audio in exam mode plays only once by default
- listening answers lock after audio/section time ends
- reading passages are text-based and selectable/copyable by default
- reading timer default is 60 minutes, configurable
- writing has Task 1 and Task 2
- writing word count tracker warns below minimum words
- speaking uses browser MediaRecorder
- speaking Part 2 includes preparation and recording time
- strict exam mode can enable tab-switch warnings
- strict exam mode can optionally restrict copy/paste
- practice mode can allow replay, re-record, and instant feedback
- one-attempt-per-test is configurable
- auto-submit happens when server time expires
- AI evaluation does not block submission
- if AI fails, attempt becomes `pending_human_review`
- no copyrighted Cambridge IELTS content is seeded or imported automatically
- platform is IELTS-style practice, not official IELTS
