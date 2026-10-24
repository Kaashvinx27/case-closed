# 🕵️‍♂️ CASE CLOSED — Immersive Detective Mystery & Investigation Platform

> **Classified Criminal Investigation Bureau Simulation**  
> Built for **AIM3140: Web Technologies** — Department of AIML, Manipal University Jaipur.

---

## 🌟 Executive Overview

**CASE CLOSED** is a full-stack detective mystery and investigation web platform. Rather than a static trivia or generic admin app, players enter a classified investigation bureau, examine authentic crime scene coordinates, catalog forensic evidence, question suspects through conditional dialogue trees, expose alibi contradictions, connect clues with red yarn on an interactive corkboard, and authoritatively submit murder accusations validated by the backend server.

The platform provides:
- **3 Complete Playable Murder Mysteries** with distinct plots, suspects, forensic evidence, alibis, contradictions, and solutions.
- **Dual Play Modes:** Instant **Guest Mode** (zero signup required) and **Registered Operative Mode** (persistent badge, score tracking, ranks, achievements, and leaderboard).
- **Authoritative Server-Side Scoring & Validation:** Case solutions are strictly protected and never leaked in client-side HTML/JSON.
- **Cinematic Noir Visual Aesthetic:** Custom dark atmospheric palette (`#0B0D10`, `#12161C`, `#191F27`, crimson `#C6283D`, gold `#D6B46A`, warm ivory `#E9E4DA`) with archival grain and responsive typography.

---

## 📚 AIM3140 Syllabus Concept Mapping

| Course Module & Concept | Implementation in CASE CLOSED |
| :--- | :--- |
| **Web Basics & HTML5** | Semantic structure, accessible landmarks, metadata grids, data tables, and interactive form controls. |
| **Styling & CSS3** | Custom noir styling (`main.css`), procedural background illustrations, corkboard pins, animations, box model layouts, and `@media` queries (`responsive.css`). |
| **Bootstrap 5** | Responsive grid system, navbar toggler, card layouts, status badges, progress bars, and modal dialogs. |
| **JavaScript & DOM** | Hotspot coordinate event listeners, live timer interval, modal openers, dynamic dialogue tree injection, and client-side form validation. |
| **Asynchronous Web (AJAX & Fetch)** | Real-time RESTful JSON endpoints for evidence discovery, interrogation responses, hint unlocks, corkboard links, and accusation evaluation without full page reloads. |
| **Python & Web Server** | Django WSGI/ASGI web server architecture, dynamic GET/POST request handling, URL routing, server-side data processing, and cryptographic token management. |
| **Database & MySQL / Relational ORM** | 20 normalized Django models managing users, sessions, suspects, evidence, hotspots, connections, results, and achievements with foreign keys and unique constraints. Configured for MySQL with automatic robust SQLite fallback. |
| **Django Framework (MVT)** | Full Model-View-Template architecture, URL dispatcher, session-based authentication, CSRF security, custom template context processors, and Django Admin portal. |

---

## 📁 Project Directory Structure

```text
case_closed/
├── manage.py                          # Django management CLI
├── requirements.txt                   # Production & local dependencies
├── .env.example                       # Environment configuration template
├── .env                               # Active local environment variables
├── .gitignore                         # Version control exclusions
├── README.md                          # Comprehensive documentation
│
├── config/                            # Core Project Configuration
│   ├── __init__.py
│   ├── settings.py                    # MySQL & SQLite database configuration, security, apps
│   ├── urls.py                        # Root URL routing & Admin header customization
│   ├── asgi.py
│   └── wsgi.py
│
└── investigations/                    # Primary Application Package
    ├── models.py                      # 20 normalized models with constraints
    ├── views.py                       # Page views, auth views, and JSON Fetch APIs
    ├── urls.py                        # App route definitions
    ├── forms.py                       # Registration, settings, and accusation forms
    ├── admin.py                       # Django Admin with inlines, filters, search
    ├── services.py                    # Session, discovery, interview & hint logic
    ├── game_logic.py                  # Authoritative solution evaluation & scoring
    ├── context_processors.py          # Global template context (cases & profiles)
    ├── tests.py                       # Automated test suite (20/20 criteria)
    │
    ├── management/commands/
    │   └── seed_cases.py              # Idempotent database seeder for all 3 cases
    │
    ├── migrations/                    # Schema migrations
    │
    ├── templates/
    │   ├── base.html                  # Master noir layout with navbar & audio engine
    │   ├── investigations/
    │   │   ├── landing.html           # Cinematic bureau introduction
    │   │   ├── dashboard.html         # Operative progress, activity chronology & files
    │   │   ├── cases.html             # Case repository with filters
    │   │   ├── case_briefing.html     # Formal briefing & victim dossier
    │   │   ├── investigation.html     # Hotspots, interrogation, corkboard, accusation
    │   │   ├── leaderboard.html       # Authoritative score table & quick search
    │   │   ├── profile.html           # Operative badge, settings & solved warrants
    │   │   └── how_to_play.html       # 10-step deduction manual & scoring table
    │   └── registration/
    │       ├── login.html             # Secure operative sign-in
    │       └── register.html          # New operative enlistment
    │
    └── static/
        ├── css/
        │   ├── main.css               # Dark noir design system
        │   ├── investigation.css      # Viewport, hotspots, dialogue & corkboard
        │   └── responsive.css         # Mobile & tablet breakpoints (375px - 1440px)
        ├── js/
        │   ├── main.js                # Web Audio API synth & CSRF utilities
        │   ├── investigation.js       # Live timer, hotspots, dialogue & accusations
        │   ├── evidence_board.js      # Corkboard card connections with SVG red yarn
        │   └── leaderboard.js         # Table filters & fast search
        └── images/
            ├── logo/bureau_badge.svg  # Vector bureau emblem
            └── cases/                 # Vector crime scene schematics
```

---

## 🧩 The Three Complete Playable Mysteries

### 1. `CASE-001`: The Midnight Will
- **Setting:** Blackthorn Manor, Private Study (Estate Mystery &bull; Easy)
- **Victim:** Adrian Blackthorn (Age 64, wealthy industrialist & collector)
- **Suspects:** Eleanor Blackthorn (daughter), Victor Hale (accountant), Clara Wren (secretary), Thomas Reed (groundskeeper)
- **Core Clues:** Burned draft will in the hearth (AD-01), stopped grandfather clock (AD-02), staged muddy terrace boots (AD-03), brass letter opener (AD-04), Helios Holdings audit (AD-05), tea laced with chloral hydrate (AD-06), duplicate master key marked "V.H." behind radiator (AD-07), and Clara's appointment diary (AD-08).
- **Culprit:** **Victor Hale**
- **Motive:** Embezzlement & Financial Fraud (Adrian's midnight audit would reveal Victor siphoned £45,000 via Helios Holdings).

### 2. `CASE-002`: The Last Frame
- **Setting:** Bellwether Museum, Conservation Room B (Art-World Thriller &bull; Medium)
- **Victim:** Julian Cross (Age 48, Chief Conservator and Renaissance scholar)
- **Suspects:** Mara Voss (deputy curator), Daniel Price (restorer), Sofia Laurent (collector), Ethan Cole (security head)
- **Core Clues:** Keycard log #04 (LF-01), UV spectrometry revealing synthetic modern zinc white on "The Veiled Saint" (LF-02), bronze frame clamp with lapis lazuli pigment (LF-03), CCTV blindspot memo (LF-04), navy cashmere blazer fibers on fire exit latch (LF-05), forged Swiss export manifest (LF-06), and Julian's notebook (LF-10).
- **Culprit:** **Daniel Price**
- **Motive:** Art Forgery and Theft (Swapped the $12M masterpiece with his forged replica to sell the original to a Swiss collector for €2.5M).

### 3. `CASE-003`: Signal Lost
- **Setting:** Orion Research Observatory, Dome 3 (Tech-Noir Mystery &bull; Hard)
- **Victim:** Dr. Nolan Pierce (Age 55, Deep Array Astrophysics Director)
- **Suspects:** Dr. Mira Shah (astronomer), Felix Grant (systems engineer), Lena Brooks (facility manager), Owen Blake (security guard)
- **Core Clues:** SCADA power surge log at 02:44 AM (SL-01), cryogenic valve wrench with thumbprints (SL-02), severed fiber optic cable (SL-03), solo patent draft (SL-04), drugged coffee flask (SL-05), terminal history deleting camera logs at 02:47 AM under 'fgrant' (SL-06), cryo tool checkout manifest (SL-07), and encrypted SSD hidden in the server vent (SL-09).
- **Culprit:** **Felix Grant**
- **Motive:** Corporate Espionage & Intellectual Property Theft (Stole the Deep Array radio algorithm to sell to Aegis Aerospace for $1.8M and asphyxiated Dr. Pierce with liquid nitrogen when discovered).

---

## ⚙️ Quick Start Installation & Execution

### 1. Prerequisites
- Python 3.10+ installed
- Virtual environment (`venv`)

### 2. Clone / Open Directory
```bash
cd /Users/abc/.gemini/antigravity/scratch/case_closed
```

### 3. Activate Virtual Environment
```bash
# On macOS / Linux
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Database (.env)
The project comes pre-configured with **SQLite** for immediate zero-dependency local demonstration.

To use **MySQL** as your primary database:
1. Ensure your local MySQL server is running (e.g. via Homebrew or MySQL Workbench).
2. Create the database:
   ```sql
   CREATE DATABASE case_closed_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Edit your `.env` file:
   ```env
   DB_ENGINE=mysql
   DB_NAME=case_closed_db
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```

### 6. Run Migrations & Seed Case Mysteries
```bash
python manage.py makemigrations investigations
python manage.py migrate
python manage.py seed_cases
```

### 7. Launch Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your web browser.

---

## 🔑 Demonstration Accounts

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Bureau Director (Superuser)** | `admin` | `admin123` | Full access to Django Admin at `/admin/` |
| **Field Detective** | `agent_holmes` | `Password123!` | Sample operative profile |
| **Guest Mode** | *(No login needed)* | *(None)* | Click "ENTER THE BUREAU" to start immediately |

---

## 🧪 Automated Test Suite

A comprehensive 20-test automated suite verifies every requirement:

```bash
python manage.py test investigations
```

Output:
```text
Found 20 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
Commencing Case Closed dataset seeding...
✓ Seeded achievements.
✓ Seeded CASE-001: The Midnight Will.
✓ Seeded CASE-002: The Last Frame.
✓ Seeded CASE-003: Signal Lost.
....................
----------------------------------------------------------------------
Ran 20 tests in 6.449s

OK
```

---

## 🛡️ Security Highlights
- **No Solution Leakage:** Culprits and motives are strictly server-authoritative and only evaluated upon POST submission.
- **CSRF Token Enforcement:** All AJAX state modifications require verified `X-CSRFToken` headers.
- **Score Duplication Defense:** Discoveries, contradictions, and hints use database unique constraints to prevent double-counting.
- **Input Sanitization:** User notes and reasoning inputs are escaped and server-validated.
- **Session Protection:** Guest sessions use cryptographically secure UUID4 tokens stored in HTTP sessions.
