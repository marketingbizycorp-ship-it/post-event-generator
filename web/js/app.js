/*
 * app.js — UI controller. Wires the four views (Speaking, Vocabulary,
 * Conversation, Progress) to the analyzer, speech and storage modules.
 */
(function () {
  const D = window.APP_DATA;
  const app = document.getElementById("app");
  const tabs = document.getElementById("tabs");

  // ---------- small DOM helpers ----------
  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    if (attrs) {
      for (const [k, v] of Object.entries(attrs)) {
        if (k === "class") node.className = v;
        else if (k === "html") node.innerHTML = v;
        else if (k.startsWith("on") && typeof v === "function") {
          node.addEventListener(k.slice(2), v);
        } else if (v !== null && v !== undefined) {
          node.setAttribute(k, v);
        }
      }
    }
    (children || []).forEach(c => {
      if (c == null) return;
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return node;
  }
  function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); }
  function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
  function fmtTime(sec) {
    const m = Math.floor(sec / 60), s = Math.round(sec % 60);
    return `${m}:${String(s).padStart(2, "0")}`;
  }

  // ===================================================================
  //  SHARED: a record + analyse panel used by Speaking & Conversation
  // ===================================================================
  function buildPractice(promptText, kind, onDone) {
    const supported = window.Speech.isRecognitionSupported();
    let recognizer = null, startedAt = 0, timerId = null;

    const status = el("div", { class: "status" }, [
      supported ? "Ready — tap Record and start speaking."
                : "Speech-to-text isn't supported in this browser. Type what you'd say below."
    ]);
    const timer = el("span", { class: "timer" }, ["0:00"]);
    const transcriptBox = el("textarea", {
      class: "transcript",
      rows: "5",
      placeholder: supported
        ? "Your words will appear here as you speak — you can also edit them."
        : "Type your spoken answer here, then tap Analyse."
    });
    const results = el("div", { class: "results" });

    const recordBtn = el("button", { class: "btn primary" }, ["● Record"]);
    const stopBtn = el("button", { class: "btn", disabled: "true" }, ["■ Stop"]);
    const analyzeBtn = el("button", { class: "btn accent" }, ["Analyse"]);

    function tickStart() {
      startedAt = Date.now();
      timerId = setInterval(() => {
        timer.textContent = fmtTime((Date.now() - startedAt) / 1000);
      }, 250);
    }
    function tickStop() { if (timerId) { clearInterval(timerId); timerId = null; } }

    recordBtn.addEventListener("click", () => {
      if (supported) {
        recognizer = window.Speech.createRecognizer({
          onInterim: t => { transcriptBox.value = t; },
          onError: msg => { status.textContent = "Mic error: " + msg + ". You can type instead."; },
          onEnd: () => {}
        });
        recognizer.start();
      }
      status.textContent = "Recording… speak naturally.";
      recordBtn.disabled = true;
      stopBtn.disabled = false;
      transcriptBox.value = "";
      tickStart();
    });

    stopBtn.addEventListener("click", () => {
      if (recognizer) recognizer.stop();
      tickStop();
      status.textContent = "Stopped. Edit if needed, then tap Analyse.";
      recordBtn.disabled = false;
      stopBtn.disabled = true;
    });

    analyzeBtn.addEventListener("click", () => {
      if (recognizer) { recognizer.stop(); recognizer = null; }
      tickStop();
      recordBtn.disabled = false;
      stopBtn.disabled = true;
      const text = transcriptBox.value.trim();
      if (!text) { status.textContent = "Nothing to analyse yet — record or type something first."; return; }
      const dur = startedAt ? (Date.now() - startedAt) / 1000 : 0;
      const report = window.Analyzer.analyze(text, dur);
      clear(results);
      results.appendChild(renderReport(report));
      window.Store.recordSession({
        kind, score: report.score, wordCount: report.wordCount,
        durationSec: report.durationSec, prompt: promptText
      });
      if (onDone) onDone(report);
      results.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });

    return el("div", { class: "practice" }, [
      el("div", { class: "controls" }, [recordBtn, stopBtn, analyzeBtn, timer]),
      status,
      transcriptBox,
      results
    ]);
  }

  // Render the analysis report card.
  function renderReport(r) {
    const scoreClass = r.score >= 80 ? "good" : r.score >= 60 ? "ok" : "low";

    const metrics = el("div", { class: "metrics" }, [
      metric("Score", r.score, "/100", scoreClass),
      metric("Words", r.wordCount, ""),
      metric("Fillers", r.fillers.total, ""),
      metric("Pace", r.wpm ? r.wpm : "—", r.wpm ? " wpm" : ""),
      metric("Variety", Math.round(r.ttr * 100), "%"),
      metric("Time", fmtTime(r.durationSec), "")
    ]);

    const sections = [el("h3", null, [`Your result: ${r.score}/100`]), metrics];

    if (r.wins.length) {
      sections.push(el("div", { class: "feedback wins" }, [
        el("h4", null, ["✅ What worked"]),
        el("ul", null, r.wins.map(w => el("li", null, [w])))
      ]));
    }
    if (r.tips.length) {
      sections.push(el("div", { class: "feedback tips" }, [
        el("h4", null, ["💡 To improve"]),
        el("ul", null, r.tips.map(t => el("li", null, [t])))
      ]));
    }
    if (r.fillers.total) {
      const list = Object.entries(r.fillers.hits).sort((a, b) => b[1] - a[1])
        .map(([w, c]) => el("span", { class: "chip" }, [`${w} ×${c}`]));
      sections.push(el("div", { class: "feedback" }, [
        el("h4", null, ["Filler words spotted"]),
        el("div", { class: "chips" }, list)
      ]));
    }
    if (r.weak.length) {
      sections.push(el("div", { class: "feedback" }, [
        el("h4", null, ["Stronger word choices"]),
        el("ul", null, r.weak.map(w =>
          el("li", null, [
            el("strong", null, [`"${w.word}"`]),
            ` → try: ${w.suggestions.slice(0, 3).join(", ")}`
          ])
        ))
      ]));
    }
    return el("div", { class: "report" }, sections);
  }
  function metric(label, value, unit, cls) {
    return el("div", { class: "metric " + (cls || "") }, [
      el("span", { class: "mval" }, [String(value), el("small", null, [unit || ""])]),
      el("span", { class: "mlabel" }, [label])
    ]);
  }

  // ===================================================================
  //  VIEW: SPEAKING
  // ===================================================================
  function renderSpeaking() {
    clear(app);
    const levels = Object.keys(D.speakingPrompts);
    const state = { level: levels[0], prompt: pick(D.speakingPrompts[levels[0]]) };

    const promptText = el("p", { class: "prompt-text" }, [state.prompt]);
    const practiceHost = el("div");

    function rebuildPractice() {
      clear(practiceHost);
      practiceHost.appendChild(buildPractice(state.prompt, "speaking"));
    }

    function newPrompt() {
      state.prompt = pick(D.speakingPrompts[state.level]);
      promptText.textContent = state.prompt;
      rebuildPractice();
    }

    const levelSelect = el("select", {
      class: "select",
      onchange: e => { state.level = e.target.value; newPrompt(); }
    }, levels.map(l => el("option", { value: l }, [labelize(l)])));

    app.appendChild(el("section", { class: "view" }, [
      el("div", { class: "view-head" }, [
        el("h2", null, ["🎤 Speaking practice"]),
        el("p", { class: "muted" }, ["Pick a prompt, speak for 30–90 seconds, then get instant feedback on fillers, pace and word choice."])
      ]),
      el("div", { class: "card prompt-card" }, [
        el("div", { class: "row between" }, [
          el("label", { class: "field" }, ["Difficulty ", levelSelect]),
          el("button", { class: "btn ghost", onclick: newPrompt }, ["↻ New prompt"])
        ]),
        el("div", { class: "row" }, [
          el("button", { class: "btn icon", title: "Hear the prompt",
            onclick: () => window.Speech.speak(state.prompt) }, ["🔊"]),
          promptText
        ])
      ]),
      el("div", { class: "card" }, [practiceHost])
    ]));

    rebuildPractice();
  }
  function labelize(s) { return s.charAt(0).toUpperCase() + s.slice(1).replace(/-/g, " "); }

  // ===================================================================
  //  VIEW: VOCABULARY
  // ===================================================================
  function renderVocab() {
    clear(app);
    const decks = Object.keys(D.vocabDecks);
    const state = { deck: decks[0], mode: "cards", idx: 0, flipped: false, quiz: null, score: 0, answered: 0 };

    const host = el("div", { class: "card" });

    function deckCards() { return D.vocabDecks[state.deck]; }

    function renderCardMode() {
      clear(host);
      const cards = deckCards();
      const card = cards[state.idx];
      const face = el("div", {
        class: "flashcard " + (state.flipped ? "flipped" : ""),
        onclick: () => { state.flipped = !state.flipped; renderCardMode(); }
      }, [
        el("div", { class: "fc-label" }, [state.flipped ? "Professional" : "Casual / informal"]),
        el("div", { class: "fc-main" }, [state.flipped ? card.pro : card.casual]),
        state.flipped ? el("div", { class: "fc-extra" }, [
          el("p", null, [el("strong", null, ["Why: "]), card.meaning]),
          el("p", { class: "muted" }, [el("strong", null, ["e.g. "]), card.example])
        ]) : el("div", { class: "fc-hint" }, ["tap to reveal the professional version"])
      ]);

      host.appendChild(el("div", null, [
        el("div", { class: "row between" }, [
          el("span", { class: "muted" }, [`Card ${state.idx + 1} / ${cards.length}`]),
          el("button", { class: "btn icon", title: "Hear it",
            onclick: ev => { ev.stopPropagation(); window.Speech.speak(state.flipped ? card.pro : card.casual); } }, ["🔊"])
        ]),
        face,
        el("div", { class: "row between" }, [
          el("button", { class: "btn ghost", onclick: () => { state.idx = (state.idx - 1 + cards.length) % cards.length; state.flipped = false; renderCardMode(); } }, ["← Prev"]),
          el("button", { class: "btn", onclick: () => { window.Store.recordVocab(1); state.idx = (state.idx + 1) % cards.length; state.flipped = false; renderCardMode(); } }, ["Next →"])
        ])
      ]));
    }

    function newQuiz() {
      const cards = deckCards();
      const correct = pick(cards);
      const distractors = cards.filter(c => c !== correct);
      const opts = [correct];
      while (opts.length < Math.min(4, cards.length)) {
        const d = pick(distractors);
        if (!opts.includes(d)) opts.push(d);
      }
      // shuffle
      for (let i = opts.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [opts[i], opts[j]] = [opts[j], opts[i]];
      }
      state.quiz = { correct, opts, done: false };
    }

    function renderQuizMode() {
      clear(host);
      if (!state.quiz) newQuiz();
      const q = state.quiz;
      const feedback = el("div", { class: "quiz-feedback" });

      const optionBtns = q.opts.map(o => el("button", {
        class: "btn option",
        onclick: () => {
          if (q.done) return;
          q.done = true;
          state.answered++;
          const right = o === q.correct;
          if (right) state.score++;
          window.Store.recordVocab(1);
          optionBtns.forEach(b => {
            b.disabled = true;
            if (b._card === q.correct) b.classList.add("correct");
            else if (b._card === o) b.classList.add("wrong");
          });
          clear(feedback);
          feedback.appendChild(el("div", { class: right ? "fb good" : "fb bad" }, [
            right ? "✅ Correct!" : "❌ Not quite.",
            el("p", null, [el("strong", null, ["Pro version: "]), q.correct.pro]),
            el("p", { class: "muted" }, [q.correct.meaning])
          ]));
          feedback.appendChild(el("button", { class: "btn accent", onclick: () => { newQuiz(); renderQuizMode(); } }, ["Next question →"]));
        }
      }, [o.pro]));
      optionBtns.forEach((b, i) => { b._card = q.opts[i]; });

      host.appendChild(el("div", null, [
        el("div", { class: "row between" }, [
          el("span", { class: "muted" }, [`Score: ${state.score} / ${state.answered}`]),
        ]),
        el("p", { class: "quiz-q" }, ['How would you say this more professionally?']),
        el("div", { class: "quiz-prompt" }, [`"${state.quiz.correct.casual}"`]),
        el("div", { class: "options" }, optionBtns),
        feedback
      ]));
    }

    function render() {
      if (state.mode === "cards") renderCardMode();
      else renderQuizMode();
    }

    const deckSelect = el("select", {
      class: "select",
      onchange: e => { state.deck = e.target.value; state.idx = 0; state.flipped = false; state.quiz = null; render(); }
    }, decks.map(d => el("option", { value: d }, [d])));

    function modeBtn(mode, label) {
      return el("button", {
        class: "btn " + (state.mode === mode ? "primary" : "ghost"),
        onclick: () => { state.mode = mode; if (mode === "quiz") { state.quiz = null; } render();
          // refresh toggle styling
          modeRow.querySelectorAll("button").forEach(b => b.classList.remove("primary"));
          modeRow.querySelectorAll("button").forEach(b => { if (b.textContent === label) b.classList.add("primary"); });
        }
      }, [label]);
    }
    const modeRow = el("div", { class: "row" }, [modeBtn("cards", "Flashcards"), modeBtn("quiz", "Quiz")]);
    // ensure initial active styling
    modeRow.querySelectorAll("button").forEach((b, i) => { b.classList.toggle("primary", i === 0); b.classList.toggle("ghost", i !== 0); });

    app.appendChild(el("section", { class: "view" }, [
      el("div", { class: "view-head" }, [
        el("h2", null, ["📚 Professional vocabulary & phrasing"]),
        el("p", { class: "muted" }, ["Swap casual phrases for polished, professional alternatives. Flip cards to learn, then test yourself."])
      ]),
      el("div", { class: "card" }, [
        el("div", { class: "row between" }, [
          el("label", { class: "field" }, ["Topic ", deckSelect]),
          modeRow
        ])
      ]),
      host
    ]));

    render();
  }

  // ===================================================================
  //  VIEW: CONVERSATION (role-play scenarios)
  // ===================================================================
  function renderConversation() {
    clear(app);
    const state = { current: null };
    const detailHost = el("div");

    function renderList() {
      clear(detailHost);
      const cards = D.scenarios.map(s => el("button", {
        class: "scenario-card",
        onclick: () => { state.current = s; renderDetail(); }
      }, [
        el("span", { class: "tag" }, [s.category]),
        el("h3", null, [s.title]),
        el("p", { class: "muted" }, [s.situation])
      ]));
      detailHost.appendChild(el("div", { class: "scenario-grid" }, cards));
    }

    function renderDetail() {
      clear(detailHost);
      const s = state.current;
      detailHost.appendChild(el("div", null, [
        el("button", { class: "btn ghost", onclick: () => { state.current = null; renderList(); } }, ["← All scenarios"]),
        el("div", { class: "card scenario-detail" }, [
          el("span", { class: "tag" }, [s.category]),
          el("h3", null, [s.title]),
          el("p", null, [el("strong", null, ["Situation: "]), s.situation]),
          el("p", null, [el("strong", null, ["Your role: "]), s.role]),
          el("div", { class: "prompt-callout" }, [
            el("button", { class: "btn icon", title: "Hear it", onclick: () => window.Speech.speak(s.prompt) }, ["🔊"]),
            el("p", null, [s.prompt])
          ]),
          el("details", { class: "hint-box" }, [
            el("summary", null, ["💬 Useful phrases (tap to reveal)"]),
            el("ul", null, s.phrases.map(p => el("li", null, [
              p, " ",
              el("button", { class: "mini", title: "Hear it", onclick: () => window.Speech.speak(p) }, ["🔊"])
            ])))
          ]),
          el("details", { class: "hint-box" }, [
            el("summary", null, ["🎯 A strong answer usually includes…"]),
            el("ul", null, s.goodAnswerIncludes.map(g => el("li", null, [g])))
          ])
        ]),
        el("div", { class: "card" }, [
          el("h4", null, ["Your turn — respond out loud"]),
          buildPractice(s.title, "conversation")
        ])
      ]));
    }

    app.appendChild(el("section", { class: "view" }, [
      el("div", { class: "view-head" }, [
        el("h2", null, ["🗣️ Conversation & soft skills"]),
        el("p", { class: "muted" }, ["Role-play real workplace moments — feedback, negotiation, conflict and small talk. Read the situation, then respond out loud."])
      ]),
      detailHost
    ]));

    renderList();
  }

  // ===================================================================
  //  VIEW: PROGRESS
  // ===================================================================
  function renderProgress() {
    clear(app);
    const s = window.Store.load();
    const streak = window.Store.currentStreak(s);
    const avg = window.Store.averageScore(s);
    const days = window.Store.practiceDays(s).size;

    const stats = el("div", { class: "metrics big" }, [
      metric("Day streak", streak, ""),
      metric("Sessions", s.sessions.length, ""),
      metric("Avg score", avg || "—", avg ? "/100" : ""),
      metric("Words spoken", s.totalWords, ""),
      metric("Practice time", fmtTime(s.totalSeconds), ""),
      metric("Vocab reviewed", s.vocabReviewed, "")
    ]);

    let history;
    if (!s.sessions.length) {
      history = el("p", { class: "muted" }, ["No sessions yet — head to Speaking or Conversation to start practising!"]);
    } else {
      history = el("ul", { class: "history" }, s.sessions.slice(0, 15).map(sess => {
        const d = new Date(sess.at);
        const cls = sess.score >= 80 ? "good" : sess.score >= 60 ? "ok" : "low";
        return el("li", null, [
          el("span", { class: "h-score " + cls }, [sess.score ? String(sess.score) : "–"]),
          el("span", { class: "h-body" }, [
            el("strong", null, [labelize(sess.kind)]),
            el("span", { class: "muted" }, [` · ${sess.wordCount} words · ${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`]),
            sess.prompt ? el("div", { class: "muted small" }, [sess.prompt]) : null
          ])
        ]);
      }));
    }

    app.appendChild(el("section", { class: "view" }, [
      el("div", { class: "view-head" }, [
        el("h2", null, ["📈 Your progress"]),
        el("p", { class: "muted" }, ["Track your consistency and improvement over time. Practise a little every day to build your streak."])
      ]),
      el("div", { class: "card" }, [stats]),
      el("div", { class: "card" }, [
        el("div", { class: "row between" }, [
          el("h3", null, ["Recent sessions"]),
          s.sessions.length ? el("button", { class: "btn ghost danger", onclick: () => {
            if (confirm("Clear all saved progress? This can't be undone.")) { window.Store.reset(); renderProgress(); }
          } }, ["Reset"]) : null
        ]),
        history
      ])
    ]));
  }

  // ===================================================================
  //  ROUTER
  // ===================================================================
  const views = {
    speaking: renderSpeaking,
    vocab: renderVocab,
    conversation: renderConversation,
    progress: renderProgress
  };

  function go(view) {
    [...tabs.children].forEach(b => b.classList.toggle("active", b.dataset.view === view));
    (views[view] || renderSpeaking)();
    window.scrollTo({ top: 0 });
  }

  tabs.addEventListener("click", e => {
    const btn = e.target.closest(".tab");
    if (btn) go(btn.dataset.view);
  });

  go("speaking");
})();
