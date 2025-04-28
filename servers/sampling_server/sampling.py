import numpy as np
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.logging_utils import MCPLogger

logger = MCPLogger(service_name='sampling-server')


class SamplingEngine:
    """Sampling engine for MCP Sampling Server."""

    def __init__(self):
        """Initialize the sampling engine."""
        self.sampling_methods = {
            'uniform': self.uniform_sampling,
            'normal': self.normal_sampling,
            'weighted': self.weighted_sampling,
            'stratified': self.stratified_sampling,
            'topk': self.top_k_sampling,
            'nucleus': self.nucleus_sampling
        }

    def sample(self, method, params):
        """Sample using the specified method and parameters."""
        if method not in self.sampling_methods:
            raise ValueError(f"Sampling method not supported: {method}")

        logger.info(f"Performing {method} sampling")
        return self.sampling_methods[method](params)

    def uniform_sampling(self, params):
        """Uniform random sampling."""
        size = params.get('size', 1)
        low = params.get('low', 0)
        high = params.get('high', 1)

        # Generate samples
        samples = np.random.uniform(low, high, size)

        return {
            'method': 'uniform',
            'samples': samples.tolist(),
            'params': params,
            'timestamp': datetime.utcnow().isoformat()
        }

    def normal_sampling(self, params):
        """Normal (Gaussian) sampling."""
        size = params.get('size', 1)
        mean = params.get('mean', 0)
        std = params.get('std', 1)

        # Generate samples
        samples = np.random.normal(mean, std, size)

        return {
            'method': 'normal',
            'samples': samples.tolist(),
            'params': params,
            'timestamp': datetime.utcnow().isoformat()
        }

    def weighted_sampling(self, params):
        """Weighted random sampling."""
        size = params.get('size', 1)
        values = params.get('values', [])
        weights = params.get('weights', [])

        if not values or not weights or len(values) != len(weights):
            raise ValueError("Values and weights must be provided and have the same length")

        # Normalize weights
        weights_sum = sum(weights)
        normalized_weights = [w / weights_sum for w in weights]

        # Generate samples
        samples_indices = np.random.choice(len(values), size=size, p=normalized_weights)
        samples = [values[i] for i in samples_indices]

        return {
            'method': 'weighted',
            'samples': samples,
            'params': params,
            'timestamp': datetime.utcnow().isoformat()
        }

    def stratified_sampling(self, params):
        """Stratified sampling."""
        strata = params.get('strata', {})
        sample_sizes = params.get('sample_sizes', {})

        if not strata or not sample_sizes:
            raise ValueError("Strata and sample sizes must be provided")

        samples = {}

        # Sample from each stratum
        for stratum_name, stratum_values in strata.items():
            size = sample_sizes.get(stratum_name, 1)

            if size > len(stratum_values):
                size = len(stratum_values)

            # Random sampling without replacement
            sampled_indices = np.random.choice(len(stratum_values), size=size, replace=False)
            samples[stratum_name] = [stratum_values[i] for i in sampled_indices]

        return {
            'method': 'stratified',
            'samples': samples,
            'params': params,
            'timestamp': datetime.utcnow().isoformat()
        }

    def top_k_sampling(self, params):
        """Top-K sampling for text generation."""
        logits = params.get('logits', [])
        k = params.get('k', 5)
        temperature = params.get('temperature', 1.0)

        if not logits:
            raise ValueError("Logits must be provided")

        # Convert logits to numpy array
        logits_array = np.array(logits)

        # Apply temperature
        if temperature > 0:
            logits_array = logits_array / temperature

        # Get top-k indices
        top_k_indices = np.argsort(logits_array)[-k:]

        # Set probabilities for top-k
        probs = np.zeros_like(logits_array)
        probs[top_k_indices] = np.exp(logits_array[top_k_indices])

        # Normalize probabilities
        probs = probs / np.sum(probs)

        # Sample from the distribution
        sample_index = np.random.choice(len(logits), p=probs)

        return {
            'method': 'topk',
            'sample_index': int(sample_index),
            'sample_probability': float(probs[sample_index]),
            'top_k_indices': top_k_indices.tolist(),
            'params': params,
            'timestamp': datetime.utcnow().isoformat()
        }

    def nucleus_sampling(self, params):
        """Nucleus (Top-p) sampling for text generation."""
        logits = params.get('logits', [])
        p = params.get('p', 0.9)
        temperature = params.get('temperature', 1.0)

        if not logits:
            raise ValueError("Logits must be provided")

        # Convert logits to numpy array
        logits_array = np.array(logits)

        # Apply temperature
        if temperature > 0:
            logits_array = logits_array / temperature

        # Convert to probabilities
        probs = np.exp(logits_array) / np.sum(np.exp(logits_array))

        # Sort in descending order
        sorted_indices = np.argsort(-probs)
        sorted_probs = probs[sorted_indices]

        # Cumulative probabilities
        cumulative_probs = np.cumsum(sorted_probs)

        # Find the indices that are in the top-p
        nucleus_indices = sorted_indices[cumulative_probs <= p]

        # Include the first index after p if needed
        if len(nucleus_indices) == 0 or cumulative_probs[0] > p:
            nucleus_indices = np.array([sorted_indices[0]])
        elif cumulative_probs[-1] < p:
            nucleus_indices = np.append(nucleus_indices, sorted_indices[len(nucleus_indices)])

        # Create a new distribution with only nucleus probabilities
        nucleus_probs = probs[nucleus_indices]
        nucleus_probs = nucleus_probs / np.sum(nucleus_probs)

        # Sample from the nucleus
        sample_idx = np.random.choice(nucleus_indices, p=nucleus_probs)

        return {
            'method': 'nucleus',
            'sample_index': int(sample_idx),
            'sample_probability': float(probs[sample_idx]),
            'nucleus_size': len(nucleus_indices),
            'nucleus_indices': nucleus_indices.tolist(),
            'params': params,
            'timestamp': datetime.utcnow().isoformat()
        }
