import numpy as np
import pytest
from orbitguard.scenario import catalog

def test_short_catalog_is_exact_prefix_of_default_scenario():
 full=catalog(701,count=2);short=catalog(701,count=2,horizon=200)
 assert np.array_equal(short[0],full[0][:11]);assert np.array_equal(short[1],full[1]);assert np.array_equal(short[2],full[2])
 assert np.array_equal(short[3],full[3][:11]);assert np.array_equal(short[4],full[4][:,:11])
@pytest.mark.parametrize('kwargs',[{'count':0},{'count':True},{'horizon':0},{'horizon':30},{'horizon':float('nan')}])
def test_invalid_catalog_dimensions(kwargs):
 with pytest.raises(ValueError):catalog(**kwargs)
