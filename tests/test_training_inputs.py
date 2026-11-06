import numpy as np
import pytest
from orbitguard.model import train


@pytest.mark.parametrize('labels',[np.ones(4),np.zeros(4),np.array([0,1,2,0]),np.array([0,1,np.nan,0])])
def test_training_requires_two_binary_classes(labels):
    with pytest.raises(ValueError):train(np.arange(16.).reshape(4,4),labels)


@pytest.mark.parametrize('features,labels',[(np.empty((0,4)),np.array([])),(np.ones((4,3)),np.array([0,1,0,1])),(np.ones((4,4)),np.array([0,1]))])
def test_training_requires_matching_nonempty_four_feature_data(features,labels):
    with pytest.raises(ValueError):train(features,labels)
