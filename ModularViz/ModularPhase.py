# drop into a .py or notebook and run
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import cmath
import math
from scipy import optimize

# --- USER: define your function f(z) here ---
# Example: a simple test function (NOT a true modular form). Replace with your f.
def f(z):
    # Example: f(z) = sin(2*pi*z)  (periodic under T, but not modular under S)
    return np.sqrt(np.pow(z,3) + z + 1)

# --- helper transforms ---
def cayley_forward(z):           # H -> D
    return (z - 1j) / (z + 1j)

def cayley_inverse(w):          # D -> H
    return 1j * (1 + w) / (1 - w)

# --- numerical modular tests for generators T and S ---
def test_modular_relations(f, k, pts=None, tol=1e-6):
    if pts is None:
        # pick random points in upper half plane: x in [-1,1], y in [0.5,3]
        rng = np.random.default_rng(12345)
        xs = rng.uniform(-0.9, 0.9, 8)
        ys = rng.uniform(0.6, 2.5, 8)
        pts = [x + 1j*y for x,y in zip(xs, ys)]
    results = []
    for z in pts:
        val_T = f(z+1)
        val = f(z)
        err_T = abs(val_T - val)
        val_S = f(-1/z)
        err_S = abs(val_S - (z**k)*val)
        results.append((z, err_T, err_S))
    return results

# --- find candidate zeros on unit disk grid, map to H, refine via rootfinder ---
def find_zeros_on_disk(f, grid_N=300, threshold=1e-2):
    xs = np.linspace(-0.99, 0.99, grid_N)
    ys = np.linspace(-0.99, 0.99, grid_N)
    W = np.zeros((grid_N, grid_N), dtype=np.complex128)
    A = np.zeros((grid_N, grid_N))
    for i,x in enumerate(xs):
        for j,y in enumerate(ys):
            w = x + 1j*y
            if abs(w) >= 1.0:
                A[j,i] = np.nan
                continue
            z = cayley_inverse(w)
            val = f(z)
            W[j,i] = val
            A[j,i] = abs(val)
    # coarse minima detection
    candidates = []
    for i in range(1, grid_N-1):
        for j in range(1, grid_N-1):
            if np.isnan(A[j,i]): continue
            window = A[j-1:j+2, i-1:i+2]
            if A[j,i] == np.nanmin(window) and A[j,i] < threshold:
                candidates.append(xs[i] + 1j*ys[j])
    # refine using 2-real-variable Newton (scipy)
    zeros = []
    for w0 in candidates:
        def system(u):
            # u is [u_re, u_im], w = u_re + i u_im
            w = u[0] + 1j*u[1]
            z = cayley_inverse(w)
            val = f(z)
            return [val.real, val.imag]
        try:
            sol = optimize.root(system, [w0.real, w0.imag], tol=1e-12)
            if sol.success:
                w_sol = sol.x[0] + 1j*sol.x[1]
                if abs(w_sol) < 1 and all(abs(w_sol - z0) > 1e-6 for z0 in zeros):
                    zeros.append(w_sol)
        except Exception:
            pass
    return A, W, xs, ys, zeros

# --- plotting functions ---
def plot_modulus(A, xs, ys, zeros=None, title='|f| on unit disk'):
    plt.figure(figsize=(6,6))
    X, Y = np.meshgrid(xs, ys)
    # mask outside disk:
    mask = np.sqrt(X**2 + Y**2) >= 1
    A_plot = A.copy()
    A_plot[mask] = np.nan
    # show log scale to tame dynamic range:
    plt.imshow(np.log10(A_plot), origin='lower',
               extent=(xs[0], xs[-1], ys[0], ys[-1]), aspect='equal')
    plt.colorbar(label='log10|f|')
    if zeros:
        zr = [z.real for z in zeros]; zi = [z.imag for z in zeros]
        plt.scatter(zr, zi, c='white', edgecolors='black', s=50, marker='x')
    plt.title(title)
    plt.xlabel('Re w'); plt.ylabel('Im w')
    plt.show()

def plot_phase(W, xs, ys, zeros=None, title='arg(f) on unit disk'):
    X, Y = np.meshgrid(xs, ys)
    mask = np.sqrt(X**2 + Y**2) >= 1
    arg = np.angle(W)
    arg[mask] = np.nan
    # HSV mapping: hue = normalized angle, value = normalized magnitude (optional)
    hue = (arg + np.pi) / (2*np.pi)
    sat = np.ones_like(hue)
    val = np.clip(np.log1p(np.abs(W)), 0, None)  # optional brightness by log mag
    # normalize val to [0,1]
    vmin, vmax = np.nanmin(val), np.nanmax(val)
    if vmax - vmin > 0:
        val = (val - vmin) / (vmax - vmin)
    hsv = np.stack([hue, sat, val], axis=-1)
    rgb = hsv_to_rgb(hsv)
    rgb[mask] = 1.0  # white outside disk
    plt.figure(figsize=(6,6))
    plt.imshow(rgb, origin='lower', extent=(xs[0], xs[-1], ys[0], ys[-1]), aspect='equal')
    if zeros:
        zr = [z.real for z in zeros]; zi = [z.imag for z in zeros]
        plt.scatter(zr, zi, c='k', s=50, marker='x')
    plt.title(title)
    plt.xlabel('Re w'); plt.ylabel('Im w')
    plt.show()

# --- Example usage ---
if __name__ == '__main__':
    # 1) test modular relations for candidate weight k
    k = 2  # supply your expected weight here
    tests = test_modular_relations(f, k)
    for z, errT, errS in tests:
        print(f"z={z:.3f}, |f(z+1)-f(z)|={errT:.2e}, |f(-1/z)-z^k f(z)|={errS:.2e}")

    # 2) find zeros on unit disk grid
    A, W, xs, ys, zeros = find_zeros_on_disk(f, grid_N=300, threshold=1e-2)
    print("Found zeros (in unit disk coords):", zeros)

    # 3) plot modulus and phase
    plot_modulus(A, xs, ys, zeros=zeros)
    plot_phase(W, xs, ys, zeros=zeros)
