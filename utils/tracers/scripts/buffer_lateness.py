import argparse
import csv
import re

import matplotlib
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("file", help="Input file with queue levels")
parser.add_argument("--include-filter", help="Regular expression for element:pad names that should be included")
parser.add_argument("--exclude-filter", help="Regular expression for element:pad names that should be excluded")
parser.add_argument("--no-latency", help="do not include latency (enabled by default)", action="store_true")
args = parser.parse_args()

include_filter = None
if args.include_filter is not None:
    include_filter = re.compile(args.include_filter)
exclude_filter = None
if args.exclude_filter is not None:
    exclude_filter = re.compile(args.exclude_filter)

pads = {}

with open(args.file, mode='r', encoding='utf_8', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        if len(row) != 7:
            continue

        if include_filter is not None and not include_filter.match(row[1]):
            continue
        if exclude_filter is not None and exclude_filter.match(row[1]):
            continue

        if not row[1] in pads:
            pads[row[1]] = {
                'buffer-clock-time': [],
                'pipeline-clock-time': [],
                'lateness': [],
                'latency': [],
            }

        wallclock = float(row[0]) / 1000000000.0
        pads[row[1]]['buffer-clock-time'].append((wallclock, float(row[3]) / 1000000000.0))
        pads[row[1]]['pipeline-clock-time'].append((wallclock, float(row[4]) / 1000000000.0))
        pads[row[1]]['lateness'].append((wallclock, float(row[5]) / 1000000000.0))
        pads[row[1]]['latency'].append((wallclock, float(row[6]) / 1000000000.0))

matplotlib.rcParams['figure.dpi'] = 200

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

fig, ax1 = plt.subplots()

ax1.set_xlabel("wallclock (s)")
ax1.set_ylabel("time (s)")
ax1.tick_params(axis='y')

for (i, (pad, values)) in enumerate(pads.items()):
    # cycle colors
    i = i % len(colors)

    ax1.plot(
        [x[0] for x in values['lateness']],
        [x[1] for x in values['lateness']],
        '.', label = '{}: lateness'.format(pad),
        color = colors[i],
    )

    if not args.no_latency:
        ax1.plot(
            [x[0] for x in values['latency']],
            [x[1] for x in values['latency']],
            '-', label = '{}: latency'.format(pad),
            color = colors[i],
        )

fig.tight_layout()
plt.legend(loc='best')

plt.show()
