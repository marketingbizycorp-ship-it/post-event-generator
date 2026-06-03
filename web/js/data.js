/*
 * data.js — All practice content for the SpeakUp app.
 * Pure data, no logic. Loaded as a global `APP_DATA` object.
 */
window.APP_DATA = {

  /* ----------------------------------------------------------------
   * SPEAKING PRACTICE PROMPTS
   * Grouped by difficulty so learners can ramp up.
   * ---------------------------------------------------------------- */
  speakingPrompts: {
    warmup: [
      "Describe your morning routine in detail.",
      "Talk about your favourite meal and how it's made.",
      "Describe the place where you grew up.",
      "Explain how to get from your home to your workplace.",
      "Talk about a hobby you enjoy and why you like it."
    ],
    professional: [
      "Introduce yourself as you would at the start of a job interview (60 seconds).",
      "Give a one-minute update on a project you are currently working on.",
      "Explain your job to someone outside your industry.",
      "Pitch an idea for improving your team's productivity.",
      "Describe a professional achievement you are proud of and why it mattered.",
      "Walk through how you would onboard a new team member.",
      "Summarise the key points of a meeting for someone who missed it."
    ],
    opinion: [
      "Should companies allow fully remote work? Argue your position.",
      "Is it better to be a specialist or a generalist in your career?",
      "What makes a great leader? Explain with examples.",
      "Should AI tools be used in education? Give your view.",
      "What is the most important soft skill in the workplace, and why?"
    ],
    storytelling: [
      "Tell a story about a time you solved a difficult problem at work.",
      "Describe a moment you received tough feedback and what you did with it.",
      "Talk about a time you had to persuade someone to change their mind.",
      "Describe a mistake you made and what you learned from it.",
      "Tell us about a time you worked under pressure to hit a deadline."
    ]
  },

  /* ----------------------------------------------------------------
   * FILLER WORDS / CRUTCH PHRASES the analyser listens for.
   * Order matters: multi-word phrases are matched before single words.
   * ---------------------------------------------------------------- */
  fillerWords: [
    "you know", "i mean", "kind of", "sort of", "you see",
    "i guess", "or something", "and stuff", "and so on",
    "um", "uh", "uhm", "erm", "ah", "er", "hmm",
    "like", "basically", "actually", "literally", "honestly",
    "just", "really", "very", "so", "well", "right", "okay", "ok"
  ],

  /* ----------------------------------------------------------------
   * WEAK -> STRONG word/phrase suggestions for professional speech.
   * ---------------------------------------------------------------- */
  weakWords: {
    "good": ["effective", "excellent", "strong", "valuable"],
    "bad": ["ineffective", "poor", "problematic", "suboptimal"],
    "big": ["significant", "substantial", "considerable", "major"],
    "small": ["minor", "modest", "limited"],
    "thing": ["aspect", "element", "factor", "component"],
    "stuff": ["material", "content", "details", "items"],
    "a lot": ["considerably", "substantially", "a great deal"],
    "get": ["obtain", "receive", "achieve", "secure"],
    "got": ["received", "obtained", "secured"],
    "make sure": ["ensure", "confirm", "guarantee"],
    "find out": ["determine", "discover", "establish"],
    "go up": ["increase", "rise", "grow"],
    "go down": ["decrease", "decline", "fall"],
    "deal with": ["address", "handle", "manage", "resolve"],
    "show": ["demonstrate", "illustrate", "highlight"],
    "help": ["support", "assist", "enable", "facilitate"],
    "use": ["leverage", "utilise", "employ"],
    "start": ["initiate", "launch", "commence"],
    "end": ["conclude", "finalise", "complete"],
    "fix": ["resolve", "rectify", "address"],
    "talk about": ["discuss", "address", "cover"]
  },

  /* ----------------------------------------------------------------
   * VOCABULARY & PHRASING DECKS
   * Each card: casual (what you might say) -> professional alternative,
   * with meaning + example for context. Used for flashcards & quiz.
   * ---------------------------------------------------------------- */
  vocabDecks: {
    "Meetings": [
      { casual: "Let's start.", pro: "Let's get the meeting underway.", meaning: "A polished way to open a meeting.", example: "Now that everyone's here, let's get the meeting underway." },
      { casual: "What do you think?", pro: "I'd value your perspective on this.", meaning: "Invite someone's opinion respectfully.", example: "Before we decide, I'd value your perspective on this." },
      { casual: "I don't agree.", pro: "I see it a little differently.", meaning: "Disagree without sounding confrontational.", example: "I see it a little differently — could I explain my reasoning?" },
      { casual: "Can you say that again?", pro: "Could you elaborate on that point?", meaning: "Ask someone to expand or repeat.", example: "Could you elaborate on that point so I'm clear?" },
      { casual: "Let's stop here.", pro: "Let's wrap up and capture the action items.", meaning: "Close a meeting professionally.", example: "We're at time, so let's wrap up and capture the action items." },
      { casual: "That's not my job.", pro: "That sits a little outside my remit, but I can point you to the right person.", meaning: "Decline ownership politely.", example: "That sits outside my remit, but I'm happy to connect you with the right person." }
    ],
    "Email & Writing": [
      { casual: "Sorry for the late reply.", pro: "Thank you for your patience while I looked into this.", meaning: "Reframe an apology positively.", example: "Thank you for your patience while I looked into this." },
      { casual: "Just checking in.", pro: "I wanted to follow up on my previous note.", meaning: "Polite follow-up phrasing.", example: "I wanted to follow up on my previous note regarding the proposal." },
      { casual: "Get back to me.", pro: "I'd appreciate your thoughts when you have a moment.", meaning: "Request a reply without pressure.", example: "I'd appreciate your thoughts when you have a moment." },
      { casual: "Let me know if you have questions.", pro: "Please don't hesitate to reach out with any questions.", meaning: "Standard closing line.", example: "Please don't hesitate to reach out with any questions." },
      { casual: "ASAP", pro: "at your earliest convenience", meaning: "Soften an urgent request.", example: "Could you review this at your earliest convenience?" }
    ],
    "Negotiation": [
      { casual: "No.", pro: "That won't work for us, but here's what we can offer.", meaning: "Reject while keeping the door open.", example: "That won't work for us, but here's what we can offer instead." },
      { casual: "That's too expensive.", pro: "Help me understand the value behind this price.", meaning: "Question cost without attacking.", example: "Before we go further, help me understand the value behind this price." },
      { casual: "Take it or leave it.", pro: "This is the strongest offer we can make at this stage.", meaning: "State a firm position professionally.", example: "This is the strongest offer we can make at this stage." },
      { casual: "I want more.", pro: "For us to move forward, we'd need to see X.", meaning: "Ask for more with a condition.", example: "For us to move forward, we'd need to see a longer warranty." },
      { casual: "Let's split it.", pro: "Could we find a middle ground that works for both sides?", meaning: "Propose a compromise.", example: "Could we find a middle ground that works for both sides?" }
    ],
    "Giving Feedback": [
      { casual: "You did this wrong.", pro: "I noticed something we could approach differently next time.", meaning: "Open feedback without blame.", example: "I noticed something we could approach differently next time." },
      { casual: "Good job.", pro: "The way you handled the client call really stood out.", meaning: "Specific praise lands harder.", example: "The way you handled the client call really stood out to me." },
      { casual: "You always do this.", pro: "I've seen this come up a couple of times — can we talk about it?", meaning: "Avoid absolutes when criticising.", example: "I've seen this come up a couple of times — can we talk about it?" },
      { casual: "Do it like this.", pro: "One approach that's worked for me is...", meaning: "Offer guidance, not orders.", example: "One approach that's worked for me is to draft the outline first." }
    ],
    "Presentations": [
      { casual: "Today I'll talk about...", pro: "By the end of this session, you'll be able to...", meaning: "Open with the audience's benefit.", example: "By the end of this session, you'll be able to run the report yourself." },
      { casual: "Next slide.", pro: "That brings us to our next point...", meaning: "Smooth verbal transition.", example: "That brings us to our next point: the budget." },
      { casual: "Um, that's it.", pro: "To summarise the three key takeaways...", meaning: "Close with a recap.", example: "To summarise the three key takeaways before we open for questions..." },
      { casual: "Any questions?", pro: "I'd be glad to take your questions now.", meaning: "Invite Q&A confidently.", example: "I'd be glad to take your questions now." }
    ],
    "Small Talk": [
      { casual: "How are you?", pro: "How has your week been treating you?", meaning: "A warmer, more open opener.", example: "Good to see you — how has your week been treating you?" },
      { casual: "Nice weather.", pro: "Have you managed to get out and enjoy this weather?", meaning: "Turn a cliché into a real question.", example: "Have you managed to get out and enjoy this weather?" },
      { casual: "What do you do?", pro: "What's keeping you busy these days?", meaning: "Less interview-like opener.", example: "So, what's keeping you busy these days?" },
      { casual: "I have to go.", pro: "It's been great chatting — I should let you get on.", meaning: "Exit a conversation gracefully.", example: "It's been great chatting — I should let you get on. Let's catch up soon." }
    ]
  },

  /* ----------------------------------------------------------------
   * CONVERSATION / SOFT-SKILL ROLE-PLAY SCENARIOS
   * Each: title, situation, your role, the prompt to respond to,
   * useful phrases, and what good responses tend to include.
   * ---------------------------------------------------------------- */
  scenarios: [
    {
      id: "feedback-peer",
      category: "Giving Feedback",
      title: "Giving a colleague constructive feedback",
      situation: "A teammate, Alex, submitted a report with several errors that delayed the project.",
      role: "You are Alex's peer. You want to raise the issue without damaging the relationship.",
      prompt: "Alex says: \"Hey, did you get a chance to look at my report? I think it turned out pretty well!\" — How do you respond?",
      phrases: [
        "I appreciate the effort you put into this.",
        "I did spot a few things I'd love to talk through.",
        "Can we look at these together so the next one goes smoothly?"
      ],
      goodAnswerIncludes: ["acknowledge effort", "be specific", "stay collaborative", "offer to help"]
    },
    {
      id: "smalltalk-networking",
      category: "Small Talk",
      title: "Networking at a professional event",
      situation: "You're at an industry conference and standing near someone you don't know during a coffee break.",
      role: "You want to start a friendly, professional conversation.",
      prompt: "You make eye contact with a stranger holding a coffee. Break the ice and keep the conversation going.",
      phrases: [
        "This is my first time at this conference — how about you?",
        "What brought you to this session?",
        "I'd love to hear what you're working on."
      ],
      goodAnswerIncludes: ["open-ended question", "share something about yourself", "show genuine interest"]
    },
    {
      id: "disagree-manager",
      category: "Speaking Up",
      title: "Disagreeing with your manager respectfully",
      situation: "Your manager proposes a deadline you believe is unrealistic.",
      role: "You want to push back without seeming difficult.",
      prompt: "Your manager says: \"Let's ship this by Friday.\" You think that's too soon. What do you say?",
      phrases: [
        "I want this to succeed, so I'd like to flag a concern about timing.",
        "To hit Friday, we'd need to drop X — is that the right trade-off?",
        "Could we aim for Monday to keep the quality high?"
      ],
      goodAnswerIncludes: ["align on the shared goal", "give a concrete reason", "propose an alternative"]
    },
    {
      id: "negotiation-raise",
      category: "Negotiation",
      title: "Asking for a raise",
      situation: "You've taken on more responsibility over the past year and want a salary increase.",
      role: "You're meeting your manager to make the case.",
      prompt: "Your manager asks: \"So, what did you want to discuss?\" Make your opening case for a raise.",
      phrases: [
        "Over the past year I've taken on X and delivered Y.",
        "Based on my contributions and market rates, I'd like to discuss my compensation.",
        "What would it take to get there?"
      ],
      goodAnswerIncludes: ["state the ask clearly", "back it with specifics", "stay calm and positive"]
    },
    {
      id: "conflict-deescalate",
      category: "Conflict",
      title: "Calming an upset client",
      situation: "A client is frustrated because a delivery was late.",
      role: "You represent your company and want to rebuild trust.",
      prompt: "The client says: \"This is the second time you've let us down. I'm not happy.\" How do you respond?",
      phrases: [
        "You're right to be frustrated, and I'm sorry this happened again.",
        "Here's exactly what went wrong and what we're doing about it.",
        "Let me make sure this doesn't happen a third time."
      ],
      goodAnswerIncludes: ["acknowledge the feeling", "take responsibility", "offer a concrete next step"]
    },
    {
      id: "intro-interview",
      category: "Interviews",
      title: "The \"Tell me about yourself\" question",
      situation: "You're in a job interview and have just been asked the classic opener.",
      role: "You want a crisp, confident 60-second answer.",
      prompt: "The interviewer says: \"So, tell me about yourself.\" Give your answer.",
      phrases: [
        "I'm a [role] with X years in [field].",
        "Most recently, I [key achievement].",
        "I'm drawn to this role because..."
      ],
      goodAnswerIncludes: ["present (who you are now)", "past (relevant experience)", "future (why this role)"]
    }
  ]
};
