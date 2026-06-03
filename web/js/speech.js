/*
 * speech.js — Thin wrappers around the browser Web Speech API.
 *  - Recognition: speech-to-text (Chrome/Edge). Gracefully reports
 *    when unsupported so the UI can fall back to typing.
 *  - Speak: text-to-speech for hearing model phrases / pronunciation.
 */
(function () {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;

  function isRecognitionSupported() {
    return !!SR;
  }

  /*
   * Create a recogniser session.
   * callbacks: { onInterim(text), onFinal(text), onError(msg), onEnd() }
   * Returns { start, stop }.
   */
  function createRecognizer(callbacks) {
    if (!SR) return null;
    const rec = new SR();
    rec.lang = "en-US";
    rec.continuous = true;
    rec.interimResults = true;

    let finalText = "";
    let manualStop = false;

    rec.onresult = function (event) {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const chunk = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalText += chunk + " ";
        } else {
          interim += chunk;
        }
      }
      if (callbacks.onInterim) callbacks.onInterim((finalText + interim).trim());
    };

    rec.onerror = function (e) {
      if (callbacks.onError) callbacks.onError(e.error || "recognition error");
    };

    rec.onend = function () {
      // Auto-restart unless the user explicitly stopped, so longer
      // answers don't get cut off by the engine's idle timeout.
      if (!manualStop) {
        try { rec.start(); return; } catch (_) { /* fall through */ }
      }
      if (callbacks.onFinal) callbacks.onFinal(finalText.trim());
      if (callbacks.onEnd) callbacks.onEnd();
    };

    return {
      start() {
        finalText = "";
        manualStop = false;
        try { rec.start(); } catch (_) { /* already started */ }
      },
      stop() {
        manualStop = true;
        rec.stop();
      }
    };
  }

  // Speak text aloud (for hearing professional phrases).
  function speak(text) {
    if (!window.speechSynthesis) return false;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "en-US";
    u.rate = 0.95;
    window.speechSynthesis.speak(u);
    return true;
  }

  window.Speech = { isRecognitionSupported, createRecognizer, speak };
})();
