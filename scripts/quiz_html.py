"""Generate inline quiz HTML for provisional induction modules."""

from __future__ import annotations

import json
import re
from pathlib import Path

QUIZZES = json.loads((Path(__file__).parent / "induction_quizzes.json").read_text(encoding="utf-8"))


def match_slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def type_label(qtype: str) -> str:
    return {
        "single": "Single choice",
        "multiple": "Multiple choice",
        "tf": "True or false",
        "match": "Match the following",
    }[qtype]


def question_card(n: int, q: dict, module_num: int) -> str:
    suffix = f"_m{module_num}"
    qtype = q["type"]
    text = f"{n}. {q['text']}"
    feedback_id = f"f{n}M{module_num}"

    if qtype == "single":
        opts = "\n".join(
            f'                    <li><label for="q{n}{opt["letter"].lower()}{suffix}"><span class="opt-txt">{opt["letter"]}. {opt["text"]}</span><input type="radio" name="q{n}{suffix}" id="q{n}{opt["letter"].lower()}{suffix}" value="{opt["letter"]}"></label></li>'
            for opt in q["options"]
        )
        body = f"                  <ul class=\"opt-list\">\n{opts}\n                  </ul>"

    elif qtype == "multiple":
        opts = "\n".join(
            f'                    <li><label for="q{n}{opt["letter"].lower()}{suffix}"><span class="opt-txt">{opt["letter"]}. {opt["text"]}</span><input type="checkbox" name="q{n}{suffix}" id="q{n}{opt["letter"].lower()}{suffix}" value="{opt["letter"]}"></label></li>'
            for opt in q["options"]
        )
        body = f"                  <ul class=\"opt-list\">\n{opts}\n                  </ul>"

    elif qtype == "tf":
        body = f"""                  <ul class="opt-list">
                    <li><label for="q{n}t{suffix}"><span class="opt-txt">True</span><input type="radio" name="q{n}{suffix}" id="q{n}t{suffix}" value="T"></label></li>
                    <li><label for="q{n}f{suffix}"><span class="opt-txt">False</span><input type="radio" name="q{n}{suffix}" id="q{n}f{suffix}" value="F"></label></li>
                  </ul>"""

    else:
        slots, chips = [], []
        for pair in q["pairs"]:
            slug = match_slug(pair["answer"])
            slots.append(
                f'                      <div class="match-slot" data-correct="{slug}"><span class="slot-label">{pair["label"]}</span><div class="slot-drop"></div></div>'
            )
            chips.append(
                f'                      <div class="match-chip" data-value="{slug}" draggable="true">{pair["answer"]}</div>'
            )
        body = f"""                  <p class="q-text q-text--match-hint">Drag each term to the matching label (or tap to select, then tap a slot).</p>
                  <div class="match-game">
                    <div class="match-column match-slots">
{chr(10).join(slots)}
                    </div>
                    <div class="match-column match-pool" id="pool8M{module_num}">
{chr(10).join(chips)}
                    </div>
                  </div>"""

    return f"""                <div class="q-card" data-q="{n}">
                  <h3>{type_label(qtype)}</h3>
                  <p class="q-text">{text}</p>
{body}
                  <div class="feedback" id="{feedback_id}"></div>
                </div>"""


def quiz_config_script(module_num: int, quiz: dict) -> str:
    correct: dict = {}
    match_feedback = ""
    for i, q in enumerate(quiz["questions"], 1):
        key = f"q{i}"
        if q["type"] in ("single", "tf"):
            correct[key] = q["correct"]
        elif q["type"] == "multiple":
            correct[key] = sorted(q["correct"])
        elif q["type"] == "match":
            match_feedback = "; ".join(f"{p['label']} -> {p['answer']}" for p in q["pairs"]) + "."

    payload = {"moduleNumber": module_num, "correct": correct, "matchFeedback": match_feedback}
    return f"<script>window.inductionQuizConfig = {json.dumps(payload)};</script>"


def quiz_section_html(module_num: int, mod: dict, next_href: str, next_lbl: str) -> str:
    quiz = QUIZZES[str(module_num)]
    is_final = module_num >= 6
    next_btn = "Return to General Induction" if is_final else f"Continue to {next_lbl}"
    next_link = "/general-induction/" if is_final else next_href
    cards = "\n".join(question_card(i, q, module_num) for i, q in enumerate(quiz["questions"], 1))
    return f"""      <section class="section gated-locked" id="quiz" data-stage="quiz" data-unlock-after="complete">
        <div class="section-top"><span class="section-pill">Module quiz</span></div>
        <div class="section-body">
          <div class="section-lock-banner">Watch the module video and open Ready for the Quiz before starting the quiz.</div>
          <p class="lead">Answer all 8 questions, then submit. You need every answer correct to pass and continue.</p>
          <div class="quiz-embed">
            <div class="quiz-inline" id="quizInlineM{module_num}">
              <div class="quiz-inline-progress">
                <div class="progress-track"><div class="progress-fill" id="progressFillM{module_num}"></div></div>
                <p class="progress-meta" id="progressTextM{module_num}">0 of 8 answered</p>
              </div>
              <header class="quiz-hero">
                <span class="tag">Module {module_num}</span>
                <h1>{mod['title']}</h1>
                <p>{quiz['hero_subtitle']}</p>
              </header>
              <form id="quizFormM{module_num}">
{cards}
                <p class="quiz-submit-hint" id="quizSubmitHintM{module_num}">Answer all 8 questions to enable Submit.</p>
                <button type="submit" class="btn-submit" id="submitBtnM{module_num}" disabled>Submit answers</button>
              </form>
              <div class="score-card" id="scoreCardM{module_num}">
                <h2>Quiz results</h2>
                <p class="score-value" id="scoreValueM{module_num}">0/8</p>
                <p class="score-msg" id="scoreMsgM{module_num}"></p>
                <a href="{next_link}" class="back-link quiz-next-btn" style="display:none">{next_btn}</a>
              </div>
            </div>
          </div>
        </div>
      </section>
{quiz_config_script(module_num, quiz)}"""
