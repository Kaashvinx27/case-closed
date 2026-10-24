/**
 * CASE CLOSED: Leaderboard Controller
 */
document.addEventListener('DOMContentLoaded', () => {
  const caseSelect = document.getElementById('leaderboardCaseFilter');
  if (caseSelect) {
    caseSelect.addEventListener('change', () => {
      window.bureauAudio.playClick();
      const val = caseSelect.value;
      const url = new URL(window.location);
      if (val === 'all') {
        url.searchParams.delete('case');
      } else {
        url.searchParams.set('case', val);
      }
      window.location = url.toString();
    });
  }

  // Client-side quick filter on detective name
  const searchInput = document.getElementById('leaderboardSearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().trim();
      const rows = document.querySelectorAll('.leaderboard-row');
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
      });
    });
  }
});
