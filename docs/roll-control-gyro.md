# Roll control: isolation, damping, and gyro stabilisation

Status: sizing and technology options. No equipment is chosen. Inputs are the final size, the 1,350 t displacement target and the GM target of 1.0 m, all from `docs/archive/68m/hull-dynamics-first-pass.md` and `docs/archive/68m/hull-size-final.md`. Placeholders are marked.

## Why roll control is needed

At GM 1.0 m the roll period is 9.7 s, clear of the 5 to 8 s sea periods, so the hull is not resonant. It still rolls, and the roll amplitude in the design sea sets crew comfort, equipment loads and the shelf life of the fittings. Three measures reduce it, in order of preference: passive damping, isolation of the sensitive equipment, and active stabilisation.

## Step 1: Roll inertia and stiffness

- Roll inertia: I = Δ × k², with k = 0.4 × B = 4.84 m. I = 1.35 × 10⁶ × 4.84² = **3.16 × 10⁷ kg·m²**
- Roll stiffness: K = Δ × g × GM = 1.35 × 10⁶ × 9.81 × 1.0 = **1.32 × 10⁷ N·m/rad**
- Natural roll frequency: ω = √(K / I) = 0.648 rad/s, a period of 9.7 s, which matches the earlier block.

## Step 2: Damping needed

A roll damping ratio ζ gives a damping coefficient c = 2ζ √(I × K). At the design roll amplitude of 5° and period 9.7 s, the peak roll rate is φ̇ = ω × φ₀ = 0.648 × 0.0873 = 0.0566 rad/s.

| Damping ratio ζ | Coefficient c (N·m·s/rad) | Peak damping torque at 5° |
|---|---|---|
| 0.05 | 2.05 × 10⁶ | **116 kN·m** |
| 0.10 | 4.09 × 10⁶ | **231 kN·m** |

A damping ratio of 0.10 is a reasonable first target for a passage-making yacht, and it is a placeholder for the owner to confirm.

## Step 3: Passive measures first

- **Bilge keels** add roll damping at low cost. Their damping is usually a few percent of critical, and the figure has to come from a model test or a published method for this hull. It is not assumed here.
- **Roll damping tanks** (free-surface or U-tube tanks) add damping without power. They take internal volume and weight low in the hull, so they are a candidate for the Tank level, but they compete with the batteries and the tender stowage for space.

Passive damping alone may reach ζ 0.05. The gap to 0.10 is the job for an active system.

## Step 4: Gyro stabilisation

A gyro stabiliser is a spinning rotor on a gimbal, precessed by a motor to produce a torque about the roll axis that opposes the roll. Required torque is T = H × ω_p, where H is the rotor's angular momentum and ω_p the precession rate.

With the 231 kN·m peak torque at ζ 0.10 and a precession rate of 0.2 rad/s (placeholder, a practical limit on the gimbal):

- **Angular momentum: H = T / ω_p = 231 × 10³ / 0.2 = 1.15 × 10⁶ kg·m²/s**
- With a 500 kg·m² rotor (placeholder), the spin speed is Ω = H / I_rotor = 2,300 rad/s, about 22,000 rpm.

A faster precession rate needs less angular momentum, so the rotor is smaller but the gimbal drive works harder. A rate of 0.4 rad/s halves H to 5.75 × 10⁵ kg·m²/s. The trade-off is set by the gimbal drive and the rotor mass, and both are open.

### What a gyro stabiliser does not do

- It damps roll. It does not hold a heel. Sustained heel from the wind is handled by the sail plan and the reefing, not the gyro.
- It works best in beam seas. Its effect is smaller on the other headings.
- It needs power continuously while running, which adds to the energy budget. The power draw is not yet calculated, and it must be added to `weights/energy-budget.json` once the unit is chosen.

## Step 5: Technology options

| Option | Principle | Strengths | Weaknesses |
|---|---|---|---|
| Flywheel gyro stabiliser | High-speed rotor on a motor-driven gimbal | Works at low speed and at rest; no appendages in the water | Heavy; continuous power; the rotor needs containment and balance checks |
| Fin stabiliser (active) | Hydrofoil fins extended from the hull, angled to produce lift | Effective at speed; lower mass for the same damping | Needs forward speed; fins in the water add drag and a hull penetration; fin mechanism needs maintenance |
| Passive tanks | Water sloshing in a tank out of phase with the roll | No power; no moving parts beyond the water | Only effective near the tank's tuned frequency; takes internal volume |
| Bilge keels | Appendages that add viscous roll damping | Lowest cost; no power | Modest damping; adds drag |

For a vessel that spends time at anchor and in harbour, the gyro is the better active choice, because fins do nothing at rest. For a vessel that cruises at speed, fins are lighter for the same damping. The owner's use profile decides which governs.

## Step 6: Isolation for the plant

The generation plant is the main source of vibration on board. For a genset running at 600 rpm (10 Hz), with mounts to isolate 90% of the force:

- Mount natural frequency: f_n = f / r, with r = √(1 + 1/T), gives **3.0 Hz** at 90% isolation and **2.2 Hz** at 95%.
- Static deflection: δ = g / (2π f_n)², giving **27 mm** at 90% and **52 mm** at 95%.

At 1,000 rpm (17 Hz) the mounts stiffen to 5.0 Hz at 90% isolation, with 10 mm deflection. Low-speed running is therefore easier to isolate, because the forcing frequency is lower, and the deflection is larger. The mount design must allow the deflection without contacting the structure, and the exhaust and fuel connections must allow for it.

## Step 7: Damping for the plant

Mounts also need damping, to stop the resonance at the mount's natural frequency being excited during start and stop, when the engine passes through its speed range. A viscous or elastomeric mount with a damping ratio of 0.1 to 0.2 is typical (placeholder). The genset start and stop sequences should pass through the mount resonance quickly.

## Open decisions

1. The owner's use profile: anchorage and harbour, or passage. This sets gyro versus fins.
2. The damping target, ζ. The 0.10 used here is a placeholder.
3. Rotor mass and spin speed, from the gyro supplier. The 500 kg·m² rotor is a placeholder.
4. Power draw of the gyro, to add to the energy budget.
5. Mass and height of the gyro and any tanks, to add to the weight register and check against the KG limit of 5.39 m.
6. Genset mount design: stiffness, damping and the deflection allowance at the exhaust and fuel connections.
