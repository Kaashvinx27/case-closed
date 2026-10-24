import logging
from django.utils import timezone
from .models import (
    InvestigationSession, CaseResult, CaseSecretSolution,
    Achievement, UserAchievement, DetectiveProfile
)

logger = logging.getLogger(__name__)


def evaluate_accusation(session, suspect, submitted_motive, selected_evidence_qs, reasoning):
    """
    Authoritative server-side evaluation of the detective's accusation against the secret solution.
    Never exposes internal solution rules to the client prior to evaluation.
    """
    case = session.case
    try:
        solution = case.solution
    except CaseSecretSolution.DoesNotExist:
        # Fallback if case solution record is missing
        return {
            'is_correct': False,
            'culprit_correct': False,
            'motive_correct': False,
            'evidence_correct': False,
            'score_awarded': 0,
            'feedback': "Case solution data is currently under sealed internal review.",
            'epilogue': "",
            'rank': "Rookie Investigator",
            'final_score': session.score
        }

    # 1. Evaluate Culprit
    culprit_correct = (suspect.id == solution.culprit.id)

    # 2. Evaluate Motive
    # Case-insensitive substring or key terms
    correct_keywords = [w.lower() for w in solution.correct_motive.split() if len(w) > 3]
    sub_motive_lower = submitted_motive.lower()
    motive_matches = sum(1 for kw in correct_keywords if kw in sub_motive_lower)
    motive_correct = (motive_matches >= max(1, len(correct_keywords) // 2)) or (
        solution.correct_motive.lower() in sub_motive_lower
    )

    # 3. Evaluate Supporting Evidence
    required_ids = set(solution.required_evidence.values_list('id', flat=True))
    submitted_ids = set(selected_evidence_qs.values_list('id', flat=True))
    # At least 60% of required evidence identified
    common_evidence = required_ids.intersection(submitted_ids)
    evidence_correct = len(common_evidence) >= max(1, len(required_ids) * 0.6)

    # Calculate points
    earned_points = 0
    if culprit_correct:
        earned_points += solution.culprit_points
    if motive_correct:
        earned_points += solution.motive_points
    if evidence_correct:
        earned_points += solution.evidence_points

    # Bonus for detailed reasoning
    if len(reasoning.strip()) > 50 and culprit_correct:
        earned_points += 25

    # Solved if the actual culprit is correctly identified
    is_overall_solved = culprit_correct

    # Combine with running session score
    # Deduct accumulated hint penalties
    base_session_score = max(0, session.score - session.hint_penalty_total)
    final_score = base_session_score + earned_points
    if not culprit_correct:
        # Modest penalty for falsely accusing an innocent suspect
        final_score = max(0, final_score - 50)

    # Determine rank for this case
    if final_score >= 450:
        rank_awarded = 'Legendary Sleuth'
    elif final_score >= 350:
        rank_awarded = 'Master Detective'
    elif final_score >= 250:
        rank_awarded = 'Senior Investigator'
    elif final_score >= 150:
        rank_awarded = 'Field Detective'
    else:
        rank_awarded = 'Rookie Investigator'

    # Calculate time taken
    time_taken = int((timezone.now() - session.started_at).total_seconds())

    # Build feedback narrative
    if culprit_correct and motive_correct and evidence_correct:
        feedback = (
            f"Flawless deduction, Detective! You saw right through {suspect.name}'s fabricated alibi, "
            f"identified the authentic motive ({solution.correct_motive}), and pinned them down "
            f"with irrefutable material evidence."
        )
    elif culprit_correct:
        feedback = (
            f"Target Confirmed! You correctly identified {suspect.name} as the true culprit. "
            f"While your reconstruction of the exact motive or supporting evidence had minor gaps, "
            f"the Bureau's warrant has been authorized and the case is closed."
        )
    else:
        feedback = (
            f"Arrest Rejected! {suspect.name} provided a verifiable timeline during formal interrogation "
            f"that exculpates them. The true perpetrator escaped justice on this attempt."
        )

    # Record or update CaseResult
    case_result, _ = CaseResult.objects.update_or_create(
        session=session,
        defaults={
            'user': session.user,
            'case': case,
            'is_solved': is_overall_solved,
            'final_score': final_score,
            'max_possible_score': solution.max_score,
            'accuracy_percentage': round((final_score / max(1, solution.max_score)) * 100, 1),
            'rank_awarded': rank_awarded,
            'time_taken_seconds': time_taken,
            'evidence_discovered_count': session.discovered_evidence.count(),
            'total_evidence_count': case.evidence_items.count(),
            'contradictions_count': session.interview_records.filter(contradiction_exposed=True).count(),
            'hints_used_count': session.hints_used_count,
        }
    )

    # Update session status
    session.status = 'completed' if is_overall_solved else 'failed'
    session.completed_at = timezone.now()
    session.score = final_score
    session.save()

    # Update user lifetime stats and evaluate achievements if registered
    unlocked_achievements = []
    if session.user:
        profile, _ = DetectiveProfile.objects.get_or_create(
            user=session.user,
            defaults={'badge_number': f"DET-{session.user.id:04d}"}
        )
        profile.update_rank_and_stats()
        unlocked_achievements = check_achievements(session.user, session, case_result)

    return {
        'is_correct': is_overall_solved,
        'culprit_correct': culprit_correct,
        'motive_correct': motive_correct,
        'evidence_correct': evidence_correct,
        'score_awarded': earned_points,
        'final_score': final_score,
        'rank': rank_awarded,
        'feedback': feedback,
        'epilogue': solution.epilogue if is_overall_solved else "Review the physical evidence and timeline contradictions before attempting a re-investigation.",
        'secret_solution': {
            'culprit_name': solution.culprit.name,
            'motive': solution.correct_motive,
            'motive_details': solution.correct_motive_details,
            'accepted_reasoning': solution.accepted_reasoning,
        } if is_overall_solved else None,
        'unlocked_achievements': unlocked_achievements
    }


def check_achievements(user, session, case_result):
    """
    Awards achievements to registered detectives based on investigation milestones.
    """
    unlocked = []

    def award(code, title, desc, icon='award', color='gold'):
        ach, _ = Achievement.objects.get_or_create(
            code=code,
            defaults={'title': title, 'description': desc, 'icon': icon, 'badge_color': color}
        )
        ua, created = UserAchievement.objects.get_or_create(user=user, achievement=ach)
        if created:
            unlocked.append({'code': code, 'title': title, 'description': desc, 'icon': icon})

    if case_result.is_solved:
        # First Case
        award('first_case', 'First Case Closed', 'Solved your first classified investigation.', 'shield-check', 'crimson')

        # No Hints Needed
        if case_result.hints_used_count == 0:
            award('no_hints', 'Pure Deduction', 'Solved an entire mystery without consulting Bureau hints.', 'lightning-charge', 'gold')

        # Sharp Eyes: discovered 100% of evidence
        if case_result.evidence_discovered_count >= case_result.total_evidence_count:
            award('sharp_eyes', 'Forensic Master', 'Discovered all available crime scene evidence items in a case.', 'eye', 'info')

        # Contradiction Hunter
        if case_result.contradictions_count >= 2:
            award('contradiction_hunter', 'Contradiction Hunter', 'Exposed 2 or more suspect lies during interrogation.', 'chat-square-quote', 'warning')

        # Perfect Deduction
        if case_result.accuracy_percentage >= 90:
            award('perfect_deduction', 'Mastermind Sleuth', 'Achieved an accuracy score of 90% or higher.', 'trophy', 'gold')

        # Marathon Detective (all 3 cases solved)
        solved_cases_count = CaseResult.objects.filter(user=user, is_solved=True).values('case').distinct().count()
        if solved_cases_count >= 3:
            award('marathon_detective', 'Bureau Legend', 'Successfully solved all three active bureau cases.', 'star-fill', 'gold')

    return unlocked
