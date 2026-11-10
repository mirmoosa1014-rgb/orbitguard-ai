import numpy as np
import pytest
from orbitguard.physics import circular,R_EARTH
@pytest.mark.parametrize('kwargs',[{'radius':-1},{'radius':R_EARTH-1},{'radius':np.inf},{'phase':np.nan},{'inclination':np.inf}])
def test_invalid_circular_orbit(kwargs):
 with pytest.raises(ValueError):circular(**kwargs)
