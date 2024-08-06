import matplotlib.pyplot as plt
import numpy as np
import scipy.signal

fs = 1e8
f0 = 1e6
f_mod = 2e4
w0 = 2 * np.pi * f0
Q = 40
tau = Q / np.pi / f0

t_max = 0.0002
t = np.arange(0, t_max, 1 / fs)

v_max = 3
v_h = 1.0
v_l = 0.5

# The transfer function for a resonator is: H(s) = w0^2 / (s^2 + w0/Q * s + w0^2)
# Here we calculate a digital equivalent via bilinear transform
filt = scipy.signal.bilinear(b=[w0**2], a=[1, w0 / Q, w0**2], fs=fs)

carrier = np.sin(w0 * t)
modulation = v_l + (v_h - v_l) * (np.sin(f_mod * 2 * np.pi * t) >= 0)

t_high_to_low = int(-tau * np.log(1 - (v_h - v_l) / (v_max + v_h)) * fs)
t_low_to_high = int(-tau * np.log(1 - (v_h - v_l) / (v_max - v_l)) * fs)
predistortion = modulation.copy()
i_high_to_low = np.where(np.diff(modulation) < 0)[0]
i_low_to_high = np.where(np.diff(modulation) > 0)[0]

for i in i_high_to_low:
    j = i + t_high_to_low
    predistortion[i:j] = -v_max

for i in i_low_to_high:
    j = i + t_low_to_high
    predistortion[i:j] = v_max

y = scipy.signal.lfilter(*filt, carrier * modulation, zi=[0, -1])[0]
y2 = scipy.signal.lfilter(*filt, carrier * predistortion)

t_usec = t * 1e6
t_usec = t_usec - 87.5
fig, axs = plt.subplots(2, 3, sharex=True)
axs[0, 0].plot(t_usec, modulation)
axs[0, 0].set_title("Modulation")
axs[0, 1].plot(t_usec, modulation * carrier)
axs[0, 1].plot(t_usec, modulation)
axs[0, 1].set_title("Modulated input")
axs[0, 2].plot(t_usec, y)
axs[0, 2].set_title("Resonator output")


axs[1, 0].plot(t_usec, predistortion)
axs[1, 1].plot(t_usec, predistortion * carrier)
axs[1, 1].plot(t_usec, predistortion)
axs[1, 2].plot(t_usec, y2)
axs[1, 2].set_xlim([0, 100])

fig.supxlabel("time (microseconds)")
fig.supylabel("signal (arb)")
plt.show()
