/**
 * CASE CLOSED: Interactive Detective Corkboard
 * Handles visual card pinning, red yarn SVG connections, and backend connection persistence.
 */

class InteractiveCorkboard {
  constructor(canvasEl) {
    this.canvas = canvasEl;
    this.slug = canvasEl.dataset.caseSlug;
    this.svg = document.getElementById('corkboardSvg');
    this.selectedCard = null;
    this.connections = [];

    this.initConnectionsFromDOM();
    this.initCardInteractions();
    this.renderYarnLines();

    window.addEventListener('resize', () => this.renderYarnLines());
  }

  initConnectionsFromDOM() {
    const raw = this.canvas.dataset.initialConnections;
    if (raw) {
      try {
        this.connections = JSON.parse(raw);
      } catch(e) {
        this.connections = [];
      }
    }
  }

  initCardInteractions() {
    const cards = this.canvas.querySelectorAll('.cork-card');
    cards.forEach(card => {
      card.addEventListener('click', (e) => {
        // Prevent click when dragging
        this.handleCardClick(card);
      });
    });

    const clearBtn = document.getElementById('clearConnectionsBtn');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        if (confirm('Clear all pinned yarn connections on this evidence board?')) {
          this.clearAllConnections();
        }
      });
    }
  }

  handleCardClick(card) {
    window.bureauAudio.playClick();

    if (!this.selectedCard) {
      // First card selection
      this.selectedCard = card;
      card.classList.add('selected');
      showBureauToast('Corkboard Pin', `Selected ${card.dataset.title}. Click another card to link with red yarn.`, 'gold');
    } else if (this.selectedCard === card) {
      // Deselect
      this.selectedCard.classList.remove('selected');
      this.selectedCard = null;
    } else {
      // Connect two cards!
      const sourceCard = this.selectedCard;
      const targetCard = card;

      sourceCard.classList.remove('selected');
      this.selectedCard = null;

      this.createConnection(
        sourceCard.dataset.type,
        Number(sourceCard.dataset.id),
        targetCard.dataset.type,
        Number(targetCard.dataset.id)
      );
    }
  }

  createConnection(sourceType, sourceId, targetType, targetId) {
    // Avoid duplicate local link
    const exists = this.connections.some(c => 
      (c.source_type === sourceType && c.source_id === sourceId && c.target_type === targetType && c.target_id === targetId) ||
      (c.source_type === targetType && c.source_id === targetId && c.target_type === sourceType && c.target_id === sourceId)
    );

    if (exists) {
      showBureauToast('Notice', 'Yarn connection already established between these cards.', 'gold');
      return;
    }

    fetch(`/api/investigate/${this.slug}/connect/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken()
      },
      body: JSON.stringify({
        source_type: sourceType,
        source_id: sourceId,
        target_type: targetType,
        target_id: targetId,
        notes: ''
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        this.connections.push({
          id: data.connection_id,
          source_type: sourceType,
          source_id: sourceId,
          target_type: targetType,
          target_id: targetId
        });
        this.renderYarnLines();
        window.bureauAudio.playDiscovery();
        showBureauToast('Yarn Pinned', 'Clues connected on the evidence corkboard.', 'crimson');
      }
    })
    .catch(err => console.error(err));
  }

  clearAllConnections() {
    this.connections.forEach(c => {
      fetch(`/api/investigate/${this.slug}/disconnect/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ connection_id: c.id })
      }).catch(() => {});
    });
    this.connections = [];
    this.renderYarnLines();
    showBureauToast('Board Reset', 'All yarn strings removed.', 'gold');
  }

  renderYarnLines() {
    if (!this.svg) return;
    this.svg.innerHTML = '';

    const canvasRect = this.canvas.getBoundingClientRect();

    this.connections.forEach(c => {
      const sourceCard = this.canvas.querySelector(`.cork-card[data-type="${c.source_type}"][data-id="${c.source_id}"]`);
      const targetCard = this.canvas.querySelector(`.cork-card[data-type="${c.target_type}"][data-id="${c.target_id}"]`);

      if (sourceCard && targetCard) {
        const sRect = sourceCard.getBoundingClientRect();
        const tRect = targetCard.getBoundingClientRect();

        const x1 = (sRect.left + sRect.width / 2) - canvasRect.left;
        const y1 = (sRect.top + sRect.height / 2) - canvasRect.top;
        const x2 = (tRect.left + tRect.width / 2) - canvasRect.left;
        const y2 = (tRect.top + tRect.height / 2) - canvasRect.top;

        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x1);
        line.setAttribute('y1', y1);
        line.setAttribute('x2', x2);
        line.setAttribute('y2', y2);
        line.setAttribute('stroke', '#C6283D');
        line.setAttribute('stroke-width', '2.5');
        line.setAttribute('stroke-linecap', 'round');
        line.setAttribute('stroke-opacity', '0.85');
        line.setAttribute('filter', 'drop-shadow(0px 2px 3px rgba(0,0,0,0.7))');

        this.svg.appendChild(line);
      }
    });
  }

  addCard(evidence) {
    // Dynamically insert evidence into corkboard if not present
    let card = this.canvas.querySelector(`.cork-card[data-type="evidence"][data-id="${evidence.id}"]`);
    if (!card) {
      const grid = document.getElementById('corkboardCardsGrid');
      if (grid) {
        card = document.createElement('div');
        card.className = 'cork-card';
        card.dataset.type = 'evidence';
        card.dataset.id = evidence.id;
        card.dataset.title = evidence.name;
        card.innerHTML = `
          <div class="cork-pin"></div>
          <div class="badge-crimson font-mono small mb-1">${evidence.code}</div>
          <h6 class="fw-bold mb-1 font-serif text-dark">${evidence.name}</h6>
          <p class="small text-muted mb-0 font-mono">${evidence.evidence_type}</p>
        `;
        card.addEventListener('click', () => this.handleCardClick(card));
        grid.appendChild(card);
      }
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('corkboardCanvas');
  if (canvas) {
    window.corkboardInstance = new InteractiveCorkboard(canvas);
  }
});
