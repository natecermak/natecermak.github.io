# Engineering backscatter

Backscatter is a name for the magnetic field induced by current flow in the circuit, which is itself induced by changes in an external magnetic field ([Faraday's law](https://en.wikipedia.org/wiki/Faraday%27s_law_of_induction)).

This basic process looks like this:
1. A changing magnetic field generates a voltage inside an inductor.
2. Voltage causes some current to flow (this depends both on the inductor and the circuit itself).
3. Current flow through the inductor creates a magnetic field. This is the backscattered magnetic field.

An important result of this process is that by changing the circuit properties dynamically, we can change the magnitude and phase of the backscattered magnetic field in order to send a signal. This is backscatter-based communication.

## Backscatter signal limitations
Due to Lenz's law, the voltage induced in the inductor will generate a current that opposes the change of magnetic field. Therefore, its not possible to passively backscatter a signal that is in phase with the driving signal, only one that is out of phase with it. More precisely, one can backscatter up to +-90 degrees from antiphase with the driving magnetic field.

## Backscattering while power harvesting (impedance-matched scenario)
Oftentimes, the inductor's current is being used to power the circuit. In that case, one often employs impedance matching to optimize power delivery to the circuit. This can be thought of as changing the load circuit's real part by adding a reactive load in parallel, and then adding a series reactance to cancel out the reactance.

## Series load


## Parallel load
By adding a parallel load, we can change the amount of current that flows through the coil and its phase.
For the following circuit, the impedance seen by the voltage source at the resonant frequency is
$$
Z_{total} = \frac{|Z_L|^2 + 2*Re(Z_L)*Z_{par}}{Z_{par} + {Z_L}^*}$
$$

And more specifically, the relative change in current, as compared to no added load (Z=infinity) is
$$
M = \frac{ I_{with Z_{par}}} }{ I_{without Z_{par}}} } = \frac{Z_{Z_{par}=\infinity}} {Z_{total}} = \frac{2*Re(Z_L)}{Z_{total}}
$$
Solving this for $Z$ as a function of $M$ yields
$$
Z = \frac{{Z_L}^* + \frac{|Z_L|^2}{2*Re(Z_L)}M }{M-1}
$$

### Example
Let's take the case of a 75uH inductor with 13 ohm resistance at 1 MHz (Q~36.25), matched to power a 500 ohm load. This leads to a parallel capacitance of 1.948nF and series capacitance of 407pF.

Suppose we want to generate a constellation of QAM values at:
1+0j: Z = open-circuit
0+0j:l
0.5+0j
0.5+0.5j
0.5-0.5j



## Backscatter switching dynamics
TBD