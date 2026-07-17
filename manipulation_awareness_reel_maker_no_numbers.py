#!/usr/bin/env python3
"""Manipulation-awareness Reel Maker — renders a heading and unnumbered awareness slides."""
import json
import os
import subprocess
import time
import sys
from pathlib import Path


def _ensure_packages(*packages):
    import importlib.util
    missing = [p for p in packages if not importlib.util.find_spec(p)]
    if missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", *missing])

_ensure_packages("PIL", "requests")
import requests


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment setting: {name}")
    return value


FB_ACCESS_TOKEN = require_env("FB_ACCESS_TOKEN")
FB_PAGE_ID = require_env("FB_PAGE_ID")
# Resolve music relative to this script, not whichever folder starts the workflow.
# This prevents a working-directory change from silently removing the background track.
MUSIC_DIR = Path(__file__).resolve().parent / "assets/music"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_VIDEO = OUTPUT_DIR / "reel.mp4"
PROGRESS_FILE = Path("darkmanipulator_progress.json")
TARGET_W, TARGET_H = 1080, 1920
HEADING_SECONDS = 4.0  # Relative display weight for the heading.
SLIDE_SECONDS = 3.0    # Relative display weight for each benefit.
# 0 = invisible; 255 = solid yellow. 150 shows the video through the box.
YELLOW_BOX_ALPHA = 150

# Add new topics ONLY at the bottom. Each topic is: heading first, then benefits.
# 50 original, education-first manipulation-awareness Reel posts.
# Each entry is shown as a heading followed by unnumbered slides.
POSTS = [{'heading': "⚠️ WARNING — YOU'RE BEING MANIPULATED: GUILT-TRIPPING",
  'benefits': ['It uses guilt to pressure a decision.',
               'It may sound like: ‘After all I did for you.’',
               'Care does not erase your right to say no.',
               'Try: ‘I hear you. My answer is still no.’'],
  'caption': 'Guilt-Tripping: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 STOP — THEY'RE ALREADY DOING THIS TO YOU: GASLIGHTING",
  'benefits': ['It repeatedly challenges your memory or feelings.',
               'One disagreement is not automatically gaslighting.',
               'Look for a pattern of denial and confusion.',
               'Keep notes and speak with someone you trust.'],
  'caption': 'Gaslighting: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "‼️ RED FLAG: DO NOT IGNORE THIS ANY LONGER: LOVE-BOMBING",
  'benefits': ['It can feel like intense affection very fast.',
               'The concern is when warmth becomes pressure or control.',
               'Healthy interest respects your pace.',
               'Slow down and watch for consistency.'],
  'caption': 'Love-Bombing: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ IF THIS FEELS FAMILIAR, YOU'RE IN DANGER: SILENT TREATMENT",
  'benefits': ['Space can be healthy when it is communicated.',
               'Silent treatment uses withdrawal as punishment.',
               'It leaves you anxious and chasing answers.',
               'Ask for a clear time to talk again.'],
  'caption': 'Silent Treatment: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 WAKE UP — THIS IS HAPPENING RIGHT NOW: BLAME SHIFTING",
  'benefits': ['The focus moves from their action to your reaction.',
               'You raise a concern, then end up apologizing.',
               'Both people can own their part.',
               'Return to the original issue calmly.'],
  'caption': 'Blame Shifting: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "‼️ BEFORE IT'S TOO LATE — READ THIS: MOVING GOALPOSTS",
  'benefits': ['You meet the request, then the rule changes.',
               'Nothing you do ever seems enough.',
               'This can keep you working for approval.',
               'Ask for clear expectations upfront.'],
  'caption': 'Moving Goalposts: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ THEY ARE HIDING THIS FROM YOU: FALSE URGENCY",
  'benefits': ['Pressure says: decide right now.',
               'Respect gives you time to think.',
               'Urgency can hide a weak argument.',
               'Pause before big choices when you can.'],
  'caption': 'False Urgency: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 YOU ARE NOT CRAZY — THIS IS REAL: BOUNDARY TESTING",
  'benefits': ['Small disrespect can test what you will tolerate.',
               'It may start as a joke or tiny favor.',
               'Your discomfort is useful information.',
               'State the boundary early and clearly.'],
  'caption': 'Boundary Testing: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ WARNING — YOU'RE BEING MANIPULATED: TRIANGULATION",
  'benefits': ['A third person gets pulled into your conflict.',
               'It can create jealousy, comparison, or pressure.',
               'Direct conversation reduces the drama.',
               'Do not compete for basic respect.'],
  'caption': 'Triangulation: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 STOP — THEY'RE ALREADY DOING THIS TO YOU: ISOLATION",
  'benefits': ['Control can make outside support feel unsafe.',
               'They may criticize every friend or family member.',
               'Healthy relationships make room for your people.',
               'Stay connected to trusted support.'],
  'caption': 'Isolation: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "‼️ RED FLAG: DO NOT IGNORE THIS ANY LONGER: FUTURE FAKING",
  'benefits': ['Big future promises can create fast attachment.',
               'Words matter less than steady actions.',
               'Plans should not be used as a leash.',
               'Check whether behavior matches the promise.'],
  'caption': 'Future Faking: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ IF THIS FEELS FAMILIAR, YOU'RE IN DANGER: PLAYING THE VICTIM",
  'benefits': ['Pain deserves compassion, but it is not a free pass.',
               'The story may erase the harm they caused.',
               'Empathy and accountability can exist together.',
               'Do not let guilt replace the facts.'],
  'caption': 'Playing the Victim: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 WAKE UP — THIS IS HAPPENING RIGHT NOW: DARVO PATTERN",
  'benefits': ['It can mean deny, attack, then reverse victim and offender.',
               'A concern becomes an attack on your character.',
               'The original issue disappears.',
               'Write down what happened before the talk shifts.'],
  'caption': 'DARVO Pattern: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "‼️ BEFORE IT'S TOO LATE — READ THIS: WITHHOLDING AFFECTION",
  'benefits': ['Affection should not be a reward for obedience.',
               'A healthy partner can need space respectfully.',
               'Control uses warmth and coldness to train behavior.',
               'Name the pattern, not just the mood.'],
  'caption': 'Withholding Affection: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ THEY ARE HIDING THIS FROM YOU: PASSIVE-AGGRESSIVE PRESSURE",
  'benefits': ['The message is hidden behind sarcasm or sighs.',
               'It makes you guess instead of discuss.',
               'Clear needs create healthier conflict.',
               'Ask: ‘What do you need directly?’'],
  'caption': 'Passive-Aggressive Pressure: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 YOU ARE NOT CRAZY — THIS IS REAL: NEGGING",
  'benefits': ['A backhanded compliment can chip away at confidence.',
               'It may be framed as teasing or honesty.',
               'Respect does not need to make you smaller.',
               'Say: ‘That comment does not work for me.’'],
  'caption': 'Negging: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ WARNING — YOU'RE BEING MANIPULATED: INTERMITTENT REINFORCEMENT",
  'benefits': ['Kindness and coldness alternate without warning.',
               'The unpredictability can make you chase the good moments.',
               'Consistency is more valuable than intensity.',
               'Judge the pattern, not the rare high point.'],
  'caption': 'Intermittent Reinforcement: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 STOP — THEY'RE ALREADY DOING THIS TO YOU: INFORMATION OVERLOAD",
  'benefits': ['Too many claims can make a simple issue feel confusing.',
               'Confusion can stop you from asking questions.',
               'You do not need to solve everything at once.',
               'Ask for one clear point at a time.'],
  'caption': 'Information Overload: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "‼️ RED FLAG: DO NOT IGNORE THIS ANY LONGER: SELECTIVE MEMORY",
  'benefits': ['They remember your mistakes but forget their promises.',
               'This can create an unfair story about you.',
               'Everyone makes mistakes; standards should be mutual.',
               'Use specific examples and dates if needed.'],
  'caption': 'Selective Memory: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ IF THIS FEELS FAMILIAR, YOU'RE IN DANGER: DOUBLE STANDARDS",
  'benefits': ['Rules apply to you but not to them.',
               'They demand privacy but inspect your phone.',
               'Fairness needs the same rule for both people.',
               'Ask whether the expectation is mutual.'],
  'caption': 'Double Standards: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 WAKE UP — THIS IS HAPPENING RIGHT NOW: JEALOUSY AS PROOF",
  'benefits': ['Jealousy is a feeling, not proof of love.',
               'Control can be disguised as protection.',
               'Trust allows friendships, privacy, and choices.',
               'Love should not require isolation.'],
  'caption': 'Jealousy as Proof: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "‼️ BEFORE IT'S TOO LATE — READ THIS: WEAPONIZED INSECURITY",
  'benefits': ['A private fear gets used to win an argument.',
               'This can make you feel exposed and small.',
               'Vulnerability needs care, not ammunition.',
               'Limit what you share with unsafe people.'],
  'caption': 'Weaponized Insecurity: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ THEY ARE HIDING THIS FROM YOU: SHAMING",
  'benefits': ['Shame attacks who you are, not what happened.',
               'It sounds like: ‘You are selfish.’',
               'Healthy feedback names a behavior and a need.',
               'You can reject insults and discuss facts.'],
  'caption': 'Shaming: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 YOU ARE NOT CRAZY — THIS IS REAL: THREATS AND ULTIMATUMS",
  'benefits': ['A boundary explains what you will do to protect yourself.',
               'A threat tries to force another person’s choice.',
               'Not every ultimatum is abusive; context matters.',
               'Notice whether there is room for respectful choice.'],
  'caption': 'Threats and Ultimatums: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ WARNING — YOU'RE BEING MANIPULATED: MONITORING",
  'benefits': ['Checking your location or messages can be framed as care.',
               'Consent and privacy still matter in relationships.',
               'Safety plans are different from constant surveillance.',
               'Talk about digital boundaries clearly.'],
  'caption': 'Monitoring: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 STOP — THEY'RE ALREADY DOING THIS TO YOU: FINANCIAL CONTROL",
  'benefits': ['Money can be used to limit someone’s choices.',
               'It may include hiding accounts or blocking work.',
               'Shared finances need transparency and agreement.',
               'Keep access to important records when possible.'],
  'caption': 'Financial Control: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "‼️ RED FLAG: DO NOT IGNORE THIS ANY LONGER: PUBLIC HUMILIATION",
  'benefits': ['Embarrassing you can create fear of speaking up.',
               'It may be called a joke after you react.',
               'A joke is not funny if it repeatedly hurts.',
               'Address it privately or step away.'],
  'caption': 'Public Humiliation: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ IF THIS FEELS FAMILIAR, YOU'RE IN DANGER: STONEWALLING",
  'benefits': ['Stonewalling shuts down every attempt to resolve conflict.',
               'A pause is healthy when there is a return time.',
               'Permanent shutdown leaves one person carrying the issue.',
               'Agree on when the conversation resumes.'],
  'caption': 'Stonewalling: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 WAKE UP — THIS IS HAPPENING RIGHT NOW: THREATENING TO LEAVE",
  'benefits': ['Breakup threats can be used to control small choices.',
               'They create fear instead of problem-solving.',
               'Real relationship concerns deserve a calm talk.',
               'Do not bargain away your boundaries to stop panic.'],
  'caption': 'Threatening to Leave: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "‼️ BEFORE IT'S TOO LATE — READ THIS: SCOREKEEPING",
  'benefits': ['Past favors become weapons in every argument.',
               'Support becomes a debt you can never repay.',
               'Healthy care is not a running invoice.',
               'Discuss the current problem on its own.'],
  'caption': 'Scorekeeping: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ THEY ARE HIDING THIS FROM YOU: MINIMIZING",
  'benefits': ['It sounds like: ‘You are too sensitive.’',
               'It shrinks the impact instead of hearing it.',
               'Feelings are data, even when views differ.',
               'Ask for the behavior to be addressed.'],
  'caption': 'Minimizing: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 YOU ARE NOT CRAZY — THIS IS REAL: DISMISSIVE HUMOR",
  'benefits': ['Serious concerns get turned into a joke.',
               'Humor can dodge accountability.',
               'You are allowed to bring a topic back.',
               'Say: ‘I am serious. Please answer me.’'],
  'caption': 'Dismissive Humor: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ WARNING — YOU'RE BEING MANIPULATED: FORCED CONFESSIONS",
  'benefits': ['Pressure for constant proof can become control.',
               'You do not have to reveal every private thought.',
               'Trust grows from voluntary honesty, not interrogation.',
               'Pause a conversation that becomes coercive.'],
  'caption': 'Forced Confessions: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 STOP — THEY'RE ALREADY DOING THIS TO YOU: COMPARISON",
  'benefits': ['Comparing you to others can trigger insecurity.',
               'It may push you to earn basic kindness.',
               'Healthy feedback does not use people as weapons.',
               'Ask for a direct request instead.'],
  'caption': 'Comparison: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "‼️ RED FLAG: DO NOT IGNORE THIS ANY LONGER: CONDITIONAL RESPECT",
  'benefits': ['Respect should not depend on perfect obedience.',
               'Disagreement is normal in close relationships.',
               'Control treats independence as betrayal.',
               'Keep your values visible when pressure rises.'],
  'caption': 'Conditional Respect: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ IF THIS FEELS FAMILIAR, YOU'RE IN DANGER: REWRITING HISTORY",
  'benefits': ['Past events get changed to fit their current story.',
               'You may leave talks doubting clear facts.',
               'Memory is imperfect, but patterns still matter.',
               'Save messages or write a private timeline.'],
  'caption': 'Rewriting History: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 WAKE UP — THIS IS HAPPENING RIGHT NOW: USING SECRETS",
  'benefits': ['A secret can be used to scare you into silence.',
               'That turns trust into leverage.',
               'You deserve support without blackmail.',
               'Tell a trusted person if safety is at risk.'],
  'caption': 'Using Secrets: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "‼️ BEFORE IT'S TOO LATE — READ THIS: WEAPONIZED HELPLESSNESS",
  'benefits': ['Someone acts unable so you carry all the work.',
               'A one-time need is different from a repeated pattern.',
               'Shared responsibility needs real effort.',
               'Name tasks and agreements clearly.'],
  'caption': 'Weaponized Helplessness: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ THEY ARE HIDING THIS FROM YOU: OVEREXPLAINING PRESSURE",
  'benefits': ['You may be pushed to justify every no.',
               'More explanation can invite more debate.',
               'A short boundary is still a boundary.',
               'Try: ‘I am not available for that.’'],
  'caption': 'Overexplaining Pressure: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 YOU ARE NOT CRAZY — THIS IS REAL: BAITING",
  'benefits': ['A person provokes you, then focuses on your reaction.',
               'The goal may be to make you look unreasonable.',
               'Pause before replying when emotions spike.',
               'Keep responses short and factual.'],
  'caption': 'Baiting: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ WARNING — YOU'RE BEING MANIPULATED: SMEAR CAMPAIGNS",
  'benefits': ['Someone may tell others a distorted story about you.',
               'It can isolate you before you can speak.',
               'You do not need to fight every rumor.',
               'Share facts with trusted people, not the whole crowd.'],
  'caption': 'Smear Campaigns: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 STOP — THEY'RE ALREADY DOING THIS TO YOU: CONTROL DISGUISED AS ADVICE",
  'benefits': ['Advice becomes a problem when no is not accepted.',
               'Care offers options; control demands obedience.',
               'Your decisions can be different from theirs.',
               'Thank them, then choose for yourself.'],
  'caption': 'Control Disguised as Advice: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "‼️ RED FLAG: DO NOT IGNORE THIS ANY LONGER: TESTING LOYALTY",
  'benefits': ['Unreasonable demands can be framed as proof of love.',
               'Love is not a test you must keep passing.',
               'Healthy loyalty includes respect for your limits.',
               'Do not trade safety for approval.'],
  'caption': 'Testing Loyalty: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ IF THIS FEELS FAMILIAR, YOU'RE IN DANGER: CONFUSING MIXED MESSAGES",
  'benefits': ['Warm words and harmful actions can coexist.',
               'Mixed signals keep you searching for clarity.',
               'Look at repeated behavior, not only apologies.',
               'Ask what will change and watch what happens.'],
  'caption': 'Confusing Mixed Messages: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 WAKE UP — THIS IS HAPPENING RIGHT NOW: PRESSURE THROUGH FEAR",
  'benefits': ['Fear can make a bad choice feel like the only choice.',
               'Threats, anger, and panic reduce clear thinking.',
               'Create distance before deciding if you can.',
               'Reach out for help if you feel unsafe.'],
  'caption': 'Pressure Through Fear: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "‼️ BEFORE IT'S TOO LATE — READ THIS: PRESSURE THROUGH OBLIGATION",
  'benefits': ['A favor can be used to demand more than you agreed to.',
               'Gratitude does not erase consent.',
               'You can appreciate help and still have limits.',
               'Say what you can offer, not what they demand.'],
  'caption': 'Pressure Through Obligation: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ THEY ARE HIDING THIS FROM YOU: PRESSURE THROUGH FLATTERY",
  'benefits': ['Praise can be used to make refusal feel selfish.',
               'It may sound like: ‘You are the only one who can.’',
               'A compliment is not a contract.',
               'Decide based on capacity, not praise.'],
  'caption': 'Pressure Through Flattery: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 YOU ARE NOT CRAZY — THIS IS REAL: HEALTHY CONFLICT CHECK",
  'benefits': ['Healthy conflict allows both people to speak.',
               'It uses specific behavior, not insults.',
               'It makes room for pauses and repair.',
               'Respect remains even during disagreement.'],
  'caption': 'Healthy Conflict Check: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "⚠️ WARNING — YOU'RE BEING MANIPULATED: TRUST YOUR PATTERN NOTES",
  'benefits': ['One moment rarely tells the whole story.',
               'Repeated fear, guilt, or confusion deserves attention.',
               'Write down behavior, dates, and how you felt.',
               'Support helps you see the pattern clearly.'],
  'caption': 'Trust Your Pattern Notes: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "🚨 STOP — THEY'RE ALREADY DOING THIS TO YOU: WHEN TO GET SUPPORT",
  'benefits': ['Talk to someone trusted when control feels normal.',
               'Reach out sooner if you feel afraid or isolated.',
               'Support is not overreacting.',
               'If you are in immediate danger, contact local emergency help.'],
  'caption': 'When to Get Support: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'}
]

# 300 additional original, education-first manipulation-awareness Reel posts.
# These describe warning signs and protective responses only; they do not teach
# viewers how to control, pressure, or exploit someone.
AWARENESS_TOPICS = [
    ("foot-in-the-door pressure", "A tiny yes is treated like permission for a much bigger ask.", "Consent to one thing is not consent to the next.", "Try: 'I agreed to the first part, not this.'"),
    ("door-in-the-face pressure", "A huge request is followed by a smaller one that suddenly feels reasonable.", "Relief can make a request feel fair when it still is not right for you.", "Choose based on your capacity, not the comparison."),
    ("lowballing", "The terms get worse only after you have invested time, hope, or money.", "An agreement can be reconsidered when the conditions change.", "Ask for the full terms in writing before continuing."),
    ("sunk-cost pressure", "You hear, 'But you have come this far,' when you want to leave.", "Past effort is not a reason to accept future harm.", "Ask what you would choose if starting today."),
    ("scarcity pressure", "Something is called rare or almost gone before you can think clearly.", "Limited supply does not remove your right to pause.", "Step back and verify the claim independently."),
    ("social-proof pressure", "You are told everybody agrees, buys, or puts up with it.", "A crowd can be wrong, and private discomfort still matters.", "Ask for evidence, not a head count."),
    ("authority pressure", "A title or confident voice is used to shut down your questions.", "Expertise deserves respect, not blind obedience.", "Ask what supports the recommendation."),
    ("reciprocity pressure", "A gift or favor quietly turns into an obligation.", "Kindness is not a contract for access or compliance.", "Say thanks without promising more than you want."),
    ("fear-based messaging", "A scary outcome is presented as certain unless you obey.", "Fear narrows thinking and makes weak claims feel urgent.", "Pause, breathe, and check the actual risk."),
    ("false dilemma", "You are told there are only two choices when there may be more.", "Pressure often hides alternatives.", "Ask: 'What other options are we leaving out?'"),
    ("loaded questions", "Any answer seems to make you admit something unfair.", "A question can contain an accusation instead of seeking truth.", "Correct the premise before answering."),
    ("leading questions", "The wording pushes you toward the answer they want.", "A fair question leaves room for your real view.", "Restate the question in neutral words."),
    ("gish gallop", "So many claims arrive at once that you cannot examine any of them.", "Speed is not evidence.", "Choose one claim and ask for support."),
    ("whataboutism", "Your concern gets replaced with a different accusation about you.", "Two issues can exist without one erasing the other.", "Return gently to the original topic."),
    ("straw-man framing", "Your actual point gets replaced with an extreme version.", "You deserve to be responded to accurately.", "Say: 'That is not what I said. My point is...'"),
    ("appeal to pity", "Their hardship is used to avoid responsibility for hurting you.", "Compassion and accountability can stand together.", "Acknowledge the pain, then name the behavior."),
    ("moral licensing", "One good act is used to excuse a repeated harmful act.", "Being kind sometimes does not cancel a pattern.", "Look at the full behavior, not one highlight."),
    ("trauma dumping for leverage", "A painful story appears only when you set a limit.", "Someone's pain matters, but your boundary still matters too.", "Offer care without abandoning your limit."),
    ("manufactured crisis", "Every request becomes an emergency that only you can solve.", "Constant crisis can train you to ignore your own needs.", "Check whether the urgency is real and shared."),
    ("time pressure", "You are denied time to read, compare, or ask someone you trust.", "Good decisions can usually survive a short pause.", "Use: 'I do not decide important things on the spot.'"),
    ("information withholding", "Key details arrive after you have already agreed.", "Informed consent needs the relevant facts first.", "Ask what has not been disclosed yet."),
    ("selective evidence", "Only facts that support one conclusion are repeated.", "A fair picture includes inconvenient facts too.", "Look for what is missing, not only what is shown."),
    ("cherry-picked statistics", "One number is used without context to make a claim feel final.", "Numbers need a source, comparison, and timeframe.", "Ask where the figure came from and what it leaves out."),
    ("fake consensus", "They claim others privately agree with them but name no one.", "Unnamed agreement is not proof.", "Speak directly with people instead of chasing rumors."),
    ("bandwagon shame", "Not joining in is framed as weird, selfish, or disloyal.", "Belonging should not require surrendering your judgment.", "Let your values choose, not the crowd's mood."),
    ("purity tests", "One imperfect choice is used to label you disloyal or bad.", "Healthy relationships allow complexity and growth.", "Reject labels and discuss the actual decision."),
    ("moving deadlines", "The deadline changes whenever you need time to think.", "Unstable deadlines can keep you anxious and compliant.", "Set your own decision time where possible."),
    ("bait-and-switch", "What was promised is not what appears after you commit.", "You are allowed to walk away from changed terms.", "Compare the offer to the original promise."),
    ("future pacing", "A vivid future is described to make you commit in the present.", "A beautiful story is not evidence of a safe pattern.", "Ground yourself in today's actions."),
    ("identity pressure", "They say a good friend, parent, worker, or partner would obey.", "Your identity is bigger than one person's demand.", "Define your own values before answering."),
    ("labeling", "A single mistake becomes a permanent name for who you are.", "Labels can silence learning and honest discussion.", "Ask for specific behavior instead of character attacks."),
    ("projection", "They accuse you of the behavior they keep showing.", "An accusation is not automatically a fact.", "Focus on observable actions and dates."),
    ("confession fishing", "They keep asking until you say something just to end the pressure.", "Relief is not the same as voluntary agreement.", "Take a break before answering loaded questions."),
    ("forced choice", "You are pushed to pick before you understand the consequences.", "A rushed choice may not be a free choice.", "Ask for time, details, and another option."),
    ("conditional apology", "You hear 'sorry you feel that way' instead of ownership.", "A repair names the action and its impact.", "Ask: 'What will change next time?'"),
    ("apology flooding", "Many apologies arrive, but the behavior never changes.", "Words of regret need follow-through.", "Watch the pattern after the apology."),
    ("premature forgiveness pressure", "You are urged to forgive before you feel heard or safe.", "Forgiveness cannot be demanded on a schedule.", "Take the time you need to decide what repair means."),
    ("forced positivity", "Your concern is called negative before anyone considers it.", "Hope is healthy; denial is not.", "Name the concern clearly and calmly."),
    ("toxic gratitude", "You are told to be grateful so you will stop naming harm.", "Gratitude and honest feedback can coexist.", "Appreciate what is real without denying what hurts."),
    ("emotional blackmail", "Love, approval, or safety is tied to doing what they want.", "Care should not be a weapon.", "Reach for support if refusal feels dangerous."),
    ("coercive texting", "Repeated calls or messages make silence feel impossible.", "Availability is not owed every minute.", "Mute, pause, and respond when you choose."),
    ("digital surveillance", "Passwords, locations, or private messages are demanded as proof.", "Trust is not built through constant access.", "Review your privacy settings and boundaries."),
    ("password pressure", "Sharing a password is framed as proof that you have nothing to hide.", "Privacy is normal, even in close relationships.", "Keep accounts secure and discuss trust directly."),
    ("location tracking pressure", "Being tracked is called love, safety, or loyalty.", "Safety planning requires consent, not control.", "Choose who can see your location and when."),
    ("public call-outs", "A private issue is exposed to make you comply from embarrassment.", "Public shame discourages honest repair.", "Step away and ask for a private conversation."),
    ("group pile-on", "Others are brought in to make one person feel outnumbered.", "More voices do not make pressure fair.", "Ask to discuss the issue one-to-one or with neutral support."),
    ("proxy fighting", "Someone sends friends or relatives to argue their case.", "Direct conflict needs direct communication.", "Avoid debating through messengers."),
    ("flying monkeys", "Third parties repeat pressure or rumors for someone else.", "You do not have to explain yourself to every messenger.", "Use one calm boundary and disengage."),
    ("hoovering", "Warm messages return just as you begin creating distance.", "A return is not proof that the old pattern is gone.", "Look for sustained change, not a sudden pull."),
    ("breadcrumbing", "Tiny bits of attention keep you waiting for more.", "Occasional contact can create hope without commitment.", "Decide what consistency you need."),
    ("orbiting", "They stay visible online while avoiding a real conversation.", "Online signals are not the same as care or clarity.", "Protect your attention and seek direct answers."),
    ("jealousy bait", "Another person is mentioned to make you compete for attention.", "Love does not require a contest.", "Refuse comparison and state what respect looks like."),
    ("triangulated praise", "Someone praises another person mainly to make you feel inadequate.", "Comparison can be a tool of control.", "Ask for a direct request without the comparison."),
    ("silent punishment", "Contact disappears after you express a need or limit.", "A respectful pause includes communication and return.", "Do not chase clarity at the cost of your boundary."),
    ("rage as leverage", "Anger becomes so big that everyone else must give in.", "Big emotion does not make a demand reasonable.", "Leave the conversation if you feel unsafe."),
    ("intimidating body language", "Size, closeness, blocking exits, or aggressive gestures change what feels safe.", "Fear changes whether a choice is freely made.", "Create space and seek immediate help if needed."),
    ("threatening self-harm for control", "A threat of self-harm appears when you try to leave or say no.", "Take threats seriously without becoming the only responder.", "Contact emergency or crisis support and tell a trusted person."),
    ("threatening exposure", "Private details are used to force silence or compliance.", "Blackmail is not care or conflict resolution.", "Save evidence and seek trusted or professional support."),
    ("reputation threats", "They warn that nobody will believe you or that they will ruin your name.", "Threats try to isolate you before you can get help.", "Document what happens and tell safe people."),
    ("legal-sounding intimidation", "Official words are used to scare you without clear facts.", "A confident claim is not legal advice.", "Check information with a qualified, independent source."),
    ("financial guilt", "Money spent on you is brought up to control your choices.", "Support should not create ownership over you.", "Separate appreciation from obligation."),
    ("financial secrecy", "Accounts, debts, or bills are hidden while you are asked to trust blindly.", "Shared financial decisions need clear information.", "Keep copies of records and ask direct questions."),
    ("career sabotage", "Your work, study, or goals are quietly undermined to make you dependent.", "Support should expand your options, not shrink them.", "Notice who benefits when your independence gets smaller."),
    ("sleep deprivation pressure", "A fight is kept going until you are too tired to think.", "Exhaustion makes consent and problem-solving harder.", "Pause the conversation and return after rest."),
    ("substance pressure", "Alcohol or drugs are pushed after you show hesitation.", "Impairment cannot create meaningful consent.", "Leave, call someone safe, or choose a clear no."),
    ("sexual coercion", "Affection, guilt, sulking, or persistence is used after a no.", "Consent must be free, informed, and ongoing.", "No explanation is required; get support if you need it."),
    ("normalizing disrespect", "Harmful behavior is called normal, traditional, or just how people are.", "Common does not mean healthy.", "Compare the behavior with your values and safety."),
    ("double-bind pressure", "Whatever you choose is treated as proof that you are wrong.", "No-win rules are designed to keep you off balance.", "Name the bind and step out of the argument."),
    ("learned helplessness pressure", "After repeated setbacks, you start believing you cannot choose differently.", "Small choices can rebuild confidence and options.", "Tell one safe person what has been happening."),
    ("dependency building", "Your outside support, skills, or resources slowly get reduced.", "Independence is protective, not disloyal.", "Keep contacts, documents, and practical options accessible."),
    ("approval addiction", "Praise arrives only when you ignore your own needs.", "You do not need to earn basic respect.", "Ask what you want before seeking approval."),
    ("selective accountability", "You must apologize in detail while they never repair anything.", "Accountability should not be one-sided.", "Ask for mutual ownership of specific actions."),
    ("weaponized therapy language", "Words like boundaries, triggers, or healing are used to dismiss you.", "Helpful language should create clarity, not silence.", "Ask for plain words and concrete behavior."),
    ("diagnosis as insult", "A mental-health label is thrown at you to end the discussion.", "Labels are not substitutes for listening.", "Return to the behavior and its impact."),
    ("revisionist apologies", "They apologize for a version of events that leaves out the harm.", "Repair starts with an accurate account.", "State what happened without debating every detail."),
]


def add_awareness_posts() -> None:
    """Add four distinct viewer-awareness scripts for each topic: 300 total."""
    angles = (
        ("⚠️ WARNING — YOU'RE BEING MANIPULATED", "You may be seeing {name}.", "{signal}", "{truth}", "{action}"),
        ("🚨 STOP — THEY'RE ALREADY DOING THIS TO YOU", "Watch for {name}.", "{signal}", "One moment is not proof. A repeated pattern deserves attention.", "{action}"),
        ("‼️ RED FLAG: DO NOT IGNORE THIS ANY LONGER", "This can look like {name}.", "{signal}", "{truth}", "You are allowed to slow the moment down."),
        ("⚠️ IF THIS FEELS FAMILIAR, YOU'RE IN DANGER", "A pattern called {name} can leave you doubting yourself.", "{signal}", "{truth}", "{action}"),
    )
    for name, signal, truth, action in AWARENESS_TOPICS:
        readable = name.title()
        for heading_hook, line1, line2, line3, line4 in angles:
            POSTS.append({
                "heading": f"{heading_hook}: {readable.upper()}",
                "benefits": [
                    line1.format(name=name), line2.format(signal=signal),
                    line3.format(truth=truth), line4.format(action=action),
                ],
                "caption": (
                    f"{readable}: spot the pattern, protect your peace. "
                    "Education only—not a diagnosis.\\n\\n"
                    "#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels"
                ),
            })


add_awareness_posts()
assert len(AWARENESS_TOPICS) == 75, "Keep 75 topics so this adds exactly 300 posts."
assert len(POSTS) == 350, "Expected 50 original posts plus 300 new awareness posts."


def load_progress() -> dict:
    try:
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_progress(data: dict) -> None:
    PROGRESS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


SEQUENCE_VERSION = "first-to-last-v1"


def next_post() -> dict:
    """Choose posts in fixed order: 1, 2, 3 … 350, then start at 1 again.

    The first run of this version deliberately starts at post 1, even if an
    older progress file was created by a previous random-post version.
    """
    data = load_progress()

    if data.get("sequence_version") != SEQUENCE_VERSION:
        # New sequential system: discard only the old picker position and begin
        # this series cleanly with technique 1.
        index = 0
        completed_cycles = 0
    else:
        try:
            next_number = int(data.get("next_post_number", 1))
        except (TypeError, ValueError):
            next_number = 1
        # Guard against a manually edited or broken progress file.
        index = max(0, min(next_number - 1, len(POSTS) - 1))
        completed_cycles = int(data.get("completed_cycles", 0))

    post = dict(POSTS[index])
    post["series_number"] = index + 1

    # Save the following post *after* selecting this one, so the next run gets
    # exactly the next technique and none are skipped or chosen at random.
    following_number = index + 2
    if following_number > len(POSTS):
        following_number = 1
        completed_cycles += 1
    data.update(
        sequence_version=SEQUENCE_VERSION,
        last_index=index,
        last_post_number=index + 1,
        next_post_number=following_number,
        completed_cycles=completed_cycles,
        last_heading=post["heading"],
    )
    save_progress(data)
    print(f"Selected post {index + 1} of {len(POSTS)}. Next: {following_number}.")
    return post


def pick_next_music() -> Path | None:
    """Use a local background track, rotating through assets/music between Reels."""
    if not MUSIC_DIR.exists():
        return None
    extensions = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
    files = sorted(p for p in MUSIC_DIR.iterdir() if p.is_file() and p.suffix.lower() in extensions)
    if not files:
        print(f"No supported music files in {MUSIC_DIR.resolve()}; rendering narration only.")
        return None
    data = load_progress()
    names = [p.name for p in files]
    previous = data.get("last_music_name", "")
    index = (names.index(previous) + 1) % len(files) if previous in names else 0
    selected = files[index]
    # Validate the actual file before rendering. This makes a bad upload visible in Actions logs.
    try:
        duration = video_duration(selected)
        if duration <= 0:
            raise ValueError("duration is zero")
    except (subprocess.CalledProcessError, ValueError) as error:
        print(f"Cannot read background music {selected.name}: {error}; rendering narration only.")
        return None
    data["last_music_name"] = selected.name
    save_progress(data)
    print(f"Background music selected: {selected.resolve()} ({duration:.1f}s)")
    return selected

def video_duration(path: Path) -> float:
    """Return duration for a narrated clip or local music file."""
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def visual_heading(heading: str) -> str:
    """Extract the short, high-impact danger word for the three-part headline."""
    import re
    plain = re.sub(r"[^A-Za-z0-9\s:'’-]", " ", heading).strip()
    topic = plain.rsplit(":", 1)[-1].strip() if ":" in plain else plain
    topic = re.sub(r"^(STOP|WARNING|RED FLAG|WAKE UP|DO NOT IGNORE THIS)\s*[-—]*\s*", "", topic, flags=re.I)
    return topic.upper()[:58]


def wrap_text(draw, text: str, font, max_width: int) -> list[str]:
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def render_slide(post: dict, active_index: int, output_png: Path) -> None:
    """Render a dark, red-and-white editorial card; active spoken point is highlighted."""
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    font_path = next((fp for fp in font_paths if Path(fp).exists()), font_paths[0])
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if not Path(regular_path).exists():
        regular_path = font_path
    title_font = ImageFont.truetype(font_path, 72)
    eyebrow_font = ImageFont.truetype(font_path, 30)
    body_font = ImageFont.truetype(regular_path, 38)
    num_font = ImageFont.truetype(font_path, 35)

    # Dark editorial board, with a strong headline modeled on the reference's hierarchy:
    # white lead-in → oversized red pattern name → white closing word.
    panel = (70, 105, 1010, 1715)
    draw.rounded_rectangle(panel, radius=26, fill=(3, 3, 4, 236), outline=(155, 8, 14, 255), width=4)
    # A small original alert mark: visual mood only, not copied artwork.
    draw.ellipse((505, 125, 575, 195), fill=(80, 0, 5, 230), outline=(255, 30, 36, 255), width=3)
    draw.polygon([(540, 137), (518, 179), (562, 179)], fill=(225, 15, 22, 255))

    topic = visual_heading(post["heading"])
    lead_font = ImageFont.truetype(font_path, 92)
    # Long subjects shrink only as much as needed, so every post keeps the same bold style.
    topic_size = 118 if len(topic) <= 22 else (100 if len(topic) <= 36 else 82)
    topic_font = ImageFont.truetype(font_path, topic_size)
    close_font = ImageFont.truetype(font_path, 108)

    def centered(text, y_pos, font, color):
        box = draw.textbbox((0, 0), text, font=font)
        draw.text(((TARGET_W - (box[2] - box[0])) // 2, y_pos), text, font=font, fill=color)
        return y_pos + (box[3] - box[1]) + 10

    # Keep the same series heading on every Reel.
    # This exact label is also included in the first narration line below.
    series_label = "4 RED FLAGS"
    label_box = draw.textbbox((0, 0), series_label, font=eyebrow_font)
    label_w = label_box[2] - label_box[0]
    label_x = (TARGET_W - label_w) // 2
    draw.rounded_rectangle((label_x - 18, 202, label_x + label_w + 18, 246),
                           radius=18, fill=(83, 0, 6, 255), outline=(235, 20, 28, 255), width=2)
    draw.text((label_x, 207), series_label, font=eyebrow_font, fill=(255, 75, 80, 255))

    y = 252
    y = centered("THEY'RE", y, lead_font, (250, 250, 250, 255))
    # The red word is the focal point, just like the supplied reference.
    for line in wrap_text(draw, topic, topic_font, 830)[:3]:
        y = centered(line, y, topic_font, (232, 18, 25, 255))
    y = centered("YOU", y, close_font, (250, 250, 250, 255))
    y += 22
    draw.line((135, y, 945, y), fill=(145, 15, 22, 255), width=3)
    y += 26

    benefits = post["benefits"][:5]
    available = 1625 - y
    block_h = max(160, min(220, available // max(1, len(benefits))))
    for i, benefit in enumerate(benefits, 1):
        active = active_index == i
        x1, x2 = 128, 952
        fill = (25, 4, 6, 245) if active else (7, 7, 8, 220)
        border = (245, 25, 33, 255) if active else (104, 14, 20, 255)
        draw.rounded_rectangle((x1, y, x2, y + block_h - 16), radius=16, fill=fill, outline=border, width=4 if active else 2)
        # Numbered red marker acts as a clean information-card icon.
        marker_fill = (235, 20, 28, 255) if active else (35, 5, 8, 255)
        draw.ellipse((x1+18, y+24, x1+82, y+88), fill=marker_fill, outline=(255, 55, 60, 255), width=2)
        nbox = draw.textbbox((0, 0), str(i), font=num_font)
        draw.text((x1+50-(nbox[2]-nbox[0])//2, y+54-(nbox[3]-nbox[1])//2), str(i), font=num_font, fill=(255,255,255,255))
        lines = wrap_text(draw, benefit, body_font, 670)
        text_color = (255, 255, 255, 255) if active else (184, 184, 184, 255)
        ty = y + 22
        for line in lines[:4]:
            draw.text((x1+105, ty), line, font=body_font, fill=text_color)
            ty += 45
        y += block_h

    # Bottom line stays clear of the Facebook caption overlay area.
    draw.text((135, 1650), "NOTICE THE PATTERN. KEEP YOUR BOUNDARIES.", font=eyebrow_font, fill=(235, 235, 235, 255))
    image.save(output_png)

def clean_narration_text(text: str) -> str:
    """Keep spoken narration natural; remove visual-only icons and punctuation noise."""
    import re
    text = re.sub(r"[^\w\s'.,!?-]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# Neural narrator supplied by Microsoft Edge's online text-to-speech service.
# Change this to another Edge neural voice if desired; see the edge-tts voice list.
NEURAL_VOICE = os.environ.get("REEL_VOICE", "en-US-AndrewMultilingualNeural")
# The voice provider can briefly throttle several back-to-back requests from hosted runners.
# Keep calls paced and retry transient failures rather than abandoning the entire Reel.
TTS_REQUEST_GAP_SECONDS = 2.0
TTS_MAX_ATTEMPTS = 4
_last_tts_request_at = 0.0


def make_narration(text: str, output_wav: Path) -> float:
    """Create natural neural speech for one slide, then add a short breathing pause."""
    global _last_tts_request_at
    spoken = clean_narration_text(text)
    raw_mp3 = output_wav.with_name(output_wav.stem + "_raw.mp3")
    last_error = ""

    for attempt in range(1, TTS_MAX_ATTEMPTS + 1):
        # Space requests out. This avoids intermittent 429/service refusals on GitHub runners.
        wait = TTS_REQUEST_GAP_SECONDS - (time.monotonic() - _last_tts_request_at)
        if wait > 0:
            time.sleep(wait)
        raw_mp3.unlink(missing_ok=True)
        result = subprocess.run([
            sys.executable, "-m", "edge_tts", "--voice", NEURAL_VOICE,
            "--rate", "+0%", "--text", spoken, "--write-media", str(raw_mp3),
        ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _last_tts_request_at = time.monotonic()
        if result.returncode == 0 and raw_mp3.exists() and raw_mp3.stat().st_size > 0:
            break
        last_error = (result.stderr or result.stdout or "The voice service returned no details.").strip()
        if attempt < TTS_MAX_ATTEMPTS:
            # Back off progressively, giving the provider time to accept the next request.
            time.sleep(2 ** attempt)
    else:
        raise RuntimeError(
            f"Andrew neural narration failed after {TTS_MAX_ATTEMPTS} attempts. "
            f"Service detail: {last_error[-700:]}"
        )

    duration = video_duration(raw_mp3) + 0.35
    # The pause is baked into the clip, keeping captions, slide timing, and audio aligned.
    subprocess.run([
        "ffmpeg", "-y", "-i", str(raw_mp3), "-af", "apad=pad_dur=0.35", "-t", f"{duration:.3f}",
        "-c:a", "pcm_s16le", str(output_wav),
    ], check=True)
    raw_mp3.unlink(missing_ok=True)
    return duration


def ass_timestamp(seconds: float) -> str:
    centiseconds = max(0, round(seconds * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, cs = divmod(remainder, 100)
    return f"{hours}:{minutes:02}:{secs:02}.{cs:02}"


def ass_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}").replace("\n", r"\N")


def make_karaoke_ass(slides: list[str], durations: list[float], output_ass: Path) -> None:
    """Write word-progress karaoke captions. Timings follow each rendered voice clip."""
    lines = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "",
        "[V4+ Styles]",
        # Secondary is white (unspoken); Primary is yellow (currently spoken/read).
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
        "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,"
        "Alignment,MarginL,MarginR,MarginV,Encoding",
        "Style: Karaoke,DejaVu Sans,56,&H0000D7FF,&H00FFFFFF,&H00101010,&H96000000,1,0,0,0,100,100,0,0,1,3,1,2,70,70,270,1",
        "", "[Events]", "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]
    cursor = 0.0
    for text, duration in zip(slides, durations):
        words = clean_narration_text(text).split()
        if not words:
            cursor += duration
            continue
        # Allocate caption progress by word length, normalized to the measured voice duration.
        weights = [max(1, len(word.strip(".,!?'-"))) for word in words]
        total_weight = sum(weights)
        chunks = []
        used = 0
        for i, (word, weight) in enumerate(zip(words, weights)):
            cs = max(1, round(duration * 100 * weight / total_weight))
            if i == len(words) - 1:
                cs = max(1, round(duration * 100) - used)
            used += cs
            chunks.append(r"{\kf" + str(cs) + "}" + ass_escape(word))
        caption = " ".join(chunks)
        lines.append(
            f"Dialogue: 0,{ass_timestamp(cursor)},{ass_timestamp(cursor + duration)},Karaoke,,0,0,0,,{{\\an2\\pos(540,1770)}}{caption}"
        )
        cursor += duration
    output_ass.write_text("\n".join(lines) + "\n", encoding="utf-8")


def concat_narration(wavs: list[Path], output_wav: Path) -> None:
    manifest = OUTPUT_DIR / "narration_concat.txt"
    manifest.write_text("".join(f"file '{wav.resolve()}'\n" for wav in wavs), encoding="utf-8")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(manifest),
        "-c:a", "pcm_s16le", str(output_wav),
    ], check=True)


def heading_narration(post: dict) -> str:
    """Speak the visible series label as part of every Reel's opening heading."""
    return f"4 Red Flags. {clean_narration_text(post['heading'])}"


def build_video(post: dict, output_path: Path) -> None:
    """Create a black editorial Reel with impact shakes, narration, karaoke, and local music."""
    # The first line intentionally includes the visible heading label, so the narrator
    # says “4 Red Flags” rather than skipping the label that appears on screen.
    slides = [heading_narration(post)] + post["benefits"]
    pngs, wavs, slide_times = [], [], []
    for i, slide in enumerate(slides):
        png = OUTPUT_DIR / f"text_overlay_{i}.png"
        wav = OUTPUT_DIR / f"narration_{i}.wav"
        render_slide(post, i, png)
        slide_duration = make_narration(slide, wav)
        pngs.append(png)
        wavs.append(wav)
        slide_times.append(slide_duration)

    narration = OUTPUT_DIR / "narration.wav"
    karaoke_ass = OUTPUT_DIR / "karaoke.ass"
    concat_narration(wavs, narration)
    make_karaoke_ass(slides, slide_times, karaoke_ass)
    total_duration = sum(slide_times)
    music = pick_next_music()

    # Pure black base matches the supplied dark editorial reference. Each new spoken card
    # gets a brief, restrained impact shake; it is visual emphasis, not nonstop motion.
    filters = ["[0:v]format=rgba[base]"]
    previous, start_time = "base", 0.0
    for i, slide_time in enumerate(slide_times):
        end_time = start_time + slide_time
        shake_end = min(end_time, start_time + 0.24)
        # Escaped commas are required inside FFmpeg expressions embedded in a filter graph.
        x = rf"10*sin(170*(t-{start_time:.3f}))*between(t\,{start_time:.3f}\,{shake_end:.3f})"
        y = rf"7*cos(205*(t-{start_time:.3f}))*between(t\,{start_time:.3f}\,{shake_end:.3f})"
        filters.append(
            f"[{i + 1}:v]scale={TARGET_W}:{TARGET_H}[card{i}];"
            rf"[{previous}][card{i}]overlay=x='{x}':y='{y}':enable='between(t\,{start_time:.3f}\,{end_time:.3f})'[v{i}]"
        )
        previous = f"v{i}"
        start_time = end_time

    escaped_ass = str(karaoke_ass.resolve()).replace("\\", "\\\\").replace(":", r"\:")
    filters.append(f"[{previous}]subtitles='{escaped_ass}'[outv]")

    # Narration stays clear while the music remains plainly audible underneath.
    # The former 0.075 setting, combined with FFmpeg's default mix normalization,
    # made the track effectively inaudible on phone speakers.
    narration_input = len(pngs) + 1
    command = [
        "ffmpeg", "-y", "-f", "lavfi", "-i",
        f"color=c=black:s={TARGET_W}x{TARGET_H}:r=30:d={total_duration:.3f}",
    ]
    for png in pngs:
        command += ["-loop", "1", "-i", str(png)]
    command += ["-i", str(narration)]
    if music:
        command += ["-stream_loop", "-1", "-i", str(music)]
        music_input = narration_input + 1
        filters.append(
            f"[{narration_input}:a]volume=1.0[narration];"
            f"[{music_input}:a]volume=0.18,afade=t=in:st=0:d=0.5,afade=t=out:st={max(0, total_duration - 0.7):.3f}:d=0.7[music];"
            "[narration][music]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]"
        )
        audio_map = "[aout]"
    else:
        print("No music file found in assets/music; rendering narration only.")
        filters.append(f"[{narration_input}:a]volume=1.15[aout]")
        audio_map = "[aout]"

    command += ["-filter_complex", ";".join(filters), "-map", "[outv]", "-map", audio_map]
    command += [
        "-t", f"{total_duration:.3f}", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(output_path),
    ]
    subprocess.run(command, check=True)

def post_to_facebook_reel(video_path: Path, caption: str) -> str:
    base_url = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/video_reels"
    started = requests.post(base_url, data={"upload_phase": "start", "access_token": FB_ACCESS_TOKEN})
    started.raise_for_status()
    data = started.json()
    video_id = data["video_id"]
    upload_url = data.get("upload_url", f"https://rupload.facebook.com/video-upload/v25.0/{video_id}")
    with video_path.open("rb") as file:
        uploaded = requests.post(upload_url, headers={
            "Authorization": f"OAuth {FB_ACCESS_TOKEN}", "offset": "0",
            "file_size": str(video_path.stat().st_size), "Content-Type": "application/octet-stream",
        }, data=file)
    uploaded.raise_for_status()
    finished = requests.post(base_url, data={
        "upload_phase": "finish", "video_id": video_id, "access_token": FB_ACCESS_TOKEN,
        "description": caption, "video_state": "PUBLISHED",
    })
    finished.raise_for_status()
    return video_id


def main():
    post = next_post()
    print(f"Making: {post['heading']}")
    build_video(post, OUTPUT_VIDEO)
    print(f"Published Facebook reel: {post_to_facebook_reel(OUTPUT_VIDEO, post['caption'])}")


if __name__ == "__main__":
    main()