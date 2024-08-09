import sys
import os
import statistics

log_file = sys.argv[1]
start_time = None
data = list()
indexed_fractions = dict()
plot_folder = 'plots_data/'

if not os.path.exists(log_file):
    print('Log file \'' + log_file + '\' does not exist')
    exit(1)

if not os.path.exists(plot_folder):
    os.mkdir(plot_folder)

print('Collecting data')

with open(log_file, 'r') as handle:
    first_line = True

    for line in handle:

        log = line.strip()

        if len(log) == 0 or log[0] != '(':
            continue

        time = log.split(' ')[3]

        if first_line:
            first_line = False
            start_time = time

        if 'INFO:' in log and 'Event 1' in log:
            event = log.split('INFO:')[1].split('->')[0].strip()
            id = log.split('ID-')[1].split('.')[0] + '.json'
            priority = log.split('json')[1][1:]
            priority = float(priority[0:priority.find('-', 2)])
            table_stats = log.split('-')[-1]
            table_current_size = int(table_stats.split('/')[0])
            table_original_size = int(table_stats.split('/')[1])
            time_point = int(time.split(':')[1]) - int(start_time.split(':')[1])
            time_entry = {'time point': time_point, 'tables': list()}

            if len(data) == 0 or data[-1]['time point'] != time_point:
                data.append(time_entry)

            table_data = {'id': id, 'table size': table_current_size, 'priority': priority}
            data[-1]['tables'].append(table_data)

            if str(time_point) not in indexed_fractions.keys():
                indexed_fractions[str(time_point)] = 0.0

        elif 'Fully indexed' in log:
            time_point = int(time.split(':')[1]) - int(start_time.split(':')[1])
            indexed = log.split('Fully indexed')[1].strip().split(' ')[0]
            fraction = int(indexed.split('/')[0]) / int(indexed.split('/')[1])
            indexed_fractions[str(time_point)] = fraction

print('Analyzing data')

indexing_time = data[-1]['time point']
time_window = 5
table_sizes = dict()
table_priorities = dict()
data_indices = list()
table_sizes['0'] = dict()
table_priorities['0'] = dict()
data_indices.append(0)

for i in range(indexing_time):
    if i > 1 and i % time_window == 0:
        data_indices.append(i)
        table_sizes[str(i)] = dict()
        table_priorities[str(i)] = dict()

data_indices.append(indexing_time - 1)
table_sizes[str(indexing_time - 1)] = dict()
table_priorities[str(indexing_time - 1)] = dict()

for i in reversed(range(indexing_time)):
    key = None

    for j in reversed(data_indices):
        if j <= i:
            key = str(j)
            break

    for table in data[i]['tables']:
        if not table['id'] in table_sizes[key].keys():
            table_sizes[key][table['id']] = table['table size']
            table_priorities[key][table['id']] = table['priority']

with open(plot_folder + 'table_size_variances.txt', 'w') as handle:
    handle.write('Variance of table sizes by time point (X-axis of time points and Y-axis of intermediate table sizes)\n')

    for time_point in data_indices:
        handle.write('Time point: ' + str(time_point) + '\n')

        sizes = list(table_sizes[str(time_point)].values())
        avg_size = statistics.mean(sizes)

        for table in table_sizes[str(time_point)].keys():
            variance = abs(table_sizes[str(time_point)][table] - avg_size)
            handle.write(str(variance) + '\n')

        handle.write('\n')

with open(plot_folder + 'table_priority_variances.txt', 'w') as handle:
    handle.write('Variance of table priorities by time point (X-axis of time points and Y-axis of intermediate table priorities)\n')

    for time_point in data_indices:
        handle.write('Time point: ' + str(time_point) + '\n')

        priorities = list(table_priorities[str(time_point)].values())
        avg_priority = statistics.mean(priorities)

        for table in table_priorities[str(time_point)].keys():
            variance = abs(table_priorities[str(time_point)][table] - avg_priority)
            handle.write(str(variance) + '\n')

        handle.write('\n')

with open(plot_folder + 'indexed_fractions.txt', 'w') as handle:
    handle.write('Fractions of indexed tables at different time points (first a list of time points, then the list of fractions)\n')
    handle.write('Time points:\n')
    prev_fraction = 0.0

    for time_point in indexed_fractions.keys():
        handle.write(time_point + '\n')

    handle.write('\nFractions:\n')

    for time_point in indexed_fractions.keys():
        fraction = indexed_fractions[time_point]

        if fraction < prev_fraction:
            fraction = prev_fraction

        handle.write(str(fraction) + '\n')
        prev_fraction = fraction

print('Done')
