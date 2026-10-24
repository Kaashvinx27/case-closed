import uuid
from django.utils import timezone
from .models import (
    InvestigationSession, CaseFile, Suspect, Evidence, CrimeSceneHotspot,
    InterviewTopic, DiscoveredEvidence, InterviewRecord, EvidenceConnection,
    InvestigationJournal, InvestigationNote, HintUsage, CaseHint
)


def get_or_create_session(request, case):
    """
    Retrieves or initializes an investigation session for the user or guest.
    Session tokens are stored in request.session['case_tokens'][case.slug].
    """
    if 'case_tokens' not in request.session:
        request.session['case_tokens'] = {}

    tokens = request.session['case_tokens']
    token = tokens.get(case.slug)

    session = None
    if token:
        session = InvestigationSession.objects.filter(session_token=token, case=case).first()

    # If user is authenticated, prefer their active user session
    if request.user.is_authenticated:
        user_session = InvestigationSession.objects.filter(
            user=request.user, case=case, status='in_progress'
        ).order_by('-started_at').first()
        if user_session:
            session = user_session
            request.session['case_tokens'][case.slug] = session.session_token
            request.session.modified = True

    if not session:
        new_token = uuid.uuid4().hex
        session = InvestigationSession.objects.create(
            session_token=new_token,
            user=request.user if request.user.is_authenticated else None,
            case=case,
            is_guest=not request.user.is_authenticated,
            status='in_progress',
            score=0
        )
        request.session['case_tokens'][case.slug] = new_token
        request.session.modified = True

        # Initial journal entry
        InvestigationJournal.objects.create(
            session=session,
            entry_type='case_opened',
            title='Investigation Commenced',
            content=f"Official dossier for {case.case_number} ({case.title}) opened. Crime scene perimeter secured."
        )

    # Link guest session if user just logged in
    elif request.user.is_authenticated and session.user is None:
        session.user = request.user
        session.is_guest = False
        session.save()

    return session


def discover_evidence_for_session(session, evidence_id):
    """
    Records an evidence discovery. Prevents duplicate scoring.
    """
    try:
        evidence = session.case.evidence_items.get(id=evidence_id)
    except Evidence.DoesNotExist:
        return {'success': False, 'error': 'Evidence item not found in this case.'}

    discovered, created = DiscoveredEvidence.objects.get_or_create(
        session=session,
        evidence=evidence,
        defaults={'points_awarded': 25}
    )

    if created:
        session.score += 25
        session.save()

        InvestigationJournal.objects.create(
            session=session,
            entry_type='evidence_discovered',
            title=f"Evidence Cataloged: {evidence.name}",
            content=f"Found at {evidence.location_found}. Initial analysis: {evidence.description[:100]}..."
        )

    return {
        'success': True,
        'created': created,
        'evidence': {
            'id': evidence.id,
            'code': evidence.code,
            'name': evidence.name,
            'evidence_type': evidence.evidence_type,
            'description': evidence.description,
            'location_found': evidence.location_found,
            'forensic_notes': evidence.forensic_notes,
            'image_icon': evidence.image_icon,
            'is_key_clue': evidence.is_key_clue
        },
        'session_score': session.score,
        'discovered_count': session.discovered_evidence.count(),
        'total_count': session.case.evidence_items.count()
    }


def conduct_suspect_interview(session, suspect_id, topic_id):
    """
    Processes suspect interrogation topic.
    Validates prerequisite evidence discovery and unlocks contradictions.
    """
    try:
        suspect = session.case.suspects.get(id=suspect_id)
        topic = suspect.interview_topics.get(id=topic_id)
    except (Suspect.DoesNotExist, InterviewTopic.DoesNotExist):
        return {'success': False, 'error': 'Interview subject or topic invalid.'}

    # Check evidence prerequisite
    discovered_ids = set(session.discovered_evidence.values_list('evidence_id', flat=True))
    if topic.required_evidence and topic.required_evidence.id not in discovered_ids:
        return {
            'success': False,
            'error': f"Topic locked. You must first locate evidence '{topic.required_evidence.name}' to pursue this line of questioning."
        }

    # Check contradiction status
    contradiction_active = False
    if topic.is_contradiction and topic.contradiction_evidence:
        if topic.contradiction_evidence.id in discovered_ids:
            contradiction_active = True

    record, created = InterviewRecord.objects.get_or_create(
        session=session,
        suspect=suspect,
        topic=topic,
        defaults={
            'contradiction_exposed': contradiction_active,
            'points_awarded': 50 if contradiction_active else 10
        }
    )

    points_added = 0
    if created:
        points_added = 50 if contradiction_active else 10
        session.score += points_added
        session.save()
    elif contradiction_active and not record.contradiction_exposed:
        # Upgrade existing record to exposed contradiction if prerequisite evidence found later
        record.contradiction_exposed = True
        record.points_awarded += 40
        record.save()
        points_added = 40
        session.score += points_added
        session.save()

    # Log to journal
    if contradiction_active:
        InvestigationJournal.objects.create(
            session=session,
            entry_type='contradiction_found',
            title=f"Contradiction Exposed: {suspect.name}",
            content=f"Confronted {suspect.name} with {topic.contradiction_evidence.name}. Subject stammered and changed statement."
        )
    elif created:
        InvestigationJournal.objects.create(
            session=session,
            entry_type='suspect_interviewed',
            title=f"Interviewed: {suspect.name}",
            content=f"Questioned regarding '{topic.title}'. Recorded formal testimony."
        )

    response_text = topic.contradiction_reaction if (contradiction_active and topic.contradiction_reaction) else topic.response_text

    return {
        'success': True,
        'topic_title': topic.title,
        'question': topic.question_text,
        'response': response_text,
        'is_contradiction': contradiction_active,
        'points_awarded': points_added,
        'session_score': session.score
    }


def request_case_hint(session, hint_level):
    """
    Grants a hint from the bureau file and logs score penalty.
    """
    try:
        hint = session.case.hints.get(hint_level=hint_level)
    except CaseHint.DoesNotExist:
        return {'success': False, 'error': f"Hint level {hint_level} not available."}

    usage, created = HintUsage.objects.get_or_create(
        session=session,
        hint=hint,
        defaults={'penalty_applied': hint.penalty_points}
    )

    if created:
        session.hints_used_count += 1
        session.hint_penalty_total += hint.penalty_points
        session.save()

        InvestigationJournal.objects.create(
            session=session,
            entry_type='hint_used',
            title=f"Bureau Hint Consultation (Level {hint.hint_level})",
            content=f"Consulted headquarters analyst memo. Penalty of {hint.penalty_points} points recorded."
        )

    return {
        'success': True,
        'hint_level': hint.hint_level,
        'hint_text': hint.hint_text,
        'penalty': hint.penalty_points,
        'total_hints_used': session.hints_used_count,
        'total_penalty': session.hint_penalty_total
    }


def create_or_update_note(session, content):
    """
    Saves an investigator's personal deduction note.
    """
    clean_content = content.strip()
    if not clean_content:
        return {'success': False, 'error': 'Note content cannot be empty.'}

    note = InvestigationNote.objects.create(
        session=session,
        content=clean_content
    )

    InvestigationJournal.objects.create(
        session=session,
        entry_type='note_added',
        title="Investigator Note Pinned",
        content=clean_content[:100] + ("..." if len(clean_content) > 100 else "")
    )

    return {
        'success': True,
        'note_id': note.id,
        'content': note.content,
        'created_at': note.created_at.strftime('%H:%M:%S')
    }


def link_board_entities(session, source_type, source_id, target_type, target_id, notes=""):
    """
    Saves corkboard red yarn string link between evidence and suspects.
    """
    conn, created = EvidenceConnection.objects.get_or_create(
        session=session,
        source_type=source_type,
        source_id=source_id,
        target_type=target_type,
        target_id=target_id,
        defaults={'notes': notes}
    )
    return {
        'success': True,
        'connection_id': conn.id,
        'created': created
    }


def remove_board_entity_link(session, connection_id):
    """
    Deletes corkboard connection.
    """
    deleted, _ = EvidenceConnection.objects.filter(session=session, id=connection_id).delete()
    return {'success': deleted > 0}
