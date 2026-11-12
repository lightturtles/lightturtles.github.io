// Step a two-transistor astable multivibrator forward in time, using an
// ideal-switch transistor model. Inputs in SI units; returns time (s), switch
// states (1 = ON) and node voltages (V) at every step.
function simulate(R_A, R_B, C, V, dt, t_end, V_BE_on = 0.6, V_CE_sat = 0.2) {
  const n = Math.round(t_end / dt) + 1;
  const f64 = () => new Float64Array(n);
  const t = f64(), vc1 = f64(), vc2 = f64();
  const vce1 = f64(), vce2 = f64(), vbe1 = f64(), vbe2 = f64();
  const q1 = new Uint8Array(n), q2 = new Uint8Array(n);

  // Initial conditions: Q1 starts ON, both caps uncharged.
  let Q1 = true, Q2 = false;
  let ic1 = 0, ic2 = 0;

  for (let k = 0; k < n; k++) {
    if (k > 0) {
      const p = k - 1;
      // 1. Switch states from the previous step only.
      const nextQ1 = Q1 ? !(!Q2 && vbe2[p] >= V_BE_on) : vbe1[p] >= V_BE_on;
      const nextQ2 = Q2 ? !(!Q1 && vbe1[p] >= V_BE_on) : vbe2[p] >= V_BE_on;
      Q1 = nextQ1;
      Q2 = nextQ2;
      // 2. Capacitor voltages can't jump; integrate last step's current.
      vc1[k] = vc1[p] + ic1 * dt / C;
      vc2[k] = vc2[p] + ic2 * dt / C;
    }

    // 3. Node voltages from cap voltages + switch states.
    t[k] = k * dt;
    q1[k] = Q1;
    q2[k] = Q2;
    vce1[k] = Q1 ? V_CE_sat : V_BE_on - vc1[k];
    vce2[k] = Q2 ? V_CE_sat : V_BE_on - vc2[k];
    vbe1[k] = Q1 ? V_BE_on : vce2[k] + vc2[k];
    vbe2[k] = Q2 ? V_BE_on : vce1[k] + vc1[k];

    // 4. Current into the base side of each cap.
    ic1 = !Q2 ? (V - vbe2[k]) / R_B : -(V - vce1[k]) / R_A;
    ic2 = !Q1 ? (V - vbe1[k]) / R_B : -(V - vce2[k]) / R_A;
  }
  return { t, q1, q2, vc1, vc2, vce1, vbe1, vce2, vbe2 };
}

// Lets the downloaded file be used from Node too: require("./simulate.js").simulate
if (typeof module !== "undefined") module.exports = { simulate };
