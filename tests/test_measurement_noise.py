import numpy as np
import pytest
from orbitguard.estimation import update
@pytest.mark.parametrize('sigma',[-1,0,np.nan,np.inf,True])
def test_invalid_noise_rejected(sigma):
 with pytest.raises(ValueError):update(np.zeros(6),np.eye(6),np.ones(3),sigma)
