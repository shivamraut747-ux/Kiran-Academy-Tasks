# Data Dictionary

Generated from `sql/database_schema.sql`. Database: `recruitment_portal` (MySQL). 17 tables, 21 foreign keys.

Application status values: APPLIED, ELIGIBILITY_VERIFIED, SHORTLISTED, INTERVIEW_SCHEDULED, INTERVIEWED, SELECTED, REJECTED, OFFERED, JOINED, WITHDRAWN.


## qualifications

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| qualification_id | INT | No |  | PK |  |
| qualification_name | VARCHAR(100) | No |  | UNIQUE |  |
| is_active | TINYINT(1) | No | 1 |  |  |
| created_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |

## locations

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| location_id | INT | No |  | PK |  |
| city_name | VARCHAR(100) | No |  |  |  |
| state_name | VARCHAR(100) | No |  |  |  |
| country_name | VARCHAR(100) | No | 'India' |  |  |
| is_active | TINYINT(1) | No | 1 |  |  |

## roles

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| role_id | INT | No |  | PK |  |
| role_code | VARCHAR(30) | No |  | UNIQUE |  |
| role_name | VARCHAR(80) | No |  |  |  |
| is_active | TINYINT(1) | No | 1 |  |  |
| created_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |

## users

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| user_id | INT | No |  | PK |  |
| username | VARCHAR(80) | No |  | UNIQUE |  |
| password_hash | VARCHAR(255) | No |  |  |  |
| full_name | VARCHAR(120) | No |  |  |  |
| email | VARCHAR(150) | Yes |  | UNIQUE |  |
| role_id | INT | No |  | FK, → roles.role_id |  |
| status | VARCHAR(20) | No | 'ACTIVE' |  | ACTIVE, INACTIVE, LOCKED |
| last_login_at | DATETIME | Yes |  |  |  |
| created_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |

## candidates

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| candidate_id | INT | No |  | PK |  |
| candidate_code | VARCHAR(30) | No |  | UNIQUE |  |
| full_name | VARCHAR(150) | No |  |  |  |
| email | VARCHAR(150) | No |  | UNIQUE |  |
| mobile | VARCHAR(20) | No |  | UNIQUE |  |
| date_of_birth | DATE | Yes |  |  |  |
| gender | VARCHAR(20) | Yes |  |  |  |
| qualification | VARCHAR(80) | No |  |  |  |
| college | VARCHAR(180) | Yes |  |  |  |
| university | VARCHAR(180) | Yes |  |  |  |
| passing_year | SMALLINT | No |  |  |  |
| percentage | DECIMAL(5,2) | Yes |  |  |  |
| cgpa | DECIMAL(4,2) | Yes |  |  |  |
| backlog_count | INT | No | 0 |  |  |
| primary_technology | VARCHAR(80) | Yes |  |  |  |
| current_location | VARCHAR(100) | Yes |  |  |  |
| preferred_location | VARCHAR(100) | Yes |  |  |  |
| profile_status | VARCHAR(20) | No | 'ACTIVE' |  | ACTIVE, INACTIVE, ON_HOLD, BLACKLISTED |
| placement_status | VARCHAR(20) | No | 'NOT_PLACED' |  | NOT_PLACED, PLACED |
| created_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |
| updated_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |

## skills

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| skill_id | INT | No |  | PK |  |
| skill_name | VARCHAR(100) | No |  | UNIQUE |  |
| category | VARCHAR(60) | Yes |  |  |  |
| is_active | TINYINT(1) | No | 1 |  |  |

## candidate_skills

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| candidate_skill_id | INT | No |  | PK |  |
| candidate_id | INT | No |  | FK, → candidates.candidate_id |  |
| skill_id | INT | No |  | FK, → skills.skill_id |  |
| proficiency_level | VARCHAR(20) | Yes |  |  |  |
| years_experience | DECIMAL(4,1) | No | 0 |  |  |
| is_primary | TINYINT(1) | No | 0 |  |  |

## companies

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| company_id | INT | No |  | PK |  |
| company_code | VARCHAR(30) | No |  | UNIQUE |  |
| company_name | VARCHAR(180) | No |  |  |  |
| industry | VARCHAR(100) | Yes |  |  |  |
| website | VARCHAR(200) | Yes |  |  |  |
| location | VARCHAR(120) | Yes |  |  |  |
| company_type | VARCHAR(30) | Yes |  |  |  |
| hr_name | VARCHAR(120) | Yes |  |  |  |
| hr_email | VARCHAR(150) | Yes |  |  |  |
| hr_mobile | VARCHAR(20) | Yes |  |  |  |
| status | VARCHAR(20) | No | 'ACTIVE' |  | ACTIVE, INACTIVE |
| created_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |

## jobs

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| job_id | INT | No |  | PK |  |
| job_code | VARCHAR(40) | No |  | UNIQUE |  |
| company_id | INT | No |  | FK, → companies.company_id |  |
| job_title | VARCHAR(150) | No |  |  |  |
| employment_type | VARCHAR(30) | No | 'FULL_TIME' |  |  |
| location | VARCHAR(120) | No |  |  |  |
| openings | INT | No |  |  |  |
| min_package_lpa | DECIMAL(6,2) | Yes |  |  |  |
| max_package_lpa | DECIMAL(6,2) | Yes |  |  |  |
| min_percentage | DECIMAL(5,2) | Yes |  |  |  |
| min_passing_year | SMALLINT | Yes |  |  |  |
| max_passing_year | SMALLINT | Yes |  |  |  |
| max_backlogs | INT | No | 0 |  |  |
| experience_min_years | DECIMAL(4,1) | No | 0 |  |  |
| qualification_rule | VARCHAR(255) | Yes |  |  |  |
| posted_date | DATE | No |  |  |  |
| application_deadline | DATE | No |  |  |  |
| status | VARCHAR(20) | No | 'OPEN' |  | DRAFT, OPEN, CLOSED, CANCELLED |
| created_by | INT | No |  | FK, → users.user_id |  |
| created_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |

## job_skills

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| job_skill_id | INT | No |  | PK |  |
| job_id | INT | No |  | FK, → jobs.job_id |  |
| skill_id | INT | No |  | FK, → skills.skill_id |  |
| minimum_level | VARCHAR(20) | Yes |  |  |  |
| mandatory_flag | TINYINT(1) | No | 1 |  |  |

## applications

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| application_id | INT | No |  | PK |  |
| application_code | VARCHAR(40) | No |  | UNIQUE |  |
| candidate_id | INT | No |  | FK, → candidates.candidate_id |  |
| job_id | INT | No |  | FK, → jobs.job_id |  |
| applied_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |
| eligibility_status | VARCHAR(20) | No | 'PENDING' |  | PENDING, ELIGIBLE, NOT_ELIGIBLE |
| eligibility_reason | VARCHAR(500) | Yes |  |  |  |
| application_status | VARCHAR(30) | No | 'APPLIED' |  | APPLIED, ELIGIBILITY_VERIFIED, SHORTLISTED, INTERVIEW_SCHEDULED, INTERVIEWED, SELECTED, REJECTED, OFFERED, JOINED, WITHDRAWN |
| source | VARCHAR(50) | Yes |  |  |  |
| assigned_recruiter_id | INT | Yes |  | FK, → users.user_id |  |
| updated_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |

## application_history

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| history_id | BIGINT | No |  | PK |  |
| application_id | INT | No |  | FK, → applications.application_id |  |
| old_status | VARCHAR(30) | Yes |  |  |  |
| new_status | VARCHAR(30) | No |  |  |  |
| remarks | VARCHAR(500) | Yes |  |  |  |
| changed_by | INT | No |  | FK, → users.user_id |  |
| changed_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |

## interview_rounds

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| interview_id | INT | No |  | PK |  |
| application_id | INT | No |  | FK, → applications.application_id |  |
| round_number | INT | No |  |  |  |
| round_type | VARCHAR(50) | No |  |  |  |
| scheduled_date | DATE | No |  |  |  |
| scheduled_time | TIME | Yes |  |  |  |
| mode | VARCHAR(20) | No |  |  | ONLINE, OFFLINE, TELEPHONIC |
| interviewer_name | VARCHAR(120) | Yes |  |  |  |
| meeting_or_location | VARCHAR(255) | Yes |  |  |  |
| status | VARCHAR(20) | No | 'SCHEDULED' |  | SCHEDULED, COMPLETED, RESCHEDULED, CANCELLED, NO_SHOW |
| created_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |

## interview_feedback

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| feedback_id | INT | No |  | PK |  |
| interview_id | INT | No |  | FK, UNIQUE, → interview_rounds.interview_id |  |
| technical_rating | DECIMAL(3,1) | Yes |  |  |  |
| communication_rating | DECIMAL(3,1) | Yes |  |  |  |
| problem_solving_rating | DECIMAL(3,1) | Yes |  |  |  |
| overall_rating | DECIMAL(3,1) | Yes |  |  |  |
| recommendation | VARCHAR(30) | No |  |  | NEXT_ROUND, SELECTED, REJECTED, ON_HOLD |
| remarks | TEXT | Yes |  |  |  |
| submitted_by | INT | No |  | FK, → users.user_id |  |
| submitted_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |

## offers

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| offer_id | INT | No |  | PK |  |
| offer_code | VARCHAR(40) | No |  | UNIQUE |  |
| application_id | INT | No |  | FK, UNIQUE, → applications.application_id |  |
| designation | VARCHAR(120) | No |  |  |  |
| offered_package_lpa | DECIMAL(6,2) | No |  |  |  |
| offer_date | DATE | No |  |  |  |
| expected_joining_date | DATE | Yes |  |  |  |
| offer_status | VARCHAR(20) | No | 'OFFERED' |  | OFFERED, ACCEPTED, REJECTED, EXPIRED, WITHDRAWN |
| remarks | VARCHAR(500) | Yes |  |  |  |
| created_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |

## placements

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| placement_id | INT | No |  | PK |  |
| candidate_id | INT | No |  | FK, → candidates.candidate_id |  |
| company_id | INT | No |  | FK, → companies.company_id |  |
| job_id | INT | No |  | FK, → jobs.job_id |  |
| offer_id | INT | No |  | FK, UNIQUE, → offers.offer_id |  |
| designation | VARCHAR(120) | No |  |  |  |
| final_package_lpa | DECIMAL(6,2) | No |  |  |  |
| expected_joining_date | DATE | Yes |  |  |  |
| actual_joining_date | DATE | Yes |  |  |  |
| joining_status | VARCHAR(20) | No | 'PENDING' |  | PENDING, JOINED, NOT_JOINED, DEFERRED, NO_SHOW |
| placement_status | VARCHAR(20) | No | 'ACTIVE' |  | ACTIVE, CANCELLED |
| created_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |

## activity_logs

| Column | Type | Null | Default | Key / Notes | Allowed values |
|---|---|---|---|---|---|
| log_id | BIGINT | No |  | PK |  |
| user_id | INT | Yes |  | FK, → users.user_id |  |
| module_name | VARCHAR(60) | No |  |  |  |
| action_name | VARCHAR(80) | No |  |  |  |
| record_id | VARCHAR(60) | Yes |  |  |  |
| description | VARCHAR(500) | Yes |  |  |  |
| logged_at | DATETIME | No | CURRENT_TIMESTAMP |  |  |
