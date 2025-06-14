import argparse
import math
import random
import time

import numpy as np
import sounddevice as sd

import matplotlib; matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure(figsize=(5,3), facecolor='white')
ax = fig.add_axes((0., 0., 1., 1.), frameon=False, aspect=0.75)

# Parameters
n = 500  # how many circles on the screen at the same time
size = 5  # size of circles
starting_x = 1.2
delta_x = 0.004  # like the moving speed

# Circle positions
P = np.random.uniform(0,1,(n,2))
P[:,0] = np.ones(n) * starting_x

Free_position = -1

# colors
C = np.ones((n,4)) * (0.8,0.16,1,1)

# Marker sizes
S = np.ones(n) * size * 10


# Scatter plot
scat = ax.scatter(P[:,0], P[:,1], s=S, lw = 0.5,
                  edgecolors = C, facecolors='None')


# Ensure limits are [0,2] and remove ticks
ax.set_xlim(0,1.333), ax.set_xticks([])
ax.set_ylim(0,1), ax.set_yticks([])

last_frame_time = time.time()

def update(frame):

    global P, Free_position, last_frame_time

    # activate for calculating fps:
    #current_time = time.time()
    #fps = 1 / (current_time - last_frame_time)
    #print("FPS: ", fps)
    #last_frame_time = current_time

    P[:, 0] -= delta_x  # Update ring positions
    Free_position = np.argmin(P[:,0])
    scat.set_offsets(P)  # Update scatter object
    scat.set_color(C)
    return scat,  # Return the modified object

# dirty console application code
def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

columns = 120

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description="Play Unlimited",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-b', '--block-duration', type=float, metavar='DURATION', default=50,
    help='block size (default %(default)s milliseconds)')
parser.add_argument(
    '-c', '--columns', type=int, default=columns,
    help='width of spectrogram')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-g', '--gain', type=float, default=30,
    help='initial gain factor (default %(default)s)')
parser.add_argument(
    '-r', '--range', type=float, nargs=2,
    metavar=('LOW', 'HIGH'), default=[300, 2200],
    help='frequency range (default %(default)s Hz)')
args = parser.parse_args(remaining)
low, high = args.range
if high <= low:
    parser.error('HIGH must be greater than LOW')

gradient = [' ', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

try:
    samplerate = sd.query_devices(args.device, 'input')['default_samplerate']

    delta_f = (high - low) / (args.columns - 1)
    fftsize = math.ceil(samplerate / delta_f)
    low_bin = math.floor(low / delta_f)

    def callback(indata, frames, time, status):
        global Free_position, P, C
        if status:
            text = ' ' + str(status) + ' '
            print('X', text.center(args.columns, '#'), 'Y', sep='')
        if any(indata):
            magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
            magnitude *= args.gain / fftsize
            line = (gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))]
                    for x in magnitude[low_bin:low_bin + args.columns])
            #print(*line, sep='', end='|\n')
            max_mag = max(magnitude)
            pos_of_max = list(magnitude).index(max_mag)
            if pos_of_max > 0:
                y_value = pos_of_max / len(magnitude) * 10
                print(y_value)
                P[Free_position] = [starting_x, y_value]
                C[Free_position] = [0.6,y_value if 0 <= y_value <= 1 else 1,y_value if 0 <= y_value <= 1 else 1,1]
                last_circle_y_position = P[np.argmax(P[:,0])][1]
                oldest_p_index = np.argmin(P[:,0])
                P[oldest_p_index] = [starting_x - (delta_x/2), last_circle_y_position + (
                            y_value - last_circle_y_position) / 2]
                C[oldest_p_index] = [0.6,y_value if 0 <= y_value <= 1 else 1,y_value if 0 <= y_value <= 1 else 1,1]
        else:
            print('no input')



    with sd.InputStream(device=args.device, channels=1, callback=callback,
                        blocksize=int(samplerate * args.block_duration / 1000),
                        samplerate=samplerate):

        animation = animation.FuncAnimation(fig, update, interval=10, blit=True, frames=200)
        plt.show()
        while True:
            response = input()
except KeyboardInterrupt:
    parser.exit('Interrupted by user')
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))