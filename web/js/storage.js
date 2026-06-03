/*
 * storage.js — Local progress tracking via localStorage.
 * Keeps a rolling history of practice sessions plus aggregate stats.
 * Everything stays on the user's device; nothing is uploaded.
 */
(function () {
  const KEY = "speakup.progress.v1";

  function load() {
    try {
      const raw = localStorage.getItem(KEY);
      if (raw) return JSON.parse(raw);
    } catch (_) { /* ignore */ }
    return { sessions: [], totalWords: 0, totalSeconds: 0, vocabReviewed: 0 };
  }

  function save(state) {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (_) { /* ignore */ }
  }

  // Record a completed speaking/conversation session.
  function recordSession({ kind, score, wordCount, durationSec, prompt }) {
    const state = load();
    state.sessions.unshift({
      kind,
      score: score || 0,
      wordCount: wordCount || 0,
      durationSec: durationSec || 0,
      prompt: prompt || "",
      at: Date.now()
    });
    state.sessions = state.sessions.slice(0, 100); // cap history
    state.totalWords += wordCount || 0;
    state.totalSeconds += durationSec || 0;
    save(state);
    return state;
  }

  function recordVocab(n) {
    const state = load();
    state.vocabReviewed += n || 1;
    save(state);
    return state;
  }

  // Distinct calendar days with at least one session.
  function practiceDays(state) {
    const days = new Set();
    for (const s of state.sessions) {
      days.add(new Date(s.at).toDateString());
    }
    return days;
  }

  // Current consecutive-day streak ending today or yesterday.
  function currentStreak(state) {
    const days = practiceDays(state);
    if (!days.size) return 0;
    let streak = 0;
    const d = new Date();
    // allow today OR yesterday to keep the streak alive
    if (!days.has(d.toDateString())) {
      d.setDate(d.getDate() - 1);
      if (!days.has(d.toDateString())) return 0;
    }
    while (days.has(d.toDateString())) {
      streak++;
      d.setDate(d.getDate() - 1);
    }
    return streak;
  }

  function averageScore(state) {
    const scored = state.sessions.filter(s => s.score > 0);
    if (!scored.length) return 0;
    return Math.round(scored.reduce((a, s) => a + s.score, 0) / scored.length);
  }

  function reset() {
    try { localStorage.removeItem(KEY); } catch (_) { /* ignore */ }
  }

  window.Store = {
    load, recordSession, recordVocab,
    currentStreak, averageScore, practiceDays, reset
  };
})();
