# Architecture

`physics.py` owns SI-unit six-state RK4 dynamics; `scenario.py` creates bounded catalogs and compares 21 along-track impulses; `estimation.py` owns causal EKF and CV Kalman updates; `model.py` trains logistic scores and provides a missing-model distance fallback; `experiment.py` partitions whole episodes/families, tunes CV process noise and calibrates probabilities on validation only, and saves evidence. FastAPI supplies bounded read-only endpoints. React renders checked-in JSON on a canvas with 3D rotation/projection and SVG charts.

State is `[x,y,z,vx,vy,vz]` in meters and meters per second. Earth-centered inertial coordinates; no geodetic ground tracks. μ = 3.986004418e14 m³/s², spherical Earth radius 6371 km. All scenarios use two-body dynamics with RK4 steps at most 20 s; no J2.

Direct virtual ECI position observations arrive every 20 s for 600 s, with independent 80 m Gaussian noise per axis. Both estimators receive precisely the same measurements. EKF uses finite-difference transition Jacobians, initial position/velocity variances 300² m² and 3² (m/s)², acceleration process sigma .003 m/s², and Joseph-form observation covariance update. The CV Kalman filter uses the same initial covariance/observations but separately validation-tuned acceleration process sigma. Forecasting starts at the same last observation; no future truth is passed into either filter.

The static UI demonstrates saved seed 2026; live API scenario seeds are integers 0–100000, catalog capped at 12 and 1800 s. Experiments are short synchronous bounded jobs, with no unbounded background-job queue. Policy features never contain refined future truth. The evaluator computes all refined truth to score missed detections fairly; that truth is unavailable to policy ordering.

One deliberate future encounter is created by prescribing a relative state near t=1200 s and numerically integrating it backward to the present. Policies receive only the resulting present state. This is synthetic scenario generation, not a hidden future feature. Other objects use seeded relative-state perturbations.

Maneuvers are ±0.5, ±1, ±2 and zero m/s along-track impulses at t=0,300,600 s. Proposal validation caps impulse magnitude and rejects the unused terminal timestep. Every proposal uses the identical object catalog. New sampled approaches below 10 km are counted relative to nominal. Maneuvers use known simulated initial states, without robust uncertainty optimization; no command is sent to hardware.
