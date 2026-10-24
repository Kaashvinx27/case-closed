"""
Django management command: seed_cases
Populates the three complete playable fictional murder mysteries:
1. CASE-001: The Midnight Will (Blackthorn Manor)
2. CASE-002: The Last Frame (Bellwether Museum)
3. CASE-003: Signal Lost (Orion Research Observatory)

Safe to rerun multiple times without duplicating data or breaking user investigations.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from investigations.models import (
    CaseFile, Suspect, Evidence, CrimeSceneHotspot, InterviewTopic,
    CaseHint, CaseSecretSolution, Achievement
)


class Command(BaseCommand):
    help = "Seed the three authoritative Case Closed murder mysteries and achievements."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Commencing Case Closed dataset seeding..."))

        with transaction.atomic():
            self.seed_achievements()
            self.seed_case_001()
            self.seed_case_002()
            self.seed_case_003()

        self.stdout.write(self.style.SUCCESS("All three cases, suspects, evidence, hotspots, hints, and solutions successfully seeded!"))

    def seed_achievements(self):
        achievements_data = [
            {
                'code': 'first_case',
                'title': 'First Case Closed',
                'description': 'Solve your first classified murder mystery in the Bureau files.',
                'icon': 'shield-check',
                'badge_color': 'crimson'
            },
            {
                'code': 'no_hints',
                'title': 'Pure Deduction',
                'description': 'Solve an entire case without consulting any Bureau hints.',
                'icon': 'lightning-charge',
                'badge_color': 'gold'
            },
            {
                'code': 'sharp_eyes',
                'title': 'Forensic Master',
                'description': 'Locate and catalog every physical and digital evidence item in a case.',
                'icon': 'eye',
                'badge_color': 'info'
            },
            {
                'code': 'contradiction_hunter',
                'title': 'Contradiction Hunter',
                'description': 'Expose 2 or more suspect lies during formal interrogations.',
                'icon': 'chat-square-quote',
                'badge_color': 'warning'
            },
            {
                'code': 'perfect_deduction',
                'title': 'Mastermind Sleuth',
                'description': 'Achieve a 90% or higher score on your final accusation deduction.',
                'icon': 'trophy',
                'badge_color': 'gold'
            },
            {
                'code': 'marathon_detective',
                'title': 'Bureau Legend',
                'description': 'Complete all three active classified cases in the Bureau archive.',
                'icon': 'star-fill',
                'badge_color': 'gold'
            },
        ]
        for a in achievements_data:
            Achievement.objects.update_or_create(code=a['code'], defaults=a)
        self.stdout.write(self.style.SUCCESS("✓ Seeded achievements."))

    def seed_case_001(self):
        case, _ = CaseFile.objects.update_or_create(
            case_number='CASE-001',
            defaults={
                'title': 'The Midnight Will',
                'slug': 'the-midnight-will',
                'genre': 'Estate Mystery',
                'difficulty': 'Easy',
                'estimated_time': '15-20 min',
                'location': 'Blackthorn Manor, Private Study',
                'incident_date': 'October 14, 11:40 PM',
                'victim_name': 'Adrian Blackthorn',
                'victim_profile': 'Age 64. Wealthy industrialist and collector of rare artifacts. Secretive patriarch who recently discovered extensive financial irregularities.',
                'initial_findings': 'Adrian Blackthorn was found dead at his mahogany desk during a thunderstorm. The cause of death was blunt force trauma from a heavy brass letter opener. The door was locked from the inside, but a duplicate master key existed. A torn draft will was burning in the hearth.',
                'known_circumstances': 'At 8:30 PM dinner, Adrian publicly announced he would disinherit his daughter Eleanor and terminate Victor Hale as his financial trustee. The household was sequestered due to flooded roads.',
                'synopsis': 'A wealthy patriarch changes his will during a stormy dinner party. Before midnight, he is murdered in his locked study. Four suspects with distinct alibis and financial secrets remain in the manor.',
                'scene_title': 'Adrian Blackthorn\'s Private Study',
                'scene_description': 'A wood-paneled Victorian study with high arched bookshelves, a stone fireplace hearth, tall rain-streaked French windows leading to the terrace, and a heavy mahogany executive desk.',
                'scene_theme': 'study',
                'is_published': True,
                'order': 1
            }
        )

        # Suspects
        eleanor, _ = Suspect.objects.update_or_create(
            case=case, name='Eleanor Blackthorn',
            defaults={
                'age': 29,
                'occupation': 'Art Dealer & Socialite',
                'relationship_to_victim': 'Victim\'s Estranged Daughter',
                'alibi': 'Claims she argued with her father at 9:00 PM, then retreated to the conservatory weeping until midnight.',
                'known_motive': 'Faced disinheritance and crippling private gambling debts of over £80,000.',
                'personality_notes': 'Defensive, proud, anxious, frequently checking her wristwatch.',
                'portrait_icon': 'person-standing',
                'opening_statement': 'I had my differences with Father, but I loved him. When he said he would cut me off, I lost my temper, but I never went back into that study!',
                'order': 1
            }
        )

        victor, _ = Suspect.objects.update_or_create(
            case=case, name='Victor Hale',
            defaults={
                'age': 52,
                'occupation': 'Estate Financial Adviser & Fiduciary',
                'relationship_to_victim': 'Accountant & Business Manager for 15 Years',
                'alibi': 'Claims he was in the billiard room reviewing tax records alone from 11:00 PM to 11:45 PM.',
                'known_motive': 'Adrian\'s revised will initiated a comprehensive audit of all estate accounts, exposing Victor\'s systematic embezzlement.',
                'personality_notes': 'Polished, calculated, speaks with clipped precision, visibly sweats when pressed about ledgers.',
                'portrait_icon': 'person-badge',
                'opening_statement': 'Adrian was a valued client and a close associate. I spent the late evening preparing tax documentation in the billiard room. Any insinuation against my character is utterly groundless.',
                'order': 2
            }
        )

        clara, _ = Suspect.objects.update_or_create(
            case=case, name='Clara Wren',
            defaults={
                'age': 34,
                'occupation': 'Personal Secretary & Archivist',
                'relationship_to_victim': 'Confidential Assistant for 6 Years',
                'alibi': 'Delivered chamomile tea at 10:30 PM, then retired to the staff library to transcribe dictation tapes.',
                'known_motive': 'Adrian knew Clara had secretly copied confidential estate documents; her position was precarious.',
                'personality_notes': 'Observant, quiet, meticulous record-keeper with a photographic memory.',
                'portrait_icon': 'person-check',
                'opening_statement': 'Mr. Blackthorn was agitated all evening. He asked me to keep the master appointment logbook under lock and key. He told me someone was bleeding the estate dry.',
                'order': 3
            }
        )

        thomas, _ = Suspect.objects.update_or_create(
            case=case, name='Thomas Reed',
            defaults={
                'age': 45,
                'occupation': 'Head Groundskeeper',
                'relationship_to_victim': 'Estate Groundskeeper for 8 Years',
                'alibi': 'Claims he drank hard cider in the tool shed after Adrian dismissed him that afternoon for alleged insubordination.',
                'known_motive': 'Adrian fired him without pension after discovering antique estate lanterns missing.',
                'personality_notes': 'Gruff, weathered, resentful, prone to outbursts.',
                'portrait_icon': 'tools',
                'opening_statement': 'Old Adrian threw me out like rubbish after eight years of back-breaking labor. I was mad enough to spit fire, but I stayed in the tool shed all night weathering the gale.',
                'order': 4
            }
        )

        # Evidence
        ad01, _ = Evidence.objects.update_or_create(
            case=case, code='AD-01',
            defaults={
                'name': 'Disputed Draft Will',
                'evidence_type': 'Document',
                'location_found': 'Study Fireplace Hearth',
                'description': 'Torn legal draft dated October 14, 11:15 PM. Explicitly revokes Victor Hale\'s power of attorney and instructs an external forensic audit of all estate holdings.',
                'forensic_notes': 'Edges singed by fire. Scrawled in Adrian\'s genuine hand with Parker fountain pen.',
                'image_icon': 'file-earmark-break',
                'is_key_clue': True,
                'order': 1
            }
        )

        ad02, _ = Evidence.objects.update_or_create(
            case=case, code='AD-02',
            defaults={
                'name': 'Smashed Grandfather Clock',
                'evidence_type': 'Physical Object',
                'location_found': 'Study Corner by the Door',
                'description': 'Mahogany pendulum clock. Dial glass shattered and hands frozen at 11:22 PM.',
                'forensic_notes': 'Internal mechanical inspection reveals the pendulum escapement was stopped manually by hand, not by the impact. The time was intentionally staged.',
                'image_icon': 'clock-history',
                'is_key_clue': True,
                'order': 2
            }
        )

        ad03, _ = Evidence.objects.update_or_create(
            case=case, code='AD-03',
            defaults={
                'name': 'Muddy Bootprints',
                'evidence_type': 'Forensic Trace',
                'location_found': 'Terrace French Windows',
                'description': 'Heavy mud tracks corresponding to size 9 work boots leading to the study terrace.',
                'forensic_notes': 'The French windows were securely bolted from the INSIDE. Whoever left the bootprints could not have entered or exited through this window.',
                'image_icon': 'footprints',
                'is_key_clue': False,
                'order': 3
            }
        )

        ad04, _ = Evidence.objects.update_or_create(
            case=case, code='AD-04',
            defaults={
                'name': 'Antique Letter Opener',
                'evidence_type': 'Physical Object',
                'location_found': 'Mahogany Desk Surface',
                'description': 'Heavy solid brass dagger-style letter opener bearing the Blackthorn crest. Stained with blood matching Adrian.',
                'forensic_notes': 'Carefully wiped with cloth. However, microscopic residue of expensive lavender talcum powder was recovered from the decorative hilt groove.',
                'image_icon': 'shield-slash',
                'is_key_clue': True,
                'order': 4
            }
        )

        ad05, _ = Evidence.objects.update_or_create(
            case=case, code='AD-05',
            defaults={
                'name': 'Confidential Audit Ledger',
                'evidence_type': 'Document',
                'location_found': 'Concealed Desk Compartment',
                'description': 'Handwritten audit prepared by Adrian Blackthorn. Highlights £45,000 siphoned over 24 months to an offshore entity named \'Helios Holdings\'.',
                'forensic_notes': 'A note in the margin states: "Victor has been forging dividend signatures. Confront him tonight before contacting Scotland Yard."',
                'image_icon': 'journal-text',
                'is_key_clue': True,
                'order': 5
            }
        )

        ad06, _ = Evidence.objects.update_or_create(
            case=case, code='AD-06',
            defaults={
                'name': 'Porcelain Tea Cup with Sedative Residue',
                'evidence_type': 'Forensic Trace',
                'location_found': 'Study Side Table',
                'description': 'Half-consumed cup of Earl Grey tea with lemon.',
                'forensic_notes': 'Chemical toxicology reveals a heavy dose of Chloral Hydrate (a fast-acting hypnotic sedative). The sedative explain why Adrian suffered no defensive wounds.',
                'image_icon': 'cup-hot',
                'is_key_clue': True,
                'order': 6
            }
        )

        ad07, _ = Evidence.objects.update_or_create(
            case=case, code='AD-07',
            defaults={
                'name': 'Duplicate Master Key',
                'evidence_type': 'Physical Object',
                'location_found': 'Fallen Behind Cast-Iron Radiator',
                'description': 'Heavy brass passkey capable of unlocking all Blackthorn Manor interior doors, including the study.',
                'forensic_notes': 'Attached to a silver keychain engraved with the monogram \'V.H.\' Trace fibers from fine cashmere suit pocket.',
                'image_icon': 'key',
                'is_key_clue': True,
                'order': 7
            }
        )

        ad08, _ = Evidence.objects.update_or_create(
            case=case, code='AD-08',
            defaults={
                'name': 'Clara\'s Daily Appointment Diary',
                'evidence_type': 'Document',
                'location_found': 'Secretary Bureau in Hallway',
                'description': 'Official household logbook kept by Clara Wren.',
                'forensic_notes': 'Entry at 11:15 PM reads: "Private conference in Study requested by Victor Hale to resolve ledger disputes."',
                'image_icon': 'calendar-check',
                'is_key_clue': True,
                'order': 8
            }
        )

        # Hotspots
        hotspots_case1 = [
            (ad01, 'Hearth Ashes', 25.0, 68.0, 'fire', 'Search the fireplace hearth for burned documents.'),
            (ad02, 'Grandfather Clock', 12.0, 38.0, 'clock', 'Inspect the broken grandfather clock face and mechanism.'),
            (ad03, 'Terrace French Windows', 85.0, 42.0, 'door-open', 'Examine the muddy bootprints on the terrace stones.'),
            (ad04, 'Mahogany Desk', 50.0, 52.0, 'shield-slash', 'Inspect the bloodied brass letter opener on the desk blotter.'),
            (ad05, 'Secret Desk Drawer', 58.0, 56.0, 'journal-text', 'Examine the locked wooden drawer beneath the desk.'),
            (ad06, 'Side Table Tea Set', 38.0, 48.0, 'cup-hot', 'Analyze the half-empty teacup on the side table.'),
            (ad07, 'Cast-Iron Radiator', 78.0, 75.0, 'key', 'Check the narrow space behind the heating radiator.'),
            (ad08, 'Secretary Bureau', 90.0, 20.0, 'calendar-check', 'Inspect the archivist\'s appointment logbook near the hall door.'),
        ]
        for ev, label, x, y, icon, hint in hotspots_case1:
            CrimeSceneHotspot.objects.update_or_create(
                case=case, evidence=ev,
                defaults={'label': label, 'x_percent': x, 'y_percent': y, 'icon': icon, 'inspect_hint': hint}
            )

        # Interview Topics
        # Victor Hale
        InterviewTopic.objects.update_or_create(
            suspect=victor, topic_key='vh_alibi',
            defaults={
                'title': 'Billiard Room Alibi',
                'question_text': 'You claim you were in the billiard room alone between 11:00 PM and midnight?',
                'response_text': 'Precisely. I had a glass of port and was cross-referencing tax exemptions. I never left the billiard table until the screams started.',
                'order': 1
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=victor, topic_key='vh_estate_finances',
            defaults={
                'title': 'Adrian\'s Financial Inquiries',
                'question_text': 'Did Adrian question your management of the estate accounts during dinner?',
                'response_text': 'Adrian was an eccentric gentleman who often imagined discrepancies where none existed. Every transaction under my fiduciary care was fully documented.',
                'order': 2
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=victor, topic_key='vh_diary_contradiction',
            defaults={
                'title': 'Confront with Appointment Log',
                'question_text': 'Clara\'s official diary records a private 11:15 PM conference scheduled with Adrian in his study.',
                'response_text': 'That was cancelled! Or rather... wait. Clara must have made an error in her booking notes.',
                'required_evidence': ad08,
                'is_contradiction': True,
                'contradiction_evidence': ad08,
                'contradiction_reaction': 'Victor breaks into a cold sweat: "All right! I went to his door at 11:15, but he was already dead! I panicked because of the missing money!" (CONTRADICTION ESTABLISHED)',
                'order': 3
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=victor, topic_key='vh_master_key',
            defaults={
                'title': 'Engraved Master Key',
                'question_text': 'We recovered a duplicate master key behind the study radiator stamped with your monogram \'V.H.\'.',
                'response_text': 'How did that get there?! Adrian must have taken my keys during our dispute earlier this afternoon!',
                'required_evidence': ad07,
                'is_contradiction': True,
                'contradiction_evidence': ad07,
                'contradiction_reaction': 'Victor grips his collar: "You found it? I dropped it in the dark when... no! I tell you, he was going to destroy everything I spent fifteen years building!"',
                'order': 4
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=victor, topic_key='vh_helios_audit',
            defaults={
                'title': 'Helios Holdings Embezzlement',
                'question_text': 'Adrian discovered your shell corporation \'Helios Holdings\' and £45,000 in diverted funds.',
                'response_text': 'Helios was an offshore vehicle created with his verbal permission! He was suffering from cognitive decline and forgot our financial agreements!',
                'required_evidence': ad05,
                'order': 5
            }
        )

        # Eleanor
        InterviewTopic.objects.update_or_create(
            suspect=eleanor, topic_key='eb_disinherit',
            defaults={
                'title': 'Dinner Table Argument',
                'question_text': 'Adrian announced he was cutting you from his will due to debts.',
                'response_text': 'I yelled at him, yes. He was tyrannical and wanted to control my art gallery. But I would never hurt him. I went straight to the conservatory to calm down.',
                'order': 1
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=eleanor, topic_key='eb_suspicions',
            defaults={
                'title': 'Suspicions Regarding Estate Management',
                'question_text': 'Had you noticed any tension between your father and his advisers recently?',
                'response_text': 'Father had grown deeply suspicious of Victor over the last month. He told me Victor was stalling on the accounts and hiding offshore shell entities.',
                'order': 2
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=eleanor, topic_key='eb_terrace_boots',
            defaults={
                'title': 'Terrace Footprints Observation',
                'question_text': 'Did you see anyone on the terrace outside during the storm?',
                'response_text': 'From the conservatory glass, I saw someone moving in heavy boots around 11:20 PM near the study terrace, but the figure looked bulky like groundskeeper Reed.',
                'required_evidence': ad03,
                'order': 3
            }
        )

        # Clara
        InterviewTopic.objects.update_or_create(
            suspect=clara, topic_key='cw_evening_schedule',
            defaults={
                'title': 'Adrian\'s Mood & Schedule Tonight',
                'question_text': 'What was Mr. Blackthorn working on in his study throughout the late evening?',
                'response_text': 'He was reviewing audit ledgers and drafting a revised will. He instructed me to keep all appointment logbooks under lock and key and warned me that a confrontation was coming tonight.',
                'order': 1
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=clara, topic_key='cw_tea',
            defaults={
                'title': 'The Evening Tea',
                'question_text': 'Did you deliver the tea found on Adrian\'s desk?',
                'response_text': 'I made chamomile tea at 10:30 PM. But when Victor went into the kitchen at 11:00 PM, he said Adrian wanted Earl Grey instead and insisted on brewing it himself.',
                'required_evidence': ad06,
                'order': 2
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=clara, topic_key='cw_clock',
            defaults={
                'title': 'The Grandfather Clock',
                'question_text': 'Was the study clock working earlier in the evening?',
                'response_text': 'Yes! It chimed precisely at 11:00 PM when I delivered the night mail. The clock was Adrian\'s pride; it never ran slow or jammed.',
                'required_evidence': ad02,
                'order': 3
            }
        )

        # Thomas Reed
        InterviewTopic.objects.update_or_create(
            suspect=thomas, topic_key='tr_alibi',
            defaults={
                'title': 'Presence During the Gale',
                'question_text': 'Can anyone corroborate your whereabouts in the tool shed throughout the storm?',
                'response_text': 'The scullery maid saw my storm lantern glowing from the shed window through the rain. I never stepped foot near the study terrace after sundown.',
                'order': 1
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=thomas, topic_key='tr_dismissal',
            defaults={
                'title': 'Adrian\'s Threat of Dismissal',
                'question_text': 'Why did Mr. Blackthorn threaten to discharge you from service earlier today?',
                'response_text': 'Adrian accused me of stealing antique carriage lanterns! Someone moved them into the cellar, and before I could explain, he threatened to sack me without a shilling.',
                'order': 2
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=thomas, topic_key='tr_boots',
            defaults={
                'title': 'Size 9 Work Boots',
                'question_text': 'The mud tracks on the terrace match your size 9 work boots.',
                'response_text': 'Those aren\'t my current boots! My spare mud boots were stolen right off the boot rack in the back scullery around 10 o\'clock. Look at my feet—I\'ve been in my dry slippers all night!',
                'required_evidence': ad03,
                'order': 3
            }
        )

        # Hints
        CaseHint.objects.update_or_create(
            case=case, hint_level=1,
            defaults={
                'hint_text': 'Examine the locked room mechanics. How could the murderer enter and lock the study if Adrian was found inside alone? Look for duplicate keys and check who had access to the master locks.',
                'penalty_points': 0
            }
        )
        CaseHint.objects.update_or_create(
            case=case, hint_level=2,
            defaults={
                'hint_text': 'The grandfather clock stopped at 11:22 PM was stopped deliberately by hand to create an alibi. Compare Clara\'s appointment diary with Victor Hale\'s claimed billiard room timeline.',
                'penalty_points': 25
            }
        )
        CaseHint.objects.update_or_create(
            case=case, hint_level=3,
            defaults={
                'hint_text': 'Cross-reference the stamped monogram initials on the duplicate key recovered behind the radiator with the late-night visitor listed in Clara\'s 11:15 PM appointment log. Reconstruct who brewed the Earl Grey tea and whose offshore accounts were targeted in the secret desk drawer.',
                'penalty_points': 50
            }
        )

        # Secret Solution
        sol, _ = CaseSecretSolution.objects.update_or_create(
            case=case,
            defaults={
                'culprit': victor,
                'correct_motive': 'Embezzlement and Financial Fraud',
                'correct_motive_details': 'Victor Hale had systematically stolen £45,000 from the estate via Helios Holdings. Adrian\'s new will and impending midnight audit would have resulted in Victor\'s criminal conviction and financial ruin.',
                'accepted_reasoning': 'Victor laced Adrian\'s tea with chloral hydrate, used his duplicate master key (AD-07) to enter at 11:15 PM as logged in Clara\'s diary (AD-08), argued over the audit ledger (AD-05), struck Adrian with the letter opener (AD-04), burned the draft will (AD-01), stopped the clock at 11:22 PM (AD-02) to frame Thomas Reed, and fled through the interior door.',
                'epilogue': 'Scotland Yard arrived at Blackthorn Manor at dawn. Confronted with the Helios Holdings bank records and the duplicate master key with his initials recovered from behind the radiator, Victor Hale broke down and signed a full confession. Eleanor Blackthorn inherited the estate under the original protective trust.',
                'max_score': 500,
                'evidence_point_val': 25,
                'contradiction_point_val': 50,
                'culprit_points': 200,
                'motive_points': 100,
                'evidence_points': 100,
            }
        )
        sol.required_evidence.set([ad01, ad05, ad07, ad08])
        self.stdout.write(self.style.SUCCESS("✓ Seeded CASE-001: The Midnight Will."))

    def seed_case_002(self):
        case, _ = CaseFile.objects.update_or_create(
            case_number='CASE-002',
            defaults={
                'title': 'The Last Frame',
                'slug': 'the-last-frame',
                'genre': 'Art-World Thriller',
                'difficulty': 'Medium',
                'estimated_time': '20-25 min',
                'location': 'Bellwether Museum, Conservation Room B',
                'incident_date': 'November 3, 21:30 PM',
                'victim_name': 'Julian Cross',
                'victim_profile': 'Age 48. Celebrated chief conservator and scholar of Renaissance masterpieces. Globally recognized for unmasking international forgeries.',
                'initial_findings': 'Julian Cross was discovered dead on the parquet floor of Conservation Room B, struck on the skull with a heavy bronze framing clamp. The museum\'s star attraction, \'The Veiled Saint\' ($12M), remained untouched on the central easel. Security camera recording suffered a 10-minute blindspot.',
                'known_circumstances': 'An exclusive VIP fundraising gala was underway on the ground floor galleries. Electronic access to Conservation Room B was strictly restricted to authorized staff keycards.',
                'synopsis': 'During a museum gala, chief conservator Julian Cross is found bludgeoned in a secure restoration lab. The $12M masterpiece appears safe, but altered provenance records and forensic traces suggest a daring forgery ring.',
                'scene_title': 'Conservation Room B & Restoration Studio',
                'scene_description': 'A high-ceilinged archival laboratory with chemical fume hoods, UV inspection tables, restoration easels, locked glass cabinets of historical pigments, and a heavy emergency fire exit.',
                'scene_theme': 'museum',
                'is_published': True,
                'order': 2
            }
        )

        # Suspects
        mara, _ = Suspect.objects.update_or_create(
            case=case, name='Mara Voss',
            defaults={
                'age': 38,
                'occupation': 'Deputy Museum Curator',
                'relationship_to_victim': 'Professional Colleague & Rival',
                'alibi': 'Claims she escorted prominent trustees on a tour of the Renaissance wing between 21:00 and 21:35 PM.',
                'known_motive': 'Julian blocked her promotion to director and accused her of approving dubious acquisition provenance.',
                'personality_notes': 'Ambitious, poised, sharp intellect, dismissive of conservation technicalities.',
                'portrait_icon': 'person-workspace',
                'opening_statement': 'Julian was brilliant but paranoid. He treated every canvas as a crime scene. I was with our board trustees all evening; our gallery tour is on public CCTV.',
                'order': 1
            }
        )

        daniel, _ = Suspect.objects.update_or_create(
            case=case, name='Daniel Price',
            defaults={
                'age': 42,
                'occupation': 'Master Chemical Restoration Specialist',
                'relationship_to_victim': 'Technical Partner in Restoration Wing',
                'alibi': 'Claims his keycard was pickpocketed from his coat at the gala bar around 20:30 PM, and he never entered the third floor after 20:00 PM.',
                'known_motive': 'Julian discovered that Daniel had replaced \'The Veiled Saint\' with an undetectable forgery to smuggle the genuine painting to a private Swiss buyer.',
                'personality_notes': 'Nervous, hands stained with chemical solvent, speaks rapidly, glances repeatedly at exit doors.',
                'portrait_icon': 'palette',
                'opening_statement': 'I left my coat on the gala rack and someone took my card! Why would I harm Julian? We worked side-by-side for eight years restoring historic tapestries!',
                'order': 2
            }
        )

        sofia, _ = Suspect.objects.update_or_create(
            case=case, name='Sofia Laurent',
            defaults={
                'age': 45,
                'occupation': 'Private Art Collector & Philanthropist',
                'relationship_to_victim': 'Benefactor who loaned \'The Veiled Saint\'',
                'alibi': 'Giving a live broadcast speech in the Grand Atrium from 21:15 to 21:30 PM.',
                'known_motive': 'Facing bankruptcy, she contracted with Daniel to clone her own family heirloom and secretly liquidate the original.',
                'personality_notes': 'Glamorous, haughty, impeccably dressed in evening silk, guarded.',
                'portrait_icon': 'gem',
                'opening_statement': 'My family has preserved \'The Veiled Saint\' for three generations. The suggestion that I would permit harm to come to Julian or my painting is insulting.',
                'order': 3
            }
        )

        ethan, _ = Suspect.objects.update_or_create(
            case=case, name='Ethan Cole',
            defaults={
                'age': 31,
                'occupation': 'Head of Museum Security',
                'relationship_to_victim': 'Security Oversight Supervisor',
                'alibi': 'Monitoring dispatch screens in Central Command; acknowledges a 10-minute server maintenance reboot occurred.',
                'known_motive': 'Accepted cash bribes to disable third-floor surveillance cameras during gala events.',
                'personality_notes': 'Evasive, ex-police officer, defensive when questioning security protocols.',
                'portrait_icon': 'shield-lock',
                'opening_statement': 'The server reboot between 21:10 and 21:20 PM was an automated system maintenance scheduled by our IT vendor. I cannot control when the operating system pushes updates.',
                'order': 4
            }
        )

        # Evidence
        lf01, _ = Evidence.objects.update_or_create(
            case=case, code='LF-01',
            defaults={
                'name': 'Electronic Access Log #04',
                'evidence_type': 'Digital',
                'location_found': 'Room B Card Reader Database',
                'description': 'Encrypted server log showing Keycard #04 (issued to Daniel Price) swiped the magnetic lock of Conservation Room B at 21:14:22 PM.',
                'forensic_notes': 'Card was not reported lost until 22:15 PM, forty-five minutes after the body was discovered.',
                'image_icon': 'credit-card-2-front',
                'is_key_clue': True,
                'order': 1
            }
        )

        lf02, _ = Evidence.objects.update_or_create(
            case=case, code='LF-02',
            defaults={
                'name': 'UV Spectrometry Inspection',
                'evidence_type': 'Forensic',
                'location_found': 'Easel Inspection Table',
                'description': 'Portable 365nm UV lamp test on \'The Veiled Saint\'. Modern synthetic zinc white and titanium pigments fluoresce vivid yellow-green.',
                'forensic_notes': 'A genuine 15th-century Renaissance tempera does not fluoresce in this wavelength. The painting on the easel is a master-level modern forgery executed within the last 6 months.',
                'image_icon': 'lamp',
                'is_key_clue': True,
                'order': 2
            }
        )

        lf03, _ = Evidence.objects.update_or_create(
            case=case, code='LF-03',
            defaults={
                'name': 'Bloodied Bronze Frame Clamp',
                'evidence_type': 'Physical Object',
                'location_found': 'Chemical Washing Sink',
                'description': 'Heavy 4-kilogram bronze restoration clamp. Corners stained with cranial blood matching Julian Cross.',
                'forensic_notes': 'The screw threads carry traces of fresh dammar resin varnish, turpentine, and distinctive blue lapis lazuli pigment.',
                'image_icon': 'tools',
                'is_key_clue': True,
                'order': 3
            }
        )

        lf04, _ = Evidence.objects.update_or_create(
            case=case, code='LF-04',
            defaults={
                'name': 'Security Blindspot Memo',
                'evidence_type': 'Document',
                'location_found': 'Security Guard Booth Desk',
                'description': 'Handwritten memo signed by Ethan Cole scheduling the server reboot for 21:10 PM during the gala toast.',
                'forensic_notes': 'Fingerprints belonging to both Ethan Cole and Daniel Price recovered from the paper.',
                'image_icon': 'file-earmark-lock',
                'is_key_clue': False,
                'order': 4
            }
        )

        lf05, _ = Evidence.objects.update_or_create(
            case=case, code='LF-05',
            defaults={
                'name': 'Navy Cashmere Wool Fiber',
                'evidence_type': 'Forensic',
                'location_found': 'Emergency Fire Exit Latch',
                'description': 'Snagged textile fibers on the jagged metal latch of the fire exit staircase.',
                'forensic_notes': 'Spectroscopic matching confirms the fibers are 100% Mongolian navy cashmere wool identical to Daniel Price\'s bespoke gala blazer.',
                'image_icon': 'scissors',
                'is_key_clue': True,
                'order': 5
            }
        )

        lf06, _ = Evidence.objects.update_or_create(
            case=case, code='LF-06',
            defaults={
                'name': 'Forged Provenance Certificate',
                'evidence_type': 'Document',
                'location_found': 'Under Parquet Floorboard',
                'description': 'Fabricated Swiss customs export declaration authorizing shipment of an \'Unattributed 19th Century Study\' to a Geneva bonded warehouse.',
                'forensic_notes': 'Includes a forged signature of Julian Cross and the private seal of Sofia Laurent.',
                'image_icon': 'file-earmark-check',
                'is_key_clue': True,
                'order': 6
            }
        )

        lf07, _ = Evidence.objects.update_or_create(
            case=case, code='LF-07',
            defaults={
                'name': 'Daniel\'s Solvent Bench Chemicals',
                'evidence_type': 'Forensic',
                'location_found': 'Restoration Workstation #2',
                'description': 'Jars containing aged linseed oil, synthetic craquelure drying agents, and dammar varnish matching the murder weapon residue.',
                'forensic_notes': 'A container marked \'Varnish 4\' has fingerprints of Daniel Price and fresh blood smeared on the lid.',
                'image_icon': 'droplet-half',
                'is_key_clue': True,
                'order': 7
            }
        )

        lf08, _ = Evidence.objects.update_or_create(
            case=case, code='LF-08',
            defaults={
                'name': 'Swiss Wire Transfer Confirmation',
                'evidence_type': 'Digital',
                'location_found': 'Julian\'s Laptop Email Archive',
                'description': 'Flagged bank transfer notification showing an overseas advance of €2,500,000 sent from \'Kestrel Capital Geneva\' to \'Price Fine Arts LLC\'.',
                'forensic_notes': 'Julian was reviewing this transaction printout at the time of the attack.',
                'image_icon': 'currency-exchange',
                'is_key_clue': True,
                'order': 8
            }
        )

        lf09, _ = Evidence.objects.update_or_create(
            case=case, code='LF-09',
            defaults={
                'name': 'Audio Guide Acoustic Recording',
                'evidence_type': 'Digital',
                'location_found': 'Museum Audio Server',
                'description': 'Gala attendee\'s audio headset microphone in Gallery 4 picked up acoustic vibrations from Room B at 21:18 PM.',
                'forensic_notes': 'Audio spectrum reveals a heated dispute between two male voices, followed by a metallic strike and heavy footsteps rushing to the fire stairs.',
                'image_icon': 'soundwave',
                'is_key_clue': False,
                'order': 9
            }
        )

        lf10, _ = Evidence.objects.update_or_create(
            case=case, code='LF-10',
            defaults={
                'name': 'Julian\'s Handwritten Diary',
                'evidence_type': 'Document',
                'location_found': 'Julian\'s Coat Pocket',
                'description': 'Leather pocket notebook. Final entry scribbled at 20:45 PM: "The craquelure on the Saint is artificial. Daniel has betrayed us. I will confront him tonight before calling the authorities."',
                'forensic_notes': 'Verified authentic handwriting of Julian Cross.',
                'image_icon': 'book',
                'is_key_clue': True,
                'order': 10
            }
        )

        # Hotspots
        hotspots_case2 = [
            (lf01, 'Electronic Door Terminal', 8.0, 32.0, 'credit-card-2-front', 'Examine the keycard reader logs at the entrance.'),
            (lf02, 'Easel & Painting', 48.0, 40.0, 'lamp', 'Inspect \'The Veiled Saint\' under UV ultraviolet lamp.'),
            (lf03, 'Chemical Washing Sink', 28.0, 72.0, 'tools', 'Check the drainage basin of the chemical washing sink.'),
            (lf04, 'Security Terminal', 92.0, 25.0, 'file-earmark-lock', 'Review security reboot logs on the wall terminal.'),
            (lf05, 'Fire Stair Emergency Exit', 88.0, 68.0, 'scissors', 'Examine the metal fire exit latch for trace evidence.'),
            (lf06, 'Loose Floorboard', 40.0, 82.0, 'file-earmark-check', 'Inspect the uneven parquet floorboard beneath the desk.'),
            (lf07, 'Restoration Workbench', 65.0, 55.0, 'droplet-half', 'Analyze the solvent jars and pigments on Daniel\'s workbench.'),
            (lf08, 'Laptop Docking Station', 35.0, 30.0, 'currency-exchange', 'Check open browser tabs and emails on Julian\'s laptop.'),
            (lf09, 'Acoustic Audio Transmitter', 18.0, 15.0, 'soundwave', 'Inspect the gallery audio guide repeater near the ceiling.'),
            (lf10, 'Julian\'s Overcoat', 52.0, 78.0, 'book', 'Search the pockets of Julian\'s tweed coat draped on the chair.'),
        ]
        for ev, label, x, y, icon, hint in hotspots_case2:
            CrimeSceneHotspot.objects.update_or_create(
                case=case, evidence=ev,
                defaults={'label': label, 'x_percent': x, 'y_percent': y, 'icon': icon, 'inspect_hint': hint}
            )

        # Interview Topics
        # Daniel Price
        InterviewTopic.objects.update_or_create(
            suspect=daniel, topic_key='dp_keycard',
            defaults={
                'title': 'Stolen Keycard Claim',
                'question_text': 'You claim someone stole your keycard from your coat at 20:30 PM?',
                'response_text': 'Yes! I hung my coat at the gala bar. I didn\'t notice my card missing until I went to fetch my briefcase after the police arrived.',
                'order': 1
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=daniel, topic_key='dp_coat_snag',
            defaults={
                'title': 'Navy Cashmere Fiber Snag',
                'question_text': 'Fibers from your navy cashmere gala blazer were snagged on the fire exit latch of Room B.',
                'response_text': 'My coat was at the gala! How could fibers... wait, someone must have worn my jacket!',
                'required_evidence': lf05,
                'is_contradiction': True,
                'contradiction_evidence': lf05,
                'contradiction_reaction': 'Daniel turns pale, staring at the torn thread: "You found the snag?! Julian cornered me! He was going to send me to prison over a piece of painted linen!" (CONTRADICTION ESTABLISHED)',
                'order': 2
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=daniel, topic_key='dp_uv_forgery',
            defaults={
                'title': 'Modern Zinc Pigment in The Veiled Saint',
                'question_text': 'The UV test proves the painting on the easel is a modern forgery using synthetic pigments from your workbench.',
                'response_text': 'A forgery?! Sofia must have loaned us a reproduction! I only performed standard surface cleaning!',
                'required_evidence': lf02,
                'order': 3
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=daniel, topic_key='dp_swiss_transfer',
            defaults={
                'title': '€2.5 Million Swiss Transfer',
                'question_text': 'We found records of a €2.5M wire to your company account for shipping the original masterpiece to Geneva.',
                'response_text': 'That was for an independent private appraisal contract! It had nothing to do with the museum!',
                'required_evidence': lf08,
                'order': 4
            }
        )

        # Mara Voss
        InterviewTopic.objects.update_or_create(
            suspect=mara, topic_key='mv_gala',
            defaults={
                'title': 'Trustee Gallery Tour',
                'question_text': 'Were you anywhere near the third floor conservation lab during the 21:18 PM struggle?',
                'response_text': 'I was in Gallery 2 discussing Flemish tapestries with the museum president. You can check the live livestream footage.',
                'order': 1
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=mara, topic_key='mv_provenance',
            defaults={
                'title': 'Julian\'s Forgery Suspicions',
                'question_text': 'Julian wrote in his notebook that he had unmasked a forgery ring inside the restoration wing.',
                'response_text': 'Julian mentioned anomalies in the craquelure to me last week, but I assumed he was obsessing over micro-cracks. He refused to show me his notes.',
                'required_evidence': lf10,
                'order': 2
            }
        )

        # Sofia Laurent
        InterviewTopic.objects.update_or_create(
            suspect=sofia, topic_key='sl_loan',
            defaults={
                'title': 'Loan Terms and Insurance',
                'question_text': 'The Veiled Saint was insured for $15 million under your family foundation.',
                'response_text': 'Of course. It is an irreplaceable national treasure. I trusted Julian with its care completely.',
                'order': 1
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=sofia, topic_key='sl_export_forgery',
            defaults={
                'title': 'Geneva Bonded Warehouse Export',
                'question_text': 'This Swiss customs document bears your private seal approving transit of the original painting.',
                'response_text': 'My seal?! Daniel approached me about arranging an overseas private exhibition, but he assured me all documentation was certified by Julian!',
                'required_evidence': lf06,
                'order': 2
            }
        )

        # Ethan Cole
        InterviewTopic.objects.update_or_create(
            suspect=ethan, topic_key='ec_guard_duties',
            defaults={
                'title': 'Gala Security Station Duties',
                'question_text': 'What were your security responsibilities during the exhibition gala?',
                'response_text': 'I was stationed at the main security kiosk monitoring access card telemetry and alarm annunciators for all four museum floors.',
                'order': 1
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=ethan, topic_key='ec_reboot',
            defaults={
                'title': 'Camera Reboot Timing',
                'question_text': 'Why did the surveillance cameras reboot for 10 minutes at the exact moment of the murder?',
                'response_text': 'Daniel told me the high-voltage UV lamps were causing network interference and asked me to cycle the router switches. I had no idea what he was doing upstairs!',
                'required_evidence': lf04,
                'order': 2
            }
        )

        # Hints
        CaseHint.objects.update_or_create(
            case=case, hint_level=1,
            defaults={
                'hint_text': 'Examine the painting itself using forensic tools. Is the canvas on the easel truly the original Renaissance masterpiece?',
                'penalty_points': 0
            }
        )
        CaseHint.objects.update_or_create(
            case=case, hint_level=2,
            defaults={
                'hint_text': 'Check the electronic keycard log #04 and the emergency fire exit door. Someone left physical evidence behind when fleeing the crime scene.',
                'penalty_points': 25
            }
        )
        CaseHint.objects.update_or_create(
            case=case, hint_level=3,
            defaults={
                'hint_text': 'Examine the fine wool fibers caught on the emergency fire exit door latch and match them to the bespoke attire worn by one of the restoration team. Connect the chemical solvents discovered on the workbench with the warning found in Julian\'s pocket diary regarding a substituted canvas.',
                'penalty_points': 50
            }
        )

        # Secret Solution
        sol2, _ = CaseSecretSolution.objects.update_or_create(
            case=case,
            defaults={
                'culprit': daniel,
                'correct_motive': 'Art Forgery and Theft',
                'correct_motive_details': 'Daniel Price forged a replica of \'The Veiled Saint\' using modern pigments and solvents from his bench. He planned to smuggle the genuine $12M original to a Swiss collector for €2.5M. When Julian discovered the fake and confronted him, Daniel struck him with the bronze clamp.',
                'accepted_reasoning': 'Daniel swiped into Room B with keycard #04 at 21:14 (LF-01), argued with Julian as recorded on the acoustic guide (LF-09), bludgeoned Julian with the bronze frame clamp (LF-03), left solvent traces from his workbench (LF-07), and fled down the fire exit stairs where his navy cashmere coat snagged on the latch (LF-05). Julian\'s diary (LF-10) and UV spectrometry (LF-02) seal the case.',
                'epilogue': 'Interpol intercepted the genuine \'The Veiled Saint\' in a shipping crate at Zurich airport. Daniel Price was convicted of first-degree murder and antiquities fraud. The Bellwether Museum instituted dual-custody biometrics across all conservation wings.',
                'max_score': 500,
                'evidence_point_val': 25,
                'contradiction_point_val': 50,
                'culprit_points': 200,
                'motive_points': 100,
                'evidence_points': 100,
            }
        )
        sol2.required_evidence.set([lf01, lf02, lf03, lf05, lf10])
        self.stdout.write(self.style.SUCCESS("✓ Seeded CASE-002: The Last Frame."))

    def seed_case_003(self):
        case, _ = CaseFile.objects.update_or_create(
            case_number='CASE-003',
            defaults={
                'title': 'Signal Lost',
                'slug': 'signal-lost',
                'genre': 'Tech-Noir Mystery',
                'difficulty': 'Hard',
                'estimated_time': '25-30 min',
                'location': 'Orion Research Observatory, Cryogenic Receiver Control Room',
                'incident_date': 'December 12, 02:45 AM',
                'victim_name': 'Dr. Nolan Pierce',
                'victim_profile': 'Age 55. Director of Astrophysics & Deep Array Research. World authority on deep-space radio signal decoding. Arrogant, secretive, and fiercely guarded his proprietary data.',
                'initial_findings': 'Dr. Pierce was discovered asphyxiated beside the liquid nitrogen cooling manifold in Dome 3. The optical sensor array\'s coolant bypass had been manually tripped, venting liquid nitrogen into the sealed chamber. A 6-minute power surge hit Dome 3 at 02:44 AM.',
                'known_circumstances': 'The high-altitude observatory was isolated by a blizzard. Four staff members were present inside the facility. Communications to the university campus were severed, and surveillance logs had been deleted.',
                'synopsis': 'During a deep-space observation shift at an isolated mountaintop observatory, the director is asphyxiated by a cryogenic coolant release. System logs reveal erased server traces, a cut fiber optic link, and corporate espionage.',
                'scene_title': 'Dome 3 Cryogenic Array & Server Core',
                'scene_description': 'A high-tech circular observatory dome with massive optical telescope gears, pressurized liquid nitrogen pipelines, flashing server rack bays, industrial high-voltage breaker panels, and an emergency ventilation airlock.',
                'scene_theme': 'observatory',
                'is_published': True,
                'order': 3
            }
        )

        # Suspects
        mira, _ = Suspect.objects.update_or_create(
            case=case, name='Dr. Mira Shah',
            defaults={
                'age': 41,
                'occupation': 'Senior Radio Astronomer',
                'relationship_to_victim': 'Lead Co-Researcher & Scientific Collaborator',
                'alibi': 'In the observation library reviewing spectrographic plates from 01:30 to 03:00 AM.',
                'known_motive': 'Dr. Pierce filed a sole patent on the Deep Array algorithm, denying her intellectual credit on their groundbreaking discovery.',
                'personality_notes': 'Intense, methodical, speaks in precise mathematical terms, emotionally guarded.',
                'portrait_icon': 'activity',
                'opening_statement': 'Nolan stole my equations and filed for the patent behind my back. I contested it through the university ethics board. I am a scientist, not a killer.',
                'order': 1
            }
        )

        felix, _ = Suspect.objects.update_or_create(
            case=case, name='Felix Grant',
            defaults={
                'age': 35,
                'occupation': 'Chief Systems & Infrastructure Engineer',
                'relationship_to_victim': 'Observatory Hardware & Network Architect',
                'alibi': 'Claims he fell asleep in the staff lounge at 01:45 AM and never logged into any terminal or entered Dome 3 until the power alarm tripped.',
                'known_motive': 'Caught in the act of copying the proprietary algorithm onto an encrypted drive to sell to an aerospace defense contractor for $1.8M.',
                'personality_notes': 'Aloof, cyber-literate, defensive about his root credentials, nervously fidgets with server keys.',
                'portrait_icon': 'cpu',
                'opening_statement': 'I maintain the infrastructure, that\'s all. When the power spiked at 02:44, I woke up in the lounge and ran to reset the breaker. Everything else you are hearing is rumors.',
                'order': 2
            }
        )

        lena, _ = Suspect.objects.update_or_create(
            case=case, name='Lena Brooks',
            defaults={
                'age': 39,
                'occupation': 'Facility & Cryogenics Operations Manager',
                'relationship_to_victim': 'Operational Supervisor of Dome Equipment',
                'alibi': 'Calibrating pressure valves in auxiliary Dome 1 between 02:00 and 03:15 AM.',
                'known_motive': 'Threatened with termination by Pierce over hazardous cryogenic storage compliance audits.',
                'personality_notes': 'Practical, safety-conscious, keeps meticulous physical equipment sign-out sheets.',
                'portrait_icon': 'clipboard-data',
                'opening_statement': 'Liquid nitrogen is not a toy; it expands 700 times into gas and displaces all oxygen in seconds. Whoever opened that valve knew exactly what they were doing.',
                'order': 3
            }
        )

        owen, _ = Suspect.objects.update_or_create(
            case=case, name='Owen Blake',
            defaults={
                'age': 47,
                'occupation': 'Night Security Officer',
                'relationship_to_victim': 'Perimeter Guard & Safety Officer',
                'alibi': 'Claims he was on continuous foot patrol around the telescope base until he felt sudden dizziness and blacked out.',
                'known_motive': 'Pierce had caught Owen selling discarded facility electronics on online auction forums.',
                'personality_notes': 'Weary, ex-military communications technician, embarrassed by lapse of duty.',
                'portrait_icon': 'shield-shaded',
                'opening_statement': 'I had two cups of coffee at midnight and started feeling numb and dizzy by 01:30. Someone doped my flask; I didn\'t wake up until the facility sirens started blaring.',
                'order': 4
            }
        )

        # Evidence
        sl01, _ = Evidence.objects.update_or_create(
            case=case, code='SL-01',
            defaults={
                'name': 'SCADA Power Surge Log',
                'evidence_type': 'Digital',
                'location_found': 'Engineering Console 4',
                'description': 'Automated grid event recording an electrical surge at 02:44:12 AM initiated from Engineering Console 4. Tripped main breakers for 6 minutes.',
                'forensic_notes': 'Surge was triggered via terminal commands using hardware root credentials belonging to Felix Grant.',
                'image_icon': 'lightning',
                'is_key_clue': True,
                'order': 1
            }
        )

        sl02, _ = Evidence.objects.update_or_create(
            case=case, code='SL-02',
            defaults={
                'name': 'Cryogenic Coolant Valve Wrench',
                'evidence_type': 'Physical Object',
                'location_found': 'Beside Nitrogen Tank Manifold',
                'description': 'Heavy 24-inch industrial steel wrench used to manually force open the pressurized liquid nitrogen exhaust bypass.',
                'forensic_notes': 'Greasy fingerprint residues on the rubberized handle match the index and thumb of Felix Grant.',
                'image_icon': 'wrench',
                'is_key_clue': True,
                'order': 2
            }
        )

        sl03, _ = Evidence.objects.update_or_create(
            case=case, code='SL-03',
            defaults={
                'name': 'Severed Backup Fiber Cable',
                'evidence_type': 'Physical Object',
                'location_found': 'Main Data Trench Floor',
                'description': 'Armored fiber-optic uplink cleanly cut with precision carbon-steel wire strippers.',
                'forensic_notes': 'Prevented the automated offsite transmission of the Deep Array algorithm telemetry to university cloud servers.',
                'image_icon': 'hdd-network',
                'is_key_clue': True,
                'order': 3
            }
        )

        sl04, _ = Evidence.objects.update_or_create(
            case=case, code='SL-04',
            defaults={
                'name': 'Dr. Pierce\'s Solo Patent Draft',
                'evidence_type': 'Document',
                'location_found': 'Pierce\'s Desk Safe',
                'description': 'Confidential patent application listing Nolan Pierce as sole inventor of the Deep Array signal architecture.',
                'forensic_notes': 'Explicitly excludes Dr. Mira Shah and Felix Grant from commercial royalty distributions.',
                'image_icon': 'file-earmark-lock2',
                'is_key_clue': True,
                'order': 4
            }
        )

        sl05, _ = Evidence.objects.update_or_create(
            case=case, code='SL-05',
            defaults={
                'name': 'Doped Coffee Thermos',
                'evidence_type': 'Forensic',
                'location_found': 'Security Guard Booth',
                'description': 'Stainless steel thermos containing black coffee mixed with 20mg of Zolpidem (hypnotic sedative).',
                'forensic_notes': 'Explains why Officer Owen Blake lost consciousness and failed to respond to the initial breach alarms.',
                'image_icon': 'cup',
                'is_key_clue': False,
                'order': 5
            }
        )

        sl06, _ = Evidence.objects.update_or_create(
            case=case, code='SL-06',
            defaults={
                'name': 'Terminal Session Deletion History',
                'evidence_type': 'Digital',
                'location_found': 'Primary Server Node 02',
                'description': 'Bash shell audit log showing commands executed at 02:47:33 AM under username \'fgrant\': rm -rf /var/log/surveillance/dome3/*.log.',
                'forensic_notes': 'Executed 3 minutes after the cryogenic release, wiping camera surveillance records during the power outage.',
                'image_icon': 'terminal',
                'is_key_clue': True,
                'order': 6
            }
        )

        sl07, _ = Evidence.objects.update_or_create(
            case=case, code='SL-07',
            defaults={
                'name': 'Cryogenic Tool Sign-Out Clipboard',
                'evidence_type': 'Document',
                'location_found': 'Cryo Storage Bay Desk',
                'description': 'Physical maintenance logbook kept by Lena Brooks.',
                'forensic_notes': 'Entry at 01:30 AM shows Felix Grant checked out the high-pressure valve wrench (SL-02) and an insulated thermal hood under the pretext of \'filter maintenance\'.',
                'image_icon': 'clipboard-check',
                'is_key_clue': True,
                'order': 7
            }
        )

        sl08, _ = Evidence.objects.update_or_create(
            case=case, code='SL-08',
            defaults={
                'name': 'Thermal IR Surveillance Cache',
                'evidence_type': 'Digital',
                'location_found': 'Autonomous Buffer Memory',
                'description': 'Cached infrared thermal snapshot recorded at 02:43:10 AM in the corridor outside Dome 3.',
                'forensic_notes': 'Shows an individual wearing high-voltage anti-static engineering coveralls and thermal mittens entering Dome 3.',
                'image_icon': 'camera-video',
                'is_key_clue': True,
                'order': 8
            }
        )

        sl09, _ = Evidence.objects.update_or_create(
            case=case, code='SL-09',
            defaults={
                'name': 'Encrypted NVMe Flash Drive',
                'evidence_type': 'Digital',
                'location_found': 'Server Rack Ventilation Shaft',
                'description': 'Military-grade encrypted SSD recovered from behind Server Bay 4. Contains 1.2 TB of uncompressed telescope radio frequency captures and proprietary algorithms.',
                'forensic_notes': 'Addressed to an external corporate email: acquisitions@aegisaerospace.com with a payoff agreement for $1,800,000.',
                'image_icon': 'usb-drive',
                'is_key_clue': True,
                'order': 9
            }
        )

        sl10, _ = Evidence.objects.update_or_create(
            case=case, code='SL-10',
            defaults={
                'name': 'Nitrogen Sensor Jumper Wire',
                'evidence_type': 'Forensic',
                'location_found': 'Dome 3 Safety Junction Box',
                'description': 'Copper alligator jumper clip placed across the nitrogen sensor terminals.',
                'forensic_notes': 'Electronically suppressed the acoustic emergency evacuation sirens, preventing Dr. Pierce from receiving auditory warning of the oxygen depletion.',
                'image_icon': 'cpu-fill',
                'is_key_clue': True,
                'order': 10
            }
        )

        # Hotspots
        hotspots_case3 = [
            (sl01, 'SCADA Grid Console 4', 15.0, 45.0, 'lightning', 'Inspect the SCADA telemetry terminal for power surges.'),
            (sl02, 'Nitrogen Manifold Valve', 52.0, 68.0, 'wrench', 'Examine the pressurized nitrogen pipeline valve and floor.'),
            (sl03, 'Underfloor Cable Trench', 35.0, 85.0, 'hdd-network', 'Inspect the open fiber-optic cable trench under the floor grates.'),
            (sl04, 'Director Pierce\'s Desk Safe', 78.0, 30.0, 'file-earmark-lock2', 'Check the electronic wall safe behind Dr. Pierce\'s desk.'),
            (sl05, 'Security Console', 8.0, 18.0, 'cup', 'Analyze the coffee flask in the security entrance alcove.'),
            (sl06, 'Primary Server Rack Node 02', 82.0, 62.0, 'terminal', 'Inspect the root shell command logs on Server Rack 2.'),
            (sl07, 'Cryo Maintenance Desk', 25.0, 22.0, 'clipboard-check', 'Review the physical tool checkout clipboard in the bay.'),
            (sl08, 'Corridor IR Camera Buffer', 92.0, 12.0, 'camera-video', 'Access the standalone memory buffer of the corridor IR camera.'),
            (sl09, 'Server Rack Ventilation Shaft', 72.0, 78.0, 'usb-drive', 'Search the exhaust ventilation vent behind the servers.'),
            (sl10, 'Safety Relay Junction Box', 42.0, 35.0, 'cpu-fill', 'Examine the nitrogen alarm electrical junction box on the pillar.'),
        ]
        for ev, label, x, y, icon, hint in hotspots_case3:
            CrimeSceneHotspot.objects.update_or_create(
                case=case, evidence=ev,
                defaults={'label': label, 'x_percent': x, 'y_percent': y, 'icon': icon, 'inspect_hint': hint}
            )

        # Interview Topics
        # Felix Grant
        InterviewTopic.objects.update_or_create(
            suspect=felix, topic_key='fg_lounge_alibi',
            defaults={
                'title': 'Staff Lounge Alibi',
                'question_text': 'You claim you were asleep in the staff lounge from 01:45 to 02:50 AM?',
                'response_text': 'Yes, completely dead to the world until the emergency alarm woke me. I never touched a terminal or entered Dome 3 during that window.',
                'order': 1
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=felix, topic_key='fg_deletion_contradiction',
            defaults={
                'title': 'Terminal Deletion Commands',
                'question_text': 'Server logs show user \'fgrant\' executing surveillance deletion commands at 02:47 AM from Server Node 02.',
                'response_text': 'That must be an automated cron script! I have automated cleanup daemons running hourly!',
                'required_evidence': sl06,
                'is_contradiction': True,
                'contradiction_evidence': sl06,
                'contradiction_reaction': 'Felix breaks down: "A cron script doesn\'t type interactive root commands! You pulled the terminal bash history?! Nolan caught me in the server bay... he was going to destroy me!" (CONTRADICTION ESTABLISHED)',
                'order': 2
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=felix, topic_key='fg_wrench_checkout',
            defaults={
                'title': 'Valve Wrench Sign-Out',
                'question_text': 'Lena\'s clipboard records your signature checking out the cryogenic valve wrench at 01:30 AM.',
                'response_text': 'I checked it out for routine preventative maintenance on the cooling pumps earlier in the night!',
                'required_evidence': sl07,
                'is_contradiction': True,
                'contradiction_evidence': sl07,
                'contradiction_reaction': 'Felix stammered: "I forgot I had it with me in Dome 3... look, it was an accident! The valve jammed open!"',
                'order': 3
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=felix, topic_key='fg_encrypted_drive',
            defaults={
                'title': 'Encrypted Drive for Aegis Aerospace',
                'question_text': 'We recovered an encrypted flash drive hidden in the server ventilation shaft containing stolen array algorithms.',
                'response_text': 'Pierce was robbing all of us! He was patenting our life\'s work under his sole name while we made standard university salaries!',
                'required_evidence': sl09,
                'order': 4
            }
        )

        # Dr. Mira Shah
        InterviewTopic.objects.update_or_create(
            suspect=mira, topic_key='ms_research_shift',
            defaults={
                'title': 'Observatory Control Room Shift',
                'question_text': 'What were your scientific responsibilities in the control room tonight?',
                'response_text': 'I was calibrating the receiver frequency bands for the scheduled pulsar sweep until the sudden power surge scrambled our sensor inputs.',
                'order': 1
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=mira, topic_key='ms_patent',
            defaults={
                'title': 'Dr. Pierce\'s Patent Monopoly',
                'question_text': 'Dr. Pierce filed for sole patent ownership of the Deep Array algorithm.',
                'response_text': 'I knew he was pursuing it, but I filed a legal injunction with the federal patent office. I had no motive to murder him; his death actually delays the legal proceedings.',
                'required_evidence': sl04,
                'order': 2
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=mira, topic_key='ms_fiber_cable',
            defaults={
                'title': 'Severed Fiber Link',
                'question_text': 'The backup fiber cable was severed before the murder.',
                'response_text': 'Only someone with physical keys to the sub-floor cable trenches could reach that conduit. Felix and Lena hold the only maintenance keys.',
                'required_evidence': sl03,
                'order': 3
            }
        )

        # Lena Brooks
        InterviewTopic.objects.update_or_create(
            suspect=lena, topic_key='lb_facility_systems',
            defaults={
                'title': 'Cryogenic Valve Protocols',
                'question_text': 'How are the cryogenic coolant lines in Dome 3 monitored during active observation?',
                'response_text': 'Every cooling valve has automated pressure telemetry and an audible alarm siren that sounds if oxygen levels dip below 19%.',
                'order': 1
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=lena, topic_key='lb_safety_sensor',
            defaults={
                'title': 'Jumpered Nitrogen Alarm',
                'question_text': 'Someone placed a jumper wire across the nitrogen sensor terminals to silence the sirens.',
                'response_text': 'That is criminal negligence! The acoustic siren is the only warning researchers have when nitrogen displaces breathable air. Whoever did that wanted Nolan to suffocate without knowing.',
                'required_evidence': sl10,
                'order': 2
            }
        )

        # Owen Blake
        InterviewTopic.objects.update_or_create(
            suspect=owen, topic_key='ob_lockdown_security',
            defaults={
                'title': 'Perimeter Storm Lockdown',
                'question_text': 'Could anyone have entered the research facility from outside during the blizzard?',
                'response_text': 'Impossible. The blizzard made exterior travel lethal, and all external blast doors were electronically bolted. Only people already inside with lab badges could move around.',
                'order': 1
            }
        )
        InterviewTopic.objects.update_or_create(
            suspect=owen, topic_key='ob_coffee_drugging',
            defaults={
                'title': 'Zolpidem in Thermos',
                'question_text': 'Toxicology tests found heavy sleeping medication in your coffee thermos.',
                'response_text': 'I knew it! I left my thermos on the break room counter at 01:00 AM while checking the exterior weather sensor. Felix was in the kitchen at that time!',
                'required_evidence': sl05,
                'order': 2
            }
        )

        # Hints
        CaseHint.objects.update_or_create(
            case=case, hint_level=1,
            defaults={
                'hint_text': 'Investigate who possessed the mechanical tools and technical credentials to override both the power grid and the nitrogen safety alarms.',
                'penalty_points': 0
            }
        )
        CaseHint.objects.update_or_create(
            case=case, hint_level=2,
            defaults={
                'hint_text': 'Check the root terminal history on Server Node 02 and the cryogenic equipment logbook. Someone was actively executing commands during the alleged alibi period.',
                'penalty_points': 25
            }
        )
        CaseHint.objects.update_or_create(
            case=case, hint_level=3,
            defaults={
                'hint_text': 'Investigate the terminal shell history on Server Node 02 during the power outage and note which user account ran active deletion commands. Correlate with whoever checked out the cryogenic valve wrench from the tool clipboard at 01:30 AM, and search the server ventilation duct for concealed data.',
                'penalty_points': 50
            }
        )

        # Secret Solution
        sol3, _ = CaseSecretSolution.objects.update_or_create(
            case=case,
            defaults={
                'culprit': felix,
                'correct_motive': 'Corporate Espionage and Intellectual Property Theft',
                'correct_motive_details': 'Felix Grant copied the proprietary Deep Array algorithm onto an encrypted drive to sell to Aegis Aerospace for $1,800,000. When Dr. Pierce walked into Dome 3 and caught him red-handed, Felix cut the fiber link, silenced the gas alarms with a jumper wire, and opened the liquid nitrogen valve with his wrench to asphyxiate Pierce before wiping the camera logs.',
                'accepted_reasoning': 'Felix checked out the cryo wrench at 01:30 (SL-07), drugged guard Owen\'s coffee (SL-05), cut the fiber link (SL-03), jumpered the nitrogen sensor (SL-10), opened the coolant valve with his wrench (SL-02), triggered the power surge from console 4 at 02:44 (SL-01), deleted surveillance logs at 02:47 (SL-06), and hid the encrypted drive in the server vent (SL-09).',
                'epilogue': 'Federal investigators recovered the encrypted SSD from the ventilation shaft and matched Felix Grant\'s fingerprints to the valve wrench. Felix was indicted on federal charges of second-degree murder and economic espionage. Dr. Mira Shah was appointed interim director to complete the Deep Array research under open-access scientific principles.',
                'max_score': 500,
                'evidence_point_val': 25,
                'contradiction_point_val': 50,
                'culprit_points': 200,
                'motive_points': 100,
                'evidence_points': 100,
            }
        )
        sol3.required_evidence.set([sl01, sl02, sl06, sl09])
        self.stdout.write(self.style.SUCCESS("✓ Seeded CASE-003: Signal Lost."))
