#!/usr/bin/env python3
"""Manipulation-awareness Reel Maker — renders a heading and unnumbered awareness slides."""
import json
import os
import subprocess
import time
import sys
import random
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


FB_ACCESS_TOKEN = require_env("FB_ACCESS_TOKEN_DARK_PSY")
FB_PAGE_ID = require_env("FB_PAGE_ID_DARK_PSY")
# Resolve music relative to this script, not whichever folder starts the workflow.
# This prevents a working-directory change from silently removing the background track.
MUSIC_DIR = Path(__file__).resolve().parent / "assets/music"
# Put your own dark-character/background clips here. One is chosen at random per Reel.
VIDEO_DIR = Path(__file__).resolve().parent / "assets/videos"
VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}
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
POSTS = [{'heading': "4 Red Flags You Are Being Manipulated By Guilt-Tripping",
  'benefits': ['It uses guilt to pressure a decision.',
               'It may sound like: ‘After all I did for you.’',
               'Care does not erase your right to say no.',
               'Try: ‘I hear you. My answer is still no.’'],
  'caption': 'Guilt-Tripping: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Gaslighting",
  'benefits': ['It repeatedly challenges your memory or feelings.',
               'One disagreement is not automatically gaslighting.',
               'Look for a pattern of denial and confusion.',
               'Keep notes and speak with someone you trust.'],
  'caption': 'Gaslighting: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Love-Bombing",
  'benefits': ['It can feel like intense affection very fast.',
               'The concern is when warmth becomes pressure or control.',
               'Healthy interest respects your pace.',
               'Slow down and watch for consistency.'],
  'caption': 'Love-Bombing: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Silent Treatment",
  'benefits': ['Space can be healthy when it is communicated.',
               'Silent treatment uses withdrawal as punishment.',
               'It leaves you anxious and chasing answers.',
               'Ask for a clear time to talk again.'],
  'caption': 'Silent Treatment: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Blame Shifting",
  'benefits': ['The focus moves from their action to your reaction.',
               'You raise a concern, then end up apologizing.',
               'Both people can own their part.',
               'Return to the original issue calmly.'],
  'caption': 'Blame Shifting: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Moving Goalposts",
  'benefits': ['You meet the request, then the rule changes.',
               'Nothing you do ever seems enough.',
               'This can keep you working for approval.',
               'Ask for clear expectations upfront.'],
  'caption': 'Moving Goalposts: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By False Urgency",
  'benefits': ['Pressure says: decide right now.',
               'Respect gives you time to think.',
               'Urgency can hide a weak argument.',
               'Pause before big choices when you can.'],
  'caption': 'False Urgency: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Boundary Testing",
  'benefits': ['Small disrespect can test what you will tolerate.',
               'It may start as a joke or tiny favor.',
               'Your discomfort is useful information.',
               'State the boundary early and clearly.'],
  'caption': 'Boundary Testing: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Triangulation",
  'benefits': ['A third person gets pulled into your conflict.',
               'It can create jealousy, comparison, or pressure.',
               'Direct conversation reduces the drama.',
               'Do not compete for basic respect.'],
  'caption': 'Triangulation: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Isolation",
  'benefits': ['Control can make outside support feel unsafe.',
               'They may criticize every friend or family member.',
               'Healthy relationships make room for your people.',
               'Stay connected to trusted support.'],
  'caption': 'Isolation: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Future Faking",
  'benefits': ['Big future promises can create fast attachment.',
               'Words matter less than steady actions.',
               'Plans should not be used as a leash.',
               'Check whether behavior matches the promise.'],
  'caption': 'Future Faking: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Playing The Victim",
  'benefits': ['Pain deserves compassion, but it is not a free pass.',
               'The story may erase the harm they caused.',
               'Empathy and accountability can exist together.',
               'Do not let guilt replace the facts.'],
  'caption': 'Playing the Victim: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Darvo Pattern",
  'benefits': ['It can mean deny, attack, then reverse victim and offender.',
               'A concern becomes an attack on your character.',
               'The original issue disappears.',
               'Write down what happened before the talk shifts.'],
  'caption': 'DARVO Pattern: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Withholding Affection",
  'benefits': ['Affection should not be a reward for obedience.',
               'A healthy partner can need space respectfully.',
               'Control uses warmth and coldness to train behavior.',
               'Name the pattern, not just the mood.'],
  'caption': 'Withholding Affection: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Passive-Aggressive Pressure",
  'benefits': ['The message is hidden behind sarcasm or sighs.',
               'It makes you guess instead of discuss.',
               'Clear needs create healthier conflict.',
               'Ask: ‘What do you need directly?’'],
  'caption': 'Passive-Aggressive Pressure: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Negging",
  'benefits': ['A backhanded compliment can chip away at confidence.',
               'It may be framed as teasing or honesty.',
               'Respect does not need to make you smaller.',
               'Say: ‘That comment does not work for me.’'],
  'caption': 'Negging: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Intermittent Reinforcement",
  'benefits': ['Kindness and coldness alternate without warning.',
               'The unpredictability can make you chase the good moments.',
               'Consistency is more valuable than intensity.',
               'Judge the pattern, not the rare high point.'],
  'caption': 'Intermittent Reinforcement: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Information Overload",
  'benefits': ['Too many claims can make a simple issue feel confusing.',
               'Confusion can stop you from asking questions.',
               'You do not need to solve everything at once.',
               'Ask for one clear point at a time.'],
  'caption': 'Information Overload: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Selective Memory",
  'benefits': ['They remember your mistakes but forget their promises.',
               'This can create an unfair story about you.',
               'Everyone makes mistakes; standards should be mutual.',
               'Use specific examples and dates if needed.'],
  'caption': 'Selective Memory: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Double Standards",
  'benefits': ['Rules apply to you but not to them.',
               'They demand privacy but inspect your phone.',
               'Fairness needs the same rule for both people.',
               'Ask whether the expectation is mutual.'],
  'caption': 'Double Standards: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Jealousy As Proof",
  'benefits': ['Jealousy is a feeling, not proof of love.',
               'Control can be disguised as protection.',
               'Trust allows friendships, privacy, and choices.',
               'Love should not require isolation.'],
  'caption': 'Jealousy as Proof: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Weaponized Insecurity",
  'benefits': ['A private fear gets used to win an argument.',
               'This can make you feel exposed and small.',
               'Vulnerability needs care, not ammunition.',
               'Limit what you share with unsafe people.'],
  'caption': 'Weaponized Insecurity: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Shaming",
  'benefits': ['Shame attacks who you are, not what happened.',
               'It sounds like: ‘You are selfish.’',
               'Healthy feedback names a behavior and a need.',
               'You can reject insults and discuss facts.'],
  'caption': 'Shaming: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Threats And Ultimatums",
  'benefits': ['A boundary explains what you will do to protect yourself.',
               'A threat tries to force another person’s choice.',
               'Not every ultimatum is abusive; context matters.',
               'Notice whether there is room for respectful choice.'],
  'caption': 'Threats and Ultimatums: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Monitoring",
  'benefits': ['Checking your location or messages can be framed as care.',
               'Consent and privacy still matter in relationships.',
               'Safety plans are different from constant surveillance.',
               'Talk about digital boundaries clearly.'],
  'caption': 'Monitoring: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Financial Control",
  'benefits': ['Money can be used to limit someone’s choices.',
               'It may include hiding accounts or blocking work.',
               'Shared finances need transparency and agreement.',
               'Keep access to important records when possible.'],
  'caption': 'Financial Control: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Public Humiliation",
  'benefits': ['Embarrassing you can create fear of speaking up.',
               'It may be called a joke after you react.',
               'A joke is not funny if it repeatedly hurts.',
               'Address it privately or step away.'],
  'caption': 'Public Humiliation: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Stonewalling",
  'benefits': ['Stonewalling shuts down every attempt to resolve conflict.',
               'A pause is healthy when there is a return time.',
               'Permanent shutdown leaves one person carrying the issue.',
               'Agree on when the conversation resumes.'],
  'caption': 'Stonewalling: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Threatening To Leave",
  'benefits': ['Breakup threats can be used to control small choices.',
               'They create fear instead of problem-solving.',
               'Real relationship concerns deserve a calm talk.',
               'Do not bargain away your boundaries to stop panic.'],
  'caption': 'Threatening to Leave: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Scorekeeping",
  'benefits': ['Past favors become weapons in every argument.',
               'Support becomes a debt you can never repay.',
               'Healthy care is not a running invoice.',
               'Discuss the current problem on its own.'],
  'caption': 'Scorekeeping: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Minimizing",
  'benefits': ['It sounds like: ‘You are too sensitive.’',
               'It shrinks the impact instead of hearing it.',
               'Feelings are data, even when views differ.',
               'Ask for the behavior to be addressed.'],
  'caption': 'Minimizing: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Dismissive Humor",
  'benefits': ['Serious concerns get turned into a joke.',
               'Humor can dodge accountability.',
               'You are allowed to bring a topic back.',
               'Say: ‘I am serious. Please answer me.’'],
  'caption': 'Dismissive Humor: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Forced Confessions",
  'benefits': ['Pressure for constant proof can become control.',
               'You do not have to reveal every private thought.',
               'Trust grows from voluntary honesty, not interrogation.',
               'Pause a conversation that becomes coercive.'],
  'caption': 'Forced Confessions: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Comparison",
  'benefits': ['Comparing you to others can trigger insecurity.',
               'It may push you to earn basic kindness.',
               'Healthy feedback does not use people as weapons.',
               'Ask for a direct request instead.'],
  'caption': 'Comparison: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Conditional Respect",
  'benefits': ['Respect should not depend on perfect obedience.',
               'Disagreement is normal in close relationships.',
               'Control treats independence as betrayal.',
               'Keep your values visible when pressure rises.'],
  'caption': 'Conditional Respect: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Rewriting History",
  'benefits': ['Past events get changed to fit their current story.',
               'You may leave talks doubting clear facts.',
               'Memory is imperfect, but patterns still matter.',
               'Save messages or write a private timeline.'],
  'caption': 'Rewriting History: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Using Secrets",
  'benefits': ['A secret can be used to scare you into silence.',
               'That turns trust into leverage.',
               'You deserve support without blackmail.',
               'Tell a trusted person if safety is at risk.'],
  'caption': 'Using Secrets: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Weaponized Helplessness",
  'benefits': ['Someone acts unable so you carry all the work.',
               'A one-time need is different from a repeated pattern.',
               'Shared responsibility needs real effort.',
               'Name tasks and agreements clearly.'],
  'caption': 'Weaponized Helplessness: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Overexplaining Pressure",
  'benefits': ['You may be pushed to justify every no.',
               'More explanation can invite more debate.',
               'A short boundary is still a boundary.',
               'Try: ‘I am not available for that.’'],
  'caption': 'Overexplaining Pressure: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Baiting",
  'benefits': ['A person provokes you, then focuses on your reaction.',
               'The goal may be to make you look unreasonable.',
               'Pause before replying when emotions spike.',
               'Keep responses short and factual.'],
  'caption': 'Baiting: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Smear Campaigns",
  'benefits': ['Someone may tell others a distorted story about you.',
               'It can isolate you before you can speak.',
               'You do not need to fight every rumor.',
               'Share facts with trusted people, not the whole crowd.'],
  'caption': 'Smear Campaigns: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Control Disguised As Advice",
  'benefits': ['Advice becomes a problem when no is not accepted.',
               'Care offers options; control demands obedience.',
               'Your decisions can be different from theirs.',
               'Thank them, then choose for yourself.'],
  'caption': 'Control Disguised as Advice: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Testing Loyalty",
  'benefits': ['Unreasonable demands can be framed as proof of love.',
               'Love is not a test you must keep passing.',
               'Healthy loyalty includes respect for your limits.',
               'Do not trade safety for approval.'],
  'caption': 'Testing Loyalty: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Confusing Mixed Messages",
  'benefits': ['Warm words and harmful actions can coexist.',
               'Mixed signals keep you searching for clarity.',
               'Look at repeated behavior, not only apologies.',
               'Ask what will change and watch what happens.'],
  'caption': 'Confusing Mixed Messages: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Pressure Through Fear",
  'benefits': ['Fear can make a bad choice feel like the only choice.',
               'Threats, anger, and panic reduce clear thinking.',
               'Create distance before deciding if you can.',
               'Reach out for help if you feel unsafe.'],
  'caption': 'Pressure Through Fear: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Pressure Through Obligation",
  'benefits': ['A favor can be used to demand more than you agreed to.',
               'Gratitude does not erase consent.',
               'You can appreciate help and still have limits.',
               'Say what you can offer, not what they demand.'],
  'caption': 'Pressure Through Obligation: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Pressure Through Flattery",
  'benefits': ['Praise can be used to make refusal feel selfish.',
               'It may sound like: ‘You are the only one who can.’',
               'A compliment is not a contract.',
               'Decide based on capacity, not praise.'],
  'caption': 'Pressure Through Flattery: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Healthy Conflict Check",
  'benefits': ['Healthy conflict allows both people to speak.',
               'It uses specific behavior, not insults.',
               'It makes room for pauses and repair.',
               'Respect remains even during disagreement.'],
  'caption': 'Healthy Conflict Check: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By Trust Your Pattern Notes",
  'benefits': ['One moment rarely tells the whole story.',
               'Repeated fear, guilt, or confusion deserves attention.',
               'Write down behavior, dates, and how you felt.',
               'Support helps you see the pattern clearly.'],
  'caption': 'Trust Your Pattern Notes: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels'},
 {'heading': "4 Red Flags You Are Being Manipulated By When To Get Support",
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
                "heading": f"4 Red Flags You Are Being Manipulated By {readable}",
                # This is a plain-language definition used for the final spoken awareness message.
                "definition": signal,
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

# 350 more original Reel scripts, built as fresh awareness angles for 70 of the
# existing topics. They extend the library without teaching manipulation tactics.
EXTENDED_ANGLES = (
    ("Notice this pattern", "A warning sign can be {name}.", "{signal}", "{truth}", "{action}"),
    ("Pause and check this", "{name} can hide inside ordinary moments.", "{signal}", "Patterns matter more than one isolated moment.", "{action}"),
    ("Do not ignore this red flag", "This may be {name}.", "{signal}", "{truth}", "You deserve time, clarity, and a choice."),
    ("Protect your peace", "Watch for {name} when a situation feels confusing.", "{signal}", "Your discomfort is information, not a problem to silence.", "{action}"),
    ("Know the pattern", "{name} can make a reasonable boundary feel difficult.", "{signal}", "{truth}", "Pause before deciding and use support if you need it."),
)

def add_extended_awareness_posts() -> None:
    """Add 5 additional education-first scripts for each of 70 established topics."""
    for name, signal, truth, action in AWARENESS_TOPICS[:70]:
        readable = name.title()
        for hook, line1, line2, line3, line4 in EXTENDED_ANGLES:
            POSTS.append({
                "heading": f"4 Red Flags You Are Being Manipulated By {readable}",
                "definition": signal,
                "benefits": [
                    line1.format(name=name), line2.format(signal=signal),
                    line3.format(truth=truth), line4.format(action=action),
                ],
                "caption": (
                    f"{readable}: recognize the pattern and protect your peace. "
                    "Education only—not a diagnosis.\n\n"
                    "#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels"
                ),
            })


add_extended_awareness_posts()
# Original posts use their first awareness point as the concise definition. Additional
# posts carry a dedicated definition from their topic data above.
for _post in POSTS:
    _post.setdefault("definition", _post["benefits"][0])

# COMPLETE REVIEW LIST — all 1,100 posts are written below as plain Python data.
# This assignment is the final post library used by the app. Scroll here to review
# every original post and every new post individually.
POSTS = \
[{'heading': '4 Red Flags You Are Being Manipulated By Guilt-Tripping',
  'benefits': ['It uses guilt to pressure a decision.',
               'It may sound like: ‘After all I did for you.’',
               'Care does not erase your right to say no.',
               'Try: ‘I hear you. My answer is still no.’'],
  'caption': 'Guilt-Tripping: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'It uses guilt to pressure a decision.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Gaslighting',
  'benefits': ['It repeatedly challenges your memory or feelings.',
               'One disagreement is not automatically gaslighting.',
               'Look for a pattern of denial and confusion.',
               'Keep notes and speak with someone you trust.'],
  'caption': 'Gaslighting: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'It repeatedly challenges your memory or feelings.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Love-Bombing',
  'benefits': ['It can feel like intense affection very fast.',
               'The concern is when warmth becomes pressure or control.',
               'Healthy interest respects your pace.',
               'Slow down and watch for consistency.'],
  'caption': 'Love-Bombing: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'It can feel like intense affection very fast.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Silent Treatment',
  'benefits': ['Space can be healthy when it is communicated.',
               'Silent treatment uses withdrawal as punishment.',
               'It leaves you anxious and chasing answers.',
               'Ask for a clear time to talk again.'],
  'caption': 'Silent Treatment: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Space can be healthy when it is communicated.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Blame Shifting',
  'benefits': ['The focus moves from their action to your reaction.',
               'You raise a concern, then end up apologizing.',
               'Both people can own their part.',
               'Return to the original issue calmly.'],
  'caption': 'Blame Shifting: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'The focus moves from their action to your reaction.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moving Goalposts',
  'benefits': ['You meet the request, then the rule changes.',
               'Nothing you do ever seems enough.',
               'This can keep you working for approval.',
               'Ask for clear expectations upfront.'],
  'caption': 'Moving Goalposts: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'You meet the request, then the rule changes.'},
 {'heading': '4 Red Flags You Are Being Manipulated By False Urgency',
  'benefits': ['Pressure says: decide right now.',
               'Respect gives you time to think.',
               'Urgency can hide a weak argument.',
               'Pause before big choices when you can.'],
  'caption': 'False Urgency: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Pressure says: decide right now.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Boundary Testing',
  'benefits': ['Small disrespect can test what you will tolerate.',
               'It may start as a joke or tiny favor.',
               'Your discomfort is useful information.',
               'State the boundary early and clearly.'],
  'caption': 'Boundary Testing: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Small disrespect can test what you will tolerate.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Triangulation',
  'benefits': ['A third person gets pulled into your conflict.',
               'It can create jealousy, comparison, or pressure.',
               'Direct conversation reduces the drama.',
               'Do not compete for basic respect.'],
  'caption': 'Triangulation: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'A third person gets pulled into your conflict.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Isolation',
  'benefits': ['Control can make outside support feel unsafe.',
               'They may criticize every friend or family member.',
               'Healthy relationships make room for your people.',
               'Stay connected to trusted support.'],
  'caption': 'Isolation: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Control can make outside support feel unsafe.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Future Faking',
  'benefits': ['Big future promises can create fast attachment.',
               'Words matter less than steady actions.',
               'Plans should not be used as a leash.',
               'Check whether behavior matches the promise.'],
  'caption': 'Future Faking: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Big future promises can create fast attachment.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Playing The Victim',
  'benefits': ['Pain deserves compassion, but it is not a free pass.',
               'The story may erase the harm they caused.',
               'Empathy and accountability can exist together.',
               'Do not let guilt replace the facts.'],
  'caption': 'Playing the Victim: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Pain deserves compassion, but it is not a free pass.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Darvo Pattern',
  'benefits': ['It can mean deny, attack, then reverse victim and offender.',
               'A concern becomes an attack on your character.',
               'The original issue disappears.',
               'Write down what happened before the talk shifts.'],
  'caption': 'DARVO Pattern: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'It can mean deny, attack, then reverse victim and offender.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Withholding Affection',
  'benefits': ['Affection should not be a reward for obedience.',
               'A healthy partner can need space respectfully.',
               'Control uses warmth and coldness to train behavior.',
               'Name the pattern, not just the mood.'],
  'caption': 'Withholding Affection: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Affection should not be a reward for obedience.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Passive-Aggressive Pressure',
  'benefits': ['The message is hidden behind sarcasm or sighs.',
               'It makes you guess instead of discuss.',
               'Clear needs create healthier conflict.',
               'Ask: ‘What do you need directly?’'],
  'caption': 'Passive-Aggressive Pressure: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'The message is hidden behind sarcasm or sighs.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Negging',
  'benefits': ['A backhanded compliment can chip away at confidence.',
               'It may be framed as teasing or honesty.',
               'Respect does not need to make you smaller.',
               'Say: ‘That comment does not work for me.’'],
  'caption': 'Negging: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'A backhanded compliment can chip away at confidence.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Intermittent Reinforcement',
  'benefits': ['Kindness and coldness alternate without warning.',
               'The unpredictability can make you chase the good moments.',
               'Consistency is more valuable than intensity.',
               'Judge the pattern, not the rare high point.'],
  'caption': 'Intermittent Reinforcement: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Kindness and coldness alternate without warning.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Information Overload',
  'benefits': ['Too many claims can make a simple issue feel confusing.',
               'Confusion can stop you from asking questions.',
               'You do not need to solve everything at once.',
               'Ask for one clear point at a time.'],
  'caption': 'Information Overload: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Too many claims can make a simple issue feel confusing.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Memory',
  'benefits': ['They remember your mistakes but forget their promises.',
               'This can create an unfair story about you.',
               'Everyone makes mistakes; standards should be mutual.',
               'Use specific examples and dates if needed.'],
  'caption': 'Selective Memory: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'They remember your mistakes but forget their promises.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Double Standards',
  'benefits': ['Rules apply to you but not to them.',
               'They demand privacy but inspect your phone.',
               'Fairness needs the same rule for both people.',
               'Ask whether the expectation is mutual.'],
  'caption': 'Double Standards: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Rules apply to you but not to them.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Jealousy As Proof',
  'benefits': ['Jealousy is a feeling, not proof of love.',
               'Control can be disguised as protection.',
               'Trust allows friendships, privacy, and choices.',
               'Love should not require isolation.'],
  'caption': 'Jealousy as Proof: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Jealousy is a feeling, not proof of love.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Weaponized Insecurity',
  'benefits': ['A private fear gets used to win an argument.',
               'This can make you feel exposed and small.',
               'Vulnerability needs care, not ammunition.',
               'Limit what you share with unsafe people.'],
  'caption': 'Weaponized Insecurity: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'A private fear gets used to win an argument.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Shaming',
  'benefits': ['Shame attacks who you are, not what happened.',
               'It sounds like: ‘You are selfish.’',
               'Healthy feedback names a behavior and a need.',
               'You can reject insults and discuss facts.'],
  'caption': 'Shaming: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Shame attacks who you are, not what happened.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threats And Ultimatums',
  'benefits': ['A boundary explains what you will do to protect yourself.',
               'A threat tries to force another person’s choice.',
               'Not every ultimatum is abusive; context matters.',
               'Notice whether there is room for respectful choice.'],
  'caption': 'Threats and Ultimatums: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'A boundary explains what you will do to protect yourself.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Monitoring',
  'benefits': ['Checking your location or messages can be framed as care.',
               'Consent and privacy still matter in relationships.',
               'Safety plans are different from constant surveillance.',
               'Talk about digital boundaries clearly.'],
  'caption': 'Monitoring: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Checking your location or messages can be framed as care.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Control',
  'benefits': ['Money can be used to limit someone’s choices.',
               'It may include hiding accounts or blocking work.',
               'Shared finances need transparency and agreement.',
               'Keep access to important records when possible.'],
  'caption': 'Financial Control: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Money can be used to limit someone’s choices.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Public Humiliation',
  'benefits': ['Embarrassing you can create fear of speaking up.',
               'It may be called a joke after you react.',
               'A joke is not funny if it repeatedly hurts.',
               'Address it privately or step away.'],
  'caption': 'Public Humiliation: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Embarrassing you can create fear of speaking up.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Stonewalling',
  'benefits': ['Stonewalling shuts down every attempt to resolve conflict.',
               'A pause is healthy when there is a return time.',
               'Permanent shutdown leaves one person carrying the issue.',
               'Agree on when the conversation resumes.'],
  'caption': 'Stonewalling: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Stonewalling shuts down every attempt to resolve conflict.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening To Leave',
  'benefits': ['Breakup threats can be used to control small choices.',
               'They create fear instead of problem-solving.',
               'Real relationship concerns deserve a calm talk.',
               'Do not bargain away your boundaries to stop panic.'],
  'caption': 'Threatening to Leave: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Breakup threats can be used to control small choices.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Scorekeeping',
  'benefits': ['Past favors become weapons in every argument.',
               'Support becomes a debt you can never repay.',
               'Healthy care is not a running invoice.',
               'Discuss the current problem on its own.'],
  'caption': 'Scorekeeping: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Past favors become weapons in every argument.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Minimizing',
  'benefits': ['It sounds like: ‘You are too sensitive.’',
               'It shrinks the impact instead of hearing it.',
               'Feelings are data, even when views differ.',
               'Ask for the behavior to be addressed.'],
  'caption': 'Minimizing: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'It sounds like: ‘You are too sensitive.’'},
 {'heading': '4 Red Flags You Are Being Manipulated By Dismissive Humor',
  'benefits': ['Serious concerns get turned into a joke.',
               'Humor can dodge accountability.',
               'You are allowed to bring a topic back.',
               'Say: ‘I am serious. Please answer me.’'],
  'caption': 'Dismissive Humor: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Serious concerns get turned into a joke.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Confessions',
  'benefits': ['Pressure for constant proof can become control.',
               'You do not have to reveal every private thought.',
               'Trust grows from voluntary honesty, not interrogation.',
               'Pause a conversation that becomes coercive.'],
  'caption': 'Forced Confessions: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Pressure for constant proof can become control.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Comparison',
  'benefits': ['Comparing you to others can trigger insecurity.',
               'It may push you to earn basic kindness.',
               'Healthy feedback does not use people as weapons.',
               'Ask for a direct request instead.'],
  'caption': 'Comparison: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Comparing you to others can trigger insecurity.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Conditional Respect',
  'benefits': ['Respect should not depend on perfect obedience.',
               'Disagreement is normal in close relationships.',
               'Control treats independence as betrayal.',
               'Keep your values visible when pressure rises.'],
  'caption': 'Conditional Respect: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Respect should not depend on perfect obedience.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Rewriting History',
  'benefits': ['Past events get changed to fit their current story.',
               'You may leave talks doubting clear facts.',
               'Memory is imperfect, but patterns still matter.',
               'Save messages or write a private timeline.'],
  'caption': 'Rewriting History: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Past events get changed to fit their current story.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Using Secrets',
  'benefits': ['A secret can be used to scare you into silence.',
               'That turns trust into leverage.',
               'You deserve support without blackmail.',
               'Tell a trusted person if safety is at risk.'],
  'caption': 'Using Secrets: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'A secret can be used to scare you into silence.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Weaponized Helplessness',
  'benefits': ['Someone acts unable so you carry all the work.',
               'A one-time need is different from a repeated pattern.',
               'Shared responsibility needs real effort.',
               'Name tasks and agreements clearly.'],
  'caption': 'Weaponized Helplessness: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Someone acts unable so you carry all the work.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Overexplaining Pressure',
  'benefits': ['You may be pushed to justify every no.',
               'More explanation can invite more debate.',
               'A short boundary is still a boundary.',
               'Try: ‘I am not available for that.’'],
  'caption': 'Overexplaining Pressure: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'You may be pushed to justify every no.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Baiting',
  'benefits': ['A person provokes you, then focuses on your reaction.',
               'The goal may be to make you look unreasonable.',
               'Pause before replying when emotions spike.',
               'Keep responses short and factual.'],
  'caption': 'Baiting: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'A person provokes you, then focuses on your reaction.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Smear Campaigns',
  'benefits': ['Someone may tell others a distorted story about you.',
               'It can isolate you before you can speak.',
               'You do not need to fight every rumor.',
               'Share facts with trusted people, not the whole crowd.'],
  'caption': 'Smear Campaigns: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Someone may tell others a distorted story about you.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Control Disguised As Advice',
  'benefits': ['Advice becomes a problem when no is not accepted.',
               'Care offers options; control demands obedience.',
               'Your decisions can be different from theirs.',
               'Thank them, then choose for yourself.'],
  'caption': 'Control Disguised as Advice: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Advice becomes a problem when no is not accepted.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Testing Loyalty',
  'benefits': ['Unreasonable demands can be framed as proof of love.',
               'Love is not a test you must keep passing.',
               'Healthy loyalty includes respect for your limits.',
               'Do not trade safety for approval.'],
  'caption': 'Testing Loyalty: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Unreasonable demands can be framed as proof of love.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Confusing Mixed Messages',
  'benefits': ['Warm words and harmful actions can coexist.',
               'Mixed signals keep you searching for clarity.',
               'Look at repeated behavior, not only apologies.',
               'Ask what will change and watch what happens.'],
  'caption': 'Confusing Mixed Messages: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Warm words and harmful actions can coexist.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Pressure Through Fear',
  'benefits': ['Fear can make a bad choice feel like the only choice.',
               'Threats, anger, and panic reduce clear thinking.',
               'Create distance before deciding if you can.',
               'Reach out for help if you feel unsafe.'],
  'caption': 'Pressure Through Fear: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Fear can make a bad choice feel like the only choice.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Pressure Through Obligation',
  'benefits': ['A favor can be used to demand more than you agreed to.',
               'Gratitude does not erase consent.',
               'You can appreciate help and still have limits.',
               'Say what you can offer, not what they demand.'],
  'caption': 'Pressure Through Obligation: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'A favor can be used to demand more than you agreed to.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Pressure Through Flattery',
  'benefits': ['Praise can be used to make refusal feel selfish.',
               'It may sound like: ‘You are the only one who can.’',
               'A compliment is not a contract.',
               'Decide based on capacity, not praise.'],
  'caption': 'Pressure Through Flattery: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Praise can be used to make refusal feel selfish.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Healthy Conflict Check',
  'benefits': ['Healthy conflict allows both people to speak.',
               'It uses specific behavior, not insults.',
               'It makes room for pauses and repair.',
               'Respect remains even during disagreement.'],
  'caption': 'Healthy Conflict Check: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Healthy conflict allows both people to speak.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Trust Your Pattern Notes',
  'benefits': ['One moment rarely tells the whole story.',
               'Repeated fear, guilt, or confusion deserves attention.',
               'Write down behavior, dates, and how you felt.',
               'Support helps you see the pattern clearly.'],
  'caption': 'Trust Your Pattern Notes: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'One moment rarely tells the whole story.'},
 {'heading': '4 Red Flags You Are Being Manipulated By When To Get Support',
  'benefits': ['Talk to someone trusted when control feels normal.',
               'Reach out sooner if you feel afraid or isolated.',
               'Support is not overreacting.',
               'If you are in immediate danger, contact local emergency help.'],
  'caption': 'When to Get Support: learn the pattern, protect your peace.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #RelationshipAdvice #Reels',
  'definition': 'Talk to someone trusted when control feels normal.'},
 {'heading': '4 Red Flags You Are Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['You may be seeing foot-in-the-door pressure.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Consent to one thing is not consent to the next.',
               "Try: 'I agreed to the first part, not this.'"],
  'caption': 'Foot-In-The-Door Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['Watch for foot-in-the-door pressure.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'One moment is not proof. A repeated pattern deserves attention.',
               "Try: 'I agreed to the first part, not this.'"],
  'caption': 'Foot-In-The-Door Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['This can look like foot-in-the-door pressure.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Consent to one thing is not consent to the next.',
               'You are allowed to slow the moment down.'],
  'caption': 'Foot-In-The-Door Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['A pattern called foot-in-the-door pressure can leave you doubting yourself.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Consent to one thing is not consent to the next.',
               "Try: 'I agreed to the first part, not this.'"],
  'caption': 'Foot-In-The-Door Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['You may be seeing door-in-the-face pressure.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Relief can make a request feel fair when it still is not right for you.',
               'Choose based on your capacity, not the comparison.'],
  'caption': 'Door-In-The-Face Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['Watch for door-in-the-face pressure.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Choose based on your capacity, not the comparison.'],
  'caption': 'Door-In-The-Face Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['This can look like door-in-the-face pressure.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Relief can make a request feel fair when it still is not right for you.',
               'You are allowed to slow the moment down.'],
  'caption': 'Door-In-The-Face Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['A pattern called door-in-the-face pressure can leave you doubting yourself.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Relief can make a request feel fair when it still is not right for you.',
               'Choose based on your capacity, not the comparison.'],
  'caption': 'Door-In-The-Face Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['You may be seeing lowballing.',
               'The terms get worse only after you have invested time, hope, or money.',
               'An agreement can be reconsidered when the conditions change.',
               'Ask for the full terms in writing before continuing.'],
  'caption': 'Lowballing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['Watch for lowballing.',
               'The terms get worse only after you have invested time, hope, or money.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Ask for the full terms in writing before continuing.'],
  'caption': 'Lowballing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['This can look like lowballing.',
               'The terms get worse only after you have invested time, hope, or money.',
               'An agreement can be reconsidered when the conditions change.',
               'You are allowed to slow the moment down.'],
  'caption': 'Lowballing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['A pattern called lowballing can leave you doubting yourself.',
               'The terms get worse only after you have invested time, hope, or money.',
               'An agreement can be reconsidered when the conditions change.',
               'Ask for the full terms in writing before continuing.'],
  'caption': 'Lowballing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['You may be seeing sunk-cost pressure.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Past effort is not a reason to accept future harm.',
               'Ask what you would choose if starting today.'],
  'caption': 'Sunk-Cost Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['Watch for sunk-cost pressure.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'One moment is not proof. A repeated pattern deserves attention.',
               'Ask what you would choose if starting today.'],
  'caption': 'Sunk-Cost Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['This can look like sunk-cost pressure.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Past effort is not a reason to accept future harm.',
               'You are allowed to slow the moment down.'],
  'caption': 'Sunk-Cost Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['A pattern called sunk-cost pressure can leave you doubting yourself.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Past effort is not a reason to accept future harm.',
               'Ask what you would choose if starting today.'],
  'caption': 'Sunk-Cost Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['You may be seeing scarcity pressure.',
               'Something is called rare or almost gone before you can think clearly.',
               'Limited supply does not remove your right to pause.',
               'Step back and verify the claim independently.'],
  'caption': 'Scarcity Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['Watch for scarcity pressure.',
               'Something is called rare or almost gone before you can think clearly.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Step back and verify the claim independently.'],
  'caption': 'Scarcity Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['This can look like scarcity pressure.',
               'Something is called rare or almost gone before you can think clearly.',
               'Limited supply does not remove your right to pause.',
               'You are allowed to slow the moment down.'],
  'caption': 'Scarcity Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['A pattern called scarcity pressure can leave you doubting yourself.',
               'Something is called rare or almost gone before you can think clearly.',
               'Limited supply does not remove your right to pause.',
               'Step back and verify the claim independently.'],
  'caption': 'Scarcity Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['You may be seeing social-proof pressure.',
               'You are told everybody agrees, buys, or puts up with it.',
               'A crowd can be wrong, and private discomfort still matters.',
               'Ask for evidence, not a head count.'],
  'caption': 'Social-Proof Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['Watch for social-proof pressure.',
               'You are told everybody agrees, buys, or puts up with it.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Ask for evidence, not a head count.'],
  'caption': 'Social-Proof Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['This can look like social-proof pressure.',
               'You are told everybody agrees, buys, or puts up with it.',
               'A crowd can be wrong, and private discomfort still matters.',
               'You are allowed to slow the moment down.'],
  'caption': 'Social-Proof Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['A pattern called social-proof pressure can leave you doubting yourself.',
               'You are told everybody agrees, buys, or puts up with it.',
               'A crowd can be wrong, and private discomfort still matters.',
               'Ask for evidence, not a head count.'],
  'caption': 'Social-Proof Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['You may be seeing authority pressure.',
               'A title or confident voice is used to shut down your questions.',
               'Expertise deserves respect, not blind obedience.',
               'Ask what supports the recommendation.'],
  'caption': 'Authority Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['Watch for authority pressure.',
               'A title or confident voice is used to shut down your questions.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Ask what supports the recommendation.'],
  'caption': 'Authority Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['This can look like authority pressure.',
               'A title or confident voice is used to shut down your questions.',
               'Expertise deserves respect, not blind obedience.',
               'You are allowed to slow the moment down.'],
  'caption': 'Authority Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['A pattern called authority pressure can leave you doubting yourself.',
               'A title or confident voice is used to shut down your questions.',
               'Expertise deserves respect, not blind obedience.',
               'Ask what supports the recommendation.'],
  'caption': 'Authority Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['You may be seeing reciprocity pressure.',
               'A gift or favor quietly turns into an obligation.',
               'Kindness is not a contract for access or compliance.',
               'Say thanks without promising more than you want.'],
  'caption': 'Reciprocity Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['Watch for reciprocity pressure.',
               'A gift or favor quietly turns into an obligation.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Say thanks without promising more than you want.'],
  'caption': 'Reciprocity Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['This can look like reciprocity pressure.',
               'A gift or favor quietly turns into an obligation.',
               'Kindness is not a contract for access or compliance.',
               'You are allowed to slow the moment down.'],
  'caption': 'Reciprocity Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['A pattern called reciprocity pressure can leave you doubting yourself.',
               'A gift or favor quietly turns into an obligation.',
               'Kindness is not a contract for access or compliance.',
               'Say thanks without promising more than you want.'],
  'caption': 'Reciprocity Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['You may be seeing fear-based messaging.',
               'A scary outcome is presented as certain unless you obey.',
               'Fear narrows thinking and makes weak claims feel urgent.',
               'Pause, breathe, and check the actual risk.'],
  'caption': 'Fear-Based Messaging: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['Watch for fear-based messaging.',
               'A scary outcome is presented as certain unless you obey.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Pause, breathe, and check the actual risk.'],
  'caption': 'Fear-Based Messaging: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['This can look like fear-based messaging.',
               'A scary outcome is presented as certain unless you obey.',
               'Fear narrows thinking and makes weak claims feel urgent.',
               'You are allowed to slow the moment down.'],
  'caption': 'Fear-Based Messaging: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['A pattern called fear-based messaging can leave you doubting yourself.',
               'A scary outcome is presented as certain unless you obey.',
               'Fear narrows thinking and makes weak claims feel urgent.',
               'Pause, breathe, and check the actual risk.'],
  'caption': 'Fear-Based Messaging: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['You may be seeing false dilemma.',
               'You are told there are only two choices when there may be more.',
               'Pressure often hides alternatives.',
               "Ask: 'What other options are we leaving out?'"],
  'caption': 'False Dilemma: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['Watch for false dilemma.',
               'You are told there are only two choices when there may be more.',
               'One moment is not proof. A repeated pattern deserves attention.',
               "Ask: 'What other options are we leaving out?'"],
  'caption': 'False Dilemma: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['This can look like false dilemma.',
               'You are told there are only two choices when there may be more.',
               'Pressure often hides alternatives.',
               'You are allowed to slow the moment down.'],
  'caption': 'False Dilemma: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['A pattern called false dilemma can leave you doubting yourself.',
               'You are told there are only two choices when there may be more.',
               'Pressure often hides alternatives.',
               "Ask: 'What other options are we leaving out?'"],
  'caption': 'False Dilemma: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['You may be seeing loaded questions.',
               'Any answer seems to make you admit something unfair.',
               'A question can contain an accusation instead of seeking truth.',
               'Correct the premise before answering.'],
  'caption': 'Loaded Questions: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['Watch for loaded questions.',
               'Any answer seems to make you admit something unfair.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Correct the premise before answering.'],
  'caption': 'Loaded Questions: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['This can look like loaded questions.',
               'Any answer seems to make you admit something unfair.',
               'A question can contain an accusation instead of seeking truth.',
               'You are allowed to slow the moment down.'],
  'caption': 'Loaded Questions: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['A pattern called loaded questions can leave you doubting yourself.',
               'Any answer seems to make you admit something unfair.',
               'A question can contain an accusation instead of seeking truth.',
               'Correct the premise before answering.'],
  'caption': 'Loaded Questions: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['You may be seeing leading questions.',
               'The wording pushes you toward the answer they want.',
               'A fair question leaves room for your real view.',
               'Restate the question in neutral words.'],
  'caption': 'Leading Questions: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['Watch for leading questions.',
               'The wording pushes you toward the answer they want.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Restate the question in neutral words.'],
  'caption': 'Leading Questions: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['This can look like leading questions.',
               'The wording pushes you toward the answer they want.',
               'A fair question leaves room for your real view.',
               'You are allowed to slow the moment down.'],
  'caption': 'Leading Questions: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['A pattern called leading questions can leave you doubting yourself.',
               'The wording pushes you toward the answer they want.',
               'A fair question leaves room for your real view.',
               'Restate the question in neutral words.'],
  'caption': 'Leading Questions: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['You may be seeing gish gallop.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Speed is not evidence.',
               'Choose one claim and ask for support.'],
  'caption': 'Gish Gallop: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['Watch for gish gallop.',
               'So many claims arrive at once that you cannot examine any of them.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Choose one claim and ask for support.'],
  'caption': 'Gish Gallop: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['This can look like gish gallop.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Speed is not evidence.',
               'You are allowed to slow the moment down.'],
  'caption': 'Gish Gallop: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['A pattern called gish gallop can leave you doubting yourself.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Speed is not evidence.',
               'Choose one claim and ask for support.'],
  'caption': 'Gish Gallop: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['You may be seeing whataboutism.',
               'Your concern gets replaced with a different accusation about you.',
               'Two issues can exist without one erasing the other.',
               'Return gently to the original topic.'],
  'caption': 'Whataboutism: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['Watch for whataboutism.',
               'Your concern gets replaced with a different accusation about you.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Return gently to the original topic.'],
  'caption': 'Whataboutism: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['This can look like whataboutism.',
               'Your concern gets replaced with a different accusation about you.',
               'Two issues can exist without one erasing the other.',
               'You are allowed to slow the moment down.'],
  'caption': 'Whataboutism: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['A pattern called whataboutism can leave you doubting yourself.',
               'Your concern gets replaced with a different accusation about you.',
               'Two issues can exist without one erasing the other.',
               'Return gently to the original topic.'],
  'caption': 'Whataboutism: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['You may be seeing straw-man framing.',
               'Your actual point gets replaced with an extreme version.',
               'You deserve to be responded to accurately.',
               "Say: 'That is not what I said. My point is...'"],
  'caption': 'Straw-Man Framing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['Watch for straw-man framing.',
               'Your actual point gets replaced with an extreme version.',
               'One moment is not proof. A repeated pattern deserves attention.',
               "Say: 'That is not what I said. My point is...'"],
  'caption': 'Straw-Man Framing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['This can look like straw-man framing.',
               'Your actual point gets replaced with an extreme version.',
               'You deserve to be responded to accurately.',
               'You are allowed to slow the moment down.'],
  'caption': 'Straw-Man Framing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['A pattern called straw-man framing can leave you doubting yourself.',
               'Your actual point gets replaced with an extreme version.',
               'You deserve to be responded to accurately.',
               "Say: 'That is not what I said. My point is...'"],
  'caption': 'Straw-Man Framing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['You may be seeing appeal to pity.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Compassion and accountability can stand together.',
               'Acknowledge the pain, then name the behavior.'],
  'caption': 'Appeal To Pity: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['Watch for appeal to pity.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Acknowledge the pain, then name the behavior.'],
  'caption': 'Appeal To Pity: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['This can look like appeal to pity.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Compassion and accountability can stand together.',
               'You are allowed to slow the moment down.'],
  'caption': 'Appeal To Pity: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['A pattern called appeal to pity can leave you doubting yourself.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Compassion and accountability can stand together.',
               'Acknowledge the pain, then name the behavior.'],
  'caption': 'Appeal To Pity: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['You may be seeing moral licensing.',
               'One good act is used to excuse a repeated harmful act.',
               'Being kind sometimes does not cancel a pattern.',
               'Look at the full behavior, not one highlight.'],
  'caption': 'Moral Licensing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['Watch for moral licensing.',
               'One good act is used to excuse a repeated harmful act.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Look at the full behavior, not one highlight.'],
  'caption': 'Moral Licensing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['This can look like moral licensing.',
               'One good act is used to excuse a repeated harmful act.',
               'Being kind sometimes does not cancel a pattern.',
               'You are allowed to slow the moment down.'],
  'caption': 'Moral Licensing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['A pattern called moral licensing can leave you doubting yourself.',
               'One good act is used to excuse a repeated harmful act.',
               'Being kind sometimes does not cancel a pattern.',
               'Look at the full behavior, not one highlight.'],
  'caption': 'Moral Licensing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['You may be seeing trauma dumping for leverage.',
               'A painful story appears only when you set a limit.',
               "Someone's pain matters, but your boundary still matters too.",
               'Offer care without abandoning your limit.'],
  'caption': 'Trauma Dumping For Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['Watch for trauma dumping for leverage.',
               'A painful story appears only when you set a limit.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Offer care without abandoning your limit.'],
  'caption': 'Trauma Dumping For Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['This can look like trauma dumping for leverage.',
               'A painful story appears only when you set a limit.',
               "Someone's pain matters, but your boundary still matters too.",
               'You are allowed to slow the moment down.'],
  'caption': 'Trauma Dumping For Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['A pattern called trauma dumping for leverage can leave you doubting yourself.',
               'A painful story appears only when you set a limit.',
               "Someone's pain matters, but your boundary still matters too.",
               'Offer care without abandoning your limit.'],
  'caption': 'Trauma Dumping For Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['You may be seeing manufactured crisis.',
               'Every request becomes an emergency that only you can solve.',
               'Constant crisis can train you to ignore your own needs.',
               'Check whether the urgency is real and shared.'],
  'caption': 'Manufactured Crisis: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['Watch for manufactured crisis.',
               'Every request becomes an emergency that only you can solve.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Check whether the urgency is real and shared.'],
  'caption': 'Manufactured Crisis: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['This can look like manufactured crisis.',
               'Every request becomes an emergency that only you can solve.',
               'Constant crisis can train you to ignore your own needs.',
               'You are allowed to slow the moment down.'],
  'caption': 'Manufactured Crisis: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['A pattern called manufactured crisis can leave you doubting yourself.',
               'Every request becomes an emergency that only you can solve.',
               'Constant crisis can train you to ignore your own needs.',
               'Check whether the urgency is real and shared.'],
  'caption': 'Manufactured Crisis: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['You may be seeing time pressure.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Good decisions can usually survive a short pause.',
               "Use: 'I do not decide important things on the spot.'"],
  'caption': 'Time Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['Watch for time pressure.',
               'You are denied time to read, compare, or ask someone you trust.',
               'One moment is not proof. A repeated pattern deserves attention.',
               "Use: 'I do not decide important things on the spot.'"],
  'caption': 'Time Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['This can look like time pressure.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Good decisions can usually survive a short pause.',
               'You are allowed to slow the moment down.'],
  'caption': 'Time Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['A pattern called time pressure can leave you doubting yourself.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Good decisions can usually survive a short pause.',
               "Use: 'I do not decide important things on the spot.'"],
  'caption': 'Time Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['You may be seeing information withholding.',
               'Key details arrive after you have already agreed.',
               'Informed consent needs the relevant facts first.',
               'Ask what has not been disclosed yet.'],
  'caption': 'Information Withholding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['Watch for information withholding.',
               'Key details arrive after you have already agreed.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Ask what has not been disclosed yet.'],
  'caption': 'Information Withholding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['This can look like information withholding.',
               'Key details arrive after you have already agreed.',
               'Informed consent needs the relevant facts first.',
               'You are allowed to slow the moment down.'],
  'caption': 'Information Withholding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['A pattern called information withholding can leave you doubting yourself.',
               'Key details arrive after you have already agreed.',
               'Informed consent needs the relevant facts first.',
               'Ask what has not been disclosed yet.'],
  'caption': 'Information Withholding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['You may be seeing selective evidence.',
               'Only facts that support one conclusion are repeated.',
               'A fair picture includes inconvenient facts too.',
               'Look for what is missing, not only what is shown.'],
  'caption': 'Selective Evidence: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['Watch for selective evidence.',
               'Only facts that support one conclusion are repeated.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Look for what is missing, not only what is shown.'],
  'caption': 'Selective Evidence: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['This can look like selective evidence.',
               'Only facts that support one conclusion are repeated.',
               'A fair picture includes inconvenient facts too.',
               'You are allowed to slow the moment down.'],
  'caption': 'Selective Evidence: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['A pattern called selective evidence can leave you doubting yourself.',
               'Only facts that support one conclusion are repeated.',
               'A fair picture includes inconvenient facts too.',
               'Look for what is missing, not only what is shown.'],
  'caption': 'Selective Evidence: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['You may be seeing cherry-picked statistics.',
               'One number is used without context to make a claim feel final.',
               'Numbers need a source, comparison, and timeframe.',
               'Ask where the figure came from and what it leaves out.'],
  'caption': 'Cherry-Picked Statistics: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['Watch for cherry-picked statistics.',
               'One number is used without context to make a claim feel final.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Ask where the figure came from and what it leaves out.'],
  'caption': 'Cherry-Picked Statistics: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['This can look like cherry-picked statistics.',
               'One number is used without context to make a claim feel final.',
               'Numbers need a source, comparison, and timeframe.',
               'You are allowed to slow the moment down.'],
  'caption': 'Cherry-Picked Statistics: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['A pattern called cherry-picked statistics can leave you doubting yourself.',
               'One number is used without context to make a claim feel final.',
               'Numbers need a source, comparison, and timeframe.',
               'Ask where the figure came from and what it leaves out.'],
  'caption': 'Cherry-Picked Statistics: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['You may be seeing fake consensus.',
               'They claim others privately agree with them but name no one.',
               'Unnamed agreement is not proof.',
               'Speak directly with people instead of chasing rumors.'],
  'caption': 'Fake Consensus: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['Watch for fake consensus.',
               'They claim others privately agree with them but name no one.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Speak directly with people instead of chasing rumors.'],
  'caption': 'Fake Consensus: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['This can look like fake consensus.',
               'They claim others privately agree with them but name no one.',
               'Unnamed agreement is not proof.',
               'You are allowed to slow the moment down.'],
  'caption': 'Fake Consensus: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['A pattern called fake consensus can leave you doubting yourself.',
               'They claim others privately agree with them but name no one.',
               'Unnamed agreement is not proof.',
               'Speak directly with people instead of chasing rumors.'],
  'caption': 'Fake Consensus: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['You may be seeing bandwagon shame.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Belonging should not require surrendering your judgment.',
               "Let your values choose, not the crowd's mood."],
  'caption': 'Bandwagon Shame: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['Watch for bandwagon shame.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'One moment is not proof. A repeated pattern deserves attention.',
               "Let your values choose, not the crowd's mood."],
  'caption': 'Bandwagon Shame: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['This can look like bandwagon shame.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Belonging should not require surrendering your judgment.',
               'You are allowed to slow the moment down.'],
  'caption': 'Bandwagon Shame: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['A pattern called bandwagon shame can leave you doubting yourself.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Belonging should not require surrendering your judgment.',
               "Let your values choose, not the crowd's mood."],
  'caption': 'Bandwagon Shame: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['You may be seeing purity tests.',
               'One imperfect choice is used to label you disloyal or bad.',
               'Healthy relationships allow complexity and growth.',
               'Reject labels and discuss the actual decision.'],
  'caption': 'Purity Tests: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['Watch for purity tests.',
               'One imperfect choice is used to label you disloyal or bad.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Reject labels and discuss the actual decision.'],
  'caption': 'Purity Tests: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['This can look like purity tests.',
               'One imperfect choice is used to label you disloyal or bad.',
               'Healthy relationships allow complexity and growth.',
               'You are allowed to slow the moment down.'],
  'caption': 'Purity Tests: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['A pattern called purity tests can leave you doubting yourself.',
               'One imperfect choice is used to label you disloyal or bad.',
               'Healthy relationships allow complexity and growth.',
               'Reject labels and discuss the actual decision.'],
  'caption': 'Purity Tests: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['You may be seeing moving deadlines.',
               'The deadline changes whenever you need time to think.',
               'Unstable deadlines can keep you anxious and compliant.',
               'Set your own decision time where possible.'],
  'caption': 'Moving Deadlines: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['Watch for moving deadlines.',
               'The deadline changes whenever you need time to think.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Set your own decision time where possible.'],
  'caption': 'Moving Deadlines: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['This can look like moving deadlines.',
               'The deadline changes whenever you need time to think.',
               'Unstable deadlines can keep you anxious and compliant.',
               'You are allowed to slow the moment down.'],
  'caption': 'Moving Deadlines: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['A pattern called moving deadlines can leave you doubting yourself.',
               'The deadline changes whenever you need time to think.',
               'Unstable deadlines can keep you anxious and compliant.',
               'Set your own decision time where possible.'],
  'caption': 'Moving Deadlines: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['You may be seeing bait-and-switch.',
               'What was promised is not what appears after you commit.',
               'You are allowed to walk away from changed terms.',
               'Compare the offer to the original promise.'],
  'caption': 'Bait-And-Switch: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['Watch for bait-and-switch.',
               'What was promised is not what appears after you commit.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Compare the offer to the original promise.'],
  'caption': 'Bait-And-Switch: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['This can look like bait-and-switch.',
               'What was promised is not what appears after you commit.',
               'You are allowed to walk away from changed terms.',
               'You are allowed to slow the moment down.'],
  'caption': 'Bait-And-Switch: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['A pattern called bait-and-switch can leave you doubting yourself.',
               'What was promised is not what appears after you commit.',
               'You are allowed to walk away from changed terms.',
               'Compare the offer to the original promise.'],
  'caption': 'Bait-And-Switch: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['You may be seeing future pacing.',
               'A vivid future is described to make you commit in the present.',
               'A beautiful story is not evidence of a safe pattern.',
               "Ground yourself in today's actions."],
  'caption': 'Future Pacing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['Watch for future pacing.',
               'A vivid future is described to make you commit in the present.',
               'One moment is not proof. A repeated pattern deserves attention.',
               "Ground yourself in today's actions."],
  'caption': 'Future Pacing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['This can look like future pacing.',
               'A vivid future is described to make you commit in the present.',
               'A beautiful story is not evidence of a safe pattern.',
               'You are allowed to slow the moment down.'],
  'caption': 'Future Pacing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['A pattern called future pacing can leave you doubting yourself.',
               'A vivid future is described to make you commit in the present.',
               'A beautiful story is not evidence of a safe pattern.',
               "Ground yourself in today's actions."],
  'caption': 'Future Pacing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['You may be seeing identity pressure.',
               'They say a good friend, parent, worker, or partner would obey.',
               "Your identity is bigger than one person's demand.",
               'Define your own values before answering.'],
  'caption': 'Identity Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['Watch for identity pressure.',
               'They say a good friend, parent, worker, or partner would obey.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Define your own values before answering.'],
  'caption': 'Identity Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['This can look like identity pressure.',
               'They say a good friend, parent, worker, or partner would obey.',
               "Your identity is bigger than one person's demand.",
               'You are allowed to slow the moment down.'],
  'caption': 'Identity Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['A pattern called identity pressure can leave you doubting yourself.',
               'They say a good friend, parent, worker, or partner would obey.',
               "Your identity is bigger than one person's demand.",
               'Define your own values before answering.'],
  'caption': 'Identity Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['You may be seeing labeling.',
               'A single mistake becomes a permanent name for who you are.',
               'Labels can silence learning and honest discussion.',
               'Ask for specific behavior instead of character attacks.'],
  'caption': 'Labeling: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['Watch for labeling.',
               'A single mistake becomes a permanent name for who you are.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Ask for specific behavior instead of character attacks.'],
  'caption': 'Labeling: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['This can look like labeling.',
               'A single mistake becomes a permanent name for who you are.',
               'Labels can silence learning and honest discussion.',
               'You are allowed to slow the moment down.'],
  'caption': 'Labeling: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['A pattern called labeling can leave you doubting yourself.',
               'A single mistake becomes a permanent name for who you are.',
               'Labels can silence learning and honest discussion.',
               'Ask for specific behavior instead of character attacks.'],
  'caption': 'Labeling: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['You may be seeing projection.',
               'They accuse you of the behavior they keep showing.',
               'An accusation is not automatically a fact.',
               'Focus on observable actions and dates.'],
  'caption': 'Projection: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['Watch for projection.',
               'They accuse you of the behavior they keep showing.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Focus on observable actions and dates.'],
  'caption': 'Projection: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['This can look like projection.',
               'They accuse you of the behavior they keep showing.',
               'An accusation is not automatically a fact.',
               'You are allowed to slow the moment down.'],
  'caption': 'Projection: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['A pattern called projection can leave you doubting yourself.',
               'They accuse you of the behavior they keep showing.',
               'An accusation is not automatically a fact.',
               'Focus on observable actions and dates.'],
  'caption': 'Projection: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['You may be seeing confession fishing.',
               'They keep asking until you say something just to end the pressure.',
               'Relief is not the same as voluntary agreement.',
               'Take a break before answering loaded questions.'],
  'caption': 'Confession Fishing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['Watch for confession fishing.',
               'They keep asking until you say something just to end the pressure.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Take a break before answering loaded questions.'],
  'caption': 'Confession Fishing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['This can look like confession fishing.',
               'They keep asking until you say something just to end the pressure.',
               'Relief is not the same as voluntary agreement.',
               'You are allowed to slow the moment down.'],
  'caption': 'Confession Fishing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['A pattern called confession fishing can leave you doubting yourself.',
               'They keep asking until you say something just to end the pressure.',
               'Relief is not the same as voluntary agreement.',
               'Take a break before answering loaded questions.'],
  'caption': 'Confession Fishing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['You may be seeing forced choice.',
               'You are pushed to pick before you understand the consequences.',
               'A rushed choice may not be a free choice.',
               'Ask for time, details, and another option.'],
  'caption': 'Forced Choice: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['Watch for forced choice.',
               'You are pushed to pick before you understand the consequences.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Ask for time, details, and another option.'],
  'caption': 'Forced Choice: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['This can look like forced choice.',
               'You are pushed to pick before you understand the consequences.',
               'A rushed choice may not be a free choice.',
               'You are allowed to slow the moment down.'],
  'caption': 'Forced Choice: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['A pattern called forced choice can leave you doubting yourself.',
               'You are pushed to pick before you understand the consequences.',
               'A rushed choice may not be a free choice.',
               'Ask for time, details, and another option.'],
  'caption': 'Forced Choice: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['You may be seeing conditional apology.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'A repair names the action and its impact.',
               "Ask: 'What will change next time?'"],
  'caption': 'Conditional Apology: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['Watch for conditional apology.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'One moment is not proof. A repeated pattern deserves attention.',
               "Ask: 'What will change next time?'"],
  'caption': 'Conditional Apology: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['This can look like conditional apology.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'A repair names the action and its impact.',
               'You are allowed to slow the moment down.'],
  'caption': 'Conditional Apology: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['A pattern called conditional apology can leave you doubting yourself.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'A repair names the action and its impact.',
               "Ask: 'What will change next time?'"],
  'caption': 'Conditional Apology: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['You may be seeing apology flooding.',
               'Many apologies arrive, but the behavior never changes.',
               'Words of regret need follow-through.',
               'Watch the pattern after the apology.'],
  'caption': 'Apology Flooding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['Watch for apology flooding.',
               'Many apologies arrive, but the behavior never changes.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Watch the pattern after the apology.'],
  'caption': 'Apology Flooding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['This can look like apology flooding.',
               'Many apologies arrive, but the behavior never changes.',
               'Words of regret need follow-through.',
               'You are allowed to slow the moment down.'],
  'caption': 'Apology Flooding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['A pattern called apology flooding can leave you doubting yourself.',
               'Many apologies arrive, but the behavior never changes.',
               'Words of regret need follow-through.',
               'Watch the pattern after the apology.'],
  'caption': 'Apology Flooding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['You may be seeing premature forgiveness pressure.',
               'You are urged to forgive before you feel heard or safe.',
               'Forgiveness cannot be demanded on a schedule.',
               'Take the time you need to decide what repair means.'],
  'caption': 'Premature Forgiveness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['Watch for premature forgiveness pressure.',
               'You are urged to forgive before you feel heard or safe.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Take the time you need to decide what repair means.'],
  'caption': 'Premature Forgiveness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['This can look like premature forgiveness pressure.',
               'You are urged to forgive before you feel heard or safe.',
               'Forgiveness cannot be demanded on a schedule.',
               'You are allowed to slow the moment down.'],
  'caption': 'Premature Forgiveness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['A pattern called premature forgiveness pressure can leave you doubting yourself.',
               'You are urged to forgive before you feel heard or safe.',
               'Forgiveness cannot be demanded on a schedule.',
               'Take the time you need to decide what repair means.'],
  'caption': 'Premature Forgiveness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['You may be seeing forced positivity.',
               'Your concern is called negative before anyone considers it.',
               'Hope is healthy; denial is not.',
               'Name the concern clearly and calmly.'],
  'caption': 'Forced Positivity: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['Watch for forced positivity.',
               'Your concern is called negative before anyone considers it.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Name the concern clearly and calmly.'],
  'caption': 'Forced Positivity: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['This can look like forced positivity.',
               'Your concern is called negative before anyone considers it.',
               'Hope is healthy; denial is not.',
               'You are allowed to slow the moment down.'],
  'caption': 'Forced Positivity: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['A pattern called forced positivity can leave you doubting yourself.',
               'Your concern is called negative before anyone considers it.',
               'Hope is healthy; denial is not.',
               'Name the concern clearly and calmly.'],
  'caption': 'Forced Positivity: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['You may be seeing toxic gratitude.',
               'You are told to be grateful so you will stop naming harm.',
               'Gratitude and honest feedback can coexist.',
               'Appreciate what is real without denying what hurts.'],
  'caption': 'Toxic Gratitude: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['Watch for toxic gratitude.',
               'You are told to be grateful so you will stop naming harm.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Appreciate what is real without denying what hurts.'],
  'caption': 'Toxic Gratitude: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['This can look like toxic gratitude.',
               'You are told to be grateful so you will stop naming harm.',
               'Gratitude and honest feedback can coexist.',
               'You are allowed to slow the moment down.'],
  'caption': 'Toxic Gratitude: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['A pattern called toxic gratitude can leave you doubting yourself.',
               'You are told to be grateful so you will stop naming harm.',
               'Gratitude and honest feedback can coexist.',
               'Appreciate what is real without denying what hurts.'],
  'caption': 'Toxic Gratitude: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['You may be seeing emotional blackmail.',
               'Love, approval, or safety is tied to doing what they want.',
               'Care should not be a weapon.',
               'Reach for support if refusal feels dangerous.'],
  'caption': 'Emotional Blackmail: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['Watch for emotional blackmail.',
               'Love, approval, or safety is tied to doing what they want.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Reach for support if refusal feels dangerous.'],
  'caption': 'Emotional Blackmail: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['This can look like emotional blackmail.',
               'Love, approval, or safety is tied to doing what they want.',
               'Care should not be a weapon.',
               'You are allowed to slow the moment down.'],
  'caption': 'Emotional Blackmail: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['A pattern called emotional blackmail can leave you doubting yourself.',
               'Love, approval, or safety is tied to doing what they want.',
               'Care should not be a weapon.',
               'Reach for support if refusal feels dangerous.'],
  'caption': 'Emotional Blackmail: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['You may be seeing coercive texting.',
               'Repeated calls or messages make silence feel impossible.',
               'Availability is not owed every minute.',
               'Mute, pause, and respond when you choose.'],
  'caption': 'Coercive Texting: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['Watch for coercive texting.',
               'Repeated calls or messages make silence feel impossible.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Mute, pause, and respond when you choose.'],
  'caption': 'Coercive Texting: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['This can look like coercive texting.',
               'Repeated calls or messages make silence feel impossible.',
               'Availability is not owed every minute.',
               'You are allowed to slow the moment down.'],
  'caption': 'Coercive Texting: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['A pattern called coercive texting can leave you doubting yourself.',
               'Repeated calls or messages make silence feel impossible.',
               'Availability is not owed every minute.',
               'Mute, pause, and respond when you choose.'],
  'caption': 'Coercive Texting: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['You may be seeing digital surveillance.',
               'Passwords, locations, or private messages are demanded as proof.',
               'Trust is not built through constant access.',
               'Review your privacy settings and boundaries.'],
  'caption': 'Digital Surveillance: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['Watch for digital surveillance.',
               'Passwords, locations, or private messages are demanded as proof.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Review your privacy settings and boundaries.'],
  'caption': 'Digital Surveillance: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['This can look like digital surveillance.',
               'Passwords, locations, or private messages are demanded as proof.',
               'Trust is not built through constant access.',
               'You are allowed to slow the moment down.'],
  'caption': 'Digital Surveillance: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['A pattern called digital surveillance can leave you doubting yourself.',
               'Passwords, locations, or private messages are demanded as proof.',
               'Trust is not built through constant access.',
               'Review your privacy settings and boundaries.'],
  'caption': 'Digital Surveillance: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['You may be seeing password pressure.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'Privacy is normal, even in close relationships.',
               'Keep accounts secure and discuss trust directly.'],
  'caption': 'Password Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['Watch for password pressure.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Keep accounts secure and discuss trust directly.'],
  'caption': 'Password Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['This can look like password pressure.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'Privacy is normal, even in close relationships.',
               'You are allowed to slow the moment down.'],
  'caption': 'Password Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['A pattern called password pressure can leave you doubting yourself.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'Privacy is normal, even in close relationships.',
               'Keep accounts secure and discuss trust directly.'],
  'caption': 'Password Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['You may be seeing location tracking pressure.',
               'Being tracked is called love, safety, or loyalty.',
               'Safety planning requires consent, not control.',
               'Choose who can see your location and when.'],
  'caption': 'Location Tracking Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['Watch for location tracking pressure.',
               'Being tracked is called love, safety, or loyalty.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Choose who can see your location and when.'],
  'caption': 'Location Tracking Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['This can look like location tracking pressure.',
               'Being tracked is called love, safety, or loyalty.',
               'Safety planning requires consent, not control.',
               'You are allowed to slow the moment down.'],
  'caption': 'Location Tracking Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['A pattern called location tracking pressure can leave you doubting yourself.',
               'Being tracked is called love, safety, or loyalty.',
               'Safety planning requires consent, not control.',
               'Choose who can see your location and when.'],
  'caption': 'Location Tracking Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['You may be seeing public call-outs.',
               'A private issue is exposed to make you comply from embarrassment.',
               'Public shame discourages honest repair.',
               'Step away and ask for a private conversation.'],
  'caption': 'Public Call-Outs: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['Watch for public call-outs.',
               'A private issue is exposed to make you comply from embarrassment.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Step away and ask for a private conversation.'],
  'caption': 'Public Call-Outs: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['This can look like public call-outs.',
               'A private issue is exposed to make you comply from embarrassment.',
               'Public shame discourages honest repair.',
               'You are allowed to slow the moment down.'],
  'caption': 'Public Call-Outs: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['A pattern called public call-outs can leave you doubting yourself.',
               'A private issue is exposed to make you comply from embarrassment.',
               'Public shame discourages honest repair.',
               'Step away and ask for a private conversation.'],
  'caption': 'Public Call-Outs: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['You may be seeing group pile-on.',
               'Others are brought in to make one person feel outnumbered.',
               'More voices do not make pressure fair.',
               'Ask to discuss the issue one-to-one or with neutral support.'],
  'caption': 'Group Pile-On: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['Watch for group pile-on.',
               'Others are brought in to make one person feel outnumbered.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Ask to discuss the issue one-to-one or with neutral support.'],
  'caption': 'Group Pile-On: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['This can look like group pile-on.',
               'Others are brought in to make one person feel outnumbered.',
               'More voices do not make pressure fair.',
               'You are allowed to slow the moment down.'],
  'caption': 'Group Pile-On: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['A pattern called group pile-on can leave you doubting yourself.',
               'Others are brought in to make one person feel outnumbered.',
               'More voices do not make pressure fair.',
               'Ask to discuss the issue one-to-one or with neutral support.'],
  'caption': 'Group Pile-On: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['You may be seeing proxy fighting.',
               'Someone sends friends or relatives to argue their case.',
               'Direct conflict needs direct communication.',
               'Avoid debating through messengers.'],
  'caption': 'Proxy Fighting: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['Watch for proxy fighting.',
               'Someone sends friends or relatives to argue their case.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Avoid debating through messengers.'],
  'caption': 'Proxy Fighting: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['This can look like proxy fighting.',
               'Someone sends friends or relatives to argue their case.',
               'Direct conflict needs direct communication.',
               'You are allowed to slow the moment down.'],
  'caption': 'Proxy Fighting: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['A pattern called proxy fighting can leave you doubting yourself.',
               'Someone sends friends or relatives to argue their case.',
               'Direct conflict needs direct communication.',
               'Avoid debating through messengers.'],
  'caption': 'Proxy Fighting: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['You may be seeing flying monkeys.',
               'Third parties repeat pressure or rumors for someone else.',
               'You do not have to explain yourself to every messenger.',
               'Use one calm boundary and disengage.'],
  'caption': 'Flying Monkeys: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['Watch for flying monkeys.',
               'Third parties repeat pressure or rumors for someone else.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Use one calm boundary and disengage.'],
  'caption': 'Flying Monkeys: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['This can look like flying monkeys.',
               'Third parties repeat pressure or rumors for someone else.',
               'You do not have to explain yourself to every messenger.',
               'You are allowed to slow the moment down.'],
  'caption': 'Flying Monkeys: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['A pattern called flying monkeys can leave you doubting yourself.',
               'Third parties repeat pressure or rumors for someone else.',
               'You do not have to explain yourself to every messenger.',
               'Use one calm boundary and disengage.'],
  'caption': 'Flying Monkeys: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['You may be seeing hoovering.',
               'Warm messages return just as you begin creating distance.',
               'A return is not proof that the old pattern is gone.',
               'Look for sustained change, not a sudden pull.'],
  'caption': 'Hoovering: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['Watch for hoovering.',
               'Warm messages return just as you begin creating distance.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Look for sustained change, not a sudden pull.'],
  'caption': 'Hoovering: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['This can look like hoovering.',
               'Warm messages return just as you begin creating distance.',
               'A return is not proof that the old pattern is gone.',
               'You are allowed to slow the moment down.'],
  'caption': 'Hoovering: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['A pattern called hoovering can leave you doubting yourself.',
               'Warm messages return just as you begin creating distance.',
               'A return is not proof that the old pattern is gone.',
               'Look for sustained change, not a sudden pull.'],
  'caption': 'Hoovering: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['You may be seeing breadcrumbing.',
               'Tiny bits of attention keep you waiting for more.',
               'Occasional contact can create hope without commitment.',
               'Decide what consistency you need.'],
  'caption': 'Breadcrumbing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['Watch for breadcrumbing.',
               'Tiny bits of attention keep you waiting for more.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Decide what consistency you need.'],
  'caption': 'Breadcrumbing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['This can look like breadcrumbing.',
               'Tiny bits of attention keep you waiting for more.',
               'Occasional contact can create hope without commitment.',
               'You are allowed to slow the moment down.'],
  'caption': 'Breadcrumbing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['A pattern called breadcrumbing can leave you doubting yourself.',
               'Tiny bits of attention keep you waiting for more.',
               'Occasional contact can create hope without commitment.',
               'Decide what consistency you need.'],
  'caption': 'Breadcrumbing: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['You may be seeing orbiting.',
               'They stay visible online while avoiding a real conversation.',
               'Online signals are not the same as care or clarity.',
               'Protect your attention and seek direct answers.'],
  'caption': 'Orbiting: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['Watch for orbiting.',
               'They stay visible online while avoiding a real conversation.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Protect your attention and seek direct answers.'],
  'caption': 'Orbiting: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['This can look like orbiting.',
               'They stay visible online while avoiding a real conversation.',
               'Online signals are not the same as care or clarity.',
               'You are allowed to slow the moment down.'],
  'caption': 'Orbiting: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['A pattern called orbiting can leave you doubting yourself.',
               'They stay visible online while avoiding a real conversation.',
               'Online signals are not the same as care or clarity.',
               'Protect your attention and seek direct answers.'],
  'caption': 'Orbiting: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['You may be seeing jealousy bait.',
               'Another person is mentioned to make you compete for attention.',
               'Love does not require a contest.',
               'Refuse comparison and state what respect looks like.'],
  'caption': 'Jealousy Bait: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['Watch for jealousy bait.',
               'Another person is mentioned to make you compete for attention.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Refuse comparison and state what respect looks like.'],
  'caption': 'Jealousy Bait: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['This can look like jealousy bait.',
               'Another person is mentioned to make you compete for attention.',
               'Love does not require a contest.',
               'You are allowed to slow the moment down.'],
  'caption': 'Jealousy Bait: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['A pattern called jealousy bait can leave you doubting yourself.',
               'Another person is mentioned to make you compete for attention.',
               'Love does not require a contest.',
               'Refuse comparison and state what respect looks like.'],
  'caption': 'Jealousy Bait: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['You may be seeing triangulated praise.',
               'Someone praises another person mainly to make you feel inadequate.',
               'Comparison can be a tool of control.',
               'Ask for a direct request without the comparison.'],
  'caption': 'Triangulated Praise: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['Watch for triangulated praise.',
               'Someone praises another person mainly to make you feel inadequate.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Ask for a direct request without the comparison.'],
  'caption': 'Triangulated Praise: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['This can look like triangulated praise.',
               'Someone praises another person mainly to make you feel inadequate.',
               'Comparison can be a tool of control.',
               'You are allowed to slow the moment down.'],
  'caption': 'Triangulated Praise: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['A pattern called triangulated praise can leave you doubting yourself.',
               'Someone praises another person mainly to make you feel inadequate.',
               'Comparison can be a tool of control.',
               'Ask for a direct request without the comparison.'],
  'caption': 'Triangulated Praise: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['You may be seeing silent punishment.',
               'Contact disappears after you express a need or limit.',
               'A respectful pause includes communication and return.',
               'Do not chase clarity at the cost of your boundary.'],
  'caption': 'Silent Punishment: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['Watch for silent punishment.',
               'Contact disappears after you express a need or limit.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Do not chase clarity at the cost of your boundary.'],
  'caption': 'Silent Punishment: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['This can look like silent punishment.',
               'Contact disappears after you express a need or limit.',
               'A respectful pause includes communication and return.',
               'You are allowed to slow the moment down.'],
  'caption': 'Silent Punishment: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['A pattern called silent punishment can leave you doubting yourself.',
               'Contact disappears after you express a need or limit.',
               'A respectful pause includes communication and return.',
               'Do not chase clarity at the cost of your boundary.'],
  'caption': 'Silent Punishment: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['You may be seeing rage as leverage.',
               'Anger becomes so big that everyone else must give in.',
               'Big emotion does not make a demand reasonable.',
               'Leave the conversation if you feel unsafe.'],
  'caption': 'Rage As Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['Watch for rage as leverage.',
               'Anger becomes so big that everyone else must give in.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Leave the conversation if you feel unsafe.'],
  'caption': 'Rage As Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['This can look like rage as leverage.',
               'Anger becomes so big that everyone else must give in.',
               'Big emotion does not make a demand reasonable.',
               'You are allowed to slow the moment down.'],
  'caption': 'Rage As Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['A pattern called rage as leverage can leave you doubting yourself.',
               'Anger becomes so big that everyone else must give in.',
               'Big emotion does not make a demand reasonable.',
               'Leave the conversation if you feel unsafe.'],
  'caption': 'Rage As Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['You may be seeing intimidating body language.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'Fear changes whether a choice is freely made.',
               'Create space and seek immediate help if needed.'],
  'caption': 'Intimidating Body Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['Watch for intimidating body language.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Create space and seek immediate help if needed.'],
  'caption': 'Intimidating Body Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['This can look like intimidating body language.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'Fear changes whether a choice is freely made.',
               'You are allowed to slow the moment down.'],
  'caption': 'Intimidating Body Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['A pattern called intimidating body language can leave you doubting yourself.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'Fear changes whether a choice is freely made.',
               'Create space and seek immediate help if needed.'],
  'caption': 'Intimidating Body Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['You may be seeing threatening self-harm for control.',
               'A threat of self-harm appears when you try to leave or say no.',
               'Take threats seriously without becoming the only responder.',
               'Contact emergency or crisis support and tell a trusted person.'],
  'caption': 'Threatening Self-Harm For Control: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['Watch for threatening self-harm for control.',
               'A threat of self-harm appears when you try to leave or say no.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Contact emergency or crisis support and tell a trusted person.'],
  'caption': 'Threatening Self-Harm For Control: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['This can look like threatening self-harm for control.',
               'A threat of self-harm appears when you try to leave or say no.',
               'Take threats seriously without becoming the only responder.',
               'You are allowed to slow the moment down.'],
  'caption': 'Threatening Self-Harm For Control: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['A pattern called threatening self-harm for control can leave you doubting yourself.',
               'A threat of self-harm appears when you try to leave or say no.',
               'Take threats seriously without becoming the only responder.',
               'Contact emergency or crisis support and tell a trusted person.'],
  'caption': 'Threatening Self-Harm For Control: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['You may be seeing threatening exposure.',
               'Private details are used to force silence or compliance.',
               'Blackmail is not care or conflict resolution.',
               'Save evidence and seek trusted or professional support.'],
  'caption': 'Threatening Exposure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['Watch for threatening exposure.',
               'Private details are used to force silence or compliance.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Save evidence and seek trusted or professional support.'],
  'caption': 'Threatening Exposure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['This can look like threatening exposure.',
               'Private details are used to force silence or compliance.',
               'Blackmail is not care or conflict resolution.',
               'You are allowed to slow the moment down.'],
  'caption': 'Threatening Exposure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['A pattern called threatening exposure can leave you doubting yourself.',
               'Private details are used to force silence or compliance.',
               'Blackmail is not care or conflict resolution.',
               'Save evidence and seek trusted or professional support.'],
  'caption': 'Threatening Exposure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['You may be seeing reputation threats.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'Threats try to isolate you before you can get help.',
               'Document what happens and tell safe people.'],
  'caption': 'Reputation Threats: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['Watch for reputation threats.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Document what happens and tell safe people.'],
  'caption': 'Reputation Threats: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['This can look like reputation threats.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'Threats try to isolate you before you can get help.',
               'You are allowed to slow the moment down.'],
  'caption': 'Reputation Threats: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['A pattern called reputation threats can leave you doubting yourself.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'Threats try to isolate you before you can get help.',
               'Document what happens and tell safe people.'],
  'caption': 'Reputation Threats: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['You may be seeing legal-sounding intimidation.',
               'Official words are used to scare you without clear facts.',
               'A confident claim is not legal advice.',
               'Check information with a qualified, independent source.'],
  'caption': 'Legal-Sounding Intimidation: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['Watch for legal-sounding intimidation.',
               'Official words are used to scare you without clear facts.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Check information with a qualified, independent source.'],
  'caption': 'Legal-Sounding Intimidation: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['This can look like legal-sounding intimidation.',
               'Official words are used to scare you without clear facts.',
               'A confident claim is not legal advice.',
               'You are allowed to slow the moment down.'],
  'caption': 'Legal-Sounding Intimidation: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['A pattern called legal-sounding intimidation can leave you doubting yourself.',
               'Official words are used to scare you without clear facts.',
               'A confident claim is not legal advice.',
               'Check information with a qualified, independent source.'],
  'caption': 'Legal-Sounding Intimidation: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['You may be seeing financial guilt.',
               'Money spent on you is brought up to control your choices.',
               'Support should not create ownership over you.',
               'Separate appreciation from obligation.'],
  'caption': 'Financial Guilt: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['Watch for financial guilt.',
               'Money spent on you is brought up to control your choices.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Separate appreciation from obligation.'],
  'caption': 'Financial Guilt: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['This can look like financial guilt.',
               'Money spent on you is brought up to control your choices.',
               'Support should not create ownership over you.',
               'You are allowed to slow the moment down.'],
  'caption': 'Financial Guilt: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['A pattern called financial guilt can leave you doubting yourself.',
               'Money spent on you is brought up to control your choices.',
               'Support should not create ownership over you.',
               'Separate appreciation from obligation.'],
  'caption': 'Financial Guilt: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['You may be seeing financial secrecy.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'Shared financial decisions need clear information.',
               'Keep copies of records and ask direct questions.'],
  'caption': 'Financial Secrecy: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['Watch for financial secrecy.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Keep copies of records and ask direct questions.'],
  'caption': 'Financial Secrecy: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['This can look like financial secrecy.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'Shared financial decisions need clear information.',
               'You are allowed to slow the moment down.'],
  'caption': 'Financial Secrecy: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['A pattern called financial secrecy can leave you doubting yourself.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'Shared financial decisions need clear information.',
               'Keep copies of records and ask direct questions.'],
  'caption': 'Financial Secrecy: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['You may be seeing career sabotage.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'Support should expand your options, not shrink them.',
               'Notice who benefits when your independence gets smaller.'],
  'caption': 'Career Sabotage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['Watch for career sabotage.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Notice who benefits when your independence gets smaller.'],
  'caption': 'Career Sabotage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['This can look like career sabotage.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'Support should expand your options, not shrink them.',
               'You are allowed to slow the moment down.'],
  'caption': 'Career Sabotage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['A pattern called career sabotage can leave you doubting yourself.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'Support should expand your options, not shrink them.',
               'Notice who benefits when your independence gets smaller.'],
  'caption': 'Career Sabotage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['You may be seeing sleep deprivation pressure.',
               'A fight is kept going until you are too tired to think.',
               'Exhaustion makes consent and problem-solving harder.',
               'Pause the conversation and return after rest.'],
  'caption': 'Sleep Deprivation Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['Watch for sleep deprivation pressure.',
               'A fight is kept going until you are too tired to think.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Pause the conversation and return after rest.'],
  'caption': 'Sleep Deprivation Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['This can look like sleep deprivation pressure.',
               'A fight is kept going until you are too tired to think.',
               'Exhaustion makes consent and problem-solving harder.',
               'You are allowed to slow the moment down.'],
  'caption': 'Sleep Deprivation Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['A pattern called sleep deprivation pressure can leave you doubting yourself.',
               'A fight is kept going until you are too tired to think.',
               'Exhaustion makes consent and problem-solving harder.',
               'Pause the conversation and return after rest.'],
  'caption': 'Sleep Deprivation Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['You may be seeing substance pressure.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'Impairment cannot create meaningful consent.',
               'Leave, call someone safe, or choose a clear no.'],
  'caption': 'Substance Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['Watch for substance pressure.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Leave, call someone safe, or choose a clear no.'],
  'caption': 'Substance Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['This can look like substance pressure.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'Impairment cannot create meaningful consent.',
               'You are allowed to slow the moment down.'],
  'caption': 'Substance Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['A pattern called substance pressure can leave you doubting yourself.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'Impairment cannot create meaningful consent.',
               'Leave, call someone safe, or choose a clear no.'],
  'caption': 'Substance Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['You may be seeing sexual coercion.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'Consent must be free, informed, and ongoing.',
               'No explanation is required; get support if you need it.'],
  'caption': 'Sexual Coercion: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['Watch for sexual coercion.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'No explanation is required; get support if you need it.'],
  'caption': 'Sexual Coercion: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['This can look like sexual coercion.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'Consent must be free, informed, and ongoing.',
               'You are allowed to slow the moment down.'],
  'caption': 'Sexual Coercion: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['A pattern called sexual coercion can leave you doubting yourself.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'Consent must be free, informed, and ongoing.',
               'No explanation is required; get support if you need it.'],
  'caption': 'Sexual Coercion: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['You may be seeing normalizing disrespect.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'Common does not mean healthy.',
               'Compare the behavior with your values and safety.'],
  'caption': 'Normalizing Disrespect: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['Watch for normalizing disrespect.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Compare the behavior with your values and safety.'],
  'caption': 'Normalizing Disrespect: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['This can look like normalizing disrespect.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'Common does not mean healthy.',
               'You are allowed to slow the moment down.'],
  'caption': 'Normalizing Disrespect: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['A pattern called normalizing disrespect can leave you doubting yourself.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'Common does not mean healthy.',
               'Compare the behavior with your values and safety.'],
  'caption': 'Normalizing Disrespect: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['You may be seeing double-bind pressure.',
               'Whatever you choose is treated as proof that you are wrong.',
               'No-win rules are designed to keep you off balance.',
               'Name the bind and step out of the argument.'],
  'caption': 'Double-Bind Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['Watch for double-bind pressure.',
               'Whatever you choose is treated as proof that you are wrong.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Name the bind and step out of the argument.'],
  'caption': 'Double-Bind Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['This can look like double-bind pressure.',
               'Whatever you choose is treated as proof that you are wrong.',
               'No-win rules are designed to keep you off balance.',
               'You are allowed to slow the moment down.'],
  'caption': 'Double-Bind Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['A pattern called double-bind pressure can leave you doubting yourself.',
               'Whatever you choose is treated as proof that you are wrong.',
               'No-win rules are designed to keep you off balance.',
               'Name the bind and step out of the argument.'],
  'caption': 'Double-Bind Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['You may be seeing learned helplessness pressure.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'Small choices can rebuild confidence and options.',
               'Tell one safe person what has been happening.'],
  'caption': 'Learned Helplessness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['Watch for learned helplessness pressure.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Tell one safe person what has been happening.'],
  'caption': 'Learned Helplessness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['This can look like learned helplessness pressure.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'Small choices can rebuild confidence and options.',
               'You are allowed to slow the moment down.'],
  'caption': 'Learned Helplessness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['A pattern called learned helplessness pressure can leave you doubting yourself.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'Small choices can rebuild confidence and options.',
               'Tell one safe person what has been happening.'],
  'caption': 'Learned Helplessness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['You may be seeing dependency building.',
               'Your outside support, skills, or resources slowly get reduced.',
               'Independence is protective, not disloyal.',
               'Keep contacts, documents, and practical options accessible.'],
  'caption': 'Dependency Building: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['Watch for dependency building.',
               'Your outside support, skills, or resources slowly get reduced.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Keep contacts, documents, and practical options accessible.'],
  'caption': 'Dependency Building: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['This can look like dependency building.',
               'Your outside support, skills, or resources slowly get reduced.',
               'Independence is protective, not disloyal.',
               'You are allowed to slow the moment down.'],
  'caption': 'Dependency Building: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['A pattern called dependency building can leave you doubting yourself.',
               'Your outside support, skills, or resources slowly get reduced.',
               'Independence is protective, not disloyal.',
               'Keep contacts, documents, and practical options accessible.'],
  'caption': 'Dependency Building: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Approval Addiction',
  'definition': 'Praise arrives only when you ignore your own needs.',
  'benefits': ['You may be seeing approval addiction.',
               'Praise arrives only when you ignore your own needs.',
               'You do not need to earn basic respect.',
               'Ask what you want before seeking approval.'],
  'caption': 'Approval Addiction: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Approval Addiction',
  'definition': 'Praise arrives only when you ignore your own needs.',
  'benefits': ['Watch for approval addiction.',
               'Praise arrives only when you ignore your own needs.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Ask what you want before seeking approval.'],
  'caption': 'Approval Addiction: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Approval Addiction',
  'definition': 'Praise arrives only when you ignore your own needs.',
  'benefits': ['This can look like approval addiction.',
               'Praise arrives only when you ignore your own needs.',
               'You do not need to earn basic respect.',
               'You are allowed to slow the moment down.'],
  'caption': 'Approval Addiction: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Approval Addiction',
  'definition': 'Praise arrives only when you ignore your own needs.',
  'benefits': ['A pattern called approval addiction can leave you doubting yourself.',
               'Praise arrives only when you ignore your own needs.',
               'You do not need to earn basic respect.',
               'Ask what you want before seeking approval.'],
  'caption': 'Approval Addiction: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Accountability',
  'definition': 'You must apologize in detail while they never repair anything.',
  'benefits': ['You may be seeing selective accountability.',
               'You must apologize in detail while they never repair anything.',
               'Accountability should not be one-sided.',
               'Ask for mutual ownership of specific actions.'],
  'caption': 'Selective Accountability: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Accountability',
  'definition': 'You must apologize in detail while they never repair anything.',
  'benefits': ['Watch for selective accountability.',
               'You must apologize in detail while they never repair anything.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Ask for mutual ownership of specific actions.'],
  'caption': 'Selective Accountability: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Accountability',
  'definition': 'You must apologize in detail while they never repair anything.',
  'benefits': ['This can look like selective accountability.',
               'You must apologize in detail while they never repair anything.',
               'Accountability should not be one-sided.',
               'You are allowed to slow the moment down.'],
  'caption': 'Selective Accountability: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Accountability',
  'definition': 'You must apologize in detail while they never repair anything.',
  'benefits': ['A pattern called selective accountability can leave you doubting yourself.',
               'You must apologize in detail while they never repair anything.',
               'Accountability should not be one-sided.',
               'Ask for mutual ownership of specific actions.'],
  'caption': 'Selective Accountability: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Weaponized Therapy Language',
  'definition': 'Words like boundaries, triggers, or healing are used to dismiss you.',
  'benefits': ['You may be seeing weaponized therapy language.',
               'Words like boundaries, triggers, or healing are used to dismiss you.',
               'Helpful language should create clarity, not silence.',
               'Ask for plain words and concrete behavior.'],
  'caption': 'Weaponized Therapy Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Weaponized Therapy Language',
  'definition': 'Words like boundaries, triggers, or healing are used to dismiss you.',
  'benefits': ['Watch for weaponized therapy language.',
               'Words like boundaries, triggers, or healing are used to dismiss you.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Ask for plain words and concrete behavior.'],
  'caption': 'Weaponized Therapy Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Weaponized Therapy Language',
  'definition': 'Words like boundaries, triggers, or healing are used to dismiss you.',
  'benefits': ['This can look like weaponized therapy language.',
               'Words like boundaries, triggers, or healing are used to dismiss you.',
               'Helpful language should create clarity, not silence.',
               'You are allowed to slow the moment down.'],
  'caption': 'Weaponized Therapy Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Weaponized Therapy Language',
  'definition': 'Words like boundaries, triggers, or healing are used to dismiss you.',
  'benefits': ['A pattern called weaponized therapy language can leave you doubting yourself.',
               'Words like boundaries, triggers, or healing are used to dismiss you.',
               'Helpful language should create clarity, not silence.',
               'Ask for plain words and concrete behavior.'],
  'caption': 'Weaponized Therapy Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Diagnosis As Insult',
  'definition': 'A mental-health label is thrown at you to end the discussion.',
  'benefits': ['You may be seeing diagnosis as insult.',
               'A mental-health label is thrown at you to end the discussion.',
               'Labels are not substitutes for listening.',
               'Return to the behavior and its impact.'],
  'caption': 'Diagnosis As Insult: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Diagnosis As Insult',
  'definition': 'A mental-health label is thrown at you to end the discussion.',
  'benefits': ['Watch for diagnosis as insult.',
               'A mental-health label is thrown at you to end the discussion.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'Return to the behavior and its impact.'],
  'caption': 'Diagnosis As Insult: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Diagnosis As Insult',
  'definition': 'A mental-health label is thrown at you to end the discussion.',
  'benefits': ['This can look like diagnosis as insult.',
               'A mental-health label is thrown at you to end the discussion.',
               'Labels are not substitutes for listening.',
               'You are allowed to slow the moment down.'],
  'caption': 'Diagnosis As Insult: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Diagnosis As Insult',
  'definition': 'A mental-health label is thrown at you to end the discussion.',
  'benefits': ['A pattern called diagnosis as insult can leave you doubting yourself.',
               'A mental-health label is thrown at you to end the discussion.',
               'Labels are not substitutes for listening.',
               'Return to the behavior and its impact.'],
  'caption': 'Diagnosis As Insult: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Revisionist Apologies',
  'definition': 'They apologize for a version of events that leaves out the harm.',
  'benefits': ['You may be seeing revisionist apologies.',
               'They apologize for a version of events that leaves out the harm.',
               'Repair starts with an accurate account.',
               'State what happened without debating every detail.'],
  'caption': 'Revisionist Apologies: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Revisionist Apologies',
  'definition': 'They apologize for a version of events that leaves out the harm.',
  'benefits': ['Watch for revisionist apologies.',
               'They apologize for a version of events that leaves out the harm.',
               'One moment is not proof. A repeated pattern deserves attention.',
               'State what happened without debating every detail.'],
  'caption': 'Revisionist Apologies: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Revisionist Apologies',
  'definition': 'They apologize for a version of events that leaves out the harm.',
  'benefits': ['This can look like revisionist apologies.',
               'They apologize for a version of events that leaves out the harm.',
               'Repair starts with an accurate account.',
               'You are allowed to slow the moment down.'],
  'caption': 'Revisionist Apologies: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Revisionist Apologies',
  'definition': 'They apologize for a version of events that leaves out the harm.',
  'benefits': ['A pattern called revisionist apologies can leave you doubting yourself.',
               'They apologize for a version of events that leaves out the harm.',
               'Repair starts with an accurate account.',
               'State what happened without debating every detail.'],
  'caption': 'Revisionist Apologies: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\\n\\n#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['A warning sign can be foot-in-the-door pressure.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Consent to one thing is not consent to the next.',
               "Try: 'I agreed to the first part, not this.'"],
  'caption': 'Foot-In-The-Door Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['foot-in-the-door pressure can hide inside ordinary moments.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Patterns matter more than one isolated moment.',
               "Try: 'I agreed to the first part, not this.'"],
  'caption': 'Foot-In-The-Door Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['This may be foot-in-the-door pressure.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Consent to one thing is not consent to the next.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Foot-In-The-Door Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['Watch for foot-in-the-door pressure when a situation feels confusing.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Your discomfort is information, not a problem to silence.',
               "Try: 'I agreed to the first part, not this.'"],
  'caption': 'Foot-In-The-Door Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['foot-in-the-door pressure can make a reasonable boundary feel difficult.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Consent to one thing is not consent to the next.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Foot-In-The-Door Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['A warning sign can be door-in-the-face pressure.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Relief can make a request feel fair when it still is not right for you.',
               'Choose based on your capacity, not the comparison.'],
  'caption': 'Door-In-The-Face Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['door-in-the-face pressure can hide inside ordinary moments.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Patterns matter more than one isolated moment.',
               'Choose based on your capacity, not the comparison.'],
  'caption': 'Door-In-The-Face Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['This may be door-in-the-face pressure.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Relief can make a request feel fair when it still is not right for you.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Door-In-The-Face Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['Watch for door-in-the-face pressure when a situation feels confusing.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Your discomfort is information, not a problem to silence.',
               'Choose based on your capacity, not the comparison.'],
  'caption': 'Door-In-The-Face Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['door-in-the-face pressure can make a reasonable boundary feel difficult.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Relief can make a request feel fair when it still is not right for you.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Door-In-The-Face Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['A warning sign can be lowballing.',
               'The terms get worse only after you have invested time, hope, or money.',
               'An agreement can be reconsidered when the conditions change.',
               'Ask for the full terms in writing before continuing.'],
  'caption': 'Lowballing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['lowballing can hide inside ordinary moments.',
               'The terms get worse only after you have invested time, hope, or money.',
               'Patterns matter more than one isolated moment.',
               'Ask for the full terms in writing before continuing.'],
  'caption': 'Lowballing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['This may be lowballing.',
               'The terms get worse only after you have invested time, hope, or money.',
               'An agreement can be reconsidered when the conditions change.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Lowballing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['Watch for lowballing when a situation feels confusing.',
               'The terms get worse only after you have invested time, hope, or money.',
               'Your discomfort is information, not a problem to silence.',
               'Ask for the full terms in writing before continuing.'],
  'caption': 'Lowballing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['lowballing can make a reasonable boundary feel difficult.',
               'The terms get worse only after you have invested time, hope, or money.',
               'An agreement can be reconsidered when the conditions change.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Lowballing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['A warning sign can be sunk-cost pressure.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Past effort is not a reason to accept future harm.',
               'Ask what you would choose if starting today.'],
  'caption': 'Sunk-Cost Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['sunk-cost pressure can hide inside ordinary moments.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Patterns matter more than one isolated moment.',
               'Ask what you would choose if starting today.'],
  'caption': 'Sunk-Cost Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['This may be sunk-cost pressure.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Past effort is not a reason to accept future harm.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Sunk-Cost Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['Watch for sunk-cost pressure when a situation feels confusing.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Your discomfort is information, not a problem to silence.',
               'Ask what you would choose if starting today.'],
  'caption': 'Sunk-Cost Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['sunk-cost pressure can make a reasonable boundary feel difficult.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Past effort is not a reason to accept future harm.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Sunk-Cost Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['A warning sign can be scarcity pressure.',
               'Something is called rare or almost gone before you can think clearly.',
               'Limited supply does not remove your right to pause.',
               'Step back and verify the claim independently.'],
  'caption': 'Scarcity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['scarcity pressure can hide inside ordinary moments.',
               'Something is called rare or almost gone before you can think clearly.',
               'Patterns matter more than one isolated moment.',
               'Step back and verify the claim independently.'],
  'caption': 'Scarcity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['This may be scarcity pressure.',
               'Something is called rare or almost gone before you can think clearly.',
               'Limited supply does not remove your right to pause.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Scarcity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['Watch for scarcity pressure when a situation feels confusing.',
               'Something is called rare or almost gone before you can think clearly.',
               'Your discomfort is information, not a problem to silence.',
               'Step back and verify the claim independently.'],
  'caption': 'Scarcity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['scarcity pressure can make a reasonable boundary feel difficult.',
               'Something is called rare or almost gone before you can think clearly.',
               'Limited supply does not remove your right to pause.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Scarcity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['A warning sign can be social-proof pressure.',
               'You are told everybody agrees, buys, or puts up with it.',
               'A crowd can be wrong, and private discomfort still matters.',
               'Ask for evidence, not a head count.'],
  'caption': 'Social-Proof Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['social-proof pressure can hide inside ordinary moments.',
               'You are told everybody agrees, buys, or puts up with it.',
               'Patterns matter more than one isolated moment.',
               'Ask for evidence, not a head count.'],
  'caption': 'Social-Proof Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['This may be social-proof pressure.',
               'You are told everybody agrees, buys, or puts up with it.',
               'A crowd can be wrong, and private discomfort still matters.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Social-Proof Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['Watch for social-proof pressure when a situation feels confusing.',
               'You are told everybody agrees, buys, or puts up with it.',
               'Your discomfort is information, not a problem to silence.',
               'Ask for evidence, not a head count.'],
  'caption': 'Social-Proof Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['social-proof pressure can make a reasonable boundary feel difficult.',
               'You are told everybody agrees, buys, or puts up with it.',
               'A crowd can be wrong, and private discomfort still matters.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Social-Proof Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['A warning sign can be authority pressure.',
               'A title or confident voice is used to shut down your questions.',
               'Expertise deserves respect, not blind obedience.',
               'Ask what supports the recommendation.'],
  'caption': 'Authority Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['authority pressure can hide inside ordinary moments.',
               'A title or confident voice is used to shut down your questions.',
               'Patterns matter more than one isolated moment.',
               'Ask what supports the recommendation.'],
  'caption': 'Authority Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['This may be authority pressure.',
               'A title or confident voice is used to shut down your questions.',
               'Expertise deserves respect, not blind obedience.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Authority Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['Watch for authority pressure when a situation feels confusing.',
               'A title or confident voice is used to shut down your questions.',
               'Your discomfort is information, not a problem to silence.',
               'Ask what supports the recommendation.'],
  'caption': 'Authority Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['authority pressure can make a reasonable boundary feel difficult.',
               'A title or confident voice is used to shut down your questions.',
               'Expertise deserves respect, not blind obedience.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Authority Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['A warning sign can be reciprocity pressure.',
               'A gift or favor quietly turns into an obligation.',
               'Kindness is not a contract for access or compliance.',
               'Say thanks without promising more than you want.'],
  'caption': 'Reciprocity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['reciprocity pressure can hide inside ordinary moments.',
               'A gift or favor quietly turns into an obligation.',
               'Patterns matter more than one isolated moment.',
               'Say thanks without promising more than you want.'],
  'caption': 'Reciprocity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['This may be reciprocity pressure.',
               'A gift or favor quietly turns into an obligation.',
               'Kindness is not a contract for access or compliance.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Reciprocity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['Watch for reciprocity pressure when a situation feels confusing.',
               'A gift or favor quietly turns into an obligation.',
               'Your discomfort is information, not a problem to silence.',
               'Say thanks without promising more than you want.'],
  'caption': 'Reciprocity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['reciprocity pressure can make a reasonable boundary feel difficult.',
               'A gift or favor quietly turns into an obligation.',
               'Kindness is not a contract for access or compliance.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Reciprocity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['A warning sign can be fear-based messaging.',
               'A scary outcome is presented as certain unless you obey.',
               'Fear narrows thinking and makes weak claims feel urgent.',
               'Pause, breathe, and check the actual risk.'],
  'caption': 'Fear-Based Messaging: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['fear-based messaging can hide inside ordinary moments.',
               'A scary outcome is presented as certain unless you obey.',
               'Patterns matter more than one isolated moment.',
               'Pause, breathe, and check the actual risk.'],
  'caption': 'Fear-Based Messaging: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['This may be fear-based messaging.',
               'A scary outcome is presented as certain unless you obey.',
               'Fear narrows thinking and makes weak claims feel urgent.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Fear-Based Messaging: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['Watch for fear-based messaging when a situation feels confusing.',
               'A scary outcome is presented as certain unless you obey.',
               'Your discomfort is information, not a problem to silence.',
               'Pause, breathe, and check the actual risk.'],
  'caption': 'Fear-Based Messaging: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['fear-based messaging can make a reasonable boundary feel difficult.',
               'A scary outcome is presented as certain unless you obey.',
               'Fear narrows thinking and makes weak claims feel urgent.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Fear-Based Messaging: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['A warning sign can be false dilemma.',
               'You are told there are only two choices when there may be more.',
               'Pressure often hides alternatives.',
               "Ask: 'What other options are we leaving out?'"],
  'caption': 'False Dilemma: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['false dilemma can hide inside ordinary moments.',
               'You are told there are only two choices when there may be more.',
               'Patterns matter more than one isolated moment.',
               "Ask: 'What other options are we leaving out?'"],
  'caption': 'False Dilemma: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['This may be false dilemma.',
               'You are told there are only two choices when there may be more.',
               'Pressure often hides alternatives.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'False Dilemma: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['Watch for false dilemma when a situation feels confusing.',
               'You are told there are only two choices when there may be more.',
               'Your discomfort is information, not a problem to silence.',
               "Ask: 'What other options are we leaving out?'"],
  'caption': 'False Dilemma: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['false dilemma can make a reasonable boundary feel difficult.',
               'You are told there are only two choices when there may be more.',
               'Pressure often hides alternatives.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'False Dilemma: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['A warning sign can be loaded questions.',
               'Any answer seems to make you admit something unfair.',
               'A question can contain an accusation instead of seeking truth.',
               'Correct the premise before answering.'],
  'caption': 'Loaded Questions: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['loaded questions can hide inside ordinary moments.',
               'Any answer seems to make you admit something unfair.',
               'Patterns matter more than one isolated moment.',
               'Correct the premise before answering.'],
  'caption': 'Loaded Questions: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['This may be loaded questions.',
               'Any answer seems to make you admit something unfair.',
               'A question can contain an accusation instead of seeking truth.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Loaded Questions: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['Watch for loaded questions when a situation feels confusing.',
               'Any answer seems to make you admit something unfair.',
               'Your discomfort is information, not a problem to silence.',
               'Correct the premise before answering.'],
  'caption': 'Loaded Questions: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['loaded questions can make a reasonable boundary feel difficult.',
               'Any answer seems to make you admit something unfair.',
               'A question can contain an accusation instead of seeking truth.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Loaded Questions: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['A warning sign can be leading questions.',
               'The wording pushes you toward the answer they want.',
               'A fair question leaves room for your real view.',
               'Restate the question in neutral words.'],
  'caption': 'Leading Questions: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['leading questions can hide inside ordinary moments.',
               'The wording pushes you toward the answer they want.',
               'Patterns matter more than one isolated moment.',
               'Restate the question in neutral words.'],
  'caption': 'Leading Questions: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['This may be leading questions.',
               'The wording pushes you toward the answer they want.',
               'A fair question leaves room for your real view.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Leading Questions: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['Watch for leading questions when a situation feels confusing.',
               'The wording pushes you toward the answer they want.',
               'Your discomfort is information, not a problem to silence.',
               'Restate the question in neutral words.'],
  'caption': 'Leading Questions: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['leading questions can make a reasonable boundary feel difficult.',
               'The wording pushes you toward the answer they want.',
               'A fair question leaves room for your real view.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Leading Questions: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['A warning sign can be gish gallop.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Speed is not evidence.',
               'Choose one claim and ask for support.'],
  'caption': 'Gish Gallop: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['gish gallop can hide inside ordinary moments.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Patterns matter more than one isolated moment.',
               'Choose one claim and ask for support.'],
  'caption': 'Gish Gallop: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['This may be gish gallop.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Speed is not evidence.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Gish Gallop: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['Watch for gish gallop when a situation feels confusing.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Your discomfort is information, not a problem to silence.',
               'Choose one claim and ask for support.'],
  'caption': 'Gish Gallop: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['gish gallop can make a reasonable boundary feel difficult.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Speed is not evidence.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Gish Gallop: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['A warning sign can be whataboutism.',
               'Your concern gets replaced with a different accusation about you.',
               'Two issues can exist without one erasing the other.',
               'Return gently to the original topic.'],
  'caption': 'Whataboutism: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['whataboutism can hide inside ordinary moments.',
               'Your concern gets replaced with a different accusation about you.',
               'Patterns matter more than one isolated moment.',
               'Return gently to the original topic.'],
  'caption': 'Whataboutism: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['This may be whataboutism.',
               'Your concern gets replaced with a different accusation about you.',
               'Two issues can exist without one erasing the other.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Whataboutism: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['Watch for whataboutism when a situation feels confusing.',
               'Your concern gets replaced with a different accusation about you.',
               'Your discomfort is information, not a problem to silence.',
               'Return gently to the original topic.'],
  'caption': 'Whataboutism: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['whataboutism can make a reasonable boundary feel difficult.',
               'Your concern gets replaced with a different accusation about you.',
               'Two issues can exist without one erasing the other.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Whataboutism: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['A warning sign can be straw-man framing.',
               'Your actual point gets replaced with an extreme version.',
               'You deserve to be responded to accurately.',
               "Say: 'That is not what I said. My point is...'"],
  'caption': 'Straw-Man Framing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['straw-man framing can hide inside ordinary moments.',
               'Your actual point gets replaced with an extreme version.',
               'Patterns matter more than one isolated moment.',
               "Say: 'That is not what I said. My point is...'"],
  'caption': 'Straw-Man Framing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['This may be straw-man framing.',
               'Your actual point gets replaced with an extreme version.',
               'You deserve to be responded to accurately.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Straw-Man Framing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['Watch for straw-man framing when a situation feels confusing.',
               'Your actual point gets replaced with an extreme version.',
               'Your discomfort is information, not a problem to silence.',
               "Say: 'That is not what I said. My point is...'"],
  'caption': 'Straw-Man Framing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['straw-man framing can make a reasonable boundary feel difficult.',
               'Your actual point gets replaced with an extreme version.',
               'You deserve to be responded to accurately.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Straw-Man Framing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['A warning sign can be appeal to pity.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Compassion and accountability can stand together.',
               'Acknowledge the pain, then name the behavior.'],
  'caption': 'Appeal To Pity: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['appeal to pity can hide inside ordinary moments.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Patterns matter more than one isolated moment.',
               'Acknowledge the pain, then name the behavior.'],
  'caption': 'Appeal To Pity: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['This may be appeal to pity.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Compassion and accountability can stand together.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Appeal To Pity: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['Watch for appeal to pity when a situation feels confusing.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Your discomfort is information, not a problem to silence.',
               'Acknowledge the pain, then name the behavior.'],
  'caption': 'Appeal To Pity: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['appeal to pity can make a reasonable boundary feel difficult.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Compassion and accountability can stand together.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Appeal To Pity: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['A warning sign can be moral licensing.',
               'One good act is used to excuse a repeated harmful act.',
               'Being kind sometimes does not cancel a pattern.',
               'Look at the full behavior, not one highlight.'],
  'caption': 'Moral Licensing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['moral licensing can hide inside ordinary moments.',
               'One good act is used to excuse a repeated harmful act.',
               'Patterns matter more than one isolated moment.',
               'Look at the full behavior, not one highlight.'],
  'caption': 'Moral Licensing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['This may be moral licensing.',
               'One good act is used to excuse a repeated harmful act.',
               'Being kind sometimes does not cancel a pattern.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Moral Licensing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['Watch for moral licensing when a situation feels confusing.',
               'One good act is used to excuse a repeated harmful act.',
               'Your discomfort is information, not a problem to silence.',
               'Look at the full behavior, not one highlight.'],
  'caption': 'Moral Licensing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['moral licensing can make a reasonable boundary feel difficult.',
               'One good act is used to excuse a repeated harmful act.',
               'Being kind sometimes does not cancel a pattern.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Moral Licensing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['A warning sign can be trauma dumping for leverage.',
               'A painful story appears only when you set a limit.',
               "Someone's pain matters, but your boundary still matters too.",
               'Offer care without abandoning your limit.'],
  'caption': 'Trauma Dumping For Leverage: recognize the pattern and protect your peace. Education only—not '
             'a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['trauma dumping for leverage can hide inside ordinary moments.',
               'A painful story appears only when you set a limit.',
               'Patterns matter more than one isolated moment.',
               'Offer care without abandoning your limit.'],
  'caption': 'Trauma Dumping For Leverage: recognize the pattern and protect your peace. Education only—not '
             'a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['This may be trauma dumping for leverage.',
               'A painful story appears only when you set a limit.',
               "Someone's pain matters, but your boundary still matters too.",
               'You deserve time, clarity, and a choice.'],
  'caption': 'Trauma Dumping For Leverage: recognize the pattern and protect your peace. Education only—not '
             'a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['Watch for trauma dumping for leverage when a situation feels confusing.',
               'A painful story appears only when you set a limit.',
               'Your discomfort is information, not a problem to silence.',
               'Offer care without abandoning your limit.'],
  'caption': 'Trauma Dumping For Leverage: recognize the pattern and protect your peace. Education only—not '
             'a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['trauma dumping for leverage can make a reasonable boundary feel difficult.',
               'A painful story appears only when you set a limit.',
               "Someone's pain matters, but your boundary still matters too.",
               'Pause before deciding and use support if you need it.'],
  'caption': 'Trauma Dumping For Leverage: recognize the pattern and protect your peace. Education only—not '
             'a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['A warning sign can be manufactured crisis.',
               'Every request becomes an emergency that only you can solve.',
               'Constant crisis can train you to ignore your own needs.',
               'Check whether the urgency is real and shared.'],
  'caption': 'Manufactured Crisis: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['manufactured crisis can hide inside ordinary moments.',
               'Every request becomes an emergency that only you can solve.',
               'Patterns matter more than one isolated moment.',
               'Check whether the urgency is real and shared.'],
  'caption': 'Manufactured Crisis: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['This may be manufactured crisis.',
               'Every request becomes an emergency that only you can solve.',
               'Constant crisis can train you to ignore your own needs.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Manufactured Crisis: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['Watch for manufactured crisis when a situation feels confusing.',
               'Every request becomes an emergency that only you can solve.',
               'Your discomfort is information, not a problem to silence.',
               'Check whether the urgency is real and shared.'],
  'caption': 'Manufactured Crisis: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['manufactured crisis can make a reasonable boundary feel difficult.',
               'Every request becomes an emergency that only you can solve.',
               'Constant crisis can train you to ignore your own needs.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Manufactured Crisis: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['A warning sign can be time pressure.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Good decisions can usually survive a short pause.',
               "Use: 'I do not decide important things on the spot.'"],
  'caption': 'Time Pressure: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['time pressure can hide inside ordinary moments.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Patterns matter more than one isolated moment.',
               "Use: 'I do not decide important things on the spot.'"],
  'caption': 'Time Pressure: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['This may be time pressure.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Good decisions can usually survive a short pause.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Time Pressure: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['Watch for time pressure when a situation feels confusing.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Your discomfort is information, not a problem to silence.',
               "Use: 'I do not decide important things on the spot.'"],
  'caption': 'Time Pressure: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['time pressure can make a reasonable boundary feel difficult.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Good decisions can usually survive a short pause.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Time Pressure: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['A warning sign can be information withholding.',
               'Key details arrive after you have already agreed.',
               'Informed consent needs the relevant facts first.',
               'Ask what has not been disclosed yet.'],
  'caption': 'Information Withholding: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['information withholding can hide inside ordinary moments.',
               'Key details arrive after you have already agreed.',
               'Patterns matter more than one isolated moment.',
               'Ask what has not been disclosed yet.'],
  'caption': 'Information Withholding: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['This may be information withholding.',
               'Key details arrive after you have already agreed.',
               'Informed consent needs the relevant facts first.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Information Withholding: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['Watch for information withholding when a situation feels confusing.',
               'Key details arrive after you have already agreed.',
               'Your discomfort is information, not a problem to silence.',
               'Ask what has not been disclosed yet.'],
  'caption': 'Information Withholding: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['information withholding can make a reasonable boundary feel difficult.',
               'Key details arrive after you have already agreed.',
               'Informed consent needs the relevant facts first.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Information Withholding: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['A warning sign can be selective evidence.',
               'Only facts that support one conclusion are repeated.',
               'A fair picture includes inconvenient facts too.',
               'Look for what is missing, not only what is shown.'],
  'caption': 'Selective Evidence: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['selective evidence can hide inside ordinary moments.',
               'Only facts that support one conclusion are repeated.',
               'Patterns matter more than one isolated moment.',
               'Look for what is missing, not only what is shown.'],
  'caption': 'Selective Evidence: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['This may be selective evidence.',
               'Only facts that support one conclusion are repeated.',
               'A fair picture includes inconvenient facts too.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Selective Evidence: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['Watch for selective evidence when a situation feels confusing.',
               'Only facts that support one conclusion are repeated.',
               'Your discomfort is information, not a problem to silence.',
               'Look for what is missing, not only what is shown.'],
  'caption': 'Selective Evidence: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['selective evidence can make a reasonable boundary feel difficult.',
               'Only facts that support one conclusion are repeated.',
               'A fair picture includes inconvenient facts too.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Selective Evidence: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['A warning sign can be cherry-picked statistics.',
               'One number is used without context to make a claim feel final.',
               'Numbers need a source, comparison, and timeframe.',
               'Ask where the figure came from and what it leaves out.'],
  'caption': 'Cherry-Picked Statistics: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['cherry-picked statistics can hide inside ordinary moments.',
               'One number is used without context to make a claim feel final.',
               'Patterns matter more than one isolated moment.',
               'Ask where the figure came from and what it leaves out.'],
  'caption': 'Cherry-Picked Statistics: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['This may be cherry-picked statistics.',
               'One number is used without context to make a claim feel final.',
               'Numbers need a source, comparison, and timeframe.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Cherry-Picked Statistics: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['Watch for cherry-picked statistics when a situation feels confusing.',
               'One number is used without context to make a claim feel final.',
               'Your discomfort is information, not a problem to silence.',
               'Ask where the figure came from and what it leaves out.'],
  'caption': 'Cherry-Picked Statistics: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['cherry-picked statistics can make a reasonable boundary feel difficult.',
               'One number is used without context to make a claim feel final.',
               'Numbers need a source, comparison, and timeframe.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Cherry-Picked Statistics: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['A warning sign can be fake consensus.',
               'They claim others privately agree with them but name no one.',
               'Unnamed agreement is not proof.',
               'Speak directly with people instead of chasing rumors.'],
  'caption': 'Fake Consensus: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['fake consensus can hide inside ordinary moments.',
               'They claim others privately agree with them but name no one.',
               'Patterns matter more than one isolated moment.',
               'Speak directly with people instead of chasing rumors.'],
  'caption': 'Fake Consensus: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['This may be fake consensus.',
               'They claim others privately agree with them but name no one.',
               'Unnamed agreement is not proof.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Fake Consensus: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['Watch for fake consensus when a situation feels confusing.',
               'They claim others privately agree with them but name no one.',
               'Your discomfort is information, not a problem to silence.',
               'Speak directly with people instead of chasing rumors.'],
  'caption': 'Fake Consensus: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['fake consensus can make a reasonable boundary feel difficult.',
               'They claim others privately agree with them but name no one.',
               'Unnamed agreement is not proof.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Fake Consensus: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['A warning sign can be bandwagon shame.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Belonging should not require surrendering your judgment.',
               "Let your values choose, not the crowd's mood."],
  'caption': 'Bandwagon Shame: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['bandwagon shame can hide inside ordinary moments.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Patterns matter more than one isolated moment.',
               "Let your values choose, not the crowd's mood."],
  'caption': 'Bandwagon Shame: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['This may be bandwagon shame.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Belonging should not require surrendering your judgment.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Bandwagon Shame: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['Watch for bandwagon shame when a situation feels confusing.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Your discomfort is information, not a problem to silence.',
               "Let your values choose, not the crowd's mood."],
  'caption': 'Bandwagon Shame: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['bandwagon shame can make a reasonable boundary feel difficult.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Belonging should not require surrendering your judgment.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Bandwagon Shame: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['A warning sign can be purity tests.',
               'One imperfect choice is used to label you disloyal or bad.',
               'Healthy relationships allow complexity and growth.',
               'Reject labels and discuss the actual decision.'],
  'caption': 'Purity Tests: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['purity tests can hide inside ordinary moments.',
               'One imperfect choice is used to label you disloyal or bad.',
               'Patterns matter more than one isolated moment.',
               'Reject labels and discuss the actual decision.'],
  'caption': 'Purity Tests: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['This may be purity tests.',
               'One imperfect choice is used to label you disloyal or bad.',
               'Healthy relationships allow complexity and growth.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Purity Tests: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['Watch for purity tests when a situation feels confusing.',
               'One imperfect choice is used to label you disloyal or bad.',
               'Your discomfort is information, not a problem to silence.',
               'Reject labels and discuss the actual decision.'],
  'caption': 'Purity Tests: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['purity tests can make a reasonable boundary feel difficult.',
               'One imperfect choice is used to label you disloyal or bad.',
               'Healthy relationships allow complexity and growth.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Purity Tests: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['A warning sign can be moving deadlines.',
               'The deadline changes whenever you need time to think.',
               'Unstable deadlines can keep you anxious and compliant.',
               'Set your own decision time where possible.'],
  'caption': 'Moving Deadlines: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['moving deadlines can hide inside ordinary moments.',
               'The deadline changes whenever you need time to think.',
               'Patterns matter more than one isolated moment.',
               'Set your own decision time where possible.'],
  'caption': 'Moving Deadlines: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['This may be moving deadlines.',
               'The deadline changes whenever you need time to think.',
               'Unstable deadlines can keep you anxious and compliant.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Moving Deadlines: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['Watch for moving deadlines when a situation feels confusing.',
               'The deadline changes whenever you need time to think.',
               'Your discomfort is information, not a problem to silence.',
               'Set your own decision time where possible.'],
  'caption': 'Moving Deadlines: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['moving deadlines can make a reasonable boundary feel difficult.',
               'The deadline changes whenever you need time to think.',
               'Unstable deadlines can keep you anxious and compliant.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Moving Deadlines: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['A warning sign can be bait-and-switch.',
               'What was promised is not what appears after you commit.',
               'You are allowed to walk away from changed terms.',
               'Compare the offer to the original promise.'],
  'caption': 'Bait-And-Switch: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['bait-and-switch can hide inside ordinary moments.',
               'What was promised is not what appears after you commit.',
               'Patterns matter more than one isolated moment.',
               'Compare the offer to the original promise.'],
  'caption': 'Bait-And-Switch: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['This may be bait-and-switch.',
               'What was promised is not what appears after you commit.',
               'You are allowed to walk away from changed terms.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Bait-And-Switch: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['Watch for bait-and-switch when a situation feels confusing.',
               'What was promised is not what appears after you commit.',
               'Your discomfort is information, not a problem to silence.',
               'Compare the offer to the original promise.'],
  'caption': 'Bait-And-Switch: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['bait-and-switch can make a reasonable boundary feel difficult.',
               'What was promised is not what appears after you commit.',
               'You are allowed to walk away from changed terms.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Bait-And-Switch: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['A warning sign can be future pacing.',
               'A vivid future is described to make you commit in the present.',
               'A beautiful story is not evidence of a safe pattern.',
               "Ground yourself in today's actions."],
  'caption': 'Future Pacing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['future pacing can hide inside ordinary moments.',
               'A vivid future is described to make you commit in the present.',
               'Patterns matter more than one isolated moment.',
               "Ground yourself in today's actions."],
  'caption': 'Future Pacing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['This may be future pacing.',
               'A vivid future is described to make you commit in the present.',
               'A beautiful story is not evidence of a safe pattern.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Future Pacing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['Watch for future pacing when a situation feels confusing.',
               'A vivid future is described to make you commit in the present.',
               'Your discomfort is information, not a problem to silence.',
               "Ground yourself in today's actions."],
  'caption': 'Future Pacing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['future pacing can make a reasonable boundary feel difficult.',
               'A vivid future is described to make you commit in the present.',
               'A beautiful story is not evidence of a safe pattern.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Future Pacing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['A warning sign can be identity pressure.',
               'They say a good friend, parent, worker, or partner would obey.',
               "Your identity is bigger than one person's demand.",
               'Define your own values before answering.'],
  'caption': 'Identity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['identity pressure can hide inside ordinary moments.',
               'They say a good friend, parent, worker, or partner would obey.',
               'Patterns matter more than one isolated moment.',
               'Define your own values before answering.'],
  'caption': 'Identity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['This may be identity pressure.',
               'They say a good friend, parent, worker, or partner would obey.',
               "Your identity is bigger than one person's demand.",
               'You deserve time, clarity, and a choice.'],
  'caption': 'Identity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['Watch for identity pressure when a situation feels confusing.',
               'They say a good friend, parent, worker, or partner would obey.',
               'Your discomfort is information, not a problem to silence.',
               'Define your own values before answering.'],
  'caption': 'Identity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['identity pressure can make a reasonable boundary feel difficult.',
               'They say a good friend, parent, worker, or partner would obey.',
               "Your identity is bigger than one person's demand.",
               'Pause before deciding and use support if you need it.'],
  'caption': 'Identity Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['A warning sign can be labeling.',
               'A single mistake becomes a permanent name for who you are.',
               'Labels can silence learning and honest discussion.',
               'Ask for specific behavior instead of character attacks.'],
  'caption': 'Labeling: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['labeling can hide inside ordinary moments.',
               'A single mistake becomes a permanent name for who you are.',
               'Patterns matter more than one isolated moment.',
               'Ask for specific behavior instead of character attacks.'],
  'caption': 'Labeling: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['This may be labeling.',
               'A single mistake becomes a permanent name for who you are.',
               'Labels can silence learning and honest discussion.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Labeling: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['Watch for labeling when a situation feels confusing.',
               'A single mistake becomes a permanent name for who you are.',
               'Your discomfort is information, not a problem to silence.',
               'Ask for specific behavior instead of character attacks.'],
  'caption': 'Labeling: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['labeling can make a reasonable boundary feel difficult.',
               'A single mistake becomes a permanent name for who you are.',
               'Labels can silence learning and honest discussion.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Labeling: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['A warning sign can be projection.',
               'They accuse you of the behavior they keep showing.',
               'An accusation is not automatically a fact.',
               'Focus on observable actions and dates.'],
  'caption': 'Projection: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['projection can hide inside ordinary moments.',
               'They accuse you of the behavior they keep showing.',
               'Patterns matter more than one isolated moment.',
               'Focus on observable actions and dates.'],
  'caption': 'Projection: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['This may be projection.',
               'They accuse you of the behavior they keep showing.',
               'An accusation is not automatically a fact.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Projection: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['Watch for projection when a situation feels confusing.',
               'They accuse you of the behavior they keep showing.',
               'Your discomfort is information, not a problem to silence.',
               'Focus on observable actions and dates.'],
  'caption': 'Projection: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['projection can make a reasonable boundary feel difficult.',
               'They accuse you of the behavior they keep showing.',
               'An accusation is not automatically a fact.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Projection: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['A warning sign can be confession fishing.',
               'They keep asking until you say something just to end the pressure.',
               'Relief is not the same as voluntary agreement.',
               'Take a break before answering loaded questions.'],
  'caption': 'Confession Fishing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['confession fishing can hide inside ordinary moments.',
               'They keep asking until you say something just to end the pressure.',
               'Patterns matter more than one isolated moment.',
               'Take a break before answering loaded questions.'],
  'caption': 'Confession Fishing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['This may be confession fishing.',
               'They keep asking until you say something just to end the pressure.',
               'Relief is not the same as voluntary agreement.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Confession Fishing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['Watch for confession fishing when a situation feels confusing.',
               'They keep asking until you say something just to end the pressure.',
               'Your discomfort is information, not a problem to silence.',
               'Take a break before answering loaded questions.'],
  'caption': 'Confession Fishing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['confession fishing can make a reasonable boundary feel difficult.',
               'They keep asking until you say something just to end the pressure.',
               'Relief is not the same as voluntary agreement.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Confession Fishing: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['A warning sign can be forced choice.',
               'You are pushed to pick before you understand the consequences.',
               'A rushed choice may not be a free choice.',
               'Ask for time, details, and another option.'],
  'caption': 'Forced Choice: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['forced choice can hide inside ordinary moments.',
               'You are pushed to pick before you understand the consequences.',
               'Patterns matter more than one isolated moment.',
               'Ask for time, details, and another option.'],
  'caption': 'Forced Choice: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['This may be forced choice.',
               'You are pushed to pick before you understand the consequences.',
               'A rushed choice may not be a free choice.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Forced Choice: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['Watch for forced choice when a situation feels confusing.',
               'You are pushed to pick before you understand the consequences.',
               'Your discomfort is information, not a problem to silence.',
               'Ask for time, details, and another option.'],
  'caption': 'Forced Choice: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['forced choice can make a reasonable boundary feel difficult.',
               'You are pushed to pick before you understand the consequences.',
               'A rushed choice may not be a free choice.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Forced Choice: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['A warning sign can be conditional apology.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'A repair names the action and its impact.',
               "Ask: 'What will change next time?'"],
  'caption': 'Conditional Apology: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['conditional apology can hide inside ordinary moments.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'Patterns matter more than one isolated moment.',
               "Ask: 'What will change next time?'"],
  'caption': 'Conditional Apology: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['This may be conditional apology.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'A repair names the action and its impact.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Conditional Apology: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['Watch for conditional apology when a situation feels confusing.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'Your discomfort is information, not a problem to silence.',
               "Ask: 'What will change next time?'"],
  'caption': 'Conditional Apology: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['conditional apology can make a reasonable boundary feel difficult.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'A repair names the action and its impact.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Conditional Apology: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['A warning sign can be apology flooding.',
               'Many apologies arrive, but the behavior never changes.',
               'Words of regret need follow-through.',
               'Watch the pattern after the apology.'],
  'caption': 'Apology Flooding: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['apology flooding can hide inside ordinary moments.',
               'Many apologies arrive, but the behavior never changes.',
               'Patterns matter more than one isolated moment.',
               'Watch the pattern after the apology.'],
  'caption': 'Apology Flooding: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['This may be apology flooding.',
               'Many apologies arrive, but the behavior never changes.',
               'Words of regret need follow-through.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Apology Flooding: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['Watch for apology flooding when a situation feels confusing.',
               'Many apologies arrive, but the behavior never changes.',
               'Your discomfort is information, not a problem to silence.',
               'Watch the pattern after the apology.'],
  'caption': 'Apology Flooding: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['apology flooding can make a reasonable boundary feel difficult.',
               'Many apologies arrive, but the behavior never changes.',
               'Words of regret need follow-through.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Apology Flooding: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['A warning sign can be premature forgiveness pressure.',
               'You are urged to forgive before you feel heard or safe.',
               'Forgiveness cannot be demanded on a schedule.',
               'Take the time you need to decide what repair means.'],
  'caption': 'Premature Forgiveness Pressure: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['premature forgiveness pressure can hide inside ordinary moments.',
               'You are urged to forgive before you feel heard or safe.',
               'Patterns matter more than one isolated moment.',
               'Take the time you need to decide what repair means.'],
  'caption': 'Premature Forgiveness Pressure: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['This may be premature forgiveness pressure.',
               'You are urged to forgive before you feel heard or safe.',
               'Forgiveness cannot be demanded on a schedule.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Premature Forgiveness Pressure: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['Watch for premature forgiveness pressure when a situation feels confusing.',
               'You are urged to forgive before you feel heard or safe.',
               'Your discomfort is information, not a problem to silence.',
               'Take the time you need to decide what repair means.'],
  'caption': 'Premature Forgiveness Pressure: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['premature forgiveness pressure can make a reasonable boundary feel difficult.',
               'You are urged to forgive before you feel heard or safe.',
               'Forgiveness cannot be demanded on a schedule.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Premature Forgiveness Pressure: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['A warning sign can be forced positivity.',
               'Your concern is called negative before anyone considers it.',
               'Hope is healthy; denial is not.',
               'Name the concern clearly and calmly.'],
  'caption': 'Forced Positivity: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['forced positivity can hide inside ordinary moments.',
               'Your concern is called negative before anyone considers it.',
               'Patterns matter more than one isolated moment.',
               'Name the concern clearly and calmly.'],
  'caption': 'Forced Positivity: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['This may be forced positivity.',
               'Your concern is called negative before anyone considers it.',
               'Hope is healthy; denial is not.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Forced Positivity: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['Watch for forced positivity when a situation feels confusing.',
               'Your concern is called negative before anyone considers it.',
               'Your discomfort is information, not a problem to silence.',
               'Name the concern clearly and calmly.'],
  'caption': 'Forced Positivity: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['forced positivity can make a reasonable boundary feel difficult.',
               'Your concern is called negative before anyone considers it.',
               'Hope is healthy; denial is not.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Forced Positivity: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['A warning sign can be toxic gratitude.',
               'You are told to be grateful so you will stop naming harm.',
               'Gratitude and honest feedback can coexist.',
               'Appreciate what is real without denying what hurts.'],
  'caption': 'Toxic Gratitude: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['toxic gratitude can hide inside ordinary moments.',
               'You are told to be grateful so you will stop naming harm.',
               'Patterns matter more than one isolated moment.',
               'Appreciate what is real without denying what hurts.'],
  'caption': 'Toxic Gratitude: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['This may be toxic gratitude.',
               'You are told to be grateful so you will stop naming harm.',
               'Gratitude and honest feedback can coexist.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Toxic Gratitude: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['Watch for toxic gratitude when a situation feels confusing.',
               'You are told to be grateful so you will stop naming harm.',
               'Your discomfort is information, not a problem to silence.',
               'Appreciate what is real without denying what hurts.'],
  'caption': 'Toxic Gratitude: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['toxic gratitude can make a reasonable boundary feel difficult.',
               'You are told to be grateful so you will stop naming harm.',
               'Gratitude and honest feedback can coexist.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Toxic Gratitude: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['A warning sign can be emotional blackmail.',
               'Love, approval, or safety is tied to doing what they want.',
               'Care should not be a weapon.',
               'Reach for support if refusal feels dangerous.'],
  'caption': 'Emotional Blackmail: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['emotional blackmail can hide inside ordinary moments.',
               'Love, approval, or safety is tied to doing what they want.',
               'Patterns matter more than one isolated moment.',
               'Reach for support if refusal feels dangerous.'],
  'caption': 'Emotional Blackmail: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['This may be emotional blackmail.',
               'Love, approval, or safety is tied to doing what they want.',
               'Care should not be a weapon.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Emotional Blackmail: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['Watch for emotional blackmail when a situation feels confusing.',
               'Love, approval, or safety is tied to doing what they want.',
               'Your discomfort is information, not a problem to silence.',
               'Reach for support if refusal feels dangerous.'],
  'caption': 'Emotional Blackmail: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['emotional blackmail can make a reasonable boundary feel difficult.',
               'Love, approval, or safety is tied to doing what they want.',
               'Care should not be a weapon.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Emotional Blackmail: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['A warning sign can be coercive texting.',
               'Repeated calls or messages make silence feel impossible.',
               'Availability is not owed every minute.',
               'Mute, pause, and respond when you choose.'],
  'caption': 'Coercive Texting: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['coercive texting can hide inside ordinary moments.',
               'Repeated calls or messages make silence feel impossible.',
               'Patterns matter more than one isolated moment.',
               'Mute, pause, and respond when you choose.'],
  'caption': 'Coercive Texting: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['This may be coercive texting.',
               'Repeated calls or messages make silence feel impossible.',
               'Availability is not owed every minute.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Coercive Texting: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['Watch for coercive texting when a situation feels confusing.',
               'Repeated calls or messages make silence feel impossible.',
               'Your discomfort is information, not a problem to silence.',
               'Mute, pause, and respond when you choose.'],
  'caption': 'Coercive Texting: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['coercive texting can make a reasonable boundary feel difficult.',
               'Repeated calls or messages make silence feel impossible.',
               'Availability is not owed every minute.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Coercive Texting: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['A warning sign can be digital surveillance.',
               'Passwords, locations, or private messages are demanded as proof.',
               'Trust is not built through constant access.',
               'Review your privacy settings and boundaries.'],
  'caption': 'Digital Surveillance: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['digital surveillance can hide inside ordinary moments.',
               'Passwords, locations, or private messages are demanded as proof.',
               'Patterns matter more than one isolated moment.',
               'Review your privacy settings and boundaries.'],
  'caption': 'Digital Surveillance: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['This may be digital surveillance.',
               'Passwords, locations, or private messages are demanded as proof.',
               'Trust is not built through constant access.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Digital Surveillance: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['Watch for digital surveillance when a situation feels confusing.',
               'Passwords, locations, or private messages are demanded as proof.',
               'Your discomfort is information, not a problem to silence.',
               'Review your privacy settings and boundaries.'],
  'caption': 'Digital Surveillance: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['digital surveillance can make a reasonable boundary feel difficult.',
               'Passwords, locations, or private messages are demanded as proof.',
               'Trust is not built through constant access.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Digital Surveillance: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['A warning sign can be password pressure.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'Privacy is normal, even in close relationships.',
               'Keep accounts secure and discuss trust directly.'],
  'caption': 'Password Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['password pressure can hide inside ordinary moments.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'Patterns matter more than one isolated moment.',
               'Keep accounts secure and discuss trust directly.'],
  'caption': 'Password Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['This may be password pressure.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'Privacy is normal, even in close relationships.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Password Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['Watch for password pressure when a situation feels confusing.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'Your discomfort is information, not a problem to silence.',
               'Keep accounts secure and discuss trust directly.'],
  'caption': 'Password Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['password pressure can make a reasonable boundary feel difficult.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'Privacy is normal, even in close relationships.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Password Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['A warning sign can be location tracking pressure.',
               'Being tracked is called love, safety, or loyalty.',
               'Safety planning requires consent, not control.',
               'Choose who can see your location and when.'],
  'caption': 'Location Tracking Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['location tracking pressure can hide inside ordinary moments.',
               'Being tracked is called love, safety, or loyalty.',
               'Patterns matter more than one isolated moment.',
               'Choose who can see your location and when.'],
  'caption': 'Location Tracking Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['This may be location tracking pressure.',
               'Being tracked is called love, safety, or loyalty.',
               'Safety planning requires consent, not control.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Location Tracking Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['Watch for location tracking pressure when a situation feels confusing.',
               'Being tracked is called love, safety, or loyalty.',
               'Your discomfort is information, not a problem to silence.',
               'Choose who can see your location and when.'],
  'caption': 'Location Tracking Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['location tracking pressure can make a reasonable boundary feel difficult.',
               'Being tracked is called love, safety, or loyalty.',
               'Safety planning requires consent, not control.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Location Tracking Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['A warning sign can be public call-outs.',
               'A private issue is exposed to make you comply from embarrassment.',
               'Public shame discourages honest repair.',
               'Step away and ask for a private conversation.'],
  'caption': 'Public Call-Outs: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['public call-outs can hide inside ordinary moments.',
               'A private issue is exposed to make you comply from embarrassment.',
               'Patterns matter more than one isolated moment.',
               'Step away and ask for a private conversation.'],
  'caption': 'Public Call-Outs: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['This may be public call-outs.',
               'A private issue is exposed to make you comply from embarrassment.',
               'Public shame discourages honest repair.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Public Call-Outs: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['Watch for public call-outs when a situation feels confusing.',
               'A private issue is exposed to make you comply from embarrassment.',
               'Your discomfort is information, not a problem to silence.',
               'Step away and ask for a private conversation.'],
  'caption': 'Public Call-Outs: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['public call-outs can make a reasonable boundary feel difficult.',
               'A private issue is exposed to make you comply from embarrassment.',
               'Public shame discourages honest repair.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Public Call-Outs: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['A warning sign can be group pile-on.',
               'Others are brought in to make one person feel outnumbered.',
               'More voices do not make pressure fair.',
               'Ask to discuss the issue one-to-one or with neutral support.'],
  'caption': 'Group Pile-On: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['group pile-on can hide inside ordinary moments.',
               'Others are brought in to make one person feel outnumbered.',
               'Patterns matter more than one isolated moment.',
               'Ask to discuss the issue one-to-one or with neutral support.'],
  'caption': 'Group Pile-On: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['This may be group pile-on.',
               'Others are brought in to make one person feel outnumbered.',
               'More voices do not make pressure fair.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Group Pile-On: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['Watch for group pile-on when a situation feels confusing.',
               'Others are brought in to make one person feel outnumbered.',
               'Your discomfort is information, not a problem to silence.',
               'Ask to discuss the issue one-to-one or with neutral support.'],
  'caption': 'Group Pile-On: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['group pile-on can make a reasonable boundary feel difficult.',
               'Others are brought in to make one person feel outnumbered.',
               'More voices do not make pressure fair.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Group Pile-On: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['A warning sign can be proxy fighting.',
               'Someone sends friends or relatives to argue their case.',
               'Direct conflict needs direct communication.',
               'Avoid debating through messengers.'],
  'caption': 'Proxy Fighting: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['proxy fighting can hide inside ordinary moments.',
               'Someone sends friends or relatives to argue their case.',
               'Patterns matter more than one isolated moment.',
               'Avoid debating through messengers.'],
  'caption': 'Proxy Fighting: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['This may be proxy fighting.',
               'Someone sends friends or relatives to argue their case.',
               'Direct conflict needs direct communication.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Proxy Fighting: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['Watch for proxy fighting when a situation feels confusing.',
               'Someone sends friends or relatives to argue their case.',
               'Your discomfort is information, not a problem to silence.',
               'Avoid debating through messengers.'],
  'caption': 'Proxy Fighting: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['proxy fighting can make a reasonable boundary feel difficult.',
               'Someone sends friends or relatives to argue their case.',
               'Direct conflict needs direct communication.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Proxy Fighting: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['A warning sign can be flying monkeys.',
               'Third parties repeat pressure or rumors for someone else.',
               'You do not have to explain yourself to every messenger.',
               'Use one calm boundary and disengage.'],
  'caption': 'Flying Monkeys: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['flying monkeys can hide inside ordinary moments.',
               'Third parties repeat pressure or rumors for someone else.',
               'Patterns matter more than one isolated moment.',
               'Use one calm boundary and disengage.'],
  'caption': 'Flying Monkeys: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['This may be flying monkeys.',
               'Third parties repeat pressure or rumors for someone else.',
               'You do not have to explain yourself to every messenger.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Flying Monkeys: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['Watch for flying monkeys when a situation feels confusing.',
               'Third parties repeat pressure or rumors for someone else.',
               'Your discomfort is information, not a problem to silence.',
               'Use one calm boundary and disengage.'],
  'caption': 'Flying Monkeys: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['flying monkeys can make a reasonable boundary feel difficult.',
               'Third parties repeat pressure or rumors for someone else.',
               'You do not have to explain yourself to every messenger.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Flying Monkeys: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['A warning sign can be hoovering.',
               'Warm messages return just as you begin creating distance.',
               'A return is not proof that the old pattern is gone.',
               'Look for sustained change, not a sudden pull.'],
  'caption': 'Hoovering: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['hoovering can hide inside ordinary moments.',
               'Warm messages return just as you begin creating distance.',
               'Patterns matter more than one isolated moment.',
               'Look for sustained change, not a sudden pull.'],
  'caption': 'Hoovering: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['This may be hoovering.',
               'Warm messages return just as you begin creating distance.',
               'A return is not proof that the old pattern is gone.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Hoovering: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['Watch for hoovering when a situation feels confusing.',
               'Warm messages return just as you begin creating distance.',
               'Your discomfort is information, not a problem to silence.',
               'Look for sustained change, not a sudden pull.'],
  'caption': 'Hoovering: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['hoovering can make a reasonable boundary feel difficult.',
               'Warm messages return just as you begin creating distance.',
               'A return is not proof that the old pattern is gone.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Hoovering: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['A warning sign can be breadcrumbing.',
               'Tiny bits of attention keep you waiting for more.',
               'Occasional contact can create hope without commitment.',
               'Decide what consistency you need.'],
  'caption': 'Breadcrumbing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['breadcrumbing can hide inside ordinary moments.',
               'Tiny bits of attention keep you waiting for more.',
               'Patterns matter more than one isolated moment.',
               'Decide what consistency you need.'],
  'caption': 'Breadcrumbing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['This may be breadcrumbing.',
               'Tiny bits of attention keep you waiting for more.',
               'Occasional contact can create hope without commitment.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Breadcrumbing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['Watch for breadcrumbing when a situation feels confusing.',
               'Tiny bits of attention keep you waiting for more.',
               'Your discomfort is information, not a problem to silence.',
               'Decide what consistency you need.'],
  'caption': 'Breadcrumbing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['breadcrumbing can make a reasonable boundary feel difficult.',
               'Tiny bits of attention keep you waiting for more.',
               'Occasional contact can create hope without commitment.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Breadcrumbing: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['A warning sign can be orbiting.',
               'They stay visible online while avoiding a real conversation.',
               'Online signals are not the same as care or clarity.',
               'Protect your attention and seek direct answers.'],
  'caption': 'Orbiting: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['orbiting can hide inside ordinary moments.',
               'They stay visible online while avoiding a real conversation.',
               'Patterns matter more than one isolated moment.',
               'Protect your attention and seek direct answers.'],
  'caption': 'Orbiting: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['This may be orbiting.',
               'They stay visible online while avoiding a real conversation.',
               'Online signals are not the same as care or clarity.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Orbiting: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['Watch for orbiting when a situation feels confusing.',
               'They stay visible online while avoiding a real conversation.',
               'Your discomfort is information, not a problem to silence.',
               'Protect your attention and seek direct answers.'],
  'caption': 'Orbiting: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['orbiting can make a reasonable boundary feel difficult.',
               'They stay visible online while avoiding a real conversation.',
               'Online signals are not the same as care or clarity.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Orbiting: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['A warning sign can be jealousy bait.',
               'Another person is mentioned to make you compete for attention.',
               'Love does not require a contest.',
               'Refuse comparison and state what respect looks like.'],
  'caption': 'Jealousy Bait: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['jealousy bait can hide inside ordinary moments.',
               'Another person is mentioned to make you compete for attention.',
               'Patterns matter more than one isolated moment.',
               'Refuse comparison and state what respect looks like.'],
  'caption': 'Jealousy Bait: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['This may be jealousy bait.',
               'Another person is mentioned to make you compete for attention.',
               'Love does not require a contest.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Jealousy Bait: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['Watch for jealousy bait when a situation feels confusing.',
               'Another person is mentioned to make you compete for attention.',
               'Your discomfort is information, not a problem to silence.',
               'Refuse comparison and state what respect looks like.'],
  'caption': 'Jealousy Bait: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['jealousy bait can make a reasonable boundary feel difficult.',
               'Another person is mentioned to make you compete for attention.',
               'Love does not require a contest.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Jealousy Bait: recognize the pattern and protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['A warning sign can be triangulated praise.',
               'Someone praises another person mainly to make you feel inadequate.',
               'Comparison can be a tool of control.',
               'Ask for a direct request without the comparison.'],
  'caption': 'Triangulated Praise: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['triangulated praise can hide inside ordinary moments.',
               'Someone praises another person mainly to make you feel inadequate.',
               'Patterns matter more than one isolated moment.',
               'Ask for a direct request without the comparison.'],
  'caption': 'Triangulated Praise: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['This may be triangulated praise.',
               'Someone praises another person mainly to make you feel inadequate.',
               'Comparison can be a tool of control.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Triangulated Praise: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['Watch for triangulated praise when a situation feels confusing.',
               'Someone praises another person mainly to make you feel inadequate.',
               'Your discomfort is information, not a problem to silence.',
               'Ask for a direct request without the comparison.'],
  'caption': 'Triangulated Praise: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['triangulated praise can make a reasonable boundary feel difficult.',
               'Someone praises another person mainly to make you feel inadequate.',
               'Comparison can be a tool of control.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Triangulated Praise: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['A warning sign can be silent punishment.',
               'Contact disappears after you express a need or limit.',
               'A respectful pause includes communication and return.',
               'Do not chase clarity at the cost of your boundary.'],
  'caption': 'Silent Punishment: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['silent punishment can hide inside ordinary moments.',
               'Contact disappears after you express a need or limit.',
               'Patterns matter more than one isolated moment.',
               'Do not chase clarity at the cost of your boundary.'],
  'caption': 'Silent Punishment: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['This may be silent punishment.',
               'Contact disappears after you express a need or limit.',
               'A respectful pause includes communication and return.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Silent Punishment: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['Watch for silent punishment when a situation feels confusing.',
               'Contact disappears after you express a need or limit.',
               'Your discomfort is information, not a problem to silence.',
               'Do not chase clarity at the cost of your boundary.'],
  'caption': 'Silent Punishment: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['silent punishment can make a reasonable boundary feel difficult.',
               'Contact disappears after you express a need or limit.',
               'A respectful pause includes communication and return.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Silent Punishment: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['A warning sign can be rage as leverage.',
               'Anger becomes so big that everyone else must give in.',
               'Big emotion does not make a demand reasonable.',
               'Leave the conversation if you feel unsafe.'],
  'caption': 'Rage As Leverage: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['rage as leverage can hide inside ordinary moments.',
               'Anger becomes so big that everyone else must give in.',
               'Patterns matter more than one isolated moment.',
               'Leave the conversation if you feel unsafe.'],
  'caption': 'Rage As Leverage: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['This may be rage as leverage.',
               'Anger becomes so big that everyone else must give in.',
               'Big emotion does not make a demand reasonable.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Rage As Leverage: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['Watch for rage as leverage when a situation feels confusing.',
               'Anger becomes so big that everyone else must give in.',
               'Your discomfort is information, not a problem to silence.',
               'Leave the conversation if you feel unsafe.'],
  'caption': 'Rage As Leverage: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['rage as leverage can make a reasonable boundary feel difficult.',
               'Anger becomes so big that everyone else must give in.',
               'Big emotion does not make a demand reasonable.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Rage As Leverage: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['A warning sign can be intimidating body language.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'Fear changes whether a choice is freely made.',
               'Create space and seek immediate help if needed.'],
  'caption': 'Intimidating Body Language: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['intimidating body language can hide inside ordinary moments.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'Patterns matter more than one isolated moment.',
               'Create space and seek immediate help if needed.'],
  'caption': 'Intimidating Body Language: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['This may be intimidating body language.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'Fear changes whether a choice is freely made.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Intimidating Body Language: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['Watch for intimidating body language when a situation feels confusing.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'Your discomfort is information, not a problem to silence.',
               'Create space and seek immediate help if needed.'],
  'caption': 'Intimidating Body Language: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['intimidating body language can make a reasonable boundary feel difficult.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'Fear changes whether a choice is freely made.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Intimidating Body Language: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['A warning sign can be threatening self-harm for control.',
               'A threat of self-harm appears when you try to leave or say no.',
               'Take threats seriously without becoming the only responder.',
               'Contact emergency or crisis support and tell a trusted person.'],
  'caption': 'Threatening Self-Harm For Control: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['threatening self-harm for control can hide inside ordinary moments.',
               'A threat of self-harm appears when you try to leave or say no.',
               'Patterns matter more than one isolated moment.',
               'Contact emergency or crisis support and tell a trusted person.'],
  'caption': 'Threatening Self-Harm For Control: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['This may be threatening self-harm for control.',
               'A threat of self-harm appears when you try to leave or say no.',
               'Take threats seriously without becoming the only responder.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Threatening Self-Harm For Control: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['Watch for threatening self-harm for control when a situation feels confusing.',
               'A threat of self-harm appears when you try to leave or say no.',
               'Your discomfort is information, not a problem to silence.',
               'Contact emergency or crisis support and tell a trusted person.'],
  'caption': 'Threatening Self-Harm For Control: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['threatening self-harm for control can make a reasonable boundary feel difficult.',
               'A threat of self-harm appears when you try to leave or say no.',
               'Take threats seriously without becoming the only responder.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Threatening Self-Harm For Control: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['A warning sign can be threatening exposure.',
               'Private details are used to force silence or compliance.',
               'Blackmail is not care or conflict resolution.',
               'Save evidence and seek trusted or professional support.'],
  'caption': 'Threatening Exposure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['threatening exposure can hide inside ordinary moments.',
               'Private details are used to force silence or compliance.',
               'Patterns matter more than one isolated moment.',
               'Save evidence and seek trusted or professional support.'],
  'caption': 'Threatening Exposure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['This may be threatening exposure.',
               'Private details are used to force silence or compliance.',
               'Blackmail is not care or conflict resolution.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Threatening Exposure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['Watch for threatening exposure when a situation feels confusing.',
               'Private details are used to force silence or compliance.',
               'Your discomfort is information, not a problem to silence.',
               'Save evidence and seek trusted or professional support.'],
  'caption': 'Threatening Exposure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['threatening exposure can make a reasonable boundary feel difficult.',
               'Private details are used to force silence or compliance.',
               'Blackmail is not care or conflict resolution.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Threatening Exposure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['A warning sign can be reputation threats.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'Threats try to isolate you before you can get help.',
               'Document what happens and tell safe people.'],
  'caption': 'Reputation Threats: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['reputation threats can hide inside ordinary moments.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'Patterns matter more than one isolated moment.',
               'Document what happens and tell safe people.'],
  'caption': 'Reputation Threats: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['This may be reputation threats.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'Threats try to isolate you before you can get help.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Reputation Threats: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['Watch for reputation threats when a situation feels confusing.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'Your discomfort is information, not a problem to silence.',
               'Document what happens and tell safe people.'],
  'caption': 'Reputation Threats: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['reputation threats can make a reasonable boundary feel difficult.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'Threats try to isolate you before you can get help.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Reputation Threats: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['A warning sign can be legal-sounding intimidation.',
               'Official words are used to scare you without clear facts.',
               'A confident claim is not legal advice.',
               'Check information with a qualified, independent source.'],
  'caption': 'Legal-Sounding Intimidation: recognize the pattern and protect your peace. Education only—not '
             'a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['legal-sounding intimidation can hide inside ordinary moments.',
               'Official words are used to scare you without clear facts.',
               'Patterns matter more than one isolated moment.',
               'Check information with a qualified, independent source.'],
  'caption': 'Legal-Sounding Intimidation: recognize the pattern and protect your peace. Education only—not '
             'a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['This may be legal-sounding intimidation.',
               'Official words are used to scare you without clear facts.',
               'A confident claim is not legal advice.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Legal-Sounding Intimidation: recognize the pattern and protect your peace. Education only—not '
             'a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['Watch for legal-sounding intimidation when a situation feels confusing.',
               'Official words are used to scare you without clear facts.',
               'Your discomfort is information, not a problem to silence.',
               'Check information with a qualified, independent source.'],
  'caption': 'Legal-Sounding Intimidation: recognize the pattern and protect your peace. Education only—not '
             'a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['legal-sounding intimidation can make a reasonable boundary feel difficult.',
               'Official words are used to scare you without clear facts.',
               'A confident claim is not legal advice.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Legal-Sounding Intimidation: recognize the pattern and protect your peace. Education only—not '
             'a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['A warning sign can be financial guilt.',
               'Money spent on you is brought up to control your choices.',
               'Support should not create ownership over you.',
               'Separate appreciation from obligation.'],
  'caption': 'Financial Guilt: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['financial guilt can hide inside ordinary moments.',
               'Money spent on you is brought up to control your choices.',
               'Patterns matter more than one isolated moment.',
               'Separate appreciation from obligation.'],
  'caption': 'Financial Guilt: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['This may be financial guilt.',
               'Money spent on you is brought up to control your choices.',
               'Support should not create ownership over you.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Financial Guilt: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['Watch for financial guilt when a situation feels confusing.',
               'Money spent on you is brought up to control your choices.',
               'Your discomfort is information, not a problem to silence.',
               'Separate appreciation from obligation.'],
  'caption': 'Financial Guilt: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['financial guilt can make a reasonable boundary feel difficult.',
               'Money spent on you is brought up to control your choices.',
               'Support should not create ownership over you.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Financial Guilt: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['A warning sign can be financial secrecy.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'Shared financial decisions need clear information.',
               'Keep copies of records and ask direct questions.'],
  'caption': 'Financial Secrecy: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['financial secrecy can hide inside ordinary moments.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'Patterns matter more than one isolated moment.',
               'Keep copies of records and ask direct questions.'],
  'caption': 'Financial Secrecy: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['This may be financial secrecy.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'Shared financial decisions need clear information.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Financial Secrecy: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['Watch for financial secrecy when a situation feels confusing.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'Your discomfort is information, not a problem to silence.',
               'Keep copies of records and ask direct questions.'],
  'caption': 'Financial Secrecy: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['financial secrecy can make a reasonable boundary feel difficult.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'Shared financial decisions need clear information.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Financial Secrecy: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['A warning sign can be career sabotage.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'Support should expand your options, not shrink them.',
               'Notice who benefits when your independence gets smaller.'],
  'caption': 'Career Sabotage: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['career sabotage can hide inside ordinary moments.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'Patterns matter more than one isolated moment.',
               'Notice who benefits when your independence gets smaller.'],
  'caption': 'Career Sabotage: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['This may be career sabotage.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'Support should expand your options, not shrink them.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Career Sabotage: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['Watch for career sabotage when a situation feels confusing.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'Your discomfort is information, not a problem to silence.',
               'Notice who benefits when your independence gets smaller.'],
  'caption': 'Career Sabotage: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['career sabotage can make a reasonable boundary feel difficult.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'Support should expand your options, not shrink them.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Career Sabotage: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['A warning sign can be sleep deprivation pressure.',
               'A fight is kept going until you are too tired to think.',
               'Exhaustion makes consent and problem-solving harder.',
               'Pause the conversation and return after rest.'],
  'caption': 'Sleep Deprivation Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['sleep deprivation pressure can hide inside ordinary moments.',
               'A fight is kept going until you are too tired to think.',
               'Patterns matter more than one isolated moment.',
               'Pause the conversation and return after rest.'],
  'caption': 'Sleep Deprivation Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['This may be sleep deprivation pressure.',
               'A fight is kept going until you are too tired to think.',
               'Exhaustion makes consent and problem-solving harder.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Sleep Deprivation Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['Watch for sleep deprivation pressure when a situation feels confusing.',
               'A fight is kept going until you are too tired to think.',
               'Your discomfort is information, not a problem to silence.',
               'Pause the conversation and return after rest.'],
  'caption': 'Sleep Deprivation Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['sleep deprivation pressure can make a reasonable boundary feel difficult.',
               'A fight is kept going until you are too tired to think.',
               'Exhaustion makes consent and problem-solving harder.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Sleep Deprivation Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['A warning sign can be substance pressure.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'Impairment cannot create meaningful consent.',
               'Leave, call someone safe, or choose a clear no.'],
  'caption': 'Substance Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['substance pressure can hide inside ordinary moments.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'Patterns matter more than one isolated moment.',
               'Leave, call someone safe, or choose a clear no.'],
  'caption': 'Substance Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['This may be substance pressure.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'Impairment cannot create meaningful consent.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Substance Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['Watch for substance pressure when a situation feels confusing.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'Your discomfort is information, not a problem to silence.',
               'Leave, call someone safe, or choose a clear no.'],
  'caption': 'Substance Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['substance pressure can make a reasonable boundary feel difficult.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'Impairment cannot create meaningful consent.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Substance Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['A warning sign can be sexual coercion.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'Consent must be free, informed, and ongoing.',
               'No explanation is required; get support if you need it.'],
  'caption': 'Sexual Coercion: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['sexual coercion can hide inside ordinary moments.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'Patterns matter more than one isolated moment.',
               'No explanation is required; get support if you need it.'],
  'caption': 'Sexual Coercion: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['This may be sexual coercion.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'Consent must be free, informed, and ongoing.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Sexual Coercion: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['Watch for sexual coercion when a situation feels confusing.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'Your discomfort is information, not a problem to silence.',
               'No explanation is required; get support if you need it.'],
  'caption': 'Sexual Coercion: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['sexual coercion can make a reasonable boundary feel difficult.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'Consent must be free, informed, and ongoing.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Sexual Coercion: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['A warning sign can be normalizing disrespect.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'Common does not mean healthy.',
               'Compare the behavior with your values and safety.'],
  'caption': 'Normalizing Disrespect: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['normalizing disrespect can hide inside ordinary moments.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'Patterns matter more than one isolated moment.',
               'Compare the behavior with your values and safety.'],
  'caption': 'Normalizing Disrespect: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['This may be normalizing disrespect.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'Common does not mean healthy.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Normalizing Disrespect: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['Watch for normalizing disrespect when a situation feels confusing.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'Your discomfort is information, not a problem to silence.',
               'Compare the behavior with your values and safety.'],
  'caption': 'Normalizing Disrespect: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['normalizing disrespect can make a reasonable boundary feel difficult.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'Common does not mean healthy.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Normalizing Disrespect: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['A warning sign can be double-bind pressure.',
               'Whatever you choose is treated as proof that you are wrong.',
               'No-win rules are designed to keep you off balance.',
               'Name the bind and step out of the argument.'],
  'caption': 'Double-Bind Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['double-bind pressure can hide inside ordinary moments.',
               'Whatever you choose is treated as proof that you are wrong.',
               'Patterns matter more than one isolated moment.',
               'Name the bind and step out of the argument.'],
  'caption': 'Double-Bind Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['This may be double-bind pressure.',
               'Whatever you choose is treated as proof that you are wrong.',
               'No-win rules are designed to keep you off balance.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Double-Bind Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['Watch for double-bind pressure when a situation feels confusing.',
               'Whatever you choose is treated as proof that you are wrong.',
               'Your discomfort is information, not a problem to silence.',
               'Name the bind and step out of the argument.'],
  'caption': 'Double-Bind Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['double-bind pressure can make a reasonable boundary feel difficult.',
               'Whatever you choose is treated as proof that you are wrong.',
               'No-win rules are designed to keep you off balance.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Double-Bind Pressure: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['A warning sign can be learned helplessness pressure.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'Small choices can rebuild confidence and options.',
               'Tell one safe person what has been happening.'],
  'caption': 'Learned Helplessness Pressure: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['learned helplessness pressure can hide inside ordinary moments.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'Patterns matter more than one isolated moment.',
               'Tell one safe person what has been happening.'],
  'caption': 'Learned Helplessness Pressure: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['This may be learned helplessness pressure.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'Small choices can rebuild confidence and options.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Learned Helplessness Pressure: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['Watch for learned helplessness pressure when a situation feels confusing.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'Your discomfort is information, not a problem to silence.',
               'Tell one safe person what has been happening.'],
  'caption': 'Learned Helplessness Pressure: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['learned helplessness pressure can make a reasonable boundary feel difficult.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'Small choices can rebuild confidence and options.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Learned Helplessness Pressure: recognize the pattern and protect your peace. Education '
             'only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['A warning sign can be dependency building.',
               'Your outside support, skills, or resources slowly get reduced.',
               'Independence is protective, not disloyal.',
               'Keep contacts, documents, and practical options accessible.'],
  'caption': 'Dependency Building: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['dependency building can hide inside ordinary moments.',
               'Your outside support, skills, or resources slowly get reduced.',
               'Patterns matter more than one isolated moment.',
               'Keep contacts, documents, and practical options accessible.'],
  'caption': 'Dependency Building: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['This may be dependency building.',
               'Your outside support, skills, or resources slowly get reduced.',
               'Independence is protective, not disloyal.',
               'You deserve time, clarity, and a choice.'],
  'caption': 'Dependency Building: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['Watch for dependency building when a situation feels confusing.',
               'Your outside support, skills, or resources slowly get reduced.',
               'Your discomfort is information, not a problem to silence.',
               'Keep contacts, documents, and practical options accessible.'],
  'caption': 'Dependency Building: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You Are Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['dependency building can make a reasonable boundary feel difficult.',
               'Your outside support, skills, or resources slowly get reduced.',
               'Independence is protective, not disloyal.',
               'Pause before deciding and use support if you need it.'],
  'caption': 'Dependency Building: recognize the pattern and protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as foot-in-the-door pressure.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Consent to one thing is not consent to the next.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Foot-In-The-Door Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as door-in-the-face pressure.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Relief can make a request feel fair when it still is not right for you.'],
  'caption': 'Door-In-The-Face Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as lowballing.',
               'The terms get worse only after you have invested time, hope, or money.',
               'An agreement can be reconsidered when the conditions change.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Lowballing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['What to notice before you explain it away.',
               'This can show up as sunk-cost pressure.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Past effort is not a reason to accept future harm.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Sunk-Cost Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as scarcity pressure.',
               'Something is called rare or almost gone before you can think clearly.',
               'Limited supply does not remove your right to pause.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Scarcity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as social-proof pressure.',
               'You are told everybody agrees, buys, or puts up with it.',
               'A crowd can be wrong, and private discomfort still matters.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Ask for evidence, not a head count.'],
  'caption': 'Social-Proof Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as authority pressure.',
               'A title or confident voice is used to shut down your questions.',
               'Expertise deserves respect, not blind obedience.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Authority Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as reciprocity pressure.',
               'A gift or favor quietly turns into an obligation.',
               'Kindness is not a contract for access or compliance.'],
  'caption': 'Reciprocity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as fear-based messaging.',
               'A scary outcome is presented as certain unless you obey.',
               'Fear narrows thinking and makes weak claims feel urgent.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Fear-Based Messaging: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as false dilemma.',
               'You are told there are only two choices when there may be more.',
               'Pressure often hides alternatives.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'False Dilemma: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as loaded questions.',
               'Any answer seems to make you admit something unfair.',
               'A question can contain an accusation instead of seeking truth.'],
  'caption': 'Loaded Questions: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as leading questions.',
               'The wording pushes you toward the answer they want.',
               'A fair question leaves room for your real view.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Leading Questions: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as gish gallop.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Speed is not evidence.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Gish Gallop: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as whataboutism.',
               'Your concern gets replaced with a different accusation about you.',
               'Two issues can exist without one erasing the other.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Whataboutism: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as straw-man framing.',
               'Your actual point gets replaced with an extreme version.',
               'You deserve to be responded to accurately.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Straw-Man Framing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as appeal to pity.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Compassion and accountability can stand together.'],
  'caption': 'Appeal To Pity: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as moral licensing.',
               'One good act is used to excuse a repeated harmful act.',
               'Being kind sometimes does not cancel a pattern.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Moral Licensing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as trauma dumping for leverage.',
               'A painful story appears only when you set a limit.',
               "Someone's pain matters, but your boundary still matters too.",
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Trauma Dumping For Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as manufactured crisis.',
               'Every request becomes an emergency that only you can solve.',
               'Constant crisis can train you to ignore your own needs.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Check whether the urgency is real and shared.'],
  'caption': 'Manufactured Crisis: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as time pressure.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Good decisions can usually survive a short pause.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Time Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as information withholding.',
               'Key details arrive after you have already agreed.',
               'Informed consent needs the relevant facts first.'],
  'caption': 'Information Withholding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as selective evidence.',
               'Only facts that support one conclusion are repeated.',
               'A fair picture includes inconvenient facts too.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Selective Evidence: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as cherry-picked statistics.',
               'One number is used without context to make a claim feel final.',
               'Numbers need a source, comparison, and timeframe.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Cherry-Picked Statistics: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as fake consensus.',
               'They claim others privately agree with them but name no one.',
               'Unnamed agreement is not proof.'],
  'caption': 'Fake Consensus: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as bandwagon shame.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Belonging should not require surrendering your judgment.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               "Let your values choose, not the crowd's mood."],
  'caption': 'Bandwagon Shame: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as purity tests.',
               'One imperfect choice is used to label you disloyal or bad.',
               'Healthy relationships allow complexity and growth.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Purity Tests: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as moving deadlines.',
               'The deadline changes whenever you need time to think.',
               'Unstable deadlines can keep you anxious and compliant.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Set your own decision time where possible.'],
  'caption': 'Moving Deadlines: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as bait-and-switch.',
               'What was promised is not what appears after you commit.',
               'You are allowed to walk away from changed terms.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Compare the offer to the original promise.'],
  'caption': 'Bait-And-Switch: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as future pacing.',
               'A vivid future is described to make you commit in the present.',
               'A beautiful story is not evidence of a safe pattern.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Future Pacing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as identity pressure.',
               'They say a good friend, parent, worker, or partner would obey.',
               "Your identity is bigger than one person's demand.",
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Identity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as labeling.',
               'A single mistake becomes a permanent name for who you are.',
               'Labels can silence learning and honest discussion.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Labeling: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as projection.',
               'They accuse you of the behavior they keep showing.',
               'An accusation is not automatically a fact.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Projection: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as confession fishing.',
               'They keep asking until you say something just to end the pressure.',
               'Relief is not the same as voluntary agreement.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Take a break before answering loaded questions.'],
  'caption': 'Confession Fishing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as forced choice.',
               'You are pushed to pick before you understand the consequences.',
               'A rushed choice may not be a free choice.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Forced Choice: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['What to notice before you explain it away.',
               'This can show up as conditional apology.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'A repair names the action and its impact.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Conditional Apology: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as apology flooding.',
               'Many apologies arrive, but the behavior never changes.',
               'Words of regret need follow-through.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Apology Flooding: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as premature forgiveness pressure.',
               'You are urged to forgive before you feel heard or safe.',
               'Forgiveness cannot be demanded on a schedule.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Premature Forgiveness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as forced positivity.',
               'Your concern is called negative before anyone considers it.',
               'Hope is healthy; denial is not.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Forced Positivity: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as toxic gratitude.',
               'You are told to be grateful so you will stop naming harm.',
               'Gratitude and honest feedback can coexist.'],
  'caption': 'Toxic Gratitude: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as emotional blackmail.',
               'Love, approval, or safety is tied to doing what they want.',
               'Care should not be a weapon.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Emotional Blackmail: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as coercive texting.',
               'Repeated calls or messages make silence feel impossible.',
               'Availability is not owed every minute.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Coercive Texting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as digital surveillance.',
               'Passwords, locations, or private messages are demanded as proof.',
               'Trust is not built through constant access.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Digital Surveillance: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as password pressure.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'Privacy is normal, even in close relationships.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Password Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as location tracking pressure.',
               'Being tracked is called love, safety, or loyalty.',
               'Safety planning requires consent, not control.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Location Tracking Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as public call-outs.',
               'A private issue is exposed to make you comply from embarrassment.',
               'Public shame discourages honest repair.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Public Call-Outs: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as group pile-on.',
               'Others are brought in to make one person feel outnumbered.',
               'More voices do not make pressure fair.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Group Pile-On: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as proxy fighting.',
               'Someone sends friends or relatives to argue their case.',
               'Direct conflict needs direct communication.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Proxy Fighting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as flying monkeys.',
               'Third parties repeat pressure or rumors for someone else.',
               'You do not have to explain yourself to every messenger.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Flying Monkeys: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as hoovering.',
               'Warm messages return just as you begin creating distance.',
               'A return is not proof that the old pattern is gone.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Hoovering: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as breadcrumbing.',
               'Tiny bits of attention keep you waiting for more.',
               'Occasional contact can create hope without commitment.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Breadcrumbing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as orbiting.',
               'They stay visible online while avoiding a real conversation.',
               'Online signals are not the same as care or clarity.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Protect your attention and seek direct answers.'],
  'caption': 'Orbiting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as jealousy bait.',
               'Another person is mentioned to make you compete for attention.',
               'Love does not require a contest.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Jealousy Bait: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as triangulated praise.',
               'Someone praises another person mainly to make you feel inadequate.',
               'Comparison can be a tool of control.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Ask for a direct request without the comparison.'],
  'caption': 'Triangulated Praise: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as silent punishment.',
               'Contact disappears after you express a need or limit.',
               'A respectful pause includes communication and return.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Silent Punishment: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as rage as leverage.',
               'Anger becomes so big that everyone else must give in.',
               'Big emotion does not make a demand reasonable.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Leave the conversation if you feel unsafe.'],
  'caption': 'Rage As Leverage: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as intimidating body language.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'Fear changes whether a choice is freely made.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Intimidating Body Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as threatening self-harm for control.',
               'A threat of self-harm appears when you try to leave or say no.',
               'Take threats seriously without becoming the only responder.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Threatening Self-Harm For Control: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as threatening exposure.',
               'Private details are used to force silence or compliance.',
               'Blackmail is not care or conflict resolution.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Threatening Exposure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as reputation threats.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'Threats try to isolate you before you can get help.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Reputation Threats: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as legal-sounding intimidation.',
               'Official words are used to scare you without clear facts.',
               'A confident claim is not legal advice.'],
  'caption': 'Legal-Sounding Intimidation: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as financial guilt.',
               'Money spent on you is brought up to control your choices.',
               'Support should not create ownership over you.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Financial Guilt: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as financial secrecy.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'Shared financial decisions need clear information.'],
  'caption': 'Financial Secrecy: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as career sabotage.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'Support should expand your options, not shrink them.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Career Sabotage: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as sleep deprivation pressure.',
               'A fight is kept going until you are too tired to think.',
               'Exhaustion makes consent and problem-solving harder.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Sleep Deprivation Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as substance pressure.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'Impairment cannot create meaningful consent.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Substance Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as sexual coercion.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'Consent must be free, informed, and ongoing.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'No explanation is required; get support if you need it.'],
  'caption': 'Sexual Coercion: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as normalizing disrespect.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'Common does not mean healthy.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Normalizing Disrespect: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as double-bind pressure.',
               'Whatever you choose is treated as proof that you are wrong.',
               'No-win rules are designed to keep you off balance.'],
  'caption': 'Double-Bind Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as learned helplessness pressure.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'Small choices can rebuild confidence and options.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Learned Helplessness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as dependency building.',
               'Your outside support, skills, or resources slowly get reduced.',
               'Independence is protective, not disloyal.'],
  'caption': 'Dependency Building: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Approval Addiction',
  'definition': 'Praise arrives only when you ignore your own needs.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as approval addiction.',
               'Praise arrives only when you ignore your own needs.',
               'You do not need to earn basic respect.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Approval Addiction: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Selective Accountability',
  'definition': 'You must apologize in detail while they never repair anything.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as selective accountability.',
               'You must apologize in detail while they never repair anything.',
               'Accountability should not be one-sided.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Selective Accountability: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Weaponized Therapy Language',
  'definition': 'Words like boundaries, triggers, or healing are used to dismiss you.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as weaponized therapy language.',
               'Words like boundaries, triggers, or healing are used to dismiss you.',
               'Helpful language should create clarity, not silence.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Weaponized Therapy Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Diagnosis As Insult',
  'definition': 'A mental-health label is thrown at you to end the discussion.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as diagnosis as insult.',
               'A mental-health label is thrown at you to end the discussion.',
               'Labels are not substitutes for listening.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Return to the behavior and its impact.'],
  'caption': 'Diagnosis As Insult: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Revisionist Apologies',
  'definition': 'They apologize for a version of events that leaves out the harm.',
  'benefits': ['What to notice before you explain it away.',
               'This can show up as revisionist apologies.',
               'They apologize for a version of events that leaves out the harm.',
               'Repair starts with an accurate account.'],
  'caption': 'Revisionist Apologies: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as foot-in-the-door pressure.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Consent to one thing is not consent to the next.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Foot-In-The-Door Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as door-in-the-face pressure.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Relief can make a request feel fair when it still is not right for you.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Door-In-The-Face Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as lowballing.',
               'The terms get worse only after you have invested time, hope, or money.',
               'An agreement can be reconsidered when the conditions change.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Lowballing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as sunk-cost pressure.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Past effort is not a reason to accept future harm.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Sunk-Cost Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as scarcity pressure.',
               'Something is called rare or almost gone before you can think clearly.',
               'Limited supply does not remove your right to pause.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Scarcity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as social-proof pressure.',
               'You are told everybody agrees, buys, or puts up with it.',
               'A crowd can be wrong, and private discomfort still matters.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Social-Proof Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as authority pressure.',
               'A title or confident voice is used to shut down your questions.',
               'Expertise deserves respect, not blind obedience.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Authority Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as reciprocity pressure.',
               'A gift or favor quietly turns into an obligation.',
               'Kindness is not a contract for access or compliance.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Reciprocity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as fear-based messaging.',
               'A scary outcome is presented as certain unless you obey.',
               'Fear narrows thinking and makes weak claims feel urgent.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Fear-Based Messaging: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as false dilemma.',
               'You are told there are only two choices when there may be more.',
               'Pressure often hides alternatives.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               "Ask: 'What other options are we leaving out?'"],
  'caption': 'False Dilemma: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as loaded questions.',
               'Any answer seems to make you admit something unfair.',
               'A question can contain an accusation instead of seeking truth.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Correct the premise before answering.'],
  'caption': 'Loaded Questions: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as leading questions.',
               'The wording pushes you toward the answer they want.',
               'A fair question leaves room for your real view.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Leading Questions: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as gish gallop.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Speed is not evidence.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Gish Gallop: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as whataboutism.',
               'Your concern gets replaced with a different accusation about you.',
               'Two issues can exist without one erasing the other.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Return gently to the original topic.'],
  'caption': 'Whataboutism: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as straw-man framing.',
               'Your actual point gets replaced with an extreme version.',
               'You deserve to be responded to accurately.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Straw-Man Framing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as appeal to pity.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Compassion and accountability can stand together.'],
  'caption': 'Appeal To Pity: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as moral licensing.',
               'One good act is used to excuse a repeated harmful act.',
               'Being kind sometimes does not cancel a pattern.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Moral Licensing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as trauma dumping for leverage.',
               'A painful story appears only when you set a limit.',
               "Someone's pain matters, but your boundary still matters too.",
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Offer care without abandoning your limit.'],
  'caption': 'Trauma Dumping For Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as manufactured crisis.',
               'Every request becomes an emergency that only you can solve.',
               'Constant crisis can train you to ignore your own needs.'],
  'caption': 'Manufactured Crisis: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as time pressure.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Good decisions can usually survive a short pause.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Time Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as information withholding.',
               'Key details arrive after you have already agreed.',
               'Informed consent needs the relevant facts first.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Ask what has not been disclosed yet.'],
  'caption': 'Information Withholding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as selective evidence.',
               'Only facts that support one conclusion are repeated.',
               'A fair picture includes inconvenient facts too.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Selective Evidence: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as cherry-picked statistics.',
               'One number is used without context to make a claim feel final.',
               'Numbers need a source, comparison, and timeframe.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Cherry-Picked Statistics: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as fake consensus.',
               'They claim others privately agree with them but name no one.',
               'Unnamed agreement is not proof.'],
  'caption': 'Fake Consensus: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as bandwagon shame.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Belonging should not require surrendering your judgment.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Bandwagon Shame: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as purity tests.',
               'One imperfect choice is used to label you disloyal or bad.',
               'Healthy relationships allow complexity and growth.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Purity Tests: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as moving deadlines.',
               'The deadline changes whenever you need time to think.',
               'Unstable deadlines can keep you anxious and compliant.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Moving Deadlines: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as bait-and-switch.',
               'What was promised is not what appears after you commit.',
               'You are allowed to walk away from changed terms.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Compare the offer to the original promise.'],
  'caption': 'Bait-And-Switch: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as future pacing.',
               'A vivid future is described to make you commit in the present.',
               'A beautiful story is not evidence of a safe pattern.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               "Ground yourself in today's actions."],
  'caption': 'Future Pacing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as identity pressure.',
               'They say a good friend, parent, worker, or partner would obey.',
               "Your identity is bigger than one person's demand.",
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Identity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as labeling.',
               'A single mistake becomes a permanent name for who you are.',
               'Labels can silence learning and honest discussion.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Labeling: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as projection.',
               'They accuse you of the behavior they keep showing.',
               'An accusation is not automatically a fact.'],
  'caption': 'Projection: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as confession fishing.',
               'They keep asking until you say something just to end the pressure.',
               'Relief is not the same as voluntary agreement.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Confession Fishing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as forced choice.',
               'You are pushed to pick before you understand the consequences.',
               'A rushed choice may not be a free choice.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Forced Choice: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as conditional apology.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'A repair names the action and its impact.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Conditional Apology: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as apology flooding.',
               'Many apologies arrive, but the behavior never changes.',
               'Words of regret need follow-through.'],
  'caption': 'Apology Flooding: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as premature forgiveness pressure.',
               'You are urged to forgive before you feel heard or safe.',
               'Forgiveness cannot be demanded on a schedule.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Take the time you need to decide what repair means.'],
  'caption': 'Premature Forgiveness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as forced positivity.',
               'Your concern is called negative before anyone considers it.',
               'Hope is healthy; denial is not.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Forced Positivity: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as toxic gratitude.',
               'You are told to be grateful so you will stop naming harm.',
               'Gratitude and honest feedback can coexist.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Toxic Gratitude: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as emotional blackmail.',
               'Love, approval, or safety is tied to doing what they want.',
               'Care should not be a weapon.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Emotional Blackmail: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as coercive texting.',
               'Repeated calls or messages make silence feel impossible.',
               'Availability is not owed every minute.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Coercive Texting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as digital surveillance.',
               'Passwords, locations, or private messages are demanded as proof.',
               'Trust is not built through constant access.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Digital Surveillance: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as password pressure.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'Privacy is normal, even in close relationships.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Password Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as location tracking pressure.',
               'Being tracked is called love, safety, or loyalty.',
               'Safety planning requires consent, not control.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Location Tracking Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as public call-outs.',
               'A private issue is exposed to make you comply from embarrassment.',
               'Public shame discourages honest repair.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Public Call-Outs: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as group pile-on.',
               'Others are brought in to make one person feel outnumbered.',
               'More voices do not make pressure fair.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Group Pile-On: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as proxy fighting.',
               'Someone sends friends or relatives to argue their case.',
               'Direct conflict needs direct communication.'],
  'caption': 'Proxy Fighting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as flying monkeys.',
               'Third parties repeat pressure or rumors for someone else.',
               'You do not have to explain yourself to every messenger.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Flying Monkeys: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as hoovering.',
               'Warm messages return just as you begin creating distance.',
               'A return is not proof that the old pattern is gone.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Hoovering: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as breadcrumbing.',
               'Tiny bits of attention keep you waiting for more.',
               'Occasional contact can create hope without commitment.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Breadcrumbing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as orbiting.',
               'They stay visible online while avoiding a real conversation.',
               'Online signals are not the same as care or clarity.'],
  'caption': 'Orbiting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as jealousy bait.',
               'Another person is mentioned to make you compete for attention.',
               'Love does not require a contest.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Jealousy Bait: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as triangulated praise.',
               'Someone praises another person mainly to make you feel inadequate.',
               'Comparison can be a tool of control.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Triangulated Praise: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as silent punishment.',
               'Contact disappears after you express a need or limit.',
               'A respectful pause includes communication and return.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Silent Punishment: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as rage as leverage.',
               'Anger becomes so big that everyone else must give in.',
               'Big emotion does not make a demand reasonable.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Rage As Leverage: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as intimidating body language.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'Fear changes whether a choice is freely made.'],
  'caption': 'Intimidating Body Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as threatening self-harm for control.',
               'A threat of self-harm appears when you try to leave or say no.',
               'Take threats seriously without becoming the only responder.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Threatening Self-Harm For Control: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as threatening exposure.',
               'Private details are used to force silence or compliance.',
               'Blackmail is not care or conflict resolution.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Save evidence and seek trusted or professional support.'],
  'caption': 'Threatening Exposure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as reputation threats.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'Threats try to isolate you before you can get help.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Reputation Threats: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as legal-sounding intimidation.',
               'Official words are used to scare you without clear facts.',
               'A confident claim is not legal advice.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Legal-Sounding Intimidation: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as financial guilt.',
               'Money spent on you is brought up to control your choices.',
               'Support should not create ownership over you.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Financial Guilt: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as financial secrecy.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'Shared financial decisions need clear information.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Financial Secrecy: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as career sabotage.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'Support should expand your options, not shrink them.'],
  'caption': 'Career Sabotage: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as sleep deprivation pressure.',
               'A fight is kept going until you are too tired to think.',
               'Exhaustion makes consent and problem-solving harder.'],
  'caption': 'Sleep Deprivation Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as substance pressure.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'Impairment cannot create meaningful consent.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Substance Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as sexual coercion.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'Consent must be free, informed, and ongoing.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Sexual Coercion: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as normalizing disrespect.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'Common does not mean healthy.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Normalizing Disrespect: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as double-bind pressure.',
               'Whatever you choose is treated as proof that you are wrong.',
               'No-win rules are designed to keep you off balance.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Double-Bind Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as learned helplessness pressure.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'Small choices can rebuild confidence and options.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Learned Helplessness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as dependency building.',
               'Your outside support, skills, or resources slowly get reduced.',
               'Independence is protective, not disloyal.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Dependency Building: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Approval Addiction',
  'definition': 'Praise arrives only when you ignore your own needs.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as approval addiction.',
               'Praise arrives only when you ignore your own needs.',
               'You do not need to earn basic respect.'],
  'caption': 'Approval Addiction: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Selective Accountability',
  'definition': 'You must apologize in detail while they never repair anything.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as selective accountability.',
               'You must apologize in detail while they never repair anything.',
               'Accountability should not be one-sided.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Selective Accountability: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Weaponized Therapy Language',
  'definition': 'Words like boundaries, triggers, or healing are used to dismiss you.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as weaponized therapy language.',
               'Words like boundaries, triggers, or healing are used to dismiss you.',
               'Helpful language should create clarity, not silence.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Weaponized Therapy Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Diagnosis As Insult',
  'definition': 'A mental-health label is thrown at you to end the discussion.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as diagnosis as insult.',
               'A mental-health label is thrown at you to end the discussion.',
               'Labels are not substitutes for listening.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Diagnosis As Insult: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Revisionist Apologies',
  'definition': 'They apologize for a version of events that leaves out the harm.',
  'benefits': ['Do not let this pattern hide in plain sight.',
               'This can show up as revisionist apologies.',
               'They apologize for a version of events that leaves out the harm.',
               'Repair starts with an accurate account.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'State what happened without debating every detail.'],
  'caption': 'Revisionist Apologies: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as foot-in-the-door pressure.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Consent to one thing is not consent to the next.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Foot-In-The-Door Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as door-in-the-face pressure.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Relief can make a request feel fair when it still is not right for you.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Door-In-The-Face Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as lowballing.',
               'The terms get worse only after you have invested time, hope, or money.',
               'An agreement can be reconsidered when the conditions change.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Lowballing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as sunk-cost pressure.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Past effort is not a reason to accept future harm.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Ask what you would choose if starting today.'],
  'caption': 'Sunk-Cost Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as scarcity pressure.',
               'Something is called rare or almost gone before you can think clearly.',
               'Limited supply does not remove your right to pause.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Step back and verify the claim independently.'],
  'caption': 'Scarcity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as social-proof pressure.',
               'You are told everybody agrees, buys, or puts up with it.',
               'A crowd can be wrong, and private discomfort still matters.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Ask for evidence, not a head count.'],
  'caption': 'Social-Proof Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as authority pressure.',
               'A title or confident voice is used to shut down your questions.',
               'Expertise deserves respect, not blind obedience.'],
  'caption': 'Authority Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as reciprocity pressure.',
               'A gift or favor quietly turns into an obligation.',
               'Kindness is not a contract for access or compliance.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Reciprocity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as fear-based messaging.',
               'A scary outcome is presented as certain unless you obey.',
               'Fear narrows thinking and makes weak claims feel urgent.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Fear-Based Messaging: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as false dilemma.',
               'You are told there are only two choices when there may be more.',
               'Pressure often hides alternatives.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'False Dilemma: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as loaded questions.',
               'Any answer seems to make you admit something unfair.',
               'A question can contain an accusation instead of seeking truth.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Correct the premise before answering.'],
  'caption': 'Loaded Questions: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as leading questions.',
               'The wording pushes you toward the answer they want.',
               'A fair question leaves room for your real view.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Leading Questions: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as gish gallop.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Speed is not evidence.'],
  'caption': 'Gish Gallop: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as whataboutism.',
               'Your concern gets replaced with a different accusation about you.',
               'Two issues can exist without one erasing the other.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Whataboutism: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as straw-man framing.',
               'Your actual point gets replaced with an extreme version.',
               'You deserve to be responded to accurately.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               "Say: 'That is not what I said. My point is...'"],
  'caption': 'Straw-Man Framing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as appeal to pity.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Compassion and accountability can stand together.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Appeal To Pity: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as moral licensing.',
               'One good act is used to excuse a repeated harmful act.',
               'Being kind sometimes does not cancel a pattern.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Moral Licensing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as trauma dumping for leverage.',
               'A painful story appears only when you set a limit.',
               "Someone's pain matters, but your boundary still matters too.",
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Offer care without abandoning your limit.'],
  'caption': 'Trauma Dumping For Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as manufactured crisis.',
               'Every request becomes an emergency that only you can solve.',
               'Constant crisis can train you to ignore your own needs.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Manufactured Crisis: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as time pressure.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Good decisions can usually survive a short pause.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Time Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as information withholding.',
               'Key details arrive after you have already agreed.',
               'Informed consent needs the relevant facts first.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Information Withholding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as selective evidence.',
               'Only facts that support one conclusion are repeated.',
               'A fair picture includes inconvenient facts too.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Selective Evidence: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as cherry-picked statistics.',
               'One number is used without context to make a claim feel final.',
               'Numbers need a source, comparison, and timeframe.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Cherry-Picked Statistics: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as fake consensus.',
               'They claim others privately agree with them but name no one.',
               'Unnamed agreement is not proof.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Fake Consensus: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as bandwagon shame.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Belonging should not require surrendering your judgment.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               "Let your values choose, not the crowd's mood."],
  'caption': 'Bandwagon Shame: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as purity tests.',
               'One imperfect choice is used to label you disloyal or bad.',
               'Healthy relationships allow complexity and growth.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Purity Tests: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as moving deadlines.',
               'The deadline changes whenever you need time to think.',
               'Unstable deadlines can keep you anxious and compliant.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Moving Deadlines: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as bait-and-switch.',
               'What was promised is not what appears after you commit.',
               'You are allowed to walk away from changed terms.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Compare the offer to the original promise.'],
  'caption': 'Bait-And-Switch: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as future pacing.',
               'A vivid future is described to make you commit in the present.',
               'A beautiful story is not evidence of a safe pattern.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Future Pacing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as identity pressure.',
               'They say a good friend, parent, worker, or partner would obey.',
               "Your identity is bigger than one person's demand.",
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Identity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as labeling.',
               'A single mistake becomes a permanent name for who you are.',
               'Labels can silence learning and honest discussion.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Labeling: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as projection.',
               'They accuse you of the behavior they keep showing.',
               'An accusation is not automatically a fact.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Projection: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as confession fishing.',
               'They keep asking until you say something just to end the pressure.',
               'Relief is not the same as voluntary agreement.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Confession Fishing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as forced choice.',
               'You are pushed to pick before you understand the consequences.',
               'A rushed choice may not be a free choice.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Forced Choice: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as conditional apology.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'A repair names the action and its impact.'],
  'caption': 'Conditional Apology: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as apology flooding.',
               'Many apologies arrive, but the behavior never changes.',
               'Words of regret need follow-through.'],
  'caption': 'Apology Flooding: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as premature forgiveness pressure.',
               'You are urged to forgive before you feel heard or safe.',
               'Forgiveness cannot be demanded on a schedule.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Premature Forgiveness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as forced positivity.',
               'Your concern is called negative before anyone considers it.',
               'Hope is healthy; denial is not.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Forced Positivity: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as toxic gratitude.',
               'You are told to be grateful so you will stop naming harm.',
               'Gratitude and honest feedback can coexist.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Appreciate what is real without denying what hurts.'],
  'caption': 'Toxic Gratitude: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as emotional blackmail.',
               'Love, approval, or safety is tied to doing what they want.',
               'Care should not be a weapon.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Emotional Blackmail: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as coercive texting.',
               'Repeated calls or messages make silence feel impossible.',
               'Availability is not owed every minute.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Coercive Texting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as digital surveillance.',
               'Passwords, locations, or private messages are demanded as proof.',
               'Trust is not built through constant access.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Digital Surveillance: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as password pressure.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'Privacy is normal, even in close relationships.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Password Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as location tracking pressure.',
               'Being tracked is called love, safety, or loyalty.',
               'Safety planning requires consent, not control.'],
  'caption': 'Location Tracking Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as public call-outs.',
               'A private issue is exposed to make you comply from embarrassment.',
               'Public shame discourages honest repair.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Public Call-Outs: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as group pile-on.',
               'Others are brought in to make one person feel outnumbered.',
               'More voices do not make pressure fair.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Group Pile-On: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as proxy fighting.',
               'Someone sends friends or relatives to argue their case.',
               'Direct conflict needs direct communication.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Proxy Fighting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as flying monkeys.',
               'Third parties repeat pressure or rumors for someone else.',
               'You do not have to explain yourself to every messenger.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Use one calm boundary and disengage.'],
  'caption': 'Flying Monkeys: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as hoovering.',
               'Warm messages return just as you begin creating distance.',
               'A return is not proof that the old pattern is gone.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Look for sustained change, not a sudden pull.'],
  'caption': 'Hoovering: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as breadcrumbing.',
               'Tiny bits of attention keep you waiting for more.',
               'Occasional contact can create hope without commitment.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Breadcrumbing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as orbiting.',
               'They stay visible online while avoiding a real conversation.',
               'Online signals are not the same as care or clarity.'],
  'caption': 'Orbiting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as jealousy bait.',
               'Another person is mentioned to make you compete for attention.',
               'Love does not require a contest.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Jealousy Bait: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as triangulated praise.',
               'Someone praises another person mainly to make you feel inadequate.',
               'Comparison can be a tool of control.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Triangulated Praise: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as silent punishment.',
               'Contact disappears after you express a need or limit.',
               'A respectful pause includes communication and return.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Silent Punishment: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as rage as leverage.',
               'Anger becomes so big that everyone else must give in.',
               'Big emotion does not make a demand reasonable.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Leave the conversation if you feel unsafe.'],
  'caption': 'Rage As Leverage: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as intimidating body language.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'Fear changes whether a choice is freely made.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Intimidating Body Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as threatening self-harm for control.',
               'A threat of self-harm appears when you try to leave or say no.',
               'Take threats seriously without becoming the only responder.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Threatening Self-Harm For Control: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as threatening exposure.',
               'Private details are used to force silence or compliance.',
               'Blackmail is not care or conflict resolution.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Threatening Exposure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as reputation threats.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'Threats try to isolate you before you can get help.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Reputation Threats: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as legal-sounding intimidation.',
               'Official words are used to scare you without clear facts.',
               'A confident claim is not legal advice.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Legal-Sounding Intimidation: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as financial guilt.',
               'Money spent on you is brought up to control your choices.',
               'Support should not create ownership over you.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Separate appreciation from obligation.'],
  'caption': 'Financial Guilt: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as financial secrecy.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'Shared financial decisions need clear information.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Keep copies of records and ask direct questions.'],
  'caption': 'Financial Secrecy: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as career sabotage.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'Support should expand your options, not shrink them.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Career Sabotage: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as sleep deprivation pressure.',
               'A fight is kept going until you are too tired to think.',
               'Exhaustion makes consent and problem-solving harder.'],
  'caption': 'Sleep Deprivation Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as substance pressure.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'Impairment cannot create meaningful consent.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Leave, call someone safe, or choose a clear no.'],
  'caption': 'Substance Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as sexual coercion.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'Consent must be free, informed, and ongoing.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Sexual Coercion: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as normalizing disrespect.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'Common does not mean healthy.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Normalizing Disrespect: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as double-bind pressure.',
               'Whatever you choose is treated as proof that you are wrong.',
               'No-win rules are designed to keep you off balance.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Double-Bind Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as learned helplessness pressure.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'Small choices can rebuild confidence and options.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Tell one safe person what has been happening.'],
  'caption': 'Learned Helplessness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as dependency building.',
               'Your outside support, skills, or resources slowly get reduced.',
               'Independence is protective, not disloyal.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Dependency Building: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Approval Addiction',
  'definition': 'Praise arrives only when you ignore your own needs.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as approval addiction.',
               'Praise arrives only when you ignore your own needs.',
               'You do not need to earn basic respect.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Approval Addiction: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Selective Accountability',
  'definition': 'You must apologize in detail while they never repair anything.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as selective accountability.',
               'You must apologize in detail while they never repair anything.',
               'Accountability should not be one-sided.'],
  'caption': 'Selective Accountability: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Weaponized Therapy Language',
  'definition': 'Words like boundaries, triggers, or healing are used to dismiss you.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as weaponized therapy language.',
               'Words like boundaries, triggers, or healing are used to dismiss you.',
               'Helpful language should create clarity, not silence.'],
  'caption': 'Weaponized Therapy Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Diagnosis As Insult',
  'definition': 'A mental-health label is thrown at you to end the discussion.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as diagnosis as insult.',
               'A mental-health label is thrown at you to end the discussion.',
               'Labels are not substitutes for listening.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Diagnosis As Insult: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Revisionist Apologies',
  'definition': 'They apologize for a version of events that leaves out the harm.',
  'benefits': ['Pause when this starts feeling normal.',
               'This can show up as revisionist apologies.',
               'They apologize for a version of events that leaves out the harm.',
               'Repair starts with an accurate account.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'State what happened without debating every detail.'],
  'caption': 'Revisionist Apologies: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as foot-in-the-door pressure.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Consent to one thing is not consent to the next.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Foot-In-The-Door Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as door-in-the-face pressure.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Relief can make a request feel fair when it still is not right for you.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Door-In-The-Face Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as lowballing.',
               'The terms get worse only after you have invested time, hope, or money.',
               'An agreement can be reconsidered when the conditions change.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Lowballing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as sunk-cost pressure.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Past effort is not a reason to accept future harm.'],
  'caption': 'Sunk-Cost Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as scarcity pressure.',
               'Something is called rare or almost gone before you can think clearly.',
               'Limited supply does not remove your right to pause.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Step back and verify the claim independently.'],
  'caption': 'Scarcity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as social-proof pressure.',
               'You are told everybody agrees, buys, or puts up with it.',
               'A crowd can be wrong, and private discomfort still matters.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Social-Proof Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as authority pressure.',
               'A title or confident voice is used to shut down your questions.',
               'Expertise deserves respect, not blind obedience.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Authority Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as reciprocity pressure.',
               'A gift or favor quietly turns into an obligation.',
               'Kindness is not a contract for access or compliance.'],
  'caption': 'Reciprocity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as fear-based messaging.',
               'A scary outcome is presented as certain unless you obey.',
               'Fear narrows thinking and makes weak claims feel urgent.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Fear-Based Messaging: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as false dilemma.',
               'You are told there are only two choices when there may be more.',
               'Pressure often hides alternatives.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'False Dilemma: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as loaded questions.',
               'Any answer seems to make you admit something unfair.',
               'A question can contain an accusation instead of seeking truth.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Correct the premise before answering.'],
  'caption': 'Loaded Questions: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as leading questions.',
               'The wording pushes you toward the answer they want.',
               'A fair question leaves room for your real view.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Leading Questions: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as gish gallop.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Speed is not evidence.'],
  'caption': 'Gish Gallop: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as whataboutism.',
               'Your concern gets replaced with a different accusation about you.',
               'Two issues can exist without one erasing the other.'],
  'caption': 'Whataboutism: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as straw-man framing.',
               'Your actual point gets replaced with an extreme version.',
               'You deserve to be responded to accurately.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Straw-Man Framing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as appeal to pity.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Compassion and accountability can stand together.'],
  'caption': 'Appeal To Pity: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as moral licensing.',
               'One good act is used to excuse a repeated harmful act.',
               'Being kind sometimes does not cancel a pattern.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Moral Licensing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as trauma dumping for leverage.',
               'A painful story appears only when you set a limit.',
               "Someone's pain matters, but your boundary still matters too.",
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Trauma Dumping For Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as manufactured crisis.',
               'Every request becomes an emergency that only you can solve.',
               'Constant crisis can train you to ignore your own needs.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Manufactured Crisis: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as time pressure.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Good decisions can usually survive a short pause.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Time Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as information withholding.',
               'Key details arrive after you have already agreed.',
               'Informed consent needs the relevant facts first.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Information Withholding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as selective evidence.',
               'Only facts that support one conclusion are repeated.',
               'A fair picture includes inconvenient facts too.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Selective Evidence: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as cherry-picked statistics.',
               'One number is used without context to make a claim feel final.',
               'Numbers need a source, comparison, and timeframe.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Cherry-Picked Statistics: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as fake consensus.',
               'They claim others privately agree with them but name no one.',
               'Unnamed agreement is not proof.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Speak directly with people instead of chasing rumors.'],
  'caption': 'Fake Consensus: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as bandwagon shame.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Belonging should not require surrendering your judgment.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Bandwagon Shame: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as purity tests.',
               'One imperfect choice is used to label you disloyal or bad.',
               'Healthy relationships allow complexity and growth.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Purity Tests: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as moving deadlines.',
               'The deadline changes whenever you need time to think.',
               'Unstable deadlines can keep you anxious and compliant.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Set your own decision time where possible.'],
  'caption': 'Moving Deadlines: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as bait-and-switch.',
               'What was promised is not what appears after you commit.',
               'You are allowed to walk away from changed terms.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Compare the offer to the original promise.'],
  'caption': 'Bait-And-Switch: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as future pacing.',
               'A vivid future is described to make you commit in the present.',
               'A beautiful story is not evidence of a safe pattern.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Future Pacing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as identity pressure.',
               'They say a good friend, parent, worker, or partner would obey.',
               "Your identity is bigger than one person's demand.",
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Identity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as labeling.',
               'A single mistake becomes a permanent name for who you are.',
               'Labels can silence learning and honest discussion.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Labeling: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as projection.',
               'They accuse you of the behavior they keep showing.',
               'An accusation is not automatically a fact.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Focus on observable actions and dates.'],
  'caption': 'Projection: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as confession fishing.',
               'They keep asking until you say something just to end the pressure.',
               'Relief is not the same as voluntary agreement.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Confession Fishing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as forced choice.',
               'You are pushed to pick before you understand the consequences.',
               'A rushed choice may not be a free choice.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Forced Choice: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as conditional apology.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'A repair names the action and its impact.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Conditional Apology: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as apology flooding.',
               'Many apologies arrive, but the behavior never changes.',
               'Words of regret need follow-through.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Apology Flooding: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as premature forgiveness pressure.',
               'You are urged to forgive before you feel heard or safe.',
               'Forgiveness cannot be demanded on a schedule.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Premature Forgiveness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as forced positivity.',
               'Your concern is called negative before anyone considers it.',
               'Hope is healthy; denial is not.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Forced Positivity: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as toxic gratitude.',
               'You are told to be grateful so you will stop naming harm.',
               'Gratitude and honest feedback can coexist.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Toxic Gratitude: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as emotional blackmail.',
               'Love, approval, or safety is tied to doing what they want.',
               'Care should not be a weapon.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Emotional Blackmail: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as coercive texting.',
               'Repeated calls or messages make silence feel impossible.',
               'Availability is not owed every minute.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Mute, pause, and respond when you choose.'],
  'caption': 'Coercive Texting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as digital surveillance.',
               'Passwords, locations, or private messages are demanded as proof.',
               'Trust is not built through constant access.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Digital Surveillance: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as password pressure.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'Privacy is normal, even in close relationships.'],
  'caption': 'Password Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as location tracking pressure.',
               'Being tracked is called love, safety, or loyalty.',
               'Safety planning requires consent, not control.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Location Tracking Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as public call-outs.',
               'A private issue is exposed to make you comply from embarrassment.',
               'Public shame discourages honest repair.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Public Call-Outs: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as group pile-on.',
               'Others are brought in to make one person feel outnumbered.',
               'More voices do not make pressure fair.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Group Pile-On: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as proxy fighting.',
               'Someone sends friends or relatives to argue their case.',
               'Direct conflict needs direct communication.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Proxy Fighting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as flying monkeys.',
               'Third parties repeat pressure or rumors for someone else.',
               'You do not have to explain yourself to every messenger.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Flying Monkeys: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as hoovering.',
               'Warm messages return just as you begin creating distance.',
               'A return is not proof that the old pattern is gone.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Hoovering: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as breadcrumbing.',
               'Tiny bits of attention keep you waiting for more.',
               'Occasional contact can create hope without commitment.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Breadcrumbing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as orbiting.',
               'They stay visible online while avoiding a real conversation.',
               'Online signals are not the same as care or clarity.'],
  'caption': 'Orbiting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as jealousy bait.',
               'Another person is mentioned to make you compete for attention.',
               'Love does not require a contest.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Refuse comparison and state what respect looks like.'],
  'caption': 'Jealousy Bait: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as triangulated praise.',
               'Someone praises another person mainly to make you feel inadequate.',
               'Comparison can be a tool of control.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Triangulated Praise: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as silent punishment.',
               'Contact disappears after you express a need or limit.',
               'A respectful pause includes communication and return.'],
  'caption': 'Silent Punishment: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as rage as leverage.',
               'Anger becomes so big that everyone else must give in.',
               'Big emotion does not make a demand reasonable.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Rage As Leverage: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as intimidating body language.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'Fear changes whether a choice is freely made.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Intimidating Body Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as threatening self-harm for control.',
               'A threat of self-harm appears when you try to leave or say no.',
               'Take threats seriously without becoming the only responder.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Contact emergency or crisis support and tell a trusted person.'],
  'caption': 'Threatening Self-Harm For Control: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as threatening exposure.',
               'Private details are used to force silence or compliance.',
               'Blackmail is not care or conflict resolution.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Threatening Exposure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as reputation threats.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'Threats try to isolate you before you can get help.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Reputation Threats: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as legal-sounding intimidation.',
               'Official words are used to scare you without clear facts.',
               'A confident claim is not legal advice.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Check information with a qualified, independent source.'],
  'caption': 'Legal-Sounding Intimidation: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as financial guilt.',
               'Money spent on you is brought up to control your choices.',
               'Support should not create ownership over you.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Financial Guilt: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as financial secrecy.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'Shared financial decisions need clear information.'],
  'caption': 'Financial Secrecy: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as career sabotage.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'Support should expand your options, not shrink them.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Career Sabotage: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as sleep deprivation pressure.',
               'A fight is kept going until you are too tired to think.',
               'Exhaustion makes consent and problem-solving harder.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Sleep Deprivation Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as substance pressure.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'Impairment cannot create meaningful consent.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Substance Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as sexual coercion.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'Consent must be free, informed, and ongoing.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Sexual Coercion: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as normalizing disrespect.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'Common does not mean healthy.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Normalizing Disrespect: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as double-bind pressure.',
               'Whatever you choose is treated as proof that you are wrong.',
               'No-win rules are designed to keep you off balance.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Double-Bind Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as learned helplessness pressure.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'Small choices can rebuild confidence and options.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Learned Helplessness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as dependency building.',
               'Your outside support, skills, or resources slowly get reduced.',
               'Independence is protective, not disloyal.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Dependency Building: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Approval Addiction',
  'definition': 'Praise arrives only when you ignore your own needs.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as approval addiction.',
               'Praise arrives only when you ignore your own needs.',
               'You do not need to earn basic respect.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Approval Addiction: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Selective Accountability',
  'definition': 'You must apologize in detail while they never repair anything.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as selective accountability.',
               'You must apologize in detail while they never repair anything.',
               'Accountability should not be one-sided.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Selective Accountability: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Weaponized Therapy Language',
  'definition': 'Words like boundaries, triggers, or healing are used to dismiss you.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as weaponized therapy language.',
               'Words like boundaries, triggers, or healing are used to dismiss you.',
               'Helpful language should create clarity, not silence.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Weaponized Therapy Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Diagnosis As Insult',
  'definition': 'A mental-health label is thrown at you to end the discussion.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as diagnosis as insult.',
               'A mental-health label is thrown at you to end the discussion.',
               'Labels are not substitutes for listening.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Diagnosis As Insult: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Revisionist Apologies',
  'definition': 'They apologize for a version of events that leaves out the harm.',
  'benefits': ['Signs this may be more than a misunderstanding.',
               'This can show up as revisionist apologies.',
               'They apologize for a version of events that leaves out the harm.',
               'Repair starts with an accurate account.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Revisionist Apologies: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as foot-in-the-door pressure.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Consent to one thing is not consent to the next.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Foot-In-The-Door Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as door-in-the-face pressure.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Relief can make a request feel fair when it still is not right for you.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Door-In-The-Face Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as lowballing.',
               'The terms get worse only after you have invested time, hope, or money.',
               'An agreement can be reconsidered when the conditions change.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Lowballing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as sunk-cost pressure.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Past effort is not a reason to accept future harm.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Sunk-Cost Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as scarcity pressure.',
               'Something is called rare or almost gone before you can think clearly.',
               'Limited supply does not remove your right to pause.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Scarcity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as social-proof pressure.',
               'You are told everybody agrees, buys, or puts up with it.',
               'A crowd can be wrong, and private discomfort still matters.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Social-Proof Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as authority pressure.',
               'A title or confident voice is used to shut down your questions.',
               'Expertise deserves respect, not blind obedience.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Authority Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as reciprocity pressure.',
               'A gift or favor quietly turns into an obligation.',
               'Kindness is not a contract for access or compliance.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Reciprocity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as fear-based messaging.',
               'A scary outcome is presented as certain unless you obey.',
               'Fear narrows thinking and makes weak claims feel urgent.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Fear-Based Messaging: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as false dilemma.',
               'You are told there are only two choices when there may be more.',
               'Pressure often hides alternatives.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'False Dilemma: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as loaded questions.',
               'Any answer seems to make you admit something unfair.',
               'A question can contain an accusation instead of seeking truth.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Loaded Questions: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as leading questions.',
               'The wording pushes you toward the answer they want.',
               'A fair question leaves room for your real view.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Leading Questions: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as gish gallop.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Speed is not evidence.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Gish Gallop: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as whataboutism.',
               'Your concern gets replaced with a different accusation about you.',
               'Two issues can exist without one erasing the other.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Whataboutism: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as straw-man framing.',
               'Your actual point gets replaced with an extreme version.',
               'You deserve to be responded to accurately.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Straw-Man Framing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as appeal to pity.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Compassion and accountability can stand together.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Appeal To Pity: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as moral licensing.',
               'One good act is used to excuse a repeated harmful act.',
               'Being kind sometimes does not cancel a pattern.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Moral Licensing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as trauma dumping for leverage.',
               'A painful story appears only when you set a limit.',
               "Someone's pain matters, but your boundary still matters too.",
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Trauma Dumping For Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as manufactured crisis.',
               'Every request becomes an emergency that only you can solve.',
               'Constant crisis can train you to ignore your own needs.'],
  'caption': 'Manufactured Crisis: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as time pressure.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Good decisions can usually survive a short pause.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Time Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as information withholding.',
               'Key details arrive after you have already agreed.',
               'Informed consent needs the relevant facts first.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Ask what has not been disclosed yet.'],
  'caption': 'Information Withholding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as selective evidence.',
               'Only facts that support one conclusion are repeated.',
               'A fair picture includes inconvenient facts too.'],
  'caption': 'Selective Evidence: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as cherry-picked statistics.',
               'One number is used without context to make a claim feel final.',
               'Numbers need a source, comparison, and timeframe.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Cherry-Picked Statistics: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as fake consensus.',
               'They claim others privately agree with them but name no one.',
               'Unnamed agreement is not proof.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Fake Consensus: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as bandwagon shame.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Belonging should not require surrendering your judgment.'],
  'caption': 'Bandwagon Shame: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Purity Tests',
  'definition': 'One imperfect choice is used to label you disloyal or bad.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as purity tests.',
               'One imperfect choice is used to label you disloyal or bad.',
               'Healthy relationships allow complexity and growth.'],
  'caption': 'Purity Tests: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Moving Deadlines',
  'definition': 'The deadline changes whenever you need time to think.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as moving deadlines.',
               'The deadline changes whenever you need time to think.',
               'Unstable deadlines can keep you anxious and compliant.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Moving Deadlines: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Bait-And-Switch',
  'definition': 'What was promised is not what appears after you commit.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as bait-and-switch.',
               'What was promised is not what appears after you commit.',
               'You are allowed to walk away from changed terms.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Bait-And-Switch: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Future Pacing',
  'definition': 'A vivid future is described to make you commit in the present.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as future pacing.',
               'A vivid future is described to make you commit in the present.',
               'A beautiful story is not evidence of a safe pattern.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Future Pacing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Identity Pressure',
  'definition': 'They say a good friend, parent, worker, or partner would obey.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as identity pressure.',
               'They say a good friend, parent, worker, or partner would obey.',
               "Your identity is bigger than one person's demand.",
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Identity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Labeling',
  'definition': 'A single mistake becomes a permanent name for who you are.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as labeling.',
               'A single mistake becomes a permanent name for who you are.',
               'Labels can silence learning and honest discussion.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Labeling: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Projection',
  'definition': 'They accuse you of the behavior they keep showing.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as projection.',
               'They accuse you of the behavior they keep showing.',
               'An accusation is not automatically a fact.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Projection: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Confession Fishing',
  'definition': 'They keep asking until you say something just to end the pressure.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as confession fishing.',
               'They keep asking until you say something just to end the pressure.',
               'Relief is not the same as voluntary agreement.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Take a break before answering loaded questions.'],
  'caption': 'Confession Fishing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Forced Choice',
  'definition': 'You are pushed to pick before you understand the consequences.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as forced choice.',
               'You are pushed to pick before you understand the consequences.',
               'A rushed choice may not be a free choice.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Ask for time, details, and another option.'],
  'caption': 'Forced Choice: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Conditional Apology',
  'definition': "You hear 'sorry you feel that way' instead of ownership.",
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as conditional apology.',
               "You hear 'sorry you feel that way' instead of ownership.",
               'A repair names the action and its impact.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Conditional Apology: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Apology Flooding',
  'definition': 'Many apologies arrive, but the behavior never changes.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as apology flooding.',
               'Many apologies arrive, but the behavior never changes.',
               'Words of regret need follow-through.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Apology Flooding: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Premature Forgiveness Pressure',
  'definition': 'You are urged to forgive before you feel heard or safe.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as premature forgiveness pressure.',
               'You are urged to forgive before you feel heard or safe.',
               'Forgiveness cannot be demanded on a schedule.'],
  'caption': 'Premature Forgiveness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Forced Positivity',
  'definition': 'Your concern is called negative before anyone considers it.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as forced positivity.',
               'Your concern is called negative before anyone considers it.',
               'Hope is healthy; denial is not.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Forced Positivity: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Toxic Gratitude',
  'definition': 'You are told to be grateful so you will stop naming harm.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as toxic gratitude.',
               'You are told to be grateful so you will stop naming harm.',
               'Gratitude and honest feedback can coexist.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Appreciate what is real without denying what hurts.'],
  'caption': 'Toxic Gratitude: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Emotional Blackmail',
  'definition': 'Love, approval, or safety is tied to doing what they want.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as emotional blackmail.',
               'Love, approval, or safety is tied to doing what they want.',
               'Care should not be a weapon.'],
  'caption': 'Emotional Blackmail: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Coercive Texting',
  'definition': 'Repeated calls or messages make silence feel impossible.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as coercive texting.',
               'Repeated calls or messages make silence feel impossible.',
               'Availability is not owed every minute.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Coercive Texting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Digital Surveillance',
  'definition': 'Passwords, locations, or private messages are demanded as proof.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as digital surveillance.',
               'Passwords, locations, or private messages are demanded as proof.',
               'Trust is not built through constant access.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Digital Surveillance: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Password Pressure',
  'definition': 'Sharing a password is framed as proof that you have nothing to hide.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as password pressure.',
               'Sharing a password is framed as proof that you have nothing to hide.',
               'Privacy is normal, even in close relationships.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Password Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Location Tracking Pressure',
  'definition': 'Being tracked is called love, safety, or loyalty.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as location tracking pressure.',
               'Being tracked is called love, safety, or loyalty.',
               'Safety planning requires consent, not control.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Location Tracking Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Public Call-Outs',
  'definition': 'A private issue is exposed to make you comply from embarrassment.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as public call-outs.',
               'A private issue is exposed to make you comply from embarrassment.',
               'Public shame discourages honest repair.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Public Call-Outs: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Group Pile-On',
  'definition': 'Others are brought in to make one person feel outnumbered.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as group pile-on.',
               'Others are brought in to make one person feel outnumbered.',
               'More voices do not make pressure fair.'],
  'caption': 'Group Pile-On: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Proxy Fighting',
  'definition': 'Someone sends friends or relatives to argue their case.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as proxy fighting.',
               'Someone sends friends or relatives to argue their case.',
               'Direct conflict needs direct communication.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Avoid debating through messengers.'],
  'caption': 'Proxy Fighting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Flying Monkeys',
  'definition': 'Third parties repeat pressure or rumors for someone else.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as flying monkeys.',
               'Third parties repeat pressure or rumors for someone else.',
               'You do not have to explain yourself to every messenger.'],
  'caption': 'Flying Monkeys: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Hoovering',
  'definition': 'Warm messages return just as you begin creating distance.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as hoovering.',
               'Warm messages return just as you begin creating distance.',
               'A return is not proof that the old pattern is gone.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Hoovering: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Breadcrumbing',
  'definition': 'Tiny bits of attention keep you waiting for more.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as breadcrumbing.',
               'Tiny bits of attention keep you waiting for more.',
               'Occasional contact can create hope without commitment.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Breadcrumbing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Orbiting',
  'definition': 'They stay visible online while avoiding a real conversation.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as orbiting.',
               'They stay visible online while avoiding a real conversation.',
               'Online signals are not the same as care or clarity.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Orbiting: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Jealousy Bait',
  'definition': 'Another person is mentioned to make you compete for attention.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as jealousy bait.',
               'Another person is mentioned to make you compete for attention.',
               'Love does not require a contest.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Jealousy Bait: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Triangulated Praise',
  'definition': 'Someone praises another person mainly to make you feel inadequate.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as triangulated praise.',
               'Someone praises another person mainly to make you feel inadequate.',
               'Comparison can be a tool of control.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Triangulated Praise: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Silent Punishment',
  'definition': 'Contact disappears after you express a need or limit.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as silent punishment.',
               'Contact disappears after you express a need or limit.',
               'A respectful pause includes communication and return.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Silent Punishment: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Rage As Leverage',
  'definition': 'Anger becomes so big that everyone else must give in.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as rage as leverage.',
               'Anger becomes so big that everyone else must give in.',
               'Big emotion does not make a demand reasonable.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Rage As Leverage: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Intimidating Body Language',
  'definition': 'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as intimidating body language.',
               'Size, closeness, blocking exits, or aggressive gestures change what feels safe.',
               'Fear changes whether a choice is freely made.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Create space and seek immediate help if needed.'],
  'caption': 'Intimidating Body Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Threatening Self-Harm For Control',
  'definition': 'A threat of self-harm appears when you try to leave or say no.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as threatening self-harm for control.',
               'A threat of self-harm appears when you try to leave or say no.',
               'Take threats seriously without becoming the only responder.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Threatening Self-Harm For Control: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Threatening Exposure',
  'definition': 'Private details are used to force silence or compliance.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as threatening exposure.',
               'Private details are used to force silence or compliance.',
               'Blackmail is not care or conflict resolution.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Threatening Exposure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Reputation Threats',
  'definition': 'They warn that nobody will believe you or that they will ruin your name.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as reputation threats.',
               'They warn that nobody will believe you or that they will ruin your name.',
               'Threats try to isolate you before you can get help.'],
  'caption': 'Reputation Threats: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Legal-Sounding Intimidation',
  'definition': 'Official words are used to scare you without clear facts.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as legal-sounding intimidation.',
               'Official words are used to scare you without clear facts.',
               'A confident claim is not legal advice.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Legal-Sounding Intimidation: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Financial Guilt',
  'definition': 'Money spent on you is brought up to control your choices.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as financial guilt.',
               'Money spent on you is brought up to control your choices.',
               'Support should not create ownership over you.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Financial Guilt: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Financial Secrecy',
  'definition': 'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as financial secrecy.',
               'Accounts, debts, or bills are hidden while you are asked to trust blindly.',
               'Shared financial decisions need clear information.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Financial Secrecy: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Career Sabotage',
  'definition': 'Your work, study, or goals are quietly undermined to make you dependent.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as career sabotage.',
               'Your work, study, or goals are quietly undermined to make you dependent.',
               'Support should expand your options, not shrink them.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Career Sabotage: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Sleep Deprivation Pressure',
  'definition': 'A fight is kept going until you are too tired to think.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as sleep deprivation pressure.',
               'A fight is kept going until you are too tired to think.',
               'Exhaustion makes consent and problem-solving harder.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Sleep Deprivation Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Substance Pressure',
  'definition': 'Alcohol or drugs are pushed after you show hesitation.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as substance pressure.',
               'Alcohol or drugs are pushed after you show hesitation.',
               'Impairment cannot create meaningful consent.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Substance Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Sexual Coercion',
  'definition': 'Affection, guilt, sulking, or persistence is used after a no.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as sexual coercion.',
               'Affection, guilt, sulking, or persistence is used after a no.',
               'Consent must be free, informed, and ongoing.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Sexual Coercion: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Normalizing Disrespect',
  'definition': 'Harmful behavior is called normal, traditional, or just how people are.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as normalizing disrespect.',
               'Harmful behavior is called normal, traditional, or just how people are.',
               'Common does not mean healthy.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Compare the behavior with your values and safety.'],
  'caption': 'Normalizing Disrespect: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Double-Bind Pressure',
  'definition': 'Whatever you choose is treated as proof that you are wrong.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as double-bind pressure.',
               'Whatever you choose is treated as proof that you are wrong.',
               'No-win rules are designed to keep you off balance.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Double-Bind Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Learned Helplessness Pressure',
  'definition': 'After repeated setbacks, you start believing you cannot choose differently.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as learned helplessness pressure.',
               'After repeated setbacks, you start believing you cannot choose differently.',
               'Small choices can rebuild confidence and options.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Learned Helplessness Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Dependency Building',
  'definition': 'Your outside support, skills, or resources slowly get reduced.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as dependency building.',
               'Your outside support, skills, or resources slowly get reduced.',
               'Independence is protective, not disloyal.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Dependency Building: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Approval Addiction',
  'definition': 'Praise arrives only when you ignore your own needs.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as approval addiction.',
               'Praise arrives only when you ignore your own needs.',
               'You do not need to earn basic respect.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Approval Addiction: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Selective Accountability',
  'definition': 'You must apologize in detail while they never repair anything.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as selective accountability.',
               'You must apologize in detail while they never repair anything.',
               'Accountability should not be one-sided.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Selective Accountability: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Weaponized Therapy Language',
  'definition': 'Words like boundaries, triggers, or healing are used to dismiss you.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as weaponized therapy language.',
               'Words like boundaries, triggers, or healing are used to dismiss you.',
               'Helpful language should create clarity, not silence.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Weaponized Therapy Language: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Diagnosis As Insult',
  'definition': 'A mental-health label is thrown at you to end the discussion.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as diagnosis as insult.',
               'A mental-health label is thrown at you to end the discussion.',
               'Labels are not substitutes for listening.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Return to the behavior and its impact.'],
  'caption': 'Diagnosis As Insult: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Revisionist Apologies',
  'definition': 'They apologize for a version of events that leaves out the harm.',
  'benefits': ['Protect your peace when this keeps repeating.',
               'This can show up as revisionist apologies.',
               'They apologize for a version of events that leaves out the harm.',
               'Repair starts with an accurate account.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Revisionist Apologies: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Foot-In-The-Door Pressure',
  'definition': 'A tiny yes is treated like permission for a much bigger ask.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as foot-in-the-door pressure.',
               'A tiny yes is treated like permission for a much bigger ask.',
               'Consent to one thing is not consent to the next.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Foot-In-The-Door Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Door-In-The-Face Pressure',
  'definition': 'A huge request is followed by a smaller one that suddenly feels reasonable.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as door-in-the-face pressure.',
               'A huge request is followed by a smaller one that suddenly feels reasonable.',
               'Relief can make a request feel fair when it still is not right for you.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Door-In-The-Face Pressure: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Lowballing',
  'definition': 'The terms get worse only after you have invested time, hope, or money.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as lowballing.',
               'The terms get worse only after you have invested time, hope, or money.',
               'An agreement can be reconsidered when the conditions change.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Lowballing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Sunk-Cost Pressure',
  'definition': "You hear, 'But you have come this far,' when you want to leave.",
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as sunk-cost pressure.',
               "You hear, 'But you have come this far,' when you want to leave.",
               'Past effort is not a reason to accept future harm.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Sunk-Cost Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Scarcity Pressure',
  'definition': 'Something is called rare or almost gone before you can think clearly.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as scarcity pressure.',
               'Something is called rare or almost gone before you can think clearly.',
               'Limited supply does not remove your right to pause.'],
  'caption': 'Scarcity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Social-Proof Pressure',
  'definition': 'You are told everybody agrees, buys, or puts up with it.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as social-proof pressure.',
               'You are told everybody agrees, buys, or puts up with it.',
               'A crowd can be wrong, and private discomfort still matters.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Social-Proof Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Authority Pressure',
  'definition': 'A title or confident voice is used to shut down your questions.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as authority pressure.',
               'A title or confident voice is used to shut down your questions.',
               'Expertise deserves respect, not blind obedience.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Authority Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Reciprocity Pressure',
  'definition': 'A gift or favor quietly turns into an obligation.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as reciprocity pressure.',
               'A gift or favor quietly turns into an obligation.',
               'Kindness is not a contract for access or compliance.'],
  'caption': 'Reciprocity Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Fear-Based Messaging',
  'definition': 'A scary outcome is presented as certain unless you obey.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as fear-based messaging.',
               'A scary outcome is presented as certain unless you obey.',
               'Fear narrows thinking and makes weak claims feel urgent.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Fear-Based Messaging: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By False Dilemma',
  'definition': 'You are told there are only two choices when there may be more.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as false dilemma.',
               'You are told there are only two choices when there may be more.',
               'Pressure often hides alternatives.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'False Dilemma: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '5 Red Flags You’re Being Manipulated By Loaded Questions',
  'definition': 'Any answer seems to make you admit something unfair.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as loaded questions.',
               'Any answer seems to make you admit something unfair.',
               'A question can contain an accusation instead of seeking truth.',
               'One moment is not proof; repeated pressure deserves attention.'],
  'caption': 'Loaded Questions: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Leading Questions',
  'definition': 'The wording pushes you toward the answer they want.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as leading questions.',
               'The wording pushes you toward the answer they want.',
               'A fair question leaves room for your real view.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Restate the question in neutral words.'],
  'caption': 'Leading Questions: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Gish Gallop',
  'definition': 'So many claims arrive at once that you cannot examine any of them.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as gish gallop.',
               'So many claims arrive at once that you cannot examine any of them.',
               'Speed is not evidence.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Gish Gallop: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Whataboutism',
  'definition': 'Your concern gets replaced with a different accusation about you.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as whataboutism.',
               'Your concern gets replaced with a different accusation about you.',
               'Two issues can exist without one erasing the other.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Whataboutism: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Straw-Man Framing',
  'definition': 'Your actual point gets replaced with an extreme version.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as straw-man framing.',
               'Your actual point gets replaced with an extreme version.',
               'You deserve to be responded to accurately.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               "Say: 'That is not what I said. My point is...'"],
  'caption': 'Straw-Man Framing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Appeal To Pity',
  'definition': 'Their hardship is used to avoid responsibility for hurting you.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as appeal to pity.',
               'Their hardship is used to avoid responsibility for hurting you.',
               'Compassion and accountability can stand together.'],
  'caption': 'Appeal To Pity: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Moral Licensing',
  'definition': 'One good act is used to excuse a repeated harmful act.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as moral licensing.',
               'One good act is used to excuse a repeated harmful act.',
               'Being kind sometimes does not cancel a pattern.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Moral Licensing: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Trauma Dumping For Leverage',
  'definition': 'A painful story appears only when you set a limit.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as trauma dumping for leverage.',
               'A painful story appears only when you set a limit.',
               "Someone's pain matters, but your boundary still matters too."],
  'caption': 'Trauma Dumping For Leverage: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '9 Red Flags You’re Being Manipulated By Manufactured Crisis',
  'definition': 'Every request becomes an emergency that only you can solve.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as manufactured crisis.',
               'Every request becomes an emergency that only you can solve.',
               'Constant crisis can train you to ignore your own needs.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.'],
  'caption': 'Manufactured Crisis: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '7 Red Flags You’re Being Manipulated By Time Pressure',
  'definition': 'You are denied time to read, compare, or ask someone you trust.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as time pressure.',
               'You are denied time to read, compare, or ask someone you trust.',
               'Good decisions can usually survive a short pause.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.'],
  'caption': 'Time Pressure: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '8 Red Flags You’re Being Manipulated By Information Withholding',
  'definition': 'Key details arrive after you have already agreed.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as information withholding.',
               'Key details arrive after you have already agreed.',
               'Informed consent needs the relevant facts first.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.'],
  'caption': 'Information Withholding: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Selective Evidence',
  'definition': 'Only facts that support one conclusion are repeated.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as selective evidence.',
               'Only facts that support one conclusion are repeated.',
               'A fair picture includes inconvenient facts too.'],
  'caption': 'Selective Evidence: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '4 Red Flags You’re Being Manipulated By Cherry-Picked Statistics',
  'definition': 'One number is used without context to make a claim feel final.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as cherry-picked statistics.',
               'One number is used without context to make a claim feel final.',
               'Numbers need a source, comparison, and timeframe.'],
  'caption': 'Cherry-Picked Statistics: spot the pattern, protect your peace. Education only—not a '
             'diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '10 Red Flags You’re Being Manipulated By Fake Consensus',
  'definition': 'They claim others privately agree with them but name no one.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as fake consensus.',
               'They claim others privately agree with them but name no one.',
               'Unnamed agreement is not proof.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.',
               'Write down what happened so the pattern is easier to see clearly.',
               'Talk it through with someone safe who can offer a grounded view.',
               'A healthy connection makes room for your questions and your no.',
               'Speak directly with people instead of chasing rumors.'],
  'caption': 'Fake Consensus: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'},
 {'heading': '6 Red Flags You’re Being Manipulated By Bandwagon Shame',
  'definition': 'Not joining in is framed as weird, selfish, or disloyal.',
  'benefits': ['Quiet warning signs worth taking seriously.',
               'This can show up as bandwagon shame.',
               'Not joining in is framed as weird, selfish, or disloyal.',
               'Belonging should not require surrendering your judgment.',
               'One moment is not proof; repeated pressure deserves attention.',
               'Notice whether you feel rushed, guilty, confused, or afraid to disagree.'],
  'caption': 'Bandwagon Shame: spot the pattern, protect your peace. Education only—not a diagnosis.\n'
             '\n'
             '#Psychology #Boundaries #EmotionalHealth #ManipulationAwareness #Reels'}]

assert len(AWARENESS_TOPICS) == 75, "Keep 75 source topics for the awareness library."
assert len(POSTS) == 1100, "Expected 1,100 posts in the complete visible review list."


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
    """Return only the post topic from the complete visible heading."""
    import re
    plain = re.sub(r"[^\w\s:&'-]", " ", heading, flags=re.UNICODE)
    match = re.search(r"4\s+red\s+flags\s+you\s+are\s+being\s+manipulated\s+by\s+(.+)$", plain, flags=re.I)
    topic = match.group(1).strip() if match else plain.rsplit(":", 1)[-1].strip()
    return topic.upper()[:58]


def wrap_text(draw, text: str, font, max_width: int) -> list[str]:
    """Split text into lines that fit the supplied rendered width."""
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
    """Render a transparent poster overlay: copy on the left, moving character visible on the right."""
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

    # No panel or outer border: the source video remains fully visible behind the text.

    # Exact requested pixel sizes for the reference style.
    lead_font = ImageFont.truetype(font_path, 50)          # “4 RED FLAGS” — 50 px
    dark_font = ImageFont.truetype(font_path, 55)          # “DARK” — 55 px
    impact_font = ImageFont.truetype(font_path, 55)        # “MANIPULATION” — 55 px
    topic_text = visual_heading(post["heading"])
    # The main post heading fills the full video width; all other header text keeps its original size.
    heading_x = 40
    heading_width = TARGET_W - (heading_x * 2)
    base_heading_size = 55 if len(topic_text) <= 22 else (45 if len(topic_text) <= 36 else 38)
    topic_font = ImageFont.truetype(font_path, base_heading_size)
    # Increase only the main-heading font until its longest rendered line nearly fills the width.
    heading_lines_for_size = wrap_text(draw, topic_text, topic_font, heading_width)[:2]
    longest_heading = max(heading_lines_for_size, key=lambda line: draw.textbbox((0, 0), line, font=topic_font)[2])
    longest_width = draw.textbbox((0, 0), longest_heading, font=topic_font)[2]
    if longest_width:
        fitted_size = max(base_heading_size, int(base_heading_size * (heading_width / longest_width) * 0.96))
        topic_font = ImageFont.truetype(font_path, min(fitted_size, 118))
    eyebrow_font = ImageFont.truetype(font_path, 20)
    flag_count = post.get("flag_count", 4)

    # Title hierarchy follows the supplied reference: white lead, large red impact, topic in white.
    x, y = 68, 88
    draw.text((x, y), f"{flag_count} RED FLAGS", font=lead_font, fill=(245, 245, 245, 255))
    y += 34
    draw.text((x, y), "DARK", font=dark_font, fill=(245, 245, 245, 255))
    y += 34
    draw.text((x, y), "MANIPULATION", font=impact_font, fill=(231, 17, 25, 255))
    y += 43
    # The post heading alone uses the full video width. Its height grows only as needed.
    for line in wrap_text(draw, topic_text, topic_font, heading_width)[:2]:
        draw.text((heading_x, y), line, font=topic_font, fill=(242, 242, 242, 255))
        y += topic_font.size + 6
    y += 24

    benefits = post["benefits"]
    count = len(benefits)
    available = 1580 - y
    block_h = max(82, min(166, available // max(1, count)))
    # List copy and red-circle numerals use the requested fixed sizes.
    if count <= 5:
        body_size, num_size, max_lines, line_step = 35, 36, 3, 43
    elif count <= 7:
        body_size, num_size, max_lines, line_step = 35, 36, 2, 43
    else:
        body_size, num_size, max_lines, line_step = 35, 36, 2, 43
    body_font = ImageFont.truetype(regular_path, body_size)
    num_font = ImageFont.truetype(font_path, num_size)
    marker_size = 42 if count <= 5 else (37 if count <= 7 else 32)

    for i, benefit in enumerate(benefits, 1):
        active = active_index == i
        x1, x2 = 62, 666
        fill = (37, 4, 7, 0) if active else (5, 5, 6, 0)
        border = (242, 26, 35, 255) if active else (99, 15, 21, 210)
        draw.rounded_rectangle((x1, y, x2, y + block_h - 10), radius=12, fill=fill, outline=border, width=3 if active else 1)
        marker_y = y + max(10, (block_h - marker_size) // 2)
        draw.ellipse((x1 + 14, marker_y, x1 + 14 + marker_size, marker_y + marker_size), fill=(220, 18, 27, 255), outline=(255, 70, 75, 255), width=1)
        nbox = draw.textbbox((0, 0), str(i), font=num_font)
        draw.text((x1 + 14 + marker_size // 2 - (nbox[2]-nbox[0]) // 2, marker_y + marker_size // 2 - (nbox[3]-nbox[1]) // 2), str(i), font=num_font, fill=(255, 255, 255, 255))
        lines = wrap_text(draw, benefit, body_font, 510)[:max_lines]
        ty = y + max(9, (block_h - len(lines) * line_step) // 2)
        for line in lines:
            draw.text((x1 + 70, ty), line, font=body_font, fill=(255, 255, 255, 255) if active else (205, 205, 205, 255))
            ty += line_step
        y += block_h

    draw.text((68, 1685), "NOTICE THE PATTERN. PROTECT YOUR PEACE.", font=eyebrow_font, fill=(235, 235, 235, 255))
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
    """Write audio-synced captions that animate one complete line at a time.

    Unlike word karaoke, a whole readable line appears, rises in gently, then yields
    to the following line.  Line durations are proportionate to the words spoken.
    """
    from PIL import ImageFont

    lines = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
        "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,"
        "Alignment,MarginL,MarginR,MarginV,Encoding",
        # White, centered, easy to read over moving footage. No karaoke colour change.
        "Style: SingleLine,DejaVu Sans,48,&H00FFFFFF,&H00FFFFFF,&H00101010,&H96000000,1,0,0,0,100,100,0,0,1,3,1,2,70,70,270,1",
        "", "[Events]", "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 48)
    max_width = 930
    cursor = 0.0

    for text, duration in zip(slides, durations):
        words = clean_narration_text(text).split()
        if not words:
            cursor += duration
            continue

        # Build complete, natural single lines that fit inside the safe caption width.
        caption_lines, current = [], []
        for word in words:
            trial = " ".join(current + [word])
            if current and font.getlength(trial) > max_width:
                caption_lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            caption_lines.append(" ".join(current))

        weights = [max(1, sum(len(w.strip(".,!?'-")) for w in line.split())) for line in caption_lines]
        total_weight = sum(weights)
        line_cursor = cursor
        for index, (caption, weight) in enumerate(zip(caption_lines, weights)):
            line_duration = duration * weight / total_weight
            if index == len(caption_lines) - 1:
                line_end = cursor + duration
            else:
                line_end = line_cursor + line_duration
            # Each full line floats up and fades in; it never highlights individual words.
            animation = r"{\an2\move(540,1810,540,1770,0,160)\fad(100,120)}"
            lines.append(
                f"Dialogue: 0,{ass_timestamp(line_cursor)},{ass_timestamp(line_end)},SingleLine,,0,0,0,,{animation}{ass_escape(caption)}"
            )
            line_cursor = line_end
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
    """Read the on-screen heading as one clear, natural opening sentence."""
    topic = visual_heading(post["heading"]).replace("-", " ").lower()
    count = post.get("flag_count", 4)
    return f"Here are {count} red flags that you may be being manipulated by {topic}."


def ending_narration(post: dict) -> str:
    """Define the topic, then finish with a short practical awareness reminder."""
    topic = visual_heading(post["heading"]).replace("-", " ").lower()
    definition = clean_narration_text(post["definition"])
    awareness = clean_narration_text(post.get("ending_awareness", post["benefits"][-1]))
    return f"In dark psychology, {topic} means this: {definition} Awareness: {awareness}"

def make_red_flag_points(post: dict, count: int) -> list[str]:
    """Return 4–10 viewer-safety points for this topic; never instructions to manipulate."""
    core = list(post["benefits"])
    topic = visual_heading(post["heading"]).replace("-", " ").lower()
    extra_points = [
        f"Notice whether {topic} repeats after you set a boundary.",
        "Pay attention to how you feel after the interaction, not only during it.",
        "Healthy connection leaves room for questions, pauses, and no.",
        "Write down what happened if the pattern feels confusing.",
        "Talk it through with someone you trust for a clearer perspective.",
        "You deserve time, clarity, safety, and respect.",
    ]
    return (core + extra_points)[:count]


def pick_background_video() -> Path:
    """Choose one of the creator-supplied background clips from assets/videos."""
    videos = sorted(path for path in VIDEO_DIR.glob("*") if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS)
    if not videos:
        raise RuntimeError(
            f"No background videos found in {VIDEO_DIR}. Add at least one .mp4, .mov, .m4v, or .webm file to assets/videos/."
        )
    selected = random.choice(videos)
    try:
        if video_duration(selected) <= 0:
            raise RuntimeError("duration is zero")
    except Exception as error:
        raise RuntimeError(f"Cannot read background video {selected.name}: {error}") from error
    print(f"Using background video: {selected.name}")
    return selected


def build_video(post: dict, output_path: Path) -> None:
    """Create a black editorial Reel with impact shakes, narration, karaoke, and local music."""
    # Keep the visible heading, spoken opening, and number of red-flag slides aligned.
    # Each post heading begins with its approved number (4 through 10).
    flag_count = int(str(post["heading"]).split()[0])
    render_post = dict(post)
    render_post["flag_count"] = flag_count
    render_post["ending_awareness"] = post["benefits"][-1]
    render_post["benefits"] = make_red_flag_points(post, flag_count)
    slides = [heading_narration(render_post)] + render_post["benefits"] + [ending_narration(render_post)]
    pngs, wavs, slide_times = [], [], []
    for i, slide in enumerate(slides):
        png = OUTPUT_DIR / f"text_overlay_{i}.png"
        wav = OUTPUT_DIR / f"narration_{i}.wav"
        render_slide(render_post, i, png)
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

    # Creator-supplied footage fills the frame. Crop vertically and darken it so the moving
    # character remains visible without competing with the red-and-white poster copy.
    background_video = pick_background_video()
    filters = [
        f"[0:v]scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,crop={TARGET_W}:{TARGET_H},eq=brightness=-0.24:saturation=0.58,format=rgba[base]"
    ]
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
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(background_video),
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