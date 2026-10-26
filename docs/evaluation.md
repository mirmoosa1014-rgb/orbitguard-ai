# Evaluation

Run `python -m orbitguard.experiment --full`; saved JSON/CSV in `results/` is authoritative. Quick mode uses 10 train / 5 validation / 5 test episodes; full mode 30 / 5 / 15. Each seed generates one 18-object catalog and 91 sampled times over 1800 s. Entire radius/inclination families and seeds are split. The generated future encounter ensures the maneuver example is controllable during the horizon.

CV acceleration process sigma is tuned over [.003, .3, 3, 10, 30] m/s² on validation episode position MSE only; selected sigma 10 m/s² is fixed for held-out tests. The EKF uses physical gravity in its mean dynamics. Both filters receive identical noisy observations, so the baseline is competent rather than artificially deprived of measurements. Closest-approach forecasts start at the shared 600 s cutoff and compare aggregate catalog minimum separation, not per-pair collision probability.

Nominal 95% ellipsoid coverage uses χ²(3) threshold 7.8147 over 465 test updates. UI forecast shading is 1.96 times the maximum primary position-covariance axis propagated from a noisy t=0 update; it is a position scale rather than a calibrated relative-collision interval.

Both ranked policies refine five of the identical 18 candidates. Macro episode recall includes zero for zero-positive episodes, with positive and missed counts explicit in `ranking.csv`. `calibration.json` records every test label/probability; figure marker area represents bin support. The learned policy underperforms distance ranking, and this negative result is retained.

Demo OG-02: straight-line coarse propagation predicts minimum separation around 5 km while RK4 reveals a sub-kilometer future encounter. The numerical refinement corrects an acceleration-blind coarse prediction. The maneuver trade space spans approximately 0.79–2.21 km minimum catalog separation across proposals; these are deterministic comparisons, not safety guarantees. All proposals and newly introduced approaches are saved.

Python/TypeScript builds, conservation, covariance, causality, input bounds, replay, holdout, inference/fallback and API tests are recorded in progress.md. CI is prepared, not yet run remotely. The original Mac workspace disconnected; source was restored from retained authored tool-call text and deterministic outputs regenerated. No unavailable old binary was passed off as recovered.
