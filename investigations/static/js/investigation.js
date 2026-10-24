/**
 * CASE CLOSED: Investigation Workspace Controller
 * Manages Hotspots, Evidence Inspection, Suspect Interrogation, Contradictions, Hints, and Accusations.
 */

if (typeof escapeHTML !== 'function') {
  window.escapeHTML = function(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  };
}

class InvestigationWorkspace {
  constructor(caseSlug) {
    this.slug = caseSlug;
    this.discoveredIds = new Set(window.discoveredEvidenceIds || []);
    this.timerInterval = null;
    this.elapsedSeconds = 0;
    this.activeSuspectId = null;

    this.initTimer();
    this.initHotspots();
    this.initInterrogations();
    this.initHints();
    this.initNotes();
    this.initAccusation();
  }

  // 1. Authoritative Investigation Timer
  initTimer() {
    const timerDisplay = document.getElementById('investigation-timer-display');
    if (!timerDisplay) return;

    // Fetch initial authoritative elapsed seconds
    fetch(`/api/investigate/${this.slug}/state/`)
      .then(res => res.json())
      .then(data => {
        this.elapsedSeconds = data.elapsed_seconds || 0;
        this.updateTimerText();
      })
      .catch(() => {});

    this.timerInterval = setInterval(() => {
      this.elapsedSeconds++;
      this.updateTimerText();
    }, 1000);
  }

  updateTimerText() {
    const el = document.getElementById('investigation-timer-display');
    if (!el) return;
    const mins = Math.floor(this.elapsedSeconds / 60);
    const secs = this.elapsedSeconds % 60;
    el.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  // 2. Interactive Crime Scene Hotspots
  initHotspots() {
    const markers = document.querySelectorAll('.scene-hotspot-marker');
    markers.forEach(marker => {
      marker.addEventListener('click', () => {
        const evidenceId = marker.dataset.evidenceId;
        this.discoverEvidence(evidenceId, marker);
      });
      // Keyboard accessibility (Enter or Space)
      marker.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          marker.click();
        }
      });
    });
  }

  discoverEvidence(evidenceId, markerEl) {
    window.bureauAudio.playClick();

    fetch(`/api/investigate/${this.slug}/discover/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({ evidence_id: evidenceId })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        if (data.created) {
          window.bureauAudio.playDiscovery();
          showBureauToast('Evidence Cataloged', `Found: ${data.evidence.name}`, 'gold');
        }

        this.discoveredIds.add(Number(evidenceId));
        if (markerEl) {
          markerEl.classList.add('discovered');
        }

        // Update score and progress metrics
        this.updateHeaderMetrics(data.session_score, data.discovered_count, data.total_count);

        // Show Evidence Detail Modal
        this.showEvidenceDetailModal(data.evidence);

        // Dynamically unlock any interrogation topics tied to this evidence code
        if (data.evidence && data.evidence.code) {
          const lockedBtns = document.querySelectorAll(`.ask-topic-btn[data-required-code="${data.evidence.code}"]`);
          lockedBtns.forEach(btn => {
            btn.dataset.isLocked = "false";
            btn.classList.remove('locked-topic', 'text-muted', 'border-secondary');
            const lockIcon = btn.querySelector('.lock-indicator');
            if (lockIcon) lockIcon.remove();
          });
        }

        // If on the corkboard, refresh available cards
        if (window.corkboardInstance) {
          window.corkboardInstance.addCard(data.evidence);
        }
      } else {
        showBureauToast('Notice', data.error || 'Inspection failed', 'crimson');
      }
    })
    .catch(err => {
      console.error(err);
      showBureauToast('System Error', 'Could not record evidence', 'crimson');
    });
  }

  showEvidenceDetailModal(ev) {
    const modalEl = document.getElementById('evidenceDetailModal');
    if (!modalEl) return;

    document.getElementById('evidenceModalCode').textContent = ev.code;
    document.getElementById('evidenceModalTitle').textContent = ev.name;
    document.getElementById('evidenceModalType').textContent = ev.evidence_type;
    document.getElementById('evidenceModalLocation').textContent = ev.location_found;
    document.getElementById('evidenceModalDesc').textContent = ev.description;
    document.getElementById('evidenceModalForensics').textContent = ev.forensic_notes;

    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  }

  updateHeaderMetrics(score, discovered, total) {
    const scoreEl = document.getElementById('session-score-badge');
    if (scoreEl) scoreEl.textContent = `${score} PTS`;

    const countEl = document.getElementById('discovered-evidence-count');
    if (countEl) countEl.textContent = `${discovered} / ${total}`;

    const progBar = document.getElementById('investigation-progress-bar');
    if (progBar && total > 0) {
      const pct = Math.round((discovered / total) * 100);
      progBar.style.width = `${pct}%`;
    }
  }

  // 3. Suspect Interrogation & Contradiction System
  initInterrogations() {
    const suspectCards = document.querySelectorAll('.suspect-select-item');
    if (suspectCards.length > 0) {
      const activeCard = document.querySelector('.suspect-select-item.border-warning') || suspectCards[0];
      if (activeCard) {
        this.activeSuspectId = activeCard.dataset.suspectId;
      }
    }

    suspectCards.forEach(card => {
      card.addEventListener('click', () => {
        suspectCards.forEach(c => c.classList.remove('border-warning', 'bg-elevated'));
        card.classList.add('border-warning', 'bg-elevated');
        const suspectId = card.dataset.suspectId;
        this.selectSuspect(suspectId);
      });
    });

    // Global event delegation for interrogation questions across all suspect panels
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.ask-topic-btn');
      if (!btn) return;
      e.preventDefault();

      const isLocked = btn.dataset.isLocked === 'true';
      if (isLocked) {
        window.bureauAudio.playClick();
        const code = btn.dataset.requiredCode || 'Classified';
        const name = btn.dataset.requiredName || 'Evidence';
        showBureauToast(
          'Lead Locked',
          `Requires clue [${code}] ${name}. Search crime scene hotspots to discover this evidence.`,
          'crimson'
        );
        return;
      }

      const topicId = btn.dataset.topicId;
      const suspectId = btn.dataset.suspectId || this.activeSuspectId;
      if (!suspectId || !topicId) return;

      this.askSuspectQuestion(topicId, suspectId, btn);
    });
  }

  selectSuspect(suspectId) {
    this.activeSuspectId = suspectId;
    window.bureauAudio.playClick();

    // Hide all suspect panels and show active
    document.querySelectorAll('.suspect-interrogation-panel').forEach(p => p.classList.add('d-none'));
    const targetPanel = document.getElementById(`suspect-panel-${suspectId}`);
    if (targetPanel) {
      targetPanel.classList.remove('d-none');
    }
  }

  askSuspectQuestion(topicId, suspectId, btnEl) {
    if (!suspectId) return;
    window.bureauAudio.playClick();

    btnEl.disabled = true;
    const originalHTML = btnEl.innerHTML;
    btnEl.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Interrogating...';

    fetch(`/api/investigate/${this.slug}/interview/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        suspect_id: suspectId,
        topic_id: topicId
      })
    })
    .then(res => res.json())
    .then(data => {
      btnEl.disabled = false;

      if (data.success) {
        btnEl.innerHTML = '<i class="bi bi-chat-quote-fill me-1"></i> Questioned <span class="badge bg-dark text-gold border border-warning ms-1"><i class="bi bi-check-lg"></i></span>';

        if (data.is_contradiction) {
          window.bureauAudio.playContradiction();
          showBureauToast('CONTRADICTION ESTABLISHED', 'Suspect statement invalidated by physical evidence!', 'crimson');
        } else {
          showBureauToast('Interview Recorded', `Topic: ${data.topic_title}`, 'gold');
        }

        // Safely append to dialogue box without letting any render error reject the promise
        try {
          this.appendDialogueLog(suspectId, data.question, data.response, data.is_contradiction);
        } catch (renderErr) {
          console.error('Failed to render dialogue entry:', renderErr);
        }

        // Update score
        if (data.session_score !== undefined) {
          const scoreEl = document.getElementById('session-score-badge');
          if (scoreEl) scoreEl.textContent = `${data.session_score} PTS`;
        }
      } else {
        btnEl.innerHTML = originalHTML;
        showBureauToast('Topic Locked', data.error, 'crimson');
      }
    })
    .catch(err => {
      console.error(err);
      btnEl.disabled = false;
      btnEl.innerHTML = originalHTML;
      showBureauToast('Error', 'Interrogation request failed', 'crimson');
    });
  }

  appendDialogueLog(suspectId, question, response, isContradiction) {
    try {
      const logBox = document.getElementById(`dialogue-log-${suspectId}`);
      if (!logBox) return;

      // Remove empty state message if present
      const emptyState = logBox.querySelector('.empty-interview-msg, .text-muted.small.font-mono.text-center');
      if (emptyState) {
        emptyState.remove();
      }

      const entry = document.createElement('div');
      entry.className = 'mb-3 dialogue-entry';

      let contradictionHTML = '';
      if (isContradiction) {
        contradictionHTML = `
          <div class="contradiction-banner mb-2">
            <i class="bi bi-exclamation-triangle-fill me-2"></i> CONTRADICTION ESTABLISHED — STATEMENT REFUTED!
          </div>
        `;
      }

      const safeQ = (typeof escapeHTML === 'function') ? escapeHTML(question) : question;
      const safeR = (typeof escapeHTML === 'function') ? escapeHTML(response) : response;

      entry.innerHTML = `
        <div class="dialogue-bubble player-question">
          <strong class="text-crimson font-mono small d-block mb-1">DETECTIVE QUESTION:</strong>
          ${safeQ}
        </div>
        ${contradictionHTML}
        <div class="dialogue-bubble">
          <strong class="text-gold font-mono small d-block mb-1">SUBJECT RESPONSE:</strong>
          ${safeR}
        </div>
      `;
      logBox.prepend(entry);
      logBox.scrollTop = 0;
    } catch (e) {
      console.error('Error appending dialogue:', e);
    }
  }

  // 4. Bureau Hints
  initHints() {
    const hintButtons = document.querySelectorAll('.request-hint-btn');
    hintButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const level = btn.dataset.hintLevel;
        const penalty = btn.dataset.hintPenalty;

        if (confirm(`Consulting Bureau Hint (Level ${level}) will record a penalty of -${penalty} points against your final score. Do you wish to proceed?`)) {
          this.requestHint(level, btn);
        }
      });
    });
  }

  requestHint(level, btnEl) {
    window.bureauAudio.playClick();
    btnEl.disabled = true;

    fetch(`/api/investigate/${this.slug}/hint/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({ hint_level: level })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showBureauToast('Hint Received', `Level ${data.hint_level} hint decrypted. Penalty: -${data.penalty} pts`, 'crimson');
        
        const cardBody = document.getElementById(`hint-body-${level}`);
        if (cardBody) {
          cardBody.innerHTML = `
            <div class="p-3 bg-dark border border-warning rounded">
              <strong class="text-gold font-mono d-block mb-2">BUREAU ANALYST BRIEFING:</strong>
              <p class="mb-0 text-light">${data.hint_text}</p>
            </div>
          `;
        }
        btnEl.remove();
      } else {
        btnEl.disabled = false;
        showBureauToast('Notice', data.error, 'crimson');
      }
    })
    .catch(err => {
      console.error(err);
      btnEl.disabled = false;
      showBureauToast('Error', 'Failed to retrieve hint', 'crimson');
    });
  }

  // 5. Personal Detective Notes
  initNotes() {
    const noteForm = document.getElementById('detectiveNoteForm');
    if (!noteForm) return;

    noteForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = document.getElementById('detectiveNoteInput');
      const content = input.value.trim();
      if (!content) return;

      window.bureauAudio.playClick();

      fetch(`/api/investigate/${this.slug}/note/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ content: content })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          input.value = '';
          showBureauToast('Note Pinned', 'Your deduction has been recorded in the journal.', 'gold');

          const notesList = document.getElementById('detectiveNotesContainer');
          if (notesList) {
            const noteEl = document.createElement('div');
            noteEl.className = 'p-2 mb-2 bg-dark border border-secondary rounded font-mono small text-light';
            noteEl.innerHTML = `<span class="text-gold">[${data.created_at}]</span> ${data.content}`;
            notesList.prepend(noteEl);
          }
        } else {
          showBureauToast('Error', data.error, 'crimson');
        }
      })
      .catch(err => {
        console.error(err);
      });
    });
  }

  // 6. Final Accusation Submission
  initAccusation() {
    const form = document.getElementById('accusationForm');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();

      const suspectSelect = document.getElementById('accuseSuspectSelect');
      const motiveInput = document.getElementById('accuseMotiveInput');
      const reasoningInput = document.getElementById('accuseReasoningInput');

      const suspectId = suspectSelect ? suspectSelect.value : null;
      const motive = motiveInput ? motiveInput.value.trim() : '';
      const reasoning = reasoningInput ? reasoningInput.value.trim() : '';

      // Collect checked evidence checkboxes
      const checkedEvidence = Array.from(
        document.querySelectorAll('input[name="accuse_evidence"]:checked')
      ).map(cb => Number(cb.value));

      if (!suspectId) {
        alert('Please designate the accused prime suspect.');
        return;
      }
      if (!motive) {
        alert('Please specify the suspected motive.');
        return;
      }
      if (checkedEvidence.length === 0) {
        alert('Select at least one piece of supporting physical evidence.');
        return;
      }
      if (reasoning.length < 15) {
        alert('Please provide sufficient chronological deduction reasoning (min 15 characters).');
        return;
      }

      const submitBtn = document.getElementById('submitAccusationBtn');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Transmitting Warrant to Bureau...';
      }

      window.bureauAudio.playClick();

      fetch(`/api/investigate/${this.slug}/accuse/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
          suspect_id: suspectId,
          motive: motive,
          evidence_ids: checkedEvidence,
          reasoning: reasoning
        })
      })
      .then(res => res.json())
      .then(outcome => {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = 'Execute Final Accusation';
        }
        this.displayAccusationVerdict(outcome);
      })
      .catch(err => {
        console.error(err);
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = 'Execute Final Accusation';
        }
        showBureauToast('Transmission Error', 'Failed to submit accusation warrant', 'crimson');
      });
    });
  }

  displayAccusationVerdict(outcome) {
    const modalEl = document.getElementById('verdictModal');
    if (!modalEl) return;

    const box = document.getElementById('verdictBox');
    const title = document.getElementById('verdictTitle');
    const rankEl = document.getElementById('verdictRank');
    const scoreEl = document.getElementById('verdictScore');
    const feedbackEl = document.getElementById('verdictFeedback');
    const epilogueBox = document.getElementById('verdictEpilogue');
    const epilogueText = document.getElementById('verdictEpilogueText');

    if (outcome.is_correct) {
      window.bureauAudio.playDiscovery();
      box.className = 'verdict-box verdict-success';
      title.innerHTML = '<i class="bi bi-check-circle-fill text-success me-2"></i> CASE CLOSED — WARRANT UPHELD!';
    } else {
      window.bureauAudio.playContradiction();
      box.className = 'verdict-box verdict-failed';
      title.innerHTML = '<i class="bi bi-x-circle-fill text-danger me-2"></i> CASE UNSOLVED — ACCUSATION REJECTED';
    }

    rankEl.textContent = outcome.rank;
    scoreEl.textContent = `${outcome.final_score} PTS`;
    feedbackEl.textContent = outcome.feedback;

    if (outcome.is_correct && outcome.epilogue) {
      epilogueBox.classList.remove('d-none');
      epilogueText.textContent = outcome.epilogue;
    } else {
      epilogueBox.classList.add('d-none');
    }

    const modal = new bootstrap.Modal(modalEl, { backdrop: 'static', keyboard: false });
    modal.show();
  }
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('investigation-workspace-root');
  if (container) {
    const slug = container.dataset.caseSlug;
    window.investigationWorkspace = new InvestigationWorkspace(slug);
  }
});
