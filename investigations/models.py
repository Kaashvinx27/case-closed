import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class DetectiveProfile(models.Model):
    """
    Profile extension for registered detectives.
    Stores rank, lifetime score, solved cases, and user preferences.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='detective_profile')
    badge_number = models.CharField(max_length=20, unique=True)
    rank = models.CharField(max_length=50, default='Rookie Investigator')
    total_score = models.IntegerField(default=0)
    cases_solved = models.IntegerField(default=0)
    avatar = models.CharField(max_length=50, default='detective-coat')
    sound_enabled = models.BooleanField(default=False)
    reduced_motion = models.BooleanField(default=False)
    show_timer = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} [{self.badge_number}] - {self.rank}"

    def update_rank_and_stats(self):
        results = CaseResult.objects.filter(user=self.user, is_solved=True)
        self.cases_solved = results.count()
        total = sum(r.final_score for r in results)
        self.total_score = total

        if self.total_score >= 1200:
            self.rank = 'Legendary Sleuth'
        elif self.total_score >= 800:
            self.rank = 'Master Detective'
        elif self.total_score >= 450:
            self.rank = 'Senior Investigator'
        elif self.total_score >= 200:
            self.rank = 'Field Detective'
        else:
            self.rank = 'Rookie Investigator'

        self.save()
        return self.rank


class CaseFile(models.Model):
    """
    Public case file description, briefing, and parameters.
    """
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=100, unique=True)
    case_number = models.CharField(max_length=20, unique=True)
    genre = models.CharField(max_length=50)
    synopsis = models.TextField()
    incident_date = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    victim_name = models.CharField(max_length=100)
    victim_profile = models.TextField()
    initial_findings = models.TextField()
    known_circumstances = models.TextField()
    difficulty = models.CharField(
        max_length=20,
        choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')],
        default='Medium'
    )
    estimated_time = models.CharField(max_length=50, default='15-20 min')
    is_published = models.BooleanField(default=True)
    scene_title = models.CharField(max_length=100, default='Primary Crime Scene')
    scene_description = models.TextField(blank=True)
    scene_theme = models.CharField(max_length=50, default='study')  # manor, museum, observatory
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'case_number']

    def __str__(self):
        return f"{self.case_number}: {self.title}"

    @property
    def total_evidence_count(self):
        return self.evidence_items.count()

    @property
    def total_suspects_count(self):
        return self.suspects.count()


class Suspect(models.Model):
    """
    Suspect profile and background.
    """
    case = models.ForeignKey(CaseFile, on_delete=models.CASCADE, related_name='suspects')
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    occupation = models.CharField(max_length=100)
    relationship_to_victim = models.CharField(max_length=150)
    alibi = models.TextField()
    known_motive = models.TextField()
    personality_notes = models.TextField()
    portrait_icon = models.CharField(max_length=50, default='person-badge')
    opening_statement = models.TextField()
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.name} ({self.case.case_number})"


class Evidence(models.Model):
    """
    Evidence item with forensic notes and location.
    """
    EVIDENCE_TYPES = [
        ('Document', 'Document / Paperwork'),
        ('Forensic', 'Forensic Residue / Trace'),
        ('Object', 'Physical Object / Weapon'),
        ('Digital', 'Digital / System Log'),
        ('Witness', 'Witness Observation'),
    ]

    case = models.ForeignKey(CaseFile, on_delete=models.CASCADE, related_name='evidence_items')
    code = models.CharField(max_length=20)  # e.g., "AD-01", "LF-02"
    name = models.CharField(max_length=150)
    evidence_type = models.CharField(max_length=50, choices=EVIDENCE_TYPES)
    description = models.TextField()
    location_found = models.CharField(max_length=150)
    forensic_notes = models.TextField()
    image_icon = models.CharField(max_length=50, default='file-earmark-text')
    is_key_clue = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['case', 'code'], name='unique_case_evidence_code')
        ]

    def __str__(self):
        return f"[{self.code}] {self.name} ({self.case.case_number})"


class CrimeSceneHotspot(models.Model):
    """
    Visual hotspot coordinates on the crime scene map.
    """
    case = models.ForeignKey(CaseFile, on_delete=models.CASCADE, related_name='hotspots')
    evidence = models.OneToOneField(Evidence, on_delete=models.CASCADE, related_name='hotspot')
    label = models.CharField(max_length=100)
    x_percent = models.FloatField(help_text="X position in percentage 0-100")
    y_percent = models.FloatField(help_text="Y position in percentage 0-100")
    icon = models.CharField(max_length=50, default='search')
    inspect_hint = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Hotspot '{self.label}' at ({self.x_percent}%, {self.y_percent}%)"


class InterviewTopic(models.Model):
    """
    Question and dialogue node for suspect interrogation.
    Supports evidence prerequisites and contradiction establishment.
    """
    suspect = models.ForeignKey(Suspect, on_delete=models.CASCADE, related_name='interview_topics')
    title = models.CharField(max_length=150)
    topic_key = models.CharField(max_length=50)
    question_text = models.CharField(max_length=255)
    response_text = models.TextField()
    required_evidence = models.ForeignKey(
        Evidence, on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )
    is_contradiction = models.BooleanField(default=False)
    contradiction_evidence = models.ForeignKey(
        Evidence, on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )
    contradiction_reaction = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.suspect.name} - {self.title}"


class CaseHint(models.Model):
    """
    Tiered hint system for cases.
    """
    case = models.ForeignKey(CaseFile, on_delete=models.CASCADE, related_name='hints')
    hint_level = models.IntegerField(choices=[(1, 'Broad Direction'), (2, 'Specific Clue'), (3, 'Critical Deduction')])
    hint_text = models.TextField()
    penalty_points = models.IntegerField(default=0)

    class Meta:
        ordering = ['hint_level']

    def __str__(self):
        return f"{self.case.case_number} - Hint Level {self.hint_level} (-{self.penalty_points} pts)"


class CaseSecretSolution(models.Model):
    """
    Authoritative server-side solution for a case.
    NEVER serialized or revealed in public case APIs.
    """
    case = models.OneToOneField(CaseFile, on_delete=models.CASCADE, related_name='solution')
    culprit = models.ForeignKey(Suspect, on_delete=models.CASCADE, related_name='+')
    correct_motive = models.CharField(max_length=255)
    correct_motive_details = models.TextField()
    required_evidence = models.ManyToManyField(Evidence, related_name='+')
    accepted_reasoning = models.TextField()
    epilogue = models.TextField()
    max_score = models.IntegerField(default=500)
    evidence_point_val = models.IntegerField(default=25)
    contradiction_point_val = models.IntegerField(default=50)
    culprit_points = models.IntegerField(default=200)
    motive_points = models.IntegerField(default=100)
    evidence_points = models.IntegerField(default=100)

    def __str__(self):
        return f"Secret Solution for {self.case.case_number} (Culprit: {self.culprit.name})"


class InvestigationSession(models.Model):
    """
    Active or completed investigation session for a player or guest.
    """
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Closed / Unsolved'),
    ]

    session_token = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='investigation_sessions')
    case = models.ForeignKey(CaseFile, on_delete=models.CASCADE, related_name='sessions')
    is_guest = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    hints_used_count = models.IntegerField(default=0)
    hint_penalty_total = models.IntegerField(default=0)

    def __str__(self):
        user_name = self.user.username if self.user else f"Guest ({self.session_token[:8]})"
        return f"{user_name} - {self.case.case_number} [{self.status}]"


class DiscoveredEvidence(models.Model):
    """
    Tracks evidence discovered in a session to avoid duplicate scoring.
    """
    session = models.ForeignKey(InvestigationSession, on_delete=models.CASCADE, related_name='discovered_evidence')
    evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE, related_name='+')
    discovered_at = models.DateTimeField(auto_now_add=True)
    points_awarded = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'evidence'], name='unique_session_evidence')
        ]

    def __str__(self):
        return f"Session {self.session.id} -> Discovered {self.evidence.code}"


class InterviewRecord(models.Model):
    """
    Tracks completed interview topics and exposed contradictions.
    """
    session = models.ForeignKey(InvestigationSession, on_delete=models.CASCADE, related_name='interview_records')
    suspect = models.ForeignKey(Suspect, on_delete=models.CASCADE, related_name='+')
    topic = models.ForeignKey(InterviewTopic, on_delete=models.CASCADE, related_name='+')
    contradiction_exposed = models.BooleanField(default=False)
    points_awarded = models.IntegerField(default=0)
    interviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'topic'], name='unique_session_topic')
        ]

    def __str__(self):
        return f"Session {self.session.id} -> Interviewed {self.suspect.name} on {self.topic.title}"


class EvidenceConnection(models.Model):
    """
    Corkboard visual connections between evidence items or suspects.
    """
    session = models.ForeignKey(InvestigationSession, on_delete=models.CASCADE, related_name='connections')
    source_type = models.CharField(max_length=20)  # 'evidence' or 'suspect'
    source_id = models.IntegerField()
    target_type = models.CharField(max_length=20)  # 'evidence' or 'suspect'
    target_id = models.IntegerField()
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Connection: {self.source_type}#{self.source_id} <-> {self.target_type}#{self.target_id}"


class InvestigationJournal(models.Model):
    """
    Chronological activity journal of detective actions.
    """
    session = models.ForeignKey(InvestigationSession, on_delete=models.CASCADE, related_name='journal_entries')
    entry_type = models.CharField(max_length=30)
    title = models.CharField(max_length=150)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.entry_type}] {self.title}"


class InvestigationNote(models.Model):
    """
    Personal notes written by the detective on their corkboard / notepad.
    """
    session = models.ForeignKey(InvestigationSession, on_delete=models.CASCADE, related_name='detective_notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note {self.id} for session {self.session.id}"


class HintUsage(models.Model):
    """
    Records hint redemptions and point penalties.
    """
    session = models.ForeignKey(InvestigationSession, on_delete=models.CASCADE, related_name='hints_taken')
    hint = models.ForeignKey(CaseHint, on_delete=models.CASCADE, related_name='+')
    penalty_applied = models.IntegerField(default=0)
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'hint'], name='unique_session_hint')
        ]

    def __str__(self):
        return f"Session {self.session.id} used Hint L{self.hint.hint_level}"


class Accusation(models.Model):
    """
    Final accusation submission. Validated server-authoritatively against CaseSecretSolution.
    """
    session = models.ForeignKey(InvestigationSession, on_delete=models.CASCADE, related_name='accusations')
    suspect = models.ForeignKey(Suspect, on_delete=models.CASCADE, related_name='+')
    motive = models.CharField(max_length=255)
    supporting_evidence = models.ManyToManyField(Evidence, related_name='+')
    reasoning = models.TextField()
    is_correct = models.BooleanField(default=False)
    culprit_correct = models.BooleanField(default=False)
    motive_correct = models.BooleanField(default=False)
    evidence_correct = models.BooleanField(default=False)
    score_awarded = models.IntegerField(default=0)
    feedback = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Accusation on {self.suspect.name} - Correct: {self.is_correct}"


class CaseResult(models.Model):
    """
    Authoritative final case result for leaderboards and profiles.
    """
    session = models.OneToOneField(InvestigationSession, on_delete=models.CASCADE, related_name='result')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='case_results')
    case = models.ForeignKey(CaseFile, on_delete=models.CASCADE, related_name='results')
    is_solved = models.BooleanField(default=False)
    final_score = models.IntegerField(default=0)
    max_possible_score = models.IntegerField(default=500)
    accuracy_percentage = models.FloatField(default=0.0)
    rank_awarded = models.CharField(max_length=50)
    time_taken_seconds = models.IntegerField(default=0)
    evidence_discovered_count = models.IntegerField(default=0)
    total_evidence_count = models.IntegerField(default=0)
    contradictions_count = models.IntegerField(default=0)
    hints_used_count = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-final_score', 'time_taken_seconds']

    def __str__(self):
        user_name = self.user.username if self.user else "Guest Detective"
        return f"{user_name} - {self.case.case_number}: {self.final_score} pts ({self.rank_awarded})"


class Achievement(models.Model):
    """
    Badges and achievements unlocked through detective milestones.
    """
    code = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='award')
    badge_color = models.CharField(max_length=20, default='gold')

    def __str__(self):
        return f"{self.title} ({self.code})"


class UserAchievement(models.Model):
    """
    Tracks which registered user earned which achievement.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name='+')
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'achievement'], name='unique_user_achievement')
        ]

    def __str__(self):
        return f"{self.user.username} unlocked {self.achievement.title}"
