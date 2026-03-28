# Elaborato NCIS 2024/2025 — Network Slicing in SDN

## Obiettivo

Il progetto implementa il **network slicing** in un ambiente **SDN** tramite **Mininet** e **Ryu** (OpenFlow 1.3), con due componenti:

1. **Topology slicing**: isolamento logico dei gruppi di host tramite regole basate su MAC.
2. **Service slicing**: classificazione del traffico e instradamento su due percorsi con capacità diversa.

## Stack tecnologico

- Emulatore: Mininet
- Controller: Ryu
- Protocollo: OpenFlow 1.3
- Generazione traffico: iPerf (iPerf2)
- Analisi dati: Python + Matplotlib

## Struttura repository

- `scripts/topology/`: topologia + controller per topology slicing
- `scripts/service/`: topologia + controller per service slicing
- `scripts/data_analysis/`: CSV iPerf (`up.csv`, `down.csv`) e script di plotting (`data_analysis.py`)
- `elaborato_LaTeX/`: relazione in LaTeX

## Requisiti

Ambiente tipico di esecuzione (Linux/VM):

- Python 3
- Mininet
- Ryu (`ryu-manager`)
- iPerf2 (per l'output CSV con `-y C`)
- Matplotlib





