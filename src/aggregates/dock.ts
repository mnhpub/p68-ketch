// Environment model for the auto-dock program. Sensor inputs are wind, current and sea state,
// with the vessel heading. The model turns them into a lateral disturbance, in percent of full
// booster force, that the boosters must cancel to hold the vessel's position while docking.
// The gains are placeholders for review. They are not calibrated to any hull.

export type Environment = {
  windKn: number; // true wind speed, knots
  windFromDeg: number; // direction the wind blows from, degrees true
  currentKn: number; // current speed, knots
  currentSetDeg: number; // direction the current sets toward, degrees true
  waveM: number; // significant wave height, metres
  headingDeg: number; // vessel heading, degrees true
};

export const initialEnvironment: Environment = {
  windKn: 0,
  windFromDeg: 0,
  currentKn: 0,
  currentSetDeg: 0,
  waveM: 0,
  headingDeg: 0,
};

// Lateral disturbance gains, in percent of full booster force.
export const WIND_GAIN = 0.1; // per knot squared, scaled by the sine of the relative wind angle
export const CURRENT_GAIN = 10; // per knot of current, scaled by the sine of the set relative to heading
export const WAVE_GAIN = 5; // per metre of significant wave height, following the wind

const rad = (deg: number) => (deg * Math.PI) / 180;
export const normalise = (deg: number) => ((((deg + 180) % 360) + 360) % 360) - 180;

// Lateral disturbance in percent of full booster force. Positive pushes the vessel to starboard.
export function lateralDisturbance(env: Environment): number {
  // Relative wind: positive when the wind comes from starboard. A wind from port pushes to starboard.
  const relWind = rad(normalise(env.windFromDeg - env.headingDeg));
  const windPush = -Math.sin(relWind) * env.windKn * env.windKn * WIND_GAIN;

  // Current drift: the component of the set that runs to starboard of the heading.
  const currentDrift = Math.sin(rad(env.currentSetDeg - env.headingDeg)) * env.currentKn * CURRENT_GAIN;

  // Waves run with the wind, so they add a sea push in the same direction as the wind push.
  const wavePush = -Math.sin(relWind) * env.waveM * WAVE_GAIN;

  return windPush + currentDrift + wavePush;
}
