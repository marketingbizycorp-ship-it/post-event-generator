# 🎙️ SpeakUp — Soft Skills & Professional Speaking Trainer

A self-contained web app for practising **professional English speaking** and
**workplace soft skills**. It runs entirely in your browser — your microphone
audio and transcripts never leave your device, and **no API key or internet
connection is required**.

## What it does

| Tab | What you practise |
| --- | --- |
| 🎤 **Speaking** | Pick a prompt (warm-up, professional, opinion, storytelling), speak for 30–90 seconds, and get instant feedback. |
| 📚 **Vocabulary** | Learn to swap casual phrases for polished, professional ones across 6 topics. Flashcards + a self-test quiz. |
| 🗣️ **Conversation** | Role-play real workplace moments — giving feedback, negotiation, calming an upset client, small talk, asking for a raise. |
| 📈 **Progress** | A day streak, average score, words spoken and session history — all saved locally. |

## The feedback (100% rule-based, no AI)

After you speak, the app analyses your words and reports:

- **Score /100** — an overall delivery score.
- **Filler words** — counts and lists "um", "uh", "like", "you know", "basically", etc.
- **Pace** — words-per-minute, flagged if too fast (>180) or too slow (<100).
- **Vocabulary variety** — how many distinct words you used.
- **Stronger word choices** — spots vague words ("good", "thing", "deal with") and suggests sharper alternatives.
- **Repetition** and **sentence length** warnings.
- **What worked** ✅ and **To improve** 💡 lists.

## Running it

It's a static site — any static file server works. From the repo root:

```bash
cd web
python3 -m http.server 8000
```

Then open **http://localhost:8000** in your browser.

> **Tip:** Use **Chrome or Edge** for live speech-to-text (via the Web Speech
> API). In any other browser, the app falls back to a text box where you type
> what you'd say — you still get the full analysis. The microphone needs a
> secure context, which `localhost` provides.

## Project layout

```
web/
├── index.html         # app shell + tab navigation
├── styles.css         # all styling
└── js/
    ├── data.js         # prompts, vocab decks, scenarios, filler/weak-word lists
    ├── analyzer.js     # rule-based speech analysis + scoring
    ├── speech.js       # Web Speech API wrappers (recognition + text-to-speech)
    ├── storage.js      # localStorage progress tracking (streaks, history)
    └── app.js          # UI controller for all four views
```

## Customising

- **Add speaking prompts** → edit `speakingPrompts` in `js/data.js`.
- **Add vocabulary** → add cards to `vocabDecks` in `js/data.js`.
- **Add role-play scenarios** → add entries to `scenarios` in `js/data.js`.
- **Tune the scoring/filler lists** → edit `fillerWords` / `weakWords` in `js/data.js` and the rules in `js/analyzer.js`.
