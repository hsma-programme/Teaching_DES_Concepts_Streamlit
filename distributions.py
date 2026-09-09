"""
Distribution classes

To help with controlling sampling `numpy` distributions are packaged up into
classes that allow easy control of random numbers.

**Distributions included:**
* Exponential
* Log Normal
* Bernoulli
* Normal
* Uniform

Code taken from our MIT licensed sim-tools package (`pip install sim-tools`)
https://github.com/TomMonks/sim-tools
"""

from abc import ABC, abstractmethod
import numpy as np
import math

from typing import Optional


class Distribution(ABC):
    """
    Distribution abstract class
    All distributions derived from it.
    """

    def __init__(self, random_seed: Optional[int] = None):
        self.rng = np.random.default_rng(random_seed)

    @abstractmethod
    def sample(self, size: Optional[int] = None) -> float | np.ndarray:
        """
        Generate a sample from the distribution

        Params:
        -------
        size: int, optional (default=None)
            the number of samples to return.  If size=None then a single
            sample is returned.

        Returns:
        -------
        np.ndarray or scalar
        """
        pass


class Exponential(Distribution):
    """
    Convenience class for the exponential distribution.
    packages up distribution parameters, seed and random generator.
    """

    def __init__(self, mean: float, random_seed: Optional[int] = None):
        """
        Constructor

        Params:
        ------
        mean: float
            The mean of the exponential distribution

        random_seed: int, optional (default=None)
            A random seed to reproduce samples.  If set to none then a unique
            sample is created.
        """
        super().__init__(random_seed)
        self.mean = mean

    def sample(self, size: Optional[int] = None) -> float | np.ndarray:
        """
        Generate a sample from the exponential distribution

        Params:
        -------
        size: int, optional (default=None)
            the number of samples to return.  If size=None then a single
            sample is returned.
        """
        return self.rng.exponential(self.mean, size=size)


class Bernoulli(Distribution):
    """
    Convenience class for the Bernoulli distribution.
    packages up distribution parameters, seed and random generator.
    """

    def __init__(self, p: float, random_seed: Optional[int] = None):
        """
        Constructor

        Params:
        ------
        p: float
            probability of drawing a 1

        random_seed: int, optional (default=None)
            A random seed to reproduce samples.  If set to none then a unique
            sample is created.
        """
        super().__init__(random_seed)
        self.p = p

    def sample(self, size: Optional[int] = None) -> float | np.ndarray:
        """
        Generate a sample from the exponential distribution

        Params:
        -------
        size: int, optional (default=None)
            the number of samples to return.  If size=None then a single
            sample is returned.
        """
        return self.rng.binomial(n=1, p=self.p, size=size)


class Lognormal(Distribution):
    """
    Encapsulates a lognormal distirbution
    """

    def __init__(self, mean: float, stdev: float, random_seed: Optional[int] = None):
        """
        Params:
        -------
        mean: float
            mean of the lognormal distribution

        stdev: float
            standard dev of the lognormal distribution

        random_seed: int, optional (default=None)
            Random seed to control sampling
        """
        super().__init__(random_seed)
        mu, sigma = self.normal_moments_from_lognormal(mean, stdev**2)
        self.mu = mu
        self.sigma = sigma

    def normal_moments_from_lognormal(self, m, v):
        """
        Returns mu and sigma of normal distribution
        underlying a lognormal with mean m and variance v
        source: https://blogs.sas.com/content/iml/2014/06/04/simulate-lognormal
        -data-with-specified-mean-and-variance.html

        Params:
        -------
        m: float
            mean of lognormal distribution
        v: float
            variance of lognormal distribution

        Returns:
        -------
        (float, float)
        """
        phi = math.sqrt(v + m**2)
        mu = math.log(m**2 / phi)
        sigma = math.sqrt(math.log(phi**2 / m**2))
        return mu, sigma

    def sample(self, size: Optional[int] = None) -> float | np.ndarray:
        """
        Sample from the normal distribution
        """
        return self.rng.lognormal(self.mu, self.sigma, size=size)


class Normal(Distribution):
    """
    Convenience class for the normal distribution.
    packages up distribution parameters, seed and random generator.

    Use the minimum parameter to truncate the distribution
    """

    def __init__(
        self,
        mean: float,
        sigma: float,
        minimum: Optional[float] = None,
        random_seed: Optional[int] = None,
    ):
        """
        Constructor

        Params:
        ------
        mean: float
            The mean of the normal distribution

        sigma: float
            The stdev of the normal distribution

        minimum: float
            Truncate the normal distribution to a minimum
            value.

        random_seed: int, optional (default=None)
            A random seed to reproduce samples.  If set to none then a unique
            sample is created.
        """
        self.rng = np.random.default_rng(seed=random_seed)
        self.mean = mean
        self.sigma = sigma
        self.minimum = minimum

    def sample(self, size: Optional[int] = None) -> float | np.ndarray:
        """
        Generate a sample from the normal distribution

        Params:
        -------
        size: int, optional (default=None)
            the number of samples to return.  If size=None then a single
            sample is returned.
        """
        samples = self.rng.normal(self.mean, self.sigma, size=size)

        if self.minimum is None:
            return samples
        elif size is None:
            return max(self.minimum, samples)
        else:
            # index of samples with negative value
            neg_idx = np.where(samples < 0)[0]
            samples[neg_idx] = self.minimum
            return samples


class Uniform(Distribution):
    """
    Convenience class for the Uniform distribution.
    packages up distribution parameters, seed and random generator.
    """

    def __init__(
        self, low: float, high: float, random_seed: Optional[int] = None
    ) -> float | np.ndarray:
        """
        Constructor

        Params:
        ------
        low: float
            lower range of the uniform

        high: float
            upper range of the uniform

        random_seed: int, optional (default=None)
            A random seed to reproduce samples.  If set to none then a unique
            sample is created.
        """
        super().__init__(random_seed)
        self.low = low
        self.high = high

    def sample(self, size: Optional[int] = None) -> float | np.ndarray:
        """
        Generate a sample from the uniform distribution

        Params:
        -------
        size: int, optional (default=None)
            the number of samples to return.  If size=None then a single
            sample is returned.
        """
        return self.rng.uniform(low=self.low, high=self.high, size=size)
