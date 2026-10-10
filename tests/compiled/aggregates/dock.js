"use strict";
// Environment model for the auto-dock program. Sensor inputs are wind, current and sea state,
// with the vessel heading. The model turns them into a lateral disturbance, in percent of full
// booster force, that the boosters must cancel to hold the vessel's position while docking.
// The gains are placeholders for review. They are not calibrated to any hull.
Object.defineProperty(exports, "__esModule", { value: true });
exports.normalise = exports.WAVE_GAIN = exports.CURRENT_GAIN = exports.WIND_GAIN = exports.initialEnvironment = void 0;
exports.lateralDisturbance = lateralDisturbance;
exports.initialEnvironment = {
    windKn: 0,
    windFromDeg: 0,
    currentKn: 0,
    currentSetDeg: 0,
    waveM: 0,
    headingDeg: 0,
};
// Lateral disturbance gains, in percent of full booster force.
exports.WIND_GAIN = 0.1; // per knot squared, scaled by the sine of the relative wind angle
exports.CURRENT_GAIN = 10; // per knot of current, scaled by the sine of the set relative to heading
exports.WAVE_GAIN = 5; // per metre of significant wave height, following the wind
const rad = (deg) => (deg * Math.PI) / 180;
const normalise = (deg) => ((((deg + 180) % 360) + 360) % 360) - 180;
exports.normalise = normalise;
// Lateral disturbance in percent of full booster force. Positive pushes the vessel to starboard.
function lateralDisturbance(env) {
    // Relative wind: positive when the wind comes from starboard. A wind from port pushes to starboard.
    const relWind = rad((0, exports.normalise)(env.windFromDeg - env.headingDeg));
    const windPush = -Math.sin(relWind) * env.windKn * env.windKn * exports.WIND_GAIN;
    // Current drift: the component of the set that runs to starboard of the heading.
    const currentDrift = Math.sin(rad(env.currentSetDeg - env.headingDeg)) * env.currentKn * exports.CURRENT_GAIN;
    // Waves run with the wind, so they add a sea push in the same direction as the wind push.
    const wavePush = -Math.sin(relWind) * env.waveM * exports.WAVE_GAIN;
    return windPush + currentDrift + wavePush;
}
