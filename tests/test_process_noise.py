import numpy as np
import pytest
from orbitguard.estimation import estimate_cv
from orbitguard.physics import circular

@pytest.mark.parametrize('sigma', [-1, True, np.bool_(False), float('nan'), float('inf'), '10', None])
def test_invalid_process_noise_is_rejected_even_for_one_observation(sigma):
    state = circular()
    with pytest.raises(ValueError, match='acceleration sigma'):
        estimate_cv(state, [state[:3]], acceleration_sigma=sigma)

@pytest.mark.parametrize('sigma', [0, 10., np.float64(2)])
def test_valid_process_noise_produces_finite_estimates(sigma):
    state = circular()
    states, covariances, residuals = estimate_cv(state, [state[:3], state[:3]], acceleration_sigma=sigma)
    assert all(np.isfinite(values).all() for values in (states, covariances, residuals))
