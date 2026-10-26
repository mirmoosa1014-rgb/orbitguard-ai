# Explanation

An orbit is an object constantly falling toward Earth while traveling sideways fast enough to keep missing it. Straight lines are cheap guesses, but gravity bends the path. OrbitGuard tests how those guesses differ from a numerical gravity model.

Virtual sensors add noise. A Kalman filter blends model predictions and measurements. Covariance describes estimated uncertainty, which must be checked against held-out truth. A learned ranker tries to choose which possible encounters deserve more computation. Here it performs slightly worse than sorting by coarse distance.

A maneuver changes velocity a little. The simulator compares how much velocity change is spent against the smallest modeled distance. Looking better in a small artificial world never establishes real safety.

## Ten reviewer questions

1. What are the units? Meters, seconds, meters/second internally; UI distances often kilometers.
2. What physics is missing? J2, drag, other bodies and operational ephemerides.
3. What is observed? Ideal noisy Cartesian position, not real radar measurements.
4. Can future data leak into the filter? No; prefix tests verify causal updates.
5. Are baseline observations identical? Yes; CV acceleration noise is separately tuned on validation.
6. How are holdouts split? Entire radius/inclination families and episode seeds.
7. Did ML win? No; inspect the measured recall in results/metrics.json.
8. What does shading mean? A primary-position covariance scale, not collision probability.
9. Why is the encounter deliberate? It creates a testable future encounter from a physically propagated present state.
10. What remains unvalidated? Operational use, real sensors/catalogs, robust uncertainty-constrained maneuvering and remote CI.
