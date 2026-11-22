from datetime import date

class EligibilityService:

    def get_failure_reasons(self, candidate, job):
        reasons = []

        if candidate.profile_status.upper() != "ACTIVE":
            reasons.append("Candidate profile is not ACTIVE")

        if job.status.upper() != "OPEN":
            reasons.append("Job is not OPEN")

        if job.application_deadline and date.today() > job.application_deadline:
            reasons.append("Application deadline has passed")

        if candidate.percentage < job.min_percentage:
            reasons.append("Percentage below minimum requirement")

        if job.min_passing_year and candidate.passing_year < job.min_passing_year:
            reasons.append("Passing year is below allowed range")

        if job.max_passing_year and candidate.passing_year > job.max_passing_year:
            reasons.append("Passing year is above allowed range")

        if candidate.backlog_count > job.max_backlogs:
            reasons.append("Backlog count exceeds allowed limit")

        return reasons

    def is_eligible(self, candidate, job):
        return len(self.get_failure_reasons(candidate, job)) == 0
