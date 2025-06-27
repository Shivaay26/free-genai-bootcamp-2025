words — Stores individual Japanese vocabulary words.
- `id` (Primary Key): Unique identifier for each word
- `kanji` (String, Required): The word written in Japanese kanji
- `romaji` (String, Required): Romanized version of the word
- `english` (String, Required): English translation of the word
- `parts` (JSON, Required): Word components stored in JSON format

groups — Manages collections of words.
- `id` (Primary Key): Unique identifier for each group
- `name` (String, Required): Name of the group
- `words_count` (Integer, Default: 0): Counter cache for the number of words in the group

word_groups — join-table enabling many-to-many relationship between words and groups.
- `word_id` (Foreign Key): References words.id
- `group_id` (Foreign Key): References groups.id

study_activities — Defines different types of study activities available.
- `id` (Primary Key): Unique identifier for each activity
- `name` (String, Required): Name of the activity (e.g., "Flashcards", "Quiz")
- `url` (String, Required): The full URL of the study activity

study_sessions — Records individual study sessions.
- `id` (Primary Key): Unique identifier for each session
- `group_id` (Foreign Key): References groups.id
- `study_activity_id` (Foreign Key): References study_activities.id
- `created_at` (Timestamp, Default: Current Time): When the session was created

word_review_items — Tracks individual word reviews within study sessions.
- `id` (Primary Key): Unique identifier for each review
- `word_id` (Foreign Key): References words.id
- `study_session_id` (Foreign Key): References study_sessions.id
- `correct` (Boolean, Required): Whether the answer was correct
- `created_at` (Timestamp, Default: Current Time): When the review occurred

Relationships

word belongs to groups through  word_groups
group belongs to words through word_groups
session belongs to a group
session belongs to a study_activity
session has many word_review_items
word_review_item belongs to a study_session
word_review_item belongs to a word

