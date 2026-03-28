# NCIS Project 2024/2025 — Network Slicing in SDN

## Goal

This project implements **network slicing** in an **SDN** environment using **Mininet** and **Ryu** (OpenFlow 1.3), with two components:

1. **Topology slicing**: logical isolation of host groups via MAC-based rules.
2. **Service slicing**: traffic classification and forwarding over two paths with different capacity.

## Tech stack

- Emulator: Mininet
- Controller: Ryu
- Protocol: OpenFlow 1.3
- Traffic generation: iPerf (iPerf2)
- Data analysis: Python + Matplotlib

## Repository structure

- `scripts/topology/`: topology + controller for topology slicing
- `scripts/service/`: topology + controller for service slicing
- `scripts/data_analysis/`: iPerf CSVs (`up.csv`, `down.csv`) and plotting script (`data_analysis.py`)
- `elaborato_LaTeX/`: report in LaTeX

## Requirements

Typical runtime environment (Linux/VM):

- Python 3
- Mininet
- Ryu (`ryu-manager`)
- iPerf2 (for CSV output with `-y C`)
- Matplotlib





