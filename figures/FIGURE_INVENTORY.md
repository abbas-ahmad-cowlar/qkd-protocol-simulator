# Figure Inventory

Release inventory for generated figures in the QKD Protocol Simulator.
Bitmap figures are saved under `figures/` at 300 dpi. Semilogy key-rate
plots mask zero or negative values before plotting.

| # | Filename | Producing notebook | Primary figure? | Scale / dpi | Sanity check |
|---|---|---|---|---|---|
| 1 | `bb84_protocol_flow.png` | Notebook 01 | Yes | Diagram, 300 dpi | Public discussion stages shown without revealing key bits |
| 2 | `bb84_basis_matrix.png` | Notebook 01 | Yes | Linear, 300 dpi | Keep/discard cells match standard BB84 basis agreement |
| 3 | `bb84_sifted_key_dist.png` | Notebook 01 | No | Linear, 300 dpi | Sifted bits are approximately balanced for random Alice bits |
| 4 | `qber_vs_interception.png` | Notebook 02 | Yes | Linear, 300 dpi | Full intercept-resend gives QBER about 25% |
| 5 | `key_rate_vs_interception.png` | Notebook 02 | No | Linear, 300 dpi | Zero crossing matches the selected `f_ec` threshold |
| 6 | `fiber_transmittance.png` | Notebook 03 | No | Semilogy, 300 dpi | `eta(50 km)=0.1`, `eta(100 km)=0.01` for alpha=0.2 dB/km |
| 7 | `qber_vs_distance.png` | Notebook 03 | No | Linear, 300 dpi | QBER tends to 0.5 at long distance |
| 8 | `bb84_key_rate_distance.png` | Notebook 03 | Yes | Semilogy positive rates only, 300 dpi | Key rate decreases and reaches zero at the computed cutoff |
| 9 | `parameter_sensitivity.png` | Notebook 03 | No | Semilogy positive rates only, 300 dpi | Better detector efficiency or lower dark counts improves range |
| Optional | `bb84_idealized_vs_decoy.png` | Notebook 03 optional extension | No | Semilogy positive rates only, 300 dpi | Labels distinguish idealized single-photon and simplified decoy assumptions |
| 10 | `cvqkd_gaussian_modulation.png` | Notebook 04 | Yes | Equal-aspect scatter, 300 dpi | Alice samples both x_A and p_A from N(0,V_A) |
| 11 | `cvqkd_phase_space_channel.png` | Notebook 04 | No | Equal-aspect scatter, 300 dpi | Bob's cloud is attenuated and noisier than Alice's |
| 12-13 | `cvqkd_snr_and_mutual_info.png` | Notebook 04 | No | 2-panel, 300 dpi | SNR and homodyne mutual information both decrease monotonically with distance |
| 14 | `homodyne_vs_heterodyne.png` | Notebook 04 | Yes | Linear, 300 dpi | Caption says raw mutual information only, not secure-key comparison |
| 15 | `cvqkd_key_rate_distance.png` | Notebook 05 | Yes | Semilogy positive rates only, 300 dpi | Key rate decreases and reaches zero at the computed cutoff |
| 16 | `excess_noise_effect.png` | Notebook 05 | Yes | Semilogy positive rates only, 300 dpi | Higher excess noise lowers rate and cutoff distance |
