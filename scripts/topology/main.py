from topology import *

if __name__ == '__main__':
    setLogLevel('info') # imposta il livello di log su "info" per visualizzare informazioni dettagliate durante l'esecuzione del programma
    info('[MAIN] Starting the environment\n') # stampa un messaggio di log per indicare l'inizio dell'ambiente di rete, utile per il debug e la comprensione del flusso del programma
    
    env = Environment() # crea un'istanza dell'ambiente di rete, che include la definizione della topologia, la configurazione del controller e l'avvio della rete

    info("[MAIN] Running CLI\n") # stampa un messaggio di log per indicare l'avvio dell'interfaccia a riga di comando (CLI) di Mininet, che consente all'utente di interagire con la rete virtuale, eseguire comandi sui nodi e testare la connettività tra gli host
    CLI(env.net) # avvia l'interfaccia a riga di comando (CLI) di Mininet, passando la rete virtuale creata nell'ambiente come argomento, consentendo all'utente di interagire con la rete e testare la connettività tra gli host