# QKD Protocol Simulator

> Comparing Discrete-Variable (BB84) and Continuous-Variable (GG02)
> Quantum Key Distribution under stated fiber-channel assumptions.

![BB84 vs CV-QKD Protocol Comparison](figures/protocol_comparison.png)

## Overview

This repository implements and compares two fundamental Quantum Key
Distribution (QKD) protocols: **BB84** (discrete-variable) and **GG02**
(continuous-variable). The code computes asymptotic secure key-rate bounds
under explicit, reproducible parameter sets.

The simulator shows how fiber attenuation, detector dark counts, excess
noise, and reconciliation efficiency constrain the maximum secure distance
for each protocol. All numbers in plots and tables are computed from the
code; no headline values are hardcoded.

The project is organized as a standalone scientific Python repository:
small numerical modules, executable notebooks, saved 300 dpi figures, and
regression tests that keep the stated assumptions visible.

## Headline Result

Under the default parameter sets used by the comparison notebook and
headline figure:

| Protocol | Source / detector | Trust model | Cutoff | K @ 50 km |
|---|---|---|---|---|
| BB84 | idealised single-photon source | -- (single-photon) | **169.4 km** | 9.876 x 10^-4 bits / pulse |
| CV-QKD GG02 | Gaussian-modulated coherent states, balanced homodyne | untrusted detector | **74.2 km** | 9.237 x 10^-3 bits / symbol |

> **Important caveat.** The two columns use different normalisations
> (per emitted pulse vs per coherent-state symbol) and different security
> models (asymptotic simplified BB84 vs asymptotic collective Gaussian
> attack). The cutoff column is not a universal performance ranking;
> changing detector efficiency, excess noise, dark counts, or reconciliation
> efficiency changes the relative ordering. See the parameter box on the
> figure for the exact assumptions.

## Key Figures

