/*
 * analyzer.js — Rule-based speech analysis. No network, no AI.
 * Takes a transcript (+ optional spoken duration) and returns a
 * structured report with a score and actionable tips.
 */
(function () {
  const D = window.APP_DATA;

  // Escape a phrase for safe use inside a RegExp.
  function esc(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  // Split transcript into lowercase word tokens.
  function tokenize(text) {
    const m = text.toLowerCase().match(/[a-z']+/g);
    return m || [];
  }

  // Count filler words/phrases. Multi-word phrases checked first so
  // "you know" isn't double-counted as separate words.
  function countFillers(text) {
    const lower = " " + text.toLowerCase().replace(/[^a-z' ]+/g, " ").replace(/\s+/g, " ") + " ";
    const hits = {};
    let total = 0;
    for (const filler of D.fillerWords) {
      const re = new RegExp("(?:^| )" + esc(filler) + "(?= |$)", "g");
      const matches = lower.match(re);
      if (matches && matches.length) {
        hits[filler] = matches.length;
        total += matches.length;
      }
    }
    return { hits, total };
  }

  // Find weak words present in the text and their stronger alternatives.
  function findWeakWords(text) {
    const lower = " " + text.toLowerCase().replace(/[^a-z' ]+/g, " ").replace(/\s+/g, " ") + " ";
    const found = [];
    for (const [weak, strong] of Object.entries(D.weakWords)) {
      const re = new RegExp("(?:^| )" + esc(weak) + "(?= |$)", "g");
      const matches = lower.match(re);
      if (matches && matches.length) {
        found.push({ word: weak, count: matches.length, suggestions: strong });
      }
    }
    return found.sort((a, b) => b.count - a.count);
  }

  // Words repeated unusually often (excluding common stop words & fillers).
  function findRepetition(tokens) {
    const stop = new Set([
      "the", "a", "an", "and", "or", "but", "to", "of", "in", "on", "at",
      "for", "with", "is", "are", "was", "were", "be", "been", "i", "you",
      "we", "they", "it", "he", "she", "that", "this", "my", "our", "your",
      "as", "by", "from", "have", "has", "had", "do", "did", "will", "would",
      "can", "could", "should", "not", "no", "yes", "if", "then", "so", "me"
    ]);
    const counts = {};
    for (const t of tokens) {
      if (t.length < 4 || stop.has(t)) continue;
      counts[t] = (counts[t] || 0) + 1;
    }
    return Object.entries(counts)
      .filter(([, c]) => c >= 4)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([word, count]) => ({ word, count }));
  }

  // Rough sentence segmentation. Speech-to-text rarely adds punctuation,
  // so we fall back to estimating sentences from word count.
  function sentenceStats(text, wordCount) {
    const parts = text.split(/[.!?]+/).map(s => s.trim()).filter(Boolean);
    const sentenceCount = parts.length >= 2 ? parts.length : Math.max(1, Math.round(wordCount / 15));
    const avgLen = wordCount / sentenceCount;
    return { sentenceCount, avgLen };
  }

  /*
   * Main entry point.
   *   transcript: string of what was said
   *   durationSec: seconds spoken (0/undefined if unknown)
   */
  function analyze(transcript, durationSec) {
    const text = (transcript || "").trim();
    const tokens = tokenize(text);
    const wordCount = tokens.length;
    const uniqueCount = new Set(tokens).size;

    const fillers = countFillers(text);
    const weak = findWeakWords(text);
    const repeats = findRepetition(tokens);
    const sentences = sentenceStats(text, wordCount);

    // Type-token ratio = vocabulary variety (0..1). Higher is richer.
    const ttr = wordCount ? uniqueCount / wordCount : 0;

    // Words per minute (only meaningful if we timed the speech).
    const wpm = durationSec && durationSec > 2 ? Math.round((wordCount / durationSec) * 60) : null;

    const fillerRate = wordCount ? fillers.total / wordCount : 0; // fraction

    // ---- Scoring (0-100). Start at 100 and deduct for issues. ----
    let score = 100;
    const tips = [];
    const wins = [];

    if (wordCount < 20) {
      tips.push("Try to speak for longer — aim for at least 30–40 words so there's enough to work with.");
      score -= 15;
    }

    // Filler words
    if (fillerRate > 0.12) {
      score -= 25;
      tips.push(`Filler words are frequent (${fillers.total} found). Pause silently instead of saying "um", "like" or "you know".`);
    } else if (fillerRate > 0.06) {
      score -= 12;
      tips.push(`A few filler words crept in (${fillers.total}). A short pause sounds more confident than a filler.`);
    } else if (wordCount >= 20) {
      wins.push("Very few filler words — you sound clear and deliberate.");
    }

    // Pace
    if (wpm !== null) {
      if (wpm > 180) {
        score -= 12;
        tips.push(`You spoke quickly (~${wpm} wpm). Slow down to 130–160 wpm so listeners can follow.`);
      } else if (wpm < 100) {
        score -= 8;
        tips.push(`Your pace was slow (~${wpm} wpm). A little more energy will keep listeners engaged.`);
      } else {
        wins.push(`Great speaking pace (~${wpm} wpm).`);
      }
    }

    // Vocabulary variety
    if (wordCount >= 30) {
      if (ttr < 0.4) {
        score -= 10;
        tips.push("You repeated a lot of the same words. Try varying your vocabulary for richer delivery.");
      } else if (ttr > 0.55) {
        wins.push("Rich, varied vocabulary.");
      }
    }

    // Weak words
    if (weak.length >= 3) {
      score -= 10;
      tips.push("Several vague words could be sharper (see suggestions below) for a more professional tone.");
    } else if (weak.length > 0) {
      score -= 4;
    }

    // Repetition
    if (repeats.length >= 2) {
      score -= 6;
      tips.push(`You leaned on a few words repeatedly (e.g. "${repeats[0].word}"). Mix in synonyms.`);
    }

    // Sentence length
    if (sentences.avgLen > 28) {
      score -= 6;
      tips.push("Some sentences ran long. Shorter sentences are easier to follow when speaking.");
    } else if (wordCount >= 30 && sentences.avgLen >= 8 && sentences.avgLen <= 22) {
      wins.push("Well-balanced sentence length.");
    }

    score = Math.max(0, Math.min(100, Math.round(score)));

    if (!tips.length && wordCount >= 20) {
      tips.push("Excellent — keep practising to lock in this level of fluency.");
    }

    return {
      text,
      wordCount,
      uniqueCount,
      durationSec: durationSec || 0,
      wpm,
      fillers,
      fillerRate,
      weak,
      repeats,
      sentences,
      ttr,
      score,
      tips,
      wins
    };
  }

  window.Analyzer = { analyze };
})();
