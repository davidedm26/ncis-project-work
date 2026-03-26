import csv 
import matplotlib.pyplot as plt

time_up = []
throughput_up = []
jitter_up = []

time_down = []
throughput_down = []
jitter_down = []

with open('/home/jsorel/Desktop/elaborato_NCIS/scripts/data_analysis/up.csv', newline="") as f:
    reader = csv.reader(f)
    for row in reader:
        interval = row[6]
        bandwidth = float(row[8])
        t_end = float(interval.split('-')[1])
        bandwidth = bandwidth / 1e6 #Mbps
        time_up.append(t_end)
        throughput_up.append(bandwidth)
        jitter_up.append(row[9])

with open('/home/jsorel/Desktop/elaborato_NCIS/scripts/data_analysis/down.csv', newline="") as f:
    reader = csv.reader(f)
    for row in reader:
        interval = row[6]
        bandwidth = float(row[8])
        t_end = float(interval.split('-')[1])
        bandwidth = bandwidth / 1e6 #Mbps
        time_down.append(t_end)
        throughput_down.append(bandwidth)
        jitter_down.append(row[9])

throughput_up = throughput_up/10
throughput_down = throughput_down/1

plt.figure()
plt.plot(time_up, throughput_up, label='UP SLICE')
plt.plot(time_down, throughput_down, label='DOWN SLICE')
plt.xlabel('time s')
plt.ylabel('Throughput Mbps/Bandwidth')
plt.legend()
plt.grid(True)
plt.savefig('./throughput_compared.png')

plt.figure()
plt.plot(time_up, jitter_up, label='UP SLICE')
plt.plot(time_down, jitter_down, label='DOWN SLICE')
plt.xlabel('time s')
plt.ylabel('jitter ms')
plt.legend()
plt.grid(True)
plt.savefig('./jitter_compared.png')

