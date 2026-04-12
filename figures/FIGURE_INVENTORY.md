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
| 17 | `cvqkd_reconciliation_efficiency.png` | Notebook 05 | No | Semilogy positive rates only, 300 dpi | Higher reconciliation efficiency increases key rate |
| 18 | `cvqkd_pure_loss_information.png` | Notebook 05 | No | Linear, 300 dpi | Shows I(A:B), chi(B:E), and the secure region for pure loss |
| 19 | `protocol_comparison.png` | Notebook 06 | Yes | Semilogy positive rates only, 300 dpi | Caption states BB84 bits/pulse and CV bits/symbol normalisations; both cutoffs computed via `brentq` on unclamped expressions |
| Diagnostic | `bb84_key_rate_curve.png` | Notebook 01 diagnostic | No | Linear, 300 dpi | Per-sifted-bit key rate vs QBER for `f_ec` in {1.00, 1.16, 1.50}; threshold lines visible |
| Diagnostic | `bb84_vs_cvqkd_key_rate.png` | Notebook 05 diagnostic | No | Semilogy positive rates only, 300 dpi | Same overlay as figure 19 but plotted from notebook 05 to expose the per-pulse vs per-symbol normalisation difference; not a security ranking |
