import pandas
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation, FFMpegWriter
import numpy as np
from scipy.interpolate import interp1d

# inputs
brids_over_time_path = 'all_birds_over_time.csv'
freq = 'day'

birds = pandas.read_csv(brids_over_time_path)
birds.date = pandas.to_datetime(birds.date, format='%Y-%m-%d %H:%M:%S')
birds.sort_values('date', inplace=True)

sdx = birds.site == 'SKEL'
skel = birds[sdx]

# get counts for each day
if freq == 'day':
    skel_count = skel.groupby(skel.date.map(lambda x: (x.strftime('%Y-%m-%d'), x.isocalendar()[1])))['kittiwakes', 'guillemots', 'chicks', 'others'].sum()
    max_count = 500
elif freq == 'week':
    skel_count = skel.groupby(skel.date.map(lambda x: (x.strftime('%Y-%m'), x.isocalendar()[1])))['kittiwakes', 'guillemots', 'chicks', 'others'].sum()
    max_count = 2100

tween_frames = 16

date = []
kc = []
gc = []
cc = []
oc = []
# 4 frame padding
ct = 0
for index, row in skel_count.iterrows():
    if ct == 0:
        kc.append(row.kittiwakes)
        gc.append(row.guillemots)
        cc.append(row.chicks)
        oc.append(row.others)
        date.append(index[0])
    else:
        fk = interp1d([0, tween_frames + 1], [last_row.kittiwakes, row.kittiwakes])
        fg = interp1d([0, tween_frames + 1], [last_row.guillemots, row.guillemots])
        fc = interp1d([0, tween_frames + 1], [last_row.chicks, row.chicks])
        fo = interp1d([0, tween_frames + 1], [last_row.others, row.others])
        for i in range(1, tween_frames + 2):
            kc.append(fk(i))
            gc.append(fg(i))
            cc.append(fc(i))
            oc.append(fo(i))
            date.append(index[0])
    last_row = row


def init():
    ax.add_patch(k)
    ax.add_patch(g)
    ax.add_patch(c)
    ax.add_patch(o)
    text.set_text('')
    return text, k, g, c, o


def update(r):
    text.set_text(r[0])
    k.set_height(r[1] + 0.1)
    g.set_height(r[2] + 0.1)
    c.set_height(r[3] + 0.1)
    o.set_height(r[4] + 0.1)
    return text, k, g, c, o


fig, ax = plt.subplots()
k = patches.Rectangle((0, 0), 0.8, 0.1, fc='C8')
g = patches.Rectangle((1, 0), 0.8, 0.1, fc='C0')
c = patches.Rectangle((2, 0), 0.8, 0.1, fc='C6')
o = patches.Rectangle((3, 0), 0.8, 0.1, fc='C3')
labels = ['Kittiwakes', 'Guillemots', 'Chicks', 'Others']
text = plt.text(0, max_count, '', va='top', size=18)
ax.set_ylim(0, max_count)
ax.set_xlim(-0.2, 4)
plt.xticks([0.4, 1.4, 2.4, 3.4], labels)
values = zip(date, kc, gc, cc, oc)
interval = 124
ani = FuncAnimation(fig, update, values, interval=interval, init_func=init, save_count=len(date))

writer = FFMpegWriter(fps=1000 // interval)
ani.save('seabirdwatch_by_{0}_smooth.mp4'.format(freq), writer=writer, dpi=100)
