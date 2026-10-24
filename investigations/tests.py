import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.management import call_command

from investigations.models import (
    CaseFile, Suspect, Evidence, CrimeSceneHotspot, InterviewTopic,
    CaseHint, CaseSecretSolution, InvestigationSession, DiscoveredEvidence,
    InterviewRecord, Accusation, CaseResult, Achievement, DetectiveProfile
)
from investigations.services import (
    get_or_create_session, discover_evidence_for_session,
    conduct_suspect_interview, request_case_hint
)
from investigations.game_logic import evaluate_accusation


class CaseClosedComprehensiveTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Run seed command to load all 3 complete mysteries & achievements
        call_command('seed_cases')

    def setUp(self):
        self.client = Client()
        self.case1 = CaseFile.objects.get(case_number='CASE-001')
        self.case2 = CaseFile.objects.get(case_number='CASE-002')
        self.case3 = CaseFile.objects.get(case_number='CASE-003')

        # Create test detective user
        self.user = User.objects.create_user(
            username='agent_holmes',
            email='holmes@bureau.net',
            password='Password123!'
        )
        self.profile = DetectiveProfile.objects.create(
            user=self.user,
            badge_number='DET-9999',
            rank='Rookie Investigator'
        )

    # 1. Landing page loads
    def test_01_landing_page_loads(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Every Secret")
        self.assertContains(response, "ENTER THE BUREAU")

    # 2. Case listing loads
    def test_02_case_listing_loads(self):
        response = self.client.get(reverse('cases_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The Midnight Will")
        self.assertContains(response, "The Last Frame")
        self.assertContains(response, "Signal Lost")

    # 3. Case briefing is displayed correctly
    def test_03_case_briefing_displayed(self):
        response = self.client.get(reverse('case_briefing', kwargs={'case_slug': self.case1.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Adrian Blackthorn")
        self.assertContains(response, "COMMENCE CRIME SCENE INVESTIGATION")

    # 4. Guest can start an investigation
    def test_04_guest_can_start_investigation(self):
        response = self.client.get(reverse('investigation', kwargs={'case_slug': self.case1.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crime Scene Coordinates")
        # Session token should be saved in guest session
        self.assertIn('case_tokens', self.client.session)
        self.assertIn(self.case1.slug, self.client.session['case_tokens'])

    # 5. Authenticated user can start an investigation
    def test_05_authenticated_user_can_start_investigation(self):
        self.client.login(username='agent_holmes', password='Password123!')
        response = self.client.get(reverse('investigation', kwargs={'case_slug': self.case1.slug}))
        self.assertEqual(response.status_code, 200)
        session = InvestigationSession.objects.filter(user=self.user, case=self.case1).first()
        self.assertIsNotNone(session)
        self.assertFalse(session.is_guest)

    # 6. Evidence can be discovered
    def test_06_evidence_discovery_api(self):
        ev = self.case1.evidence_items.first()
        session = InvestigationSession.objects.create(
            session_token='test-token-06', case=self.case1, is_guest=True
        )
        res = discover_evidence_for_session(session, ev.id)
        self.assertTrue(res['success'])
        self.assertTrue(res['created'])
        self.assertEqual(res['session_score'], 25)
        self.assertEqual(DiscoveredEvidence.objects.filter(session=session, evidence=ev).count(), 1)

    # 7. Duplicate evidence discovery does not award duplicate points
    def test_07_no_duplicate_evidence_score(self):
        ev = self.case1.evidence_items.first()
        session = InvestigationSession.objects.create(
            session_token='test-token-07', case=self.case1, is_guest=True, score=0
        )
        res1 = discover_evidence_for_session(session, ev.id)
        self.assertEqual(res1['session_score'], 25)

        res2 = discover_evidence_for_session(session, ev.id)
        self.assertFalse(res2['created'])
        self.assertEqual(res2['session_score'], 25)
        self.assertEqual(session.score, 25)

    # 8. Suspect interviews work
    def test_08_suspect_interviews_work(self):
        suspect = self.case1.suspects.get(name='Victor Hale')
        topic = suspect.interview_topics.get(topic_key='vh_alibi')
        session = InvestigationSession.objects.create(
            session_token='test-token-08', case=self.case1, is_guest=True, score=0
        )
        res = conduct_suspect_interview(session, suspect.id, topic.id)
        self.assertTrue(res['success'])
        self.assertIn("billiard table", res['response'].lower())
        self.assertEqual(session.score, 10)

    # 9. Evidence-dependent contradictions require their prerequisites
    def test_09_contradiction_prerequisite_logic(self):
        suspect = self.case1.suspects.get(name='Victor Hale')
        contradiction_topic = suspect.interview_topics.get(topic_key='vh_diary_contradiction')
        session = InvestigationSession.objects.create(
            session_token='test-token-09', case=self.case1, is_guest=True
        )

        # Before finding diary evidence AD-08, topic is locked
        res_locked = conduct_suspect_interview(session, suspect.id, contradiction_topic.id)
        self.assertFalse(res_locked['success'])
        self.assertIn("Topic locked", res_locked['error'])

        # Now discover AD-08
        ad08 = self.case1.evidence_items.get(code='AD-08')
        discover_evidence_for_session(session, ad08.id)

        # Now interview succeeds and establishes contradiction
        res_unlocked = conduct_suspect_interview(session, suspect.id, contradiction_topic.id)
        self.assertTrue(res_unlocked['success'])
        self.assertTrue(res_unlocked['is_contradiction'])
        self.assertIn("CONTRADICTION ESTABLISHED", res_unlocked['response'])

    # 10. Hints are recorded and penalized correctly
    def test_10_hints_recorded_and_penalized(self):
        session = InvestigationSession.objects.create(
            session_token='test-token-10', case=self.case1, is_guest=True, score=100
        )
        # Level 1 hint (free)
        h1 = request_case_hint(session, 1)
        self.assertTrue(h1['success'])
        self.assertEqual(h1['penalty'], 0)
        self.assertEqual(session.hint_penalty_total, 0)

        # Level 2 hint (-25 penalty)
        h2 = request_case_hint(session, 2)
        self.assertTrue(h2['success'])
        self.assertEqual(h2['penalty'], 25)
        self.assertEqual(session.hint_penalty_total, 25)

    # 11. Invalid accusations are rejected
    def test_11_invalid_accusations_rejected(self):
        # Missing suspect and empty reasoning
        payload = {
            'suspect_id': 0,
            'motive': '',
            'evidence_ids': [],
            'reasoning': 'short'
        }
        res = self.client.post(
            reverse('api_submit_accusation', kwargs={'case_slug': self.case1.slug}),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)

    # 12. Correct accusations produce expected result
    def test_12_correct_accusations_evaluated(self):
        session = InvestigationSession.objects.create(
            session_token='test-token-12', case=self.case1, user=self.user, is_guest=False, score=100
        )
        victor = self.case1.suspects.get(name='Victor Hale')
        ev_ids = list(self.case1.evidence_items.filter(code__in=['AD-01', 'AD-05', 'AD-07', 'AD-08']).values_list('id', flat=True))
        ev_qs = self.case1.evidence_items.filter(id__in=ev_ids)

        outcome = evaluate_accusation(
            session=session,
            suspect=victor,
            submitted_motive="Embezzlement and Financial Fraud via Helios Holdings",
            selected_evidence_qs=ev_qs,
            reasoning="Victor used his master key V.H. to enter at 11:15 as logged in Clara's diary and struck Adrian to cover up the £45,000 theft."
        )
        self.assertTrue(outcome['is_correct'])
        self.assertTrue(outcome['culprit_correct'])
        self.assertTrue(outcome['motive_correct'])
        self.assertTrue(outcome['evidence_correct'])
        self.assertGreater(outcome['final_score'], 400)
        self.assertEqual(session.status, 'completed')

    # 13. Incorrect accusations are handled correctly
    def test_13_incorrect_accusations_handled(self):
        session = InvestigationSession.objects.create(
            session_token='test-token-13', case=self.case1, user=self.user, is_guest=False, score=50
        )
        innocent_suspect = self.case1.suspects.get(name='Thomas Reed')
        ev_qs = self.case1.evidence_items.filter(code='AD-03')

        outcome = evaluate_accusation(
            session=session,
            suspect=innocent_suspect,
            submitted_motive="Revenge for being fired",
            selected_evidence_qs=ev_qs,
            reasoning="He was mad about his job and left bootprints outside."
        )
        self.assertFalse(outcome['is_correct'])
        self.assertFalse(outcome['culprit_correct'])
        self.assertEqual(session.status, 'failed')
        self.assertIn("Arrest Rejected", outcome['feedback'])

    # 14. Scores are calculated on the backend
    def test_14_score_calculation_backend_authoritative(self):
        session = InvestigationSession.objects.create(
            session_token='test-token-14', case=self.case1, score=50
        )
        discover_evidence_for_session(session, self.case1.evidence_items.first().id)
        session.refresh_from_db()
        self.assertEqual(session.score, 75)

    # 15. Case results are not awarded twice
    def test_15_case_result_uniqueness_per_session(self):
        session = InvestigationSession.objects.create(
            session_token='test-token-15', case=self.case1, user=self.user, is_guest=False
        )
        victor = self.case1.suspects.get(name='Victor Hale')
        ev_qs = self.case1.evidence_items.all()

        evaluate_accusation(session, victor, "Embezzlement", ev_qs, "Full deduction reasoning details here.")
        count1 = CaseResult.objects.filter(session=session).count()
        self.assertEqual(count1, 1)

        # Evaluating again updates the same record instead of duplicating
        evaluate_accusation(session, victor, "Embezzlement", ev_qs, "Full deduction reasoning details here.")
        count2 = CaseResult.objects.filter(session=session).count()
        self.assertEqual(count2, 1)

    # 16. Private sessions cannot be accessed by unauthorized users
    def test_16_private_session_management(self):
        other_user = User.objects.create_user('agent_other', 'other@bureau.net', 'Pass12345!')
        session = InvestigationSession.objects.create(
            session_token='token-priv-16', case=self.case1, user=other_user, is_guest=False
        )
        self.assertNotEqual(session.user, self.user)

    # 17. Leaderboard rankings use real stored results
    def test_17_leaderboard_uses_real_results(self):
        # Create a genuine solved result
        session = InvestigationSession.objects.create(
            session_token='token-lb-17', case=self.case1, user=self.user, is_guest=False, status='completed'
        )
        CaseResult.objects.create(
            session=session,
            user=self.user,
            case=self.case1,
            is_solved=True,
            final_score=480,
            rank_awarded='Legendary Sleuth',
            time_taken_seconds=600
        )
        self.profile.update_rank_and_stats()

        res = self.client.get(reverse('leaderboard'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "agent_holmes")
        self.assertContains(res, "480")

    # 18. Case solutions are not leaked in public endpoints
    def test_18_solution_not_leaked_in_public_api(self):
        # Inspect case briefing and workspace HTML
        briefing_res = self.client.get(reverse('case_briefing', kwargs={'case_slug': self.case1.slug}))
        self.assertNotContains(briefing_res, "Victor Hale had systematically stolen £45,000")
        self.assertNotContains(briefing_res, "Helios Holdings bank records")

        # Inspect evidence detail endpoint
        ev = self.case1.evidence_items.first()
        ev_detail = self.client.get(reverse('api_get_evidence_detail', kwargs={'case_slug': self.case1.slug, 'evidence_id': ev.id}))
        data = ev_detail.json()
        self.assertNotIn('culprit', data)
        self.assertNotIn('solution', data)
        self.assertNotIn('secret_epilogue', data)

    # 19. Database relationships and migrations work
    def test_19_database_integrity_and_relationships(self):
        self.assertEqual(self.case1.suspects.count(), 4)
        self.assertEqual(self.case1.evidence_items.count(), 8)
        self.assertEqual(self.case2.suspects.count(), 4)
        self.assertEqual(self.case2.evidence_items.count(), 10)
        self.assertEqual(self.case3.suspects.count(), 4)
        self.assertEqual(self.case3.evidence_items.count(), 10)
        self.assertIsNotNone(self.case1.solution)
        self.assertIsNotNone(self.case2.solution)
        self.assertIsNotNone(self.case3.solution)

    # 20. Guest sessions behave consistently after navigation and refresh
    def test_20_guest_session_consistency_on_refresh(self):
        # 1st request generates guest token
        res1 = self.client.get(reverse('investigation', kwargs={'case_slug': self.case1.slug}))
        token1 = self.client.session['case_tokens'][self.case1.slug]

        # 2nd request reuses existing session
        res2 = self.client.get(reverse('investigation', kwargs={'case_slug': self.case1.slug}))
        token2 = self.client.session['case_tokens'][self.case1.slug]

        self.assertEqual(token1, token2)
        session = InvestigationSession.objects.get(session_token=token1)
        self.assertTrue(session.is_guest)
        self.assertEqual(session.status, 'in_progress')
