from django.contrib import admin
from .models import (
    DetectiveProfile, CaseFile, Suspect, Evidence, CrimeSceneHotspot,
    InterviewTopic, CaseHint, CaseSecretSolution, InvestigationSession,
    DiscoveredEvidence, InterviewRecord, EvidenceConnection,
    InvestigationJournal, InvestigationNote, HintUsage,
    Accusation, CaseResult, Achievement, UserAchievement
)


class SuspectInline(admin.TabularInline):
    model = Suspect
    extra = 1
    fields = ('name', 'age', 'occupation', 'relationship_to_victim', 'order')


class EvidenceInline(admin.TabularInline):
    model = Evidence
    extra = 1
    fields = ('code', 'name', 'evidence_type', 'location_found', 'is_key_clue', 'order')


class HotspotInline(admin.TabularInline):
    model = CrimeSceneHotspot
    extra = 1
    fields = ('evidence', 'label', 'x_percent', 'y_percent')


class CaseHintInline(admin.TabularInline):
    model = CaseHint
    extra = 1


@admin.register(CaseFile)
class CaseFileAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'title', 'genre', 'difficulty', 'estimated_time', 'is_published', 'order')
    list_filter = ('difficulty', 'genre', 'is_published')
    search_fields = ('case_number', 'title', 'victim_name', 'location')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SuspectInline, EvidenceInline, HotspotInline, CaseHintInline]


@admin.register(Suspect)
class SuspectAdmin(admin.ModelAdmin):
    list_display = ('name', 'case', 'age', 'occupation', 'relationship_to_victim', 'order')
    list_filter = ('case',)
    search_fields = ('name', 'occupation', 'alibi')


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'case', 'evidence_type', 'location_found', 'is_key_clue', 'order')
    list_filter = ('case', 'evidence_type', 'is_key_clue')
    search_fields = ('code', 'name', 'description', 'forensic_notes')


@admin.register(CrimeSceneHotspot)
class CrimeSceneHotspotAdmin(admin.ModelAdmin):
    list_display = ('label', 'case', 'evidence', 'x_percent', 'y_percent')
    list_filter = ('case',)


@admin.register(InterviewTopic)
class InterviewTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'suspect', 'topic_key', 'is_contradiction', 'order')
    list_filter = ('suspect__case', 'is_contradiction')
    search_fields = ('title', 'question_text', 'response_text')


@admin.register(CaseSecretSolution)
class CaseSecretSolutionAdmin(admin.ModelAdmin):
    list_display = ('case', 'culprit', 'correct_motive', 'max_score')
    filter_horizontal = ('required_evidence',)


@admin.register(InvestigationSession)
class InvestigationSessionAdmin(admin.ModelAdmin):
    list_display = ('session_token', 'user', 'case', 'is_guest', 'status', 'score', 'started_at', 'last_activity_at')
    list_filter = ('status', 'is_guest', 'case')
    search_fields = ('session_token', 'user__username')


@admin.register(CaseResult)
class CaseResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'case', 'is_solved', 'final_score', 'rank_awarded', 'time_taken_seconds', 'completed_at')
    list_filter = ('is_solved', 'rank_awarded', 'case')
    search_fields = ('user__username', 'case__case_number')


@admin.register(DetectiveProfile)
class DetectiveProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge_number', 'rank', 'total_score', 'cases_solved')
    list_filter = ('rank',)
    search_fields = ('user__username', 'badge_number')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'badge_color')


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'unlocked_at')
    list_filter = ('achievement',)
