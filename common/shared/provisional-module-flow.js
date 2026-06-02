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
    if (id === 'quiz') {
      el.classList.add('quiz-visible');
    }
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
    if (state.video) {
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
  var SEEK_TOLERANCE = 0.35;
  var maxWatchedTime = 0;
  var suppressSeekGuard = false;

  function formatWatchProgress() {
    if (!video || !video.duration || !isFinite(video.duration)) {
      return 'Play the video from the start. You cannot skip ahead using the timeline.';
    }
    var pct = Math.min(100, Math.round((maxWatchedTime / video.duration) * 100));
    return (
      'Watched ' +
      pct +
      '%. You must watch the full video before the quiz — the timeline cannot be used to skip ahead.'
    );
  }

  function persistMaxWatched(state) {
    if (maxWatchedTime > (state.maxWatchedTime || 0)) {
      state.maxWatchedTime = maxWatchedTime;
      saveState(state);
    }
  }

  function clampForwardSeek() {
    if (!video || suppressSeekGuard) return;
    var state = loadState();
    if (state.video) return;

    var cap = Math.max(0, maxWatchedTime);
    if (video.currentTime > cap + SEEK_TOLERANCE) {
      suppressSeekGuard = true;
      video.currentTime = cap;
      suppressSeekGuard = false;
      if (statusEl && !state.video) {
        statusEl.textContent = formatWatchProgress();
        statusEl.classList.remove('is-done');
      }
    }
  }

  function markVideoComplete() {
    var state = loadState();
    if (state.video) return;
    state.video = true;
    if (video && video.duration && isFinite(video.duration)) {
      state.maxWatchedTime = video.duration;
      maxWatchedTime = video.duration;
    }
    saveState(state);
    if (statusEl) {
      statusEl.textContent = 'Video completed. You can now open Ready for the Quiz.';
      statusEl.classList.add('is-done');
    }
    applyUnlocks(state);
    refreshProgress();
  }

  if (video) {
    var initialState = loadState();
    maxWatchedTime = Number(initialState.maxWatchedTime) || 0;
    if (initialState.video) {
      maxWatchedTime = Math.max(maxWatchedTime, video.duration || 0);
    } else if (statusEl) {
      statusEl.textContent = formatWatchProgress();
    }

    video.addEventListener('loadedmetadata', function () {
      var state = loadState();
      if (state.video) return;
      maxWatchedTime = Math.min(Number(state.maxWatchedTime) || 0, video.duration || 0);
      if (maxWatchedTime > 0) {
        suppressSeekGuard = true;
        video.currentTime = maxWatchedTime;
        suppressSeekGuard = false;
      }
      if (statusEl && !state.video) statusEl.textContent = formatWatchProgress();
    });

    video.addEventListener('timeupdate', function () {
      var state = loadState();
      if (state.video) return;
      var t = video.currentTime;
      if (t > maxWatchedTime + SEEK_TOLERANCE) {
        clampForwardSeek();
        return;
      }
      if (t > maxWatchedTime) {
        maxWatchedTime = t;
        persistMaxWatched(state);
      }
      if (statusEl && !state.video) statusEl.textContent = formatWatchProgress();
    });

    video.addEventListener('seeking', clampForwardSeek);
    video.addEventListener('seeked', clampForwardSeek);

    video.addEventListener('ended', function () {
      var state = loadState();
      if (state.video) return;
      if (video.duration && maxWatchedTime < video.duration - SEEK_TOLERANCE) {
        clampForwardSeek();
        if (statusEl) {
          statusEl.textContent =
            'Please watch the full video without skipping. The quiz unlocks when the video finishes.';
        }
        return;
      }
      markVideoComplete();
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
      unlockStage('complete');
      location.hash = 'quiz';
      var quiz = section('quiz');
      if (quiz) quiz.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  if (location.hash === '#quiz') {
    var st = loadState();
    if (st.video) {
      unlockStage('complete');
      unlockStage('quiz');
    }
  }

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
