#!/usr/bin/env python3
"""Build provisional induction: journey + video + completion + quiz per module."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from quiz_html import quiz_section_html

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((Path(__file__).parent / "modules_config.json").read_text(encoding="utf-8"))
MODULES = CONFIG["modules"]
OUT_DASH = ROOT / "general-induction" / "dashboard" / "index.html"
OUT_MOD = ROOT / "general-induction" / "modules"


def journey_items(current: int) -> str:
    rows = []
    for m in MODULES:
        n = m["number"]
        if n < current:
            cls, status = "journey-item--past", ""
        elif n == current:
            cls, status = "active", "Current module"
        else:
            cls, status = "", ""
        rows.append(
            f"""              <a class="journey-item {cls}" href="/general-induction/modules/module-{n}/">
                <div class="journey-node">
                  <span class="journey-node__kicker">Module</span>
                  <div class="journey-circle"><span class="journey-node__num">{n}</span></div>
                </div>
                <div class="journey-title">{m['title']}</div>
                <div class="journey-status">{status}</div>
              </a>"""
        )
    return "\n".join(rows)


def module_card(m: dict) -> str:
    n = m["number"]
    points = "\n".join(f"            <li>{p}</li>" for p in m["points"])
    return f"""      <article class="module-card" data-module-number="{n}">
        <div class="module-top">
          <span class="module-number">Module {n}</span>
          <h3>{m['title']}</h3>
          <p class="module-subtitle">{m['subtitle']}</p>
          <span class="module-status-badge status-not-started" id="moduleStatus{n}">Not started</span>
        </div>
        <div class="module-body">
          <p class="module-intro">{m['intro']}</p>
          <ul class="module-points">
{points}
          </ul>
          <div class="module-footer">
            <a href="/general-induction/modules/module-{n}/" class="btn btn-primary module-btn" data-module-number="{n}">Start Module</a>
          </div>
        </div>
      </article>"""


def render_dashboard() -> str:
    cards = "\n".join(module_card(m) for m in MODULES)
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>General Induction (Provisional) | clubSENsational</title>
<meta name="description" content="Provisional General Induction: six modules with video and quiz." />
<link rel="stylesheet" href="/assets/pathway-hub.css" />
<link rel="stylesheet" href="/assets/training-content-containment.css" />
<link rel="stylesheet" href="/assets/portal-induction-atmosphere.css" />
<link rel="stylesheet" href="/assets/induction-pathway-hub.css" />
<link rel="stylesheet" href="/assets/provisional-certificate.css" />
</head>
<body>
<section class="training-page" id="mainContent">
  <div class="training-wrap">
    <section class="hero hero--pathway-hub hero--induction" aria-labelledby="pathwayHubTitle">
      <div class="pathway-hero__waves" aria-hidden="true"></div>
      <div class="hero-inner hero-inner--pathway-hub">
        <div class="hero-copy">
          <p class="brand-chip">clubSENsational Staff Learning</p>
          <h1 id="pathwayHubTitle">General Induction</h1>
          <p class="hero-subtitle">Foundation training for all staff. Watch each module video, then complete the quiz. Work through all six modules in order.</p>
        </div>
        <div class="hero-logo-wrap">
          <img class="hero-logo" src="/assets/clubsensational-portal-logo.png" alt="clubSENsational logo">
        </div>
      </div>
    </section>
    <div class="modules-grid" id="pathway-modules">
{cards}
    </div>
    <section class="induction-certificate-panel" id="inductionCertificatePanel" hidden aria-labelledby="inductionCertTitle">
      <div class="induction-certificate-panel__inner">
        <div class="induction-certificate-panel__copy">
          <p class="induction-certificate-panel__kicker">Training complete</p>
          <h2 id="inductionCertTitle">Congratulations - you finished General Induction</h2>
          <p>Download your certificate with the clubSENsational logo. Keep it for your staff learning record.</p>
          <p class="induction-certificate-panel__learner" id="inductionCertificateLearnerName"></p>
          <div class="induction-certificate-panel__actions">
            <button type="button" class="btn-certificate-download" id="downloadInductionCertificate">Download certificate</button>
          </div>
        </div>
        <div class="induction-certificate-panel__logo">
          <img src="/assets/clubsensational-portal-logo.png" alt="clubSENsational" width="200" height="80" />
        </div>
      </div>
    </section>
  </div>
</section>
<script src="/shared/provisional-certificate.js"></script>
<script src="/shared/provisional-pathway.js"></script>
</body>
</html>
"""


def provisional_descriptor(mod: dict) -> str:
    return (
        "Review your place on the induction pathway, watch the module video, "
        "then pass the quiz to continue."
    )


def outcomes_section_html(mod: dict) -> str:
    items = "\n".join(
        f"""            <div class="outcome clickable-progress" data-outcome-item="{i}">
              <span class="outcome-index" aria-hidden="true"></span>
              <div>{text}</div>
            </div>"""
        for i, text in enumerate(mod["outcomes"], 1)
    )
    return f"""      <section class="section gated-locked" id="outcomes" data-stage="outcomes" data-unlock-after="journey">
        <div class="section-top"><span class="section-pill">Learning Outcomes</span></div>
        <div class="section-body">
          <div class="section-lock-banner">Complete the Induction Journey section to unlock Learning Outcomes.</div>
          <div class="section-title-row">
            <h3>What will you understand by the end of this module?</h3>
          </div>
          <div class="outcomes" data-outcomes-group="outcomes">
{items}
          </div>
          <div class="stage-helper" id="outcomesHelper">Review each learning outcome to unlock the confirmation below.</div>
          <label class="check-item clickable-progress">
            <input type="checkbox" class="overall-check" data-stage-check="outcomes" id="outcomesCheck" disabled>
            <span>I have reviewed the learning outcomes and I am clear on what this module will help me understand.</span>
          </label>
        </div>
      </section>

"""


def hero_atmosphere() -> str:
    return """          <div class="module-hero__glow"></div>
          <div class="module-hero__signature" aria-hidden="true"></div>
          <div class="module-hero__wave module-hero__wave--1"></div>
          <div class="module-hero__wave module-hero__wave--2"></div>
          <div class="module-hero__wave module-hero__wave--3"></div>
          <span class="module-hero__orb module-hero__orb--1" aria-hidden="true"></span>
          <span class="module-hero__orb module-hero__orb--2" aria-hidden="true"></span>
          <span class="module-hero__orb module-hero__orb--3" aria-hidden="true"></span>
          <span class="module-hero__orb module-hero__orb--4" aria-hidden="true"></span>"""


def render_module(mod: dict) -> str:
    n = mod["number"]
    stages = 5
    next_href = f"/general-induction/modules/module-{n + 1}/" if n < len(MODULES) else "/general-induction/"
    next_lbl = f"Module {n + 1}" if n < len(MODULES) else "pathway"
    descriptor = mod.get("subtitle") or provisional_descriptor(mod)

    nav = """
        <a class="nav-link active" href="#overview">Overview</a>
        <a class="nav-link" href="#journey">Induction Journey</a>
        <a class="nav-link" href="#outcomes">Learning Outcomes</a>
        <a class="nav-link" href="#video">Module Video</a>
        <a class="nav-link" href="#complete">Completion</a>
        <a class="nav-link" href="#quiz">Quiz</a>"""

    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Module {n} - {mod['title']} | General Induction</title>
  <meta name="description" content="{mod['subtitle']}" />
  <link rel="stylesheet" href="/assets/training-content-containment.css" />
  <link rel="stylesheet" href="/assets/induction-module-template.css" />
  <link rel="stylesheet" href="/assets/module-roadmap.css" />
  <link rel="stylesheet" href="/assets/induction-journey-connectors.css" />
  <link rel="stylesheet" href="/assets/journey-editorial-hierarchy.css" />
  <link rel="stylesheet" href="/assets/induction-journey-editorial-overrides.css" />
  <link rel="stylesheet" href="/assets/journey-node-layout.css" />
  <link rel="stylesheet" href="/assets/induction-journey-nodes.css" />
  <link rel="stylesheet" href="/assets/induction-recap-completion-theme.css" />
  <link rel="stylesheet" href="/assets/induction-quiz-theme.css" />
  <link rel="stylesheet" href="/assets/provisional-video.css" />
  <link rel="stylesheet" href="/assets/provisional-ui-overrides.css" />
  <link rel="stylesheet" href="/assets/induction-portal-theme.css" />
  <link rel="stylesheet" href="/assets/provisional-certificate.css" />
</head>
<body class="training-template-body">
<div class="portal" data-induction-module="{n}" data-provisional-induction="1">
  <aside class="sidebar">
    <div class="brand-card">
      <a href="/general-induction/" class="sidebar-logo-link">
        <img src="/assets/clubsensational-portal-logo.png" alt="clubSENsational" class="sidebar-logo-img" />
      </a>
    </div>
    <a href="/general-induction/" class="btn-back-pathway">&larr; Back to General Induction</a>
    <div class="sidebar-card">
      <h3>Module Navigation</h3>
      <div class="nav-list" id="moduleNav">{nav}
      </div>
    </div>
    <div class="sidebar-card">
      <h3>Overall Progress</h3>
      <div class="progress-track"><div class="progress-fill" id="overallProgressFill"></div></div>
      <div class="progress-meta">
        <span id="overallProgressText">0% completed</span>
        <span id="overallProgressCount">0 / {stages}</span>
      </div>
      <p class="small-note">Complete the journey, review learning outcomes, watch the video, then pass the quiz.</p>
    </div>
  </aside>

  <main class="main">
    <div class="content">
      <section class="hero section hero--module-system" id="overview" data-stage="overview">
        <div class="module-hero__atmosphere" aria-hidden="true">
{hero_atmosphere()}
        </div>
        <div class="section-top section-top--hero">
          <div class="hero-title-line">
            <div class="hero-title-line__stack">
              <p class="module-hero__kicker">General Induction &middot; Module {n}</p>
              <h2>{mod['title']}</h2>
              <p class="module-hero__descriptor">{descriptor}</p>
              <p class="module-hero__path"><span>Journey</span><span class="module-hero__path-sep" aria-hidden="true">&middot;</span><span>Outcomes</span><span class="module-hero__path-sep" aria-hidden="true">&middot;</span><span>Video</span><span class="module-hero__path-sep" aria-hidden="true">&middot;</span><span>Quiz</span></p>
            </div>
            <div class="hero-title-line__rail"><div class="hero-heading-row"><div class="hero-module-num">MODULE {n}</div></div></div>
          </div>
        </div>
        <div class="hero-actions"><button type="button" class="btn btn-primary" data-scroll="#journey">Start Module</button></div>
      </section>

      <div class="module-progress-bar">
        <div class="module-progress-top"><strong>Module Progress</strong><span id="moduleProgressText">0% completed &bull; Start the module</span></div>
        <div class="module-progress-track"><div class="module-progress-fill" id="moduleProgressFill"></div></div>
      </div>

      <section class="section" id="journey" data-stage="journey">
        <div class="section-top"><span class="section-pill">General Induction Journey</span></div>
        <div class="section-body">
          <div class="section-title-row"><h3>clubSENsational General Induction Journey</h3></div>
          <div class="journey-wrap">
            <div class="journey-track">
{journey_items(n)}
            </div>
            <div class="journey-panel" id="journeyPanel">
              <h4>Module {n} &mdash; {mod['title']}</h4>
              <p>{mod['subtitle']}</p>
            </div>
          </div>
          <label class="check-item clickable-progress">
            <input type="checkbox" class="overall-check" data-stage-check="journey">
            <span>I understand where this module sits within the General Induction pathway.</span>
          </label>
        </div>
      </section>

{outcomes_section_html(mod)}
      <section class="section gated-locked" id="video" data-stage="video" data-unlock-after="outcomes">
        <div class="section-top"><span class="section-pill">Module Video</span></div>
        <div class="section-body">
          <div class="section-lock-banner">Complete the Learning Outcomes section to unlock the module video.</div>
          <div class="section-title-row"><h3>Watch the module video</h3></div>
          <p class="lead">Watch the full video from start to finish before the quiz. You cannot skip ahead using the video timeline.</p>
          <div class="module-video-shell">
            <video class="module-video" id="moduleVideo" controls playsinline preload="metadata" controlsList="nodownload" data-video-no-seek="1" src="/assets/videos/module-{n}.mp4"></video>
            <p class="module-video-status" id="moduleVideoStatus">Video not completed yet.</p>
          </div>
          <label class="check-item clickable-progress video-complete-check" id="videoCompleteWrap" hidden>
            <input type="checkbox" class="overall-check" data-stage-check="video" id="videoCompleteCheck" disabled>
            <span>I have watched the module video.</span>
          </label>
        </div>
      </section>

      <section class="section gated-locked" id="complete" data-stage="complete" data-unlock-after="video">
        <div class="section-top"><span class="section-pill">Completion</span></div>
        <div class="section-body">
          <div class="section-lock-banner">Watch the module video to unlock Ready for the Quiz.</div>
          <div class="completion-box">
            <div class="completion-atmosphere" aria-hidden="true"></div>
            <div class="completion-inner">
              <div class="completion-pathway" role="presentation" aria-hidden="true">
                <span>Journey</span><span class="completion-pathway__sep">&middot;</span><span>Outcomes</span><span class="completion-pathway__sep">&middot;</span><span>Video</span><span class="completion-pathway__sep">&middot;</span><span class="completion-pathway__quiz">Quiz</span>
              </div>
              <h3 class="completion-title">Ready for the Quiz</h3>
              <div class="completion-body">
                <p class="completion-lead">You have watched the module video.</p>
                <p class="completion-sub">Open the quiz to consolidate your learning. Answer all 8 questions and submit when every question is complete.</p>
              </div>
              <div class="completion-actions">
                <a class="btn btn-primary" href="#quiz" id="startQuizBtn">Start Quiz</a>
              </div>
            </div>
          </div>
        </div>
      </section>

{quiz_section_html(n, mod, next_href, next_lbl)}
    </div>
  </main>
</div>
<script src="/shared/provisional-module-flow.js"></script>
<script src="/shared/provisional-certificate.js"></script>
<script src="/shared/provisional-quiz-flow.js"></script>
</body>
</html>
"""


def main() -> None:
    # Quiz pairs are defined exactly in induction_quizzes.json (no auto-patch).
    OUT_DASH.parent.mkdir(parents=True, exist_ok=True)
    OUT_DASH.write_text(render_dashboard(), encoding="utf-8")
    for mod in MODULES:
        dest = OUT_MOD / f"module-{mod['number']}" / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render_module(mod), encoding="utf-8")
        print("built", dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
