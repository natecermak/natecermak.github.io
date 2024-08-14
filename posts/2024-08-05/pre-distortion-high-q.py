import itertools

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.signal
import scipy.optimize

###### Simulation 1: controlling a single simple damped harmonic resonance

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

# The transfer function for a resonator is: H(s) = (w0^2 / Q) / (s^2 + w0/Q * s + w0^2)
# Gain at resonance is 1 (0 dB).
# Here we calculate a digital equivalent via bilinear transform
filt = scipy.signal.bilinear(b=[w0**2 / Q], a=[1, w0 / Q, w0**2], fs=fs)
# Verification
# f, h = scipy.signal.freqz(*filt, worN=65536, fs=fs)
# plt.loglog(f, np.abs(h))

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

y = scipy.signal.lfilter(*filt, carrier * modulation)
y_pre = scipy.signal.lfilter(*filt, carrier * predistortion)

t_usec = t * 1e6
t_usec = t_usec - 87.5
fig, axs = plt.subplots(2, 3, sharex='all', sharey='col')
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
axs[1, 2].plot(t_usec, y_pre)
axs[1, 2].set_xlim([0, 100])
axs[1, 2].set_ylim([-1, 1])


fig.supxlabel("time (microseconds)")
fig.supylabel("signal (arb)")
plt.show()




####### Figure out Q of cascaded filters

Qs = np.logspace(np.log10(2), np.log10(200), 40)
worN = 65536
df = pd.DataFrame(columns=('Q1', 'Q2', 'Qeff'))
i = 0
for Q1, Q2 in itertools.combinations(Qs, 2):
    w, h1 = scipy.signal.freqs(b=[1/Q1], a=[1, 1 / Q1, 1], worN=worN)
    # plt.loglog(w, np.abs(h1))
    _, h2 = scipy.signal.freqs(b=[1/Q2], a=[1, 1 / Q2, 1], worN=w)        
    w_bw = w[ np.abs(h1 * h2) > 1/np.sqrt(2) ]
    bw = np.max(w_bw) - np.min(w_bw)
    Qeff = 1 / bw
    print(f"{Q1=} {Q2=} Qeff={np.round(Qeff, 2)}")
    df.loc[i] = [Q1, Q2, Qeff]
    i += 1

# fit a simple model
p0=(1,1)
def f(x, a, b):
    return np.sum(x**a, axis=1)**b

xdata=df[['Q1', 'Q2']]
popt, pcov = scipy.optimize.curve_fit(f, xdata=xdata, ydata=df['Qeff'], p0=p0)
df['Qpred'] = f(xdata, *popt)
plt.figure()
plt.scatter(df['Qeff'], df['Qpred'])
plt.title('Predicted vs actual Q')


#### example 2: controlling a coupled resonator system

# aside from these, use the same parameters as above
Q1 = 40
Q2 = 20
Qeff = (Q1**1.577 + Q2**1.577)**0.635
tau_eff = Qeff / np.pi / f0
filt1 = scipy.signal.bilinear(b=[w0**2 / Q1], a=[1, w0 / Q1, w0**2], fs=fs)
filt2 = scipy.signal.bilinear(b=[w0**2 / Q2], a=[1, w0 / Q2, w0**2], fs=fs)

t_high_to_low = int(-tau_eff * np.log(1 - (v_h - v_l) / (v_max + v_h)) * fs)
t_low_to_high = int(-tau_eff * np.log(1 - (v_h - v_l) / (v_max - v_l)) * fs)
predistortion = modulation.copy()

for i in i_high_to_low:
    j = i + t_high_to_low
    predistortion[i:j] = -v_max

for i in i_low_to_high:
    j = i + t_low_to_high
    predistortion[i:j] = v_max

y = scipy.signal.lfilter(*filt1, carrier * modulation)
y2 = scipy.signal.lfilter(*filt2, y)

y_pre = scipy.signal.lfilter(*filt1, carrier * predistortion)
y_pre2 = scipy.signal.lfilter(*filt2, y_pre)

t_usec = t * 1e6
t_usec = t_usec - 87.5
fig, axs = plt.subplots(2, 3, sharex='all', sharey='col')
axs[0, 0].plot(t_usec, modulation)
axs[0, 0].set_title("Modulation")
axs[0, 1].plot(t_usec, modulation * carrier)
axs[0, 1].plot(t_usec, modulation)
axs[0, 1].set_title("Modulated input")
#axs[0, 2].plot(t_usec, y)
axs[0, 2].plot(t_usec, y2)
axs[0, 2].set_title("Resonance 2 output")

axs[1, 0].plot(t_usec, predistortion)
axs[1, 1].plot(t_usec, predistortion * carrier)
axs[1, 1].plot(t_usec, predistortion)
#axs[1, 2].plot(t_usec, y_pre)
axs[1, 2].plot(t_usec, y_pre2)
axs[1, 2].set_xlim([0, 100])
axs[1, 2].set_ylim([-1, 1])

fig.supxlabel("time (microseconds)")
fig.supylabel("signal (arb)")
plt.show()
