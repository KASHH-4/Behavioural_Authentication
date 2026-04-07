(function (global) {
  "use strict";

  function nowMs() {
    return Date.now();
  }

  function createTracker(config) {
    var state = {
      apiBaseUrl: config.apiBaseUrl || "http://localhost:5000",
      userId: config.userId || null,
      sessionId: null,
      flushIntervalMs: config.flushIntervalMs || 2000,
      maxBufferSize: config.maxBufferSize || 100,
      eventBuffer: [],
      isRunning: false,
      flushTimer: null,
      lastEventTs: null,
      pendingKeyDownTs: [],
      lastKeyUpTs: null,
      handlers: {}
    };

    function buildEvent(eventType, payload) {
      var ts = nowMs();
      var interEvent = state.lastEventTs === null ? null : (ts - state.lastEventTs) / 1000.0;
      state.lastEventTs = ts;

      return Object.assign(
        {
          event_type: eventType,
          timestamp: ts / 1000.0,
          inter_event_time: interEvent
        },
        payload || {}
      );
    }

    function pushEvent(evt) {
      state.eventBuffer.push(evt);
      if (state.eventBuffer.length >= state.maxBufferSize) {
        flush();
      }
    }

    async function startSession() {
      if (!state.userId) {
        throw new Error("userId is required to start session");
      }

      var response = await fetch(state.apiBaseUrl + "/start-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: state.userId })
      });

      if (!response.ok) {
        throw new Error("Failed to start session");
      }

      var data = await response.json();
      state.sessionId = data.session_id;
      return data;
    }

    async function endSession() {
      if (!state.sessionId) {
        return;
      }

      await flush();

      await fetch(state.apiBaseUrl + "/end-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: state.sessionId })
      });

      state.sessionId = null;
    }

    async function flush() {
      if (!state.sessionId || !state.userId || state.eventBuffer.length === 0) {
        return;
      }

      var batch = state.eventBuffer.splice(0, state.eventBuffer.length);

      try {
        await fetch(state.apiBaseUrl + "/collect", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: state.sessionId,
            user_id: state.userId,
            events: batch
          })
        });
      } catch (err) {
        state.eventBuffer = batch.concat(state.eventBuffer);
      }
    }

    function onMouseMove(e) {
      pushEvent(
        buildEvent("mouse_move", {
          x: e.clientX,
          y: e.clientY
        })
      );
    }

    function onClick(e) {
      pushEvent(
        buildEvent("click", {
          x: e.clientX,
          y: e.clientY
        })
      );
    }

    function onKeyDown() {
      var ts = nowMs();
      var flightTime = state.lastKeyUpTs === null ? null : (ts - state.lastKeyUpTs) / 1000.0;
      state.pendingKeyDownTs.push(ts);

      pushEvent(
        buildEvent("key_down", {
          dwell_time: null,
          flight_time: flightTime
        })
      );
    }

    function onKeyUp() {
      var ts = nowMs();
      state.lastKeyUpTs = ts;

      var downTs = state.pendingKeyDownTs.length > 0 ? state.pendingKeyDownTs.shift() : null;
      var dwellTime = downTs === null ? null : (ts - downTs) / 1000.0;

      pushEvent(
        buildEvent("key_up", {
          dwell_time: dwellTime,
          flight_time: null
        })
      );
    }

    function attachListeners() {
      state.handlers.mousemove = onMouseMove;
      state.handlers.click = onClick;
      state.handlers.keydown = onKeyDown;
      state.handlers.keyup = onKeyUp;

      window.addEventListener("mousemove", state.handlers.mousemove, { passive: true });
      window.addEventListener("click", state.handlers.click, { passive: true });
      window.addEventListener("keydown", state.handlers.keydown, { passive: true });
      window.addEventListener("keyup", state.handlers.keyup, { passive: true });
    }

    function detachListeners() {
      window.removeEventListener("mousemove", state.handlers.mousemove);
      window.removeEventListener("click", state.handlers.click);
      window.removeEventListener("keydown", state.handlers.keydown);
      window.removeEventListener("keyup", state.handlers.keyup);
    }

    async function start() {
      if (state.isRunning) {
        return;
      }

      await startSession();
      attachListeners();

      state.flushTimer = setInterval(function () {
        flush();
      }, state.flushIntervalMs);

      state.isRunning = true;
    }

    async function stop() {
      if (!state.isRunning) {
        return;
      }

      clearInterval(state.flushTimer);
      detachListeners();
      await endSession();

      state.isRunning = false;
    }

    async function getAuthScore() {
      if (!state.sessionId) {
        throw new Error("No active session for score request");
      }

      var response = await fetch(
        state.apiBaseUrl + "/auth-score?session_id=" + encodeURIComponent(state.sessionId),
        {
          method: "GET"
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch auth score");
      }

      return response.json();
    }

    return {
      start: start,
      stop: stop,
      flush: flush,
      getAuthScore: getAuthScore,
      getState: function () {
        return {
          userId: state.userId,
          sessionId: state.sessionId,
          isRunning: state.isRunning,
          bufferedEvents: state.eventBuffer.length
        };
      }
    };
  }

  global.BehaviorAuthTracker = {
    init: createTracker
  };
})(window);
