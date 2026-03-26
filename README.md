# Elaborato NCIS 2024/2025 - Consegna

## Obiettivo del Progetto

L'obiettivo del progetto è l'implementazione del **network slicing** in un ambiente **SDN (Software-Defined Networking)**. Il sistema mira a segmentare le risorse di rete per soddisfare requisiti specifici di connettività e qualità del servizio.

## Stack Tecnologico

* **Emulatore di rete:** Mininet
* **SDN Controller:** Ryu
* **Protocollo:** OpenFlow

---

## Moduli di Implementazione

### 1. Topology Slicing

Questa fase si concentra sulla restrizione dei percorsi di comunicazione tra gruppi specifici di host (slicing topologico).

**Fasi operative:**

* Definizione della topologia di rete in Mininet con almeno due slice isolati.
* Configurazione del controller Ryu per gestire lo slicing tramite regole di flusso basate su indirizzi MAC.
* **Verifica:** Utilizzo del comando `pingall` in Mininet per confermare che la comunicazione avvenga esclusivamente tra gli host autorizzati all'interno dello stesso slice.

### 2. Service Slicing

Questa fase riguarda la prioritizzazione del traffico in base alla tipologia di servizio.

**Fasi operative:**

* Configurazione del controller Ryu per l'identificazione del traffico tramite porta di destinazione e protocollo di trasporto.
* Implementazione di regole OpenFlow per classificare e instradare il traffico "video" con priorità rispetto al traffico standard (best-effort).
* **Verifica:** Utilizzo di tool di monitoraggio e generazione traffico per validare le politiche di instradamento.

---

## Test e Validazione

Per garantire il corretto funzionamento del sistema, vengono eseguiti i seguenti test:

* **Connettività:** Verifica che tutti i dispositivi possano raggiungere i target autorizzati.
* **Instradamento:** Utilizzo di **iPerf** per generare traffico UDP e verificare l'effettivo passaggio attraverso lo slice dedicato.
* **Performance:** Confronto del **throughput** del traffico video rispetto al traffico ordinario per confermare l'efficacia della prioritizzazione.

---

## Estensioni

Il progetto prevede i seguenti sviluppi opzionali:

* **Dashboard di monitoraggio:** Interfaccia grafica per la visualizzazione dello stato della rete in tempo reale.
* **Analisi Avanzata del Traffico:** Utilizzo di **D-ITG** per la generazione di profili di traffico complessi.
* **Classificazione Statistica:** Identificazione del traffico basata su statistiche dei pacchetti anziché sui numeri di porta.
* **Slicing Dinamico:** Allocazione delle risorse per il traffico video attivata esclusivamente on-demand.

