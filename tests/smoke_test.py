"""
Smoke Test for QKD Protocol Simulator
Verifies: NumPy basics, log2 edge cases, random number generation.
"""
import numpy as np

# Test 1: NumPy log2 behavior at edge cases
assert np.log2(1.0) == 0.0, "log2(1) should be 0"
assert np.log2(2.0) == 1.0, "log2(2) should be 1"

# Test 2: 0 * log2(0) — shows WHY we need masking in entropy functions
val = 0.0 * np.log2(max(0.0, 1e-300))
print(f"   0 * log2(small) = {val} -- shows need for masking")

# Test 3: Random bit generation (core of BB84)
rng = np.random.default_rng(42)
bits = rng.integers(0, 2, size=1000)
assert set(np.unique(bits)) == {0, 1}, "Should produce only 0s and 1s"
mean = np.mean(bits)
assert 0.4 < mean < 0.6, f"Mean of random bits ~0.5, got {mean}"

# Test 4: Probability normalization check
probs = np.array([0.3, 0.2, 0.15, 0.15, 0.1, 0.1])
assert np.isclose(probs.sum(), 1.0), f"Probs should sum to 1, got {probs.sum()}"

# Test 5: Joint probability matrix basics
p_xy = np.array([[0.4, 0.1], [0.1, 0.4]])
assert np.isclose(p_xy.sum(), 1.0), "Joint distribution should sum to 1"
p_x = p_xy.sum(axis=1)
p_y = p_xy.sum(axis=0)
assert np.allclose(p_x, [0.5, 0.5]), f"Marginal p(x) wrong: {p_x}"
assert np.allclose(p_y, [0.5, 0.5]), f"Marginal p(y) wrong: {p_y}"

print("All smoke tests passed. Environment ready for QKD development.")
