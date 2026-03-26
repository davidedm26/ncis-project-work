import pandas as pd 
import matplotlib.pyplot as plt 

up = pd.read_csv('/home/jsorel/Desktop/elaborato_NCIS/scripts/data_analysis/up.csv', header = None)
down = pd.read_csv('/home/jsorel/Desktop/elaborato_NCIS/scripts/data_analysis/down.csv', header = None)

columns = [
    'timestamp',
    'src',
    'src_port',
    'dst',
    'dst_port',
    'stream_id',
    'interval',
    'trasnfer_bytes',
    'bandwidth',
    'jitter',
    'lost_packets',
    'total_packets',
    'loss_ratio',
    'out_of_order'
]

up.columns = columns
down.columns = columns

up['bandwidth_mbps']=up['bandwidth']/1e6
up['time'] = up['interval'].to_list().split('-')[0]
down['bandwidth_mbps']=down['bandwidth']/1e6

plt.figure()
plt.plot(up['time'], up['bandwidth_mbps'], label='UP SLICE')
plt.plot(down['time'], down['bandwidth_mbps'], label='DOWN SLICE')
plt.xlabel('time s')
plt.ylabel('Throughput')
plt.legend()
plt.grid(True)
plt.show()

