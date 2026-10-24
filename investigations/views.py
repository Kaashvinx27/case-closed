import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Sum, Count, Q

from .models import (
    CaseFile, Suspect, Evidence, CrimeSceneHotspot, InterviewTopic,
    InvestigationSession, DiscoveredEvidence, InterviewRecord,
    EvidenceConnection, InvestigationJournal, InvestigationNote,
    Accusation, CaseResult, Achievement, UserAchievement, DetectiveProfile
)
from .forms import DetectiveRegistrationForm, DetectiveProfileSettingsForm, AccusationForm
from .services import (
    get_or_create_session, discover_evidence_for_session,
    conduct_suspect_interview, request_case_hint, create_or_update_note,
    link_board_entities, remove_board_entity_link
)
from .game_logic import evaluate_accusation


# ---------------------------------------------------------
# Web Page Views
# ---------------------------------------------------------

def landing(request):
    """
    Cinematic landing page introducing the detective bureau.
    """
    cases = CaseFile.objects.filter(is_published=True).order_by('order')
    total_cases = cases.count()
    total_detectives = DetectiveProfile.objects.count()
    completed_investigations = CaseResult.objects.filter(is_solved=True).count()
    featured_case = cases.first()

    context = {
        'cases': cases,
        'featured_case': featured_case,
        'total_cases': total_cases,
        'total_detectives': max(total_detectives, 1),
        'completed_investigations': completed_investigations,
    }
    return render(request, 'investigations/landing.html', context)


def dashboard(request):
    """
    Classified investigation terminal dashboard for logged-in or guest detectives.
    """
    cases = CaseFile.objects.filter(is_published=True).order_by('order')

    # Collect session records for the current user or guest tokens
    user_sessions = {}
    completed_cases_count = 0
    total_score = 0
    recent_activity = []

    if request.user.is_authenticated:
        profile, _ = DetectiveProfile.objects.get_or_create(
            user=request.user,
            defaults={'badge_number': f"DET-{request.user.id:04d}"}
        )
        profile.update_rank_and_stats()
        user_rank = profile.rank
        badge = profile.badge_number
        total_score = profile.total_score
        completed_cases_count = profile.cases_solved

        sessions_qs = InvestigationSession.objects.filter(user=request.user).select_related('case')
        for s in sessions_qs:
            user_sessions[s.case_id] = s

        recent_activity = InvestigationJournal.objects.filter(
            session__user=request.user
        ).order_by('-created_at')[:8]
    else:
        # Guest mode
        user_rank = 'Visiting Guest Detective'
        badge = 'GUEST-OBSERVER'
        tokens = request.session.get('case_tokens', {})
        if tokens:
            sessions_qs = InvestigationSession.objects.filter(
                session_token__in=tokens.values()
            ).select_related('case')
            for s in sessions_qs:
                user_sessions[s.case_id] = s
                if s.status == 'completed':
                    completed_cases_count += 1
                total_score += s.score

            recent_activity = InvestigationJournal.objects.filter(
                session__session_token__in=tokens.values()
            ).order_by('-created_at')[:8]

    # Calculate case card progress badges
    cases_with_status = []
    for c in cases:
        sess = user_sessions.get(c.id)
        status_label = 'Not Started'
        status_badge = 'secondary'
        pct = 0
        score = 0

        if sess:
            score = sess.score
            discovered = sess.discovered_evidence.count()
            total_ev = c.evidence_items.count()
            pct = int((discovered / max(1, total_ev)) * 100)
            if sess.status == 'completed':
                status_label = 'Case Closed (Solved)'
                status_badge = 'success'
            elif sess.status == 'failed':
                status_label = 'Unsolved Attempt'
                status_badge = 'danger'
            else:
                status_label = 'In Progress'
                status_badge = 'warning'

        cases_with_status.append({
            'case': c,
            'session': sess,
            'status_label': status_label,
            'status_badge': status_badge,
            'progress_pct': pct,
            'score': score
        })

    # Available achievements
    achievements = Achievement.objects.all()
    user_ach_ids = set()
    if request.user.is_authenticated:
        user_ach_ids = set(request.user.achievements.values_list('achievement_id', flat=True))

    context = {
        'user_rank': user_rank,
        'badge_number': badge,
        'total_score': total_score,
        'completed_cases_count': completed_cases_count,
        'cases_with_status': cases_with_status,
        'recent_activity': recent_activity,
        'achievements': achievements,
        'user_ach_ids': user_ach_ids,
        'is_guest': not request.user.is_authenticated,
    }
    return render(request, 'investigations/dashboard.html', context)


def cases_list(request):
    """
    Classified Case Files repository with filters and sorting.
    """
    cases = CaseFile.objects.filter(is_published=True).order_by('order')
    difficulty = request.GET.get('difficulty')
    status_filter = request.GET.get('status')

    # Identify user session statuses
    user_sessions = {}
    if request.user.is_authenticated:
        for s in InvestigationSession.objects.filter(user=request.user):
            user_sessions[s.case_id] = s.status
    else:
        tokens = request.session.get('case_tokens', {})
        for s in InvestigationSession.objects.filter(session_token__in=tokens.values()):
            user_sessions[s.case_id] = s.status

    filtered_cases = []
    for c in cases:
        st = user_sessions.get(c.id, 'not_started')
        if difficulty and difficulty != 'all' and c.difficulty.lower() != difficulty.lower():
            continue
        if status_filter and status_filter != 'all':
            if status_filter == 'not_started' and st != 'not_started':
                continue
            if status_filter == 'in_progress' and st != 'in_progress':
                continue
            if status_filter == 'completed' and st != 'completed':
                continue

        filtered_cases.append({
            'case': c,
            'status': st,
            'status_display': 'Case Closed' if st == 'completed' else ('Active File' if st == 'in_progress' else 'Unopened'),
            'badge_class': 'success' if st == 'completed' else ('warning' if st == 'in_progress' else 'secondary')
        })

    context = {
        'cases_data': filtered_cases,
        'current_difficulty': difficulty or 'all',
        'current_status': status_filter or 'all',
    }
    return render(request, 'investigations/cases.html', context)


def case_briefing(request, case_slug):
    """
    Formal classified briefing prior to entering the crime scene.
    """
    case = get_object_or_404(CaseFile, slug=case_slug, is_published=True)
    session = get_or_create_session(request, case)

    context = {
        'case': case,
        'session': session,
        'is_resumed': session.discovered_evidence.exists()
    }
    return render(request, 'investigations/case_briefing.html', context)


def investigation_workspace(request, case_slug):
    """
    The centerpiece interactive detective workspace.
    Contains Crime Scene Hotspots, Suspect Board, Interrogation Room,
    Interactive Corkboard, and Final Accusation controls.
    """
    case = get_object_or_404(CaseFile, slug=case_slug, is_published=True)
    session = get_or_create_session(request, case)

    # Discovered evidence IDs for this session
    discovered_qs = session.discovered_evidence.select_related('evidence')
    discovered_ids = set(d.evidence.id for d in discovered_qs)
    discovered_items = [d.evidence for d in discovered_qs]

    # Suspects and their unlocked interview topics
    suspects = list(case.suspects.prefetch_related('interview_topics').all())
    interview_records = list(
        session.interview_records.select_related('topic', 'suspect').order_by('interviewed_at')
    )
    interviews_by_suspect = {}
    for rec in interview_records:
        interviews_by_suspect.setdefault(rec.suspect_id, []).append(rec)
    for s in suspects:
        s.recorded_interviews = interviews_by_suspect.get(s.id, [])

    interviewed_topics = set(
        session.interview_records.values_list('topic_id', flat=True)
    )
    contradictions_unlocked = set(
        session.interview_records.filter(contradiction_exposed=True).values_list('topic_id', flat=True)
    )

    # Hotspots with discovery status
    hotspots = case.hotspots.select_related('evidence').all()
    hotspots_data = []
    for h in hotspots:
        is_disc = h.evidence.id in discovered_ids
        hotspots_data.append({
            'hotspot': h,
            'is_discovered': is_disc,
        })

    # Corkboard connections and notes
    connections = session.connections.all()
    notes = session.detective_notes.all()
    journal = session.journal_entries.all()[:20]

    # Hints used
    hints = case.hints.all()
    hints_used = set(session.hints_taken.values_list('hint_id', flat=True))

    # Existing completed result if already solved
    existing_result = CaseResult.objects.filter(session=session).first()

    context = {
        'case': case,
        'session': session,
        'hotspots_data': hotspots_data,
        'discovered_items': discovered_items,
        'discovered_ids': discovered_ids,
        'discovered_ids_json': json.dumps(list(discovered_ids)),
        'total_evidence_count': case.evidence_items.count(),
        'suspects': suspects,
        'interviewed_topics': interviewed_topics,
        'interview_records': session.interview_records.select_related('topic', 'suspect').all(),
        'contradictions_unlocked': contradictions_unlocked,
        'connections': connections,
        'notes': notes,
        'journal': journal,
        'hints': hints,
        'hints_used': hints_used,
        'existing_result': existing_result,
        'is_guest': session.is_guest,
    }
    return render(request, 'investigations/investigation.html', context)


def leaderboard(request):
    """
    Ranked detectives leaderboard using authoritative database results.
    """
    cases = CaseFile.objects.filter(is_published=True)
    selected_case_slug = request.GET.get('case', 'all')

    results_qs = CaseResult.objects.filter(is_solved=True).select_related('user', 'case')

    if selected_case_slug != 'all':
        results_qs = results_qs.filter(case__slug=selected_case_slug)

    # Aggregate by user if viewing all cases, or display individual case results
    if selected_case_slug == 'all':
        # Detective lifetime leaderboard
        detectives = DetectiveProfile.objects.filter(
            Q(cases_solved__gt=0) | Q(total_score__gt=0)
        ).select_related('user').order_by('-total_score', '-cases_solved')
        leaderboard_data = []
        for rank_num, det in enumerate(detectives[:50], start=1):
            avg_score = round(det.total_score / max(1, det.cases_solved), 1) if det.cases_solved > 0 else det.total_score
            leaderboard_data.append({
                'rank': rank_num,
                'username': det.user.username,
                'badge': det.badge_number,
                'rank_title': det.rank,
                'total_score': det.total_score,
                'cases_solved': det.cases_solved,
                'avg_score': avg_score,
            })
        
        # Include guest solved results
        guest_results = CaseResult.objects.filter(is_solved=True, user=None).order_by('-final_score')[:10]
        rank_offset = len(leaderboard_data) + 1
        for g_res in guest_results:
            leaderboard_data.append({
                'rank': rank_offset,
                'username': 'Guest Operative',
                'badge': f"GUEST-{g_res.session.session_token[:6].upper()}",
                'rank_title': g_res.rank_awarded,
                'total_score': g_res.final_score,
                'cases_solved': 1,
                'avg_score': g_res.final_score,
            })
            rank_offset += 1
    else:
        # Case specific leaderboard
        ranked_results = results_qs.order_by('-final_score', 'time_taken_seconds')[:50]
        leaderboard_data = []
        for rank_num, r in enumerate(ranked_results, start=1):
            user_name = r.user.username if r.user else "Anonymous Guest"
            badge = f"DET-{r.user.id:04d}" if r.user else "GUEST"
            leaderboard_data.append({
                'rank': rank_num,
                'username': user_name,
                'badge': badge,
                'rank_title': r.rank_awarded,
                'total_score': r.final_score,
                'cases_solved': 1,
                'time_taken': f"{r.time_taken_seconds // 60}m {r.time_taken_seconds % 60}s",
                'hints_used': r.hints_used_count,
            })

    context = {
        'cases': cases,
        'selected_case': selected_case_slug,
        'leaderboard_data': leaderboard_data,
    }
    return render(request, 'investigations/leaderboard.html', context)


@login_required
def profile_view(request):
    """
    Detective profile, achievements, preferences, and case history.
    """
    profile, _ = DetectiveProfile.objects.get_or_create(
        user=request.user,
        defaults={'badge_number': f"DET-{request.user.id:04d}"}
    )
    profile.update_rank_and_stats()

    if request.method == 'POST':
        form = DetectiveProfileSettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Investigator preferences updated successfully.")
            return redirect('profile')
    else:
        form = DetectiveProfileSettingsForm(instance=profile)

    completed_results = CaseResult.objects.filter(
        user=request.user
    ).select_related('case').order_by('-completed_at')

    unlocked_achievements = request.user.achievements.select_related('achievement').all()
    all_achievements = Achievement.objects.all()

    context = {
        'profile': profile,
        'form': form,
        'completed_results': completed_results,
        'unlocked_achievements': unlocked_achievements,
        'all_achievements': all_achievements,
    }
    return render(request, 'investigations/profile.html', context)


def how_to_play(request):
    """
    Tactical guide detailing the investigation process, contradiction logic, and scoring.
    """
    return render(request, 'investigations/how_to_play.html')


# ---------------------------------------------------------
# Authentication Views
# ---------------------------------------------------------

def detective_login(request):
    """
    Session-based login for bureau operatives.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back to active duty, Agent {user.username}.")

            # Link any active guest sessions in request.session to this user
            tokens = request.session.get('case_tokens', {})
            if tokens:
                InvestigationSession.objects.filter(
                    session_token__in=tokens.values(), user=None
                ).update(user=user, is_guest=False)

            next_url = request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid bureau credentials. Check your callsign and passphrase.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def detective_register(request):
    """
    New operative recruitment & registration.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = DetectiveRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            DetectiveProfile.objects.create(
                user=user,
                badge_number=f"DET-{user.id:04d}",
                rank='Rookie Investigator'
            )

            login(request, user)
            messages.success(request, f"Credentials issued. Welcome to the Bureau, Detective {user.username}.")

            # Link existing guest sessions
            tokens = request.session.get('case_tokens', {})
            if tokens:
                InvestigationSession.objects.filter(
                    session_token__in=tokens.values(), user=None
                ).update(user=user, is_guest=False)

            return redirect('dashboard')
    else:
        form = DetectiveRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def detective_logout(request):
    """
    Log out operative.
    """
    logout(request)
    messages.info(request, "Logged out of Bureau classified terminal.")
    return redirect('landing')


# ---------------------------------------------------------
# Asynchronous AJAX / JSON Endpoints (Fetch API)
# ---------------------------------------------------------

@require_POST
def api_discover_evidence(request, case_slug):
    """
    AJAX endpoint: Record evidence discovery when hotspot or clue is inspected.
    """
    case = get_object_or_404(CaseFile, slug=case_slug)
    session = get_or_create_session(request, case)

    try:
        data = json.loads(request.body.decode('utf-8'))
        evidence_id = data.get('evidence_id')
    except (ValueError, KeyError):
        return HttpResponseBadRequest(json.dumps({'error': 'Invalid JSON payload'}), content_type='application/json')

    result = discover_evidence_for_session(session, evidence_id)
    return JsonResponse(result)


@require_GET
def api_get_evidence_detail(request, case_slug, evidence_id):
    """
    AJAX endpoint: Retrieve detailed forensic dossier for an evidence item.
    """
    case = get_object_or_404(CaseFile, slug=case_slug)
    evidence = get_object_or_404(Evidence, id=evidence_id, case=case)

    return JsonResponse({
        'id': evidence.id,
        'code': evidence.code,
        'name': evidence.name,
        'evidence_type': evidence.evidence_type,
        'description': evidence.description,
        'location_found': evidence.location_found,
        'forensic_notes': evidence.forensic_notes,
        'image_icon': evidence.image_icon,
        'is_key_clue': evidence.is_key_clue,
    })


@require_POST
def api_interview_suspect(request, case_slug):
    """
    AJAX endpoint: Question suspect regarding an interrogation topic.
    """
    case = get_object_or_404(CaseFile, slug=case_slug)
    session = get_or_create_session(request, case)

    try:
        data = json.loads(request.body.decode('utf-8'))
        suspect_id = data.get('suspect_id')
        topic_id = data.get('topic_id')
    except (ValueError, KeyError):
        return HttpResponseBadRequest(json.dumps({'error': 'Invalid JSON payload'}), content_type='application/json')

    result = conduct_suspect_interview(session, suspect_id, topic_id)
    return JsonResponse(result)


@require_POST
def api_request_hint(request, case_slug):
    """
    AJAX endpoint: Request tiered bureau hint and deduct score penalty.
    """
    case = get_object_or_404(CaseFile, slug=case_slug)
    session = get_or_create_session(request, case)

    try:
        data = json.loads(request.body.decode('utf-8'))
        hint_level = int(data.get('hint_level', 1))
    except (ValueError, KeyError):
        return HttpResponseBadRequest(json.dumps({'error': 'Invalid hint level'}), content_type='application/json')

    result = request_case_hint(session, hint_level)
    return JsonResponse(result)


@require_POST
def api_save_note(request, case_slug):
    """
    AJAX endpoint: Save an investigator note to the corkboard/journal.
    """
    case = get_object_or_404(CaseFile, slug=case_slug)
    session = get_or_create_session(request, case)

    try:
        data = json.loads(request.body.decode('utf-8'))
        content = data.get('content', '')
    except (ValueError, KeyError):
        return HttpResponseBadRequest(json.dumps({'error': 'Invalid payload'}), content_type='application/json')

    result = create_or_update_note(session, content)
    return JsonResponse(result)


@require_POST
def api_connect_board(request, case_slug):
    """
    AJAX endpoint: Connect two evidence/suspect cards on the corkboard with red yarn.
    """
    case = get_object_or_404(CaseFile, slug=case_slug)
    session = get_or_create_session(request, case)

    try:
        data = json.loads(request.body.decode('utf-8'))
        source_type = data.get('source_type')
        source_id = int(data.get('source_id'))
        target_type = data.get('target_type')
        target_id = int(data.get('target_id'))
        notes = data.get('notes', '')
    except (ValueError, TypeError, KeyError):
        return HttpResponseBadRequest(json.dumps({'error': 'Invalid connection parameters'}), content_type='application/json')

    result = link_board_entities(session, source_type, source_id, target_type, target_id, notes)
    return JsonResponse(result)


@require_POST
def api_disconnect_board(request, case_slug):
    """
    AJAX endpoint: Remove connection line from corkboard.
    """
    case = get_object_or_404(CaseFile, slug=case_slug)
    session = get_or_create_session(request, case)

    try:
        data = json.loads(request.body.decode('utf-8'))
        connection_id = int(data.get('connection_id'))
    except (ValueError, TypeError, KeyError):
        return HttpResponseBadRequest(json.dumps({'error': 'Invalid connection ID'}), content_type='application/json')

    result = remove_board_entity_link(session, connection_id)
    return JsonResponse(result)


@require_POST
def api_submit_accusation(request, case_slug):
    """
    AJAX endpoint: Authoritatively submit and evaluate the player's final accusation.
    Guarantees secret solution cannot be inspected prior to final submission.
    """
    case = get_object_or_404(CaseFile, slug=case_slug)
    session = get_or_create_session(request, case)

    try:
        data = json.loads(request.body.decode('utf-8'))
        suspect_id = int(data.get('suspect_id'))
        motive = data.get('motive', '').strip()
        evidence_ids = data.get('evidence_ids', [])
        reasoning = data.get('reasoning', '').strip()
    except (ValueError, TypeError, KeyError):
        return HttpResponseBadRequest(json.dumps({'error': 'Invalid accusation data'}), content_type='application/json')

    if not motive or len(reasoning) < 10 or not suspect_id:
        return HttpResponseBadRequest(
            json.dumps({'error': 'Please provide suspect, motive, and sufficient deduction reasoning.'}),
            content_type='application/json'
        )

    suspect = get_object_or_404(Suspect, id=suspect_id, case=case)
    evidence_qs = case.evidence_items.filter(id__in=evidence_ids)

    # Evaluate against server-authoritative secret solution
    outcome = evaluate_accusation(session, suspect, motive, evidence_qs, reasoning)

    # Record Accusation model
    acc = Accusation.objects.create(
        session=session,
        suspect=suspect,
        motive=motive,
        reasoning=reasoning,
        is_correct=outcome['is_correct'],
        culprit_correct=outcome['culprit_correct'],
        motive_correct=outcome['motive_correct'],
        evidence_correct=outcome['evidence_correct'],
        score_awarded=outcome['score_awarded'],
        feedback=outcome['feedback']
    )
    acc.supporting_evidence.set(evidence_qs)

    # Log to journal
    InvestigationJournal.objects.create(
        session=session,
        entry_type='accusation_made',
        title=f"Warrant Issued: Accusation on {suspect.name}",
        content=f"Outcome: {'CASE SOLVED' if outcome['is_correct'] else 'UNSOLVED'}. Score awarded: {outcome['score_awarded']} pts."
    )

    return JsonResponse(outcome)


@require_GET
def api_get_session_state(request, case_slug):
    """
    AJAX endpoint: Fetch current session state (timer elapsed, score, discovered count).
    Ensures page refreshes preserve authoritative state.
    """
    case = get_object_or_404(CaseFile, slug=case_slug)
    session = get_or_create_session(request, case)

    elapsed_seconds = int((timezone.now() - session.started_at).total_seconds())

    return JsonResponse({
        'session_id': session.id,
        'status': session.status,
        'score': session.score,
        'hints_used': session.hints_used_count,
        'hints_penalty': session.hint_penalty_total,
        'elapsed_seconds': elapsed_seconds,
        'discovered_count': session.discovered_evidence.count(),
        'total_evidence': case.evidence_items.count(),
        'contradictions_count': session.interview_records.filter(contradiction_exposed=True).count(),
    })
