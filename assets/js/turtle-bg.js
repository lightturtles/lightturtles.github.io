(function () {
  'use strict';

  var cvs = document.getElementById('turtle-canvas');
  if (!cvs || !cvs.getContext) return;
  var ctx = cvs.getContext('2d');

  var BG_RGB  = '248,247,243'; // matches --bg: #f8f7f3
  var INK     = '#046307';     // matches --primary (dark green)
  var FWD_SPD = 120;           // px / second
  var ROT_SPD = 180;           // degrees / second
  var SPRITE_SZ = 52;          // display size of turtle sprite (px)

  // ── Turtle head — a DOM <img> element so it never smears ───────
  // The canvas handles only the fading trail; the sprite moves via
  // CSS transform and is always sharp at the current position.
  var spriteSrc = cvs.dataset.sprite || '/assets/images/turtle_sprite.png';
  var turtleEl  = document.createElement('img');
  turtleEl.src  = spriteSrc;
  turtleEl.style.cssText =
    'position:absolute;' +
    'width:'  + SPRITE_SZ + 'px;' +
    'height:' + SPRITE_SZ + 'px;' +
    'pointer-events:none;' +
    'z-index:1;' +
    'visibility:hidden;' +
    'will-change:transform;';
  cvs.parentElement.appendChild(turtleEl);

  // Each shape is an array of {f: px} (forward) or {r: deg} (right turn, negative = left).
  var programs = [
    // 5-pointed star
    [].concat.apply([], Array.apply(null, Array(5)).map(function () {
      return [{ f: 90 }, { r: 144 }];
    })),

    // PCB-style orthogonal traces
    [
      { f: 70  }, { r:  90 }, { f: 90  }, { r: -90 },
      { f: 50  }, { r:  90 }, { f: 110 }, { r:  90 },
      { f: 70  }, { r: -90 }, { f: 90  }, { r:  90 },
      { f: 50  }, { r:  90 }, { f: 60  },
    ],

    // Outward spiral (91° per step so the whole thing slowly rotates)
    [].concat.apply([], Array.apply(null, Array(22)).map(function (_, i) {
      return [{ f: 12 + i * 5 }, { r: 91 }];
    })),

    // Hexagonal walk
    [].concat.apply([], Array.apply(null, Array(18)).map(function (_, i) {
      return [{ f: 15 + i * 5 }, { r: 60 }];
    })),
  ];

  var W = 0, H = 0;

  function resize() {
    var rect = cvs.getBoundingClientRect();
    W = cvs.width  = Math.round(rect.width)  || cvs.parentElement.offsetWidth;
    H = cvs.height = Math.round(rect.height) || cvs.parentElement.offsetHeight;
    ctx.fillStyle = 'rgb(' + BG_RGB + ')';
    ctx.fillRect(0, 0, W, H);
  }

  window.addEventListener('resize', resize);
  resize();

  // ── Turtle state ────────────────────────────────────────────────
  var tx, ty, ta;
  var prevX, prevY;
  var progIdx  = programs.length - 1;
  var cmdIdx   = 0;
  var cmdDist  = 0;

  var state    = 'pausing';
  var pauseEnd = 0;

  function startNextShape() {
    progIdx = (progIdx + 1) % programs.length;
    tx = W * 0.08 + Math.random() * W * 0.84;
    ty = H * 0.12 + Math.random() * H * 0.76;
    ta = Math.random() * 360;
    prevX = tx; prevY = ty;
    cmdIdx  = 0;
    cmdDist = 0;
    state   = 'drawing';
    moveTurtleEl(); // position before revealing to prevent flash at old location
    turtleEl.style.visibility = 'visible';
  }

  function moveTurtleEl() {
    var half = SPRITE_SZ / 2;
    turtleEl.style.left      = (tx - half) + 'px';
    turtleEl.style.top       = (ty - half) + 'px';
    turtleEl.style.transform = 'rotate(' + ta + 'deg)';
  }

  // ── Animation loop ──────────────────────────────────────────────
  var lastT = null;

  function frame(now) {
    requestAnimationFrame(frame);

    var dt = lastT ? Math.min((now - lastT) / 1000, 0.05) : 0;
    lastT = now;

    if (state === 'pausing') {
      ctx.fillStyle = 'rgba(' + BG_RGB + ',0.018)';
      ctx.fillRect(0, 0, W, H);
      if (now >= pauseEnd) startNextShape();
      return;
    }

    ctx.fillStyle = 'rgba(' + BG_RGB + ',0.006)';
    ctx.fillRect(0, 0, W, H);

    var prog   = programs[progIdx];
    var budget = dt;

    while (budget > 1e-4 && cmdIdx < prog.length) {
      var cmd  = prog[cmdIdx];
      var done = false;

      if ('f' in cmd) {
        var total     = cmd.f;
        var remaining = total - cmdDist;
        var step      = Math.min(budget, remaining / FWD_SPD);
        var moved     = step * FWD_SPD;
        var rad       = ta * Math.PI / 180;
        var nx        = tx + Math.cos(rad) * moved;
        var ny        = ty + Math.sin(rad) * moved;

        ctx.beginPath();
        ctx.moveTo(prevX, prevY);
        ctx.lineTo(nx, ny);
        ctx.strokeStyle = INK;
        ctx.lineWidth   = 1;
        ctx.lineCap     = 'round';
        ctx.stroke();

        tx = prevX = nx;
        ty = prevY = ny;
        cmdDist += moved;
        budget  -= step;
        done     = cmdDist >= total - 1e-3;

      } else {
        var totalDeg = Math.abs(cmd.r);
        var dir      = cmd.r > 0 ? 1 : -1;
        var remDeg   = totalDeg - cmdDist;
        var stepDeg  = Math.min(budget, remDeg / ROT_SPD);

        ta      += dir * stepDeg * ROT_SPD;
        cmdDist += stepDeg * ROT_SPD;
        budget  -= stepDeg;
        done     = cmdDist >= totalDeg - 1e-3;
      }

      if (done) { cmdIdx++; cmdDist = 0; }
    }

    moveTurtleEl();

    if (cmdIdx >= prog.length) {
      state    = 'pausing';
      pauseEnd = now + 2500;
      turtleEl.style.visibility = 'hidden';
    }
  }

  ctx.fillStyle = 'rgb(' + BG_RGB + ')';
  ctx.fillRect(0, 0, W, H);

  state    = 'pausing';
  pauseEnd = performance.now() + 1000;
  requestAnimationFrame(frame);
})();
