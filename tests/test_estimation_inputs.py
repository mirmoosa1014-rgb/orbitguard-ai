import numpy as np
import pytest
from orbitguard.estimation import estimate,estimate_cv,update
from orbitguard.physics import circular

@pytest.mark.parametrize('method',[estimate,estimate_cv])
@pytest.mark.parametrize('dt',[0,-20,float('nan'),float('inf'),True])
def test_estimation_rejects_nonforward_or_nonfinite_sampling(method,dt):
    x=circular()
    with pytest.raises(ValueError):method(x,np.array([x[:3]]),dt=dt)

@pytest.mark.parametrize('z',[[np.nan,0,0],[0,np.inf,0],0,[[0,0,0]]])
def test_invalid_measurements_do_not_poison_filter(z):
    with pytest.raises(ValueError):update(np.zeros(6),np.eye(6),z)

def test_lists_are_accepted_without_mutating_inputs():
    x=circular().tolist();obs=[x[:3]];before=x[:]
    states,_,_=estimate(x,obs)
    assert states.shape==(1,6) and x==before
