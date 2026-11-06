import json
import numpy as np
import pytest
from orbitguard.model import FEATURES, rank_candidates, train


@pytest.mark.parametrize('field,value', [('scale', [0]*4), ('scale', [-1]*4),
    ('weights', [float('inf')]*4), ('mean', [0]), ('bias', float('inf'))])
def test_invalid_models_use_distance_fallback(tmp_path, field, value):
    model = dict(features=FEATURES, mean=[0]*4, scale=[1]*4, weights=[1]*4, bias=0)
    model[field] = value
    path = tmp_path/'ranker.json'
    path.write_text(json.dumps(model))
    order, label = rank_candidates(np.array([[3,1,0,.3],[1,1,0,.3],[2,1,0,.3]]), path)
    assert label == 'distance-fallback'
    assert order.tolist() == [1,2,0]
