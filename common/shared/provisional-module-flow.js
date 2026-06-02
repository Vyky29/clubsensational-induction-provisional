(function () {
  var portal = document.querySelector('.portal[data-provisional-induction]');
  if (!portal) return;

  var moduleNum = portal.getAttribute('data-induction-module');
  var storageKey = 'provisional-induction-module-' + moduleNum;
  var stageOrder = ['journey', 'video', 'complete', 'quiz'];
  var totalStages = stageOrder.length;

  function loadState() {
    try {
      return JSON.parse(localStorage.getItem(storageKey) || '{}');
    } catch (e) {
      return {};
    }
  }

  function saveState(state) {
    try {
      localStorage.setItem(storageKey, JSON.stringify(state));
    } catch (e) {}
    if (typeof window.provisionalRefreshPathway === 'function') {
      window.provisionalRefreshPathway();
    }
  }

  function section(id) {
    return document.getElementById(id);
  }

  function unlockStage(id) {
    var el = section(id);
    if (!el) return;
    el.classList.remove('gated-locked');
    el.classList.add('is-unlocked');
    var banner = el.querySelector('.section-lock-banner');
    if (banner) banner.style.display = 'none';
  }

  function isStageDone(id, state) {
    if (id === 'video') return !!state.video;
    if (id === 'quiz') return !!state.quizPass;
    var check = document.querySelector('[data-stage-check="' + id + '"]');
    return check && check.checked;
  }

  function refreshProgress() {
    var state = loadState();
    var done = 0;
    stageOrder.forEach(function (id) {
      if (isStageDone(id, state)) done++;
    });
    var pct = Math.round((done / totalStages) * 100);
    var fill = document.getElementById('overallProgressFill');
    var text = document.getElementById('overallProgressText');
    var count = document.getElementById('overallProgressCount');
    var modFill = document.getElementById('moduleProgressFill');
    var modText = document.getElementById('moduleProgressText');
    if (fill) fill.style.width = pct + '%';
    if (text) text.textContent = pct + '% completed';
    if (count) count.textContent = done + ' / ' + totalStages;
    if (modFill) modFill.style.width = pct + '%';
    if (modText) modText.textContent = pct + '% completed';
    return state;
  }

  function applyUnlocks(state) {
    var journeyDone = isStageDone('journey', state);
    if (journeyDone) unlockStage('video');
    if (state.video) {
      unlockStage('complete');
      var wrap = document.getElementById('videoCompleteWrap');
      if (wrap) wrap.hidden = false;
      var vCheck = document.getElementById('videoCompleteCheck');
      if (vCheck) {
        vCheck.disabled = false;
        vCheck.checked = true;
      }
    }
    if (state.video || isStageDone('complete', state)) {
      unlockStage('quiz');
    }
    if (state.quizPass) unlockStage('quiz');
  }

  document.querySelectorAll('[data-stage-check="journey"]').forEach(function (input) {
    input.addEventListener('change', function () {
      var state = loadState();
      applyUnlocks(state);
      refreshProgress();
    });
  });

  var video = document.getElementById('moduleVideo');
  var statusEl = document.getElementById('moduleVideoStatus');

  function markVideoComplete() {
    var state = loadState();
    if (state.video) return;
    state.video = true;
    saveState(state);
    if (statusEl) {
      statusEl.textContent = 'Video completed. You can now open Ready for the Quiz.';
      statusEl.classList.add('is-done');
    }
    applyUnlocks(state);
    refreshProgress();
  }

  if (video) {
    video.addEventListener('ended', markVideoComplete);
    video.addEventListener('timeupdate', function () {
      if (!video.duration || video.duration < 10) return;
      if (video.currentTime / video.duration >= 0.92) markVideoComplete();
    });
  }

  document.querySelectorAll('a[href="#quiz"], #startQuizBtn').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var state = loadState();
      if (!state.video) {
        e.preventDefault();
        alert('Please watch the module video before starting the quiz.');
        return;
      }
      e.preventDefault();
      unlockStage('quiz');
      location.hash = 'quiz';
      var quiz = section('quiz');
      if (quiz) quiz.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  document.querySelectorAll('[data-scroll]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var sel = btn.getAttribute('data-scroll');
      var target = document.querySelector(sel);
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  window.provisionalInductionMarkQuizPass = function () {
    var state = loadState();
    state.quizPass = true;
    saveState(state);
    applyUnlocks(state);
    refreshProgress();
  };

  window.provisionalInductionGetState = loadState;
  window.inductionRefreshProgress = refreshProgress;

  var state = loadState();
  applyUnlocks(state);
  refreshProgress();
})();
