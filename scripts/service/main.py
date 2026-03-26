from topology import *

if __name__ == '__main__':

    setLogLevel('info')
    info('[MAIN] Starting the environment\n')

    env = Environment()

    info("[MAIN] Running CLI\n")
    CLI(env.net)