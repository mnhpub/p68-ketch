import type {Dispatch, ReactNode} from 'react';
import {BOOSTER_PERCENT_PER_ROTATION, canCommand, HELM_DEGREES_PER_ROTATION, otherStation, RUDDER_LIMIT, stationName, type PilotState, type Shaft, type Side, type Station} from '../aggregates/pilot';
import type {PilotAction} from '../commands/pilot';
import {HoldButton, Slider} from './controls';
import {lateralDisturbance, type Environment} from '../aggregates/dock';
import {checkKey, checklistComplete, DEMO_ROUTE, headingError, PILOT_CHECKLISTS, type ChecklistId} from '../aggregates/underway';

type Props = {
  station: Station;
  state: PilotState;
  dispatch: Dispatch<PilotAction>;
};

type Subsystem = 'shaft' | 'steering' | 'thrusters';
type PathName = 'network' | 'hardwired' | 'local';

const PATHS: PathName[] = ['network', 'hardwired', 'local'];
const PATH_LABEL: Record<PathName, string> = {network: 'Network', hardwired: 'Hardwired', local: 'Local manual'};

const ENV_FIELDS: {key: keyof Environment; label: string; unit: string; min: number; max: number; step: number}[] = [
  {key: 'windKn', label: 'Wind speed', unit: ' kn', min: 0, max: 60, step: 1},
  {key: 'windFromDeg', label: 'Wind from', unit: '°', min: 0, max: 359, step: 5},
  {key: 'currentKn', label: 'Current speed', unit: ' kn', min: 0, max: 5, step: 0.5},
  {key: 'currentSetDeg', label: 'Current sets to', unit: '°', min: 0, max: 359, step: 5},
  {key: 'waveM', label: 'Wave height', unit: ' m', min: 0, max: 6, step: 0.5},
  {key: 'headingDeg', label: 'Heading', unit: '°', min: 0, max: 359, step: 5},
];
const SAIL_LABEL: Record<PilotState['sails'], string> = {
  retracted: 'Retracted',
  deployed: 'Deployed',
  maintenance: 'Maintenance lock',
};

// Which path is carrying commands for a subsystem, given the current faults.
function activePath(sub: Subsystem, state: PilotState): PathName {
  if (sub === 'steering' && state.reversion) return 'local';
  return state.networkFault ? 'hardwired' : 'network';
}

function pathStatus(path: PathName, state: PilotState, sub: Subsystem): 'ACTIVE' | 'STANDBY' | 'FAILED' {
  if (path === 'network' && state.networkFault) return 'FAILED';
  return activePath(sub, state) === path ? 'ACTIVE' : 'STANDBY';
}

function PathTable({subsystem, state}: {subsystem: Subsystem; state: PilotState}) {
  return (
    <div className="paths">
      {PATHS.map((p) => {
        const status = pathStatus(p, state, subsystem);
        return (
          <span key={p} className={`path ${status.toLowerCase()}`}>
            <b>{PATH_LABEL[p]}</b>
            {status}
          </span>
        );
      })}
    </div>
  );
}

function Card({title, children, className = ''}: {title: string; children: ReactNode; className?: string}) {
  return (
    <section className={`card ${className}`}>
      <h3>{title}</h3>
      {children}
    </section>
  );
}

export default function PilotingConsole({station, state, dispatch}: Props) {
  const holder = state.authority;
  const mine = holder === station;
  const live = canCommand(state, station);
  const other = otherStation(station);
  const alarms = state.log.filter((l) => l.level === 'alarm').length;
  const shaftName: Record<Shaft, string> = {port: 'Port shaft', stbd: 'Starboard shaft'};
  const sideName: Record<Side, string> = {bow: 'Bow thruster', stern: 'Stern thruster'};

  const rudderText =
    state.rudder === 0 ? 'Centred' : state.rudder < 0 ? `Port ${-state.rudder}°` : `Starboard ${state.rudder}°`;
  const helmTurn = (turns: number) => dispatch({type: 'helm', turns, by: station});

  return (
    <div className="console">
      <header className="console-head">
        <div>
          <span className="eyebrow">Helm · {stationName(station)}</span>
          <h2>{mine ? 'You hold control' : `${stationName(holder)} holds control`}</h2>
        </div>
        <div className="head-status">
          <span className={`pill ${state.estop ? 'alarm' : ''}`}>{state.estop ? 'Emergency stop active' : 'Propulsion enabled'}</span>
          <span className="pill">
            {state.reversion ? 'Manual reversion' : state.autopilot ? 'Autopilot' : state.dock ? 'Dock mode' : state.underway ? 'Underway' : 'Hand steering'}
          </span>
          <span className={`pill ${state.networkFault ? 'warn' : ''}`}>
            {state.networkFault ? 'Primary network lost' : 'Primary network OK'}
          </span>
          <span className={`pill ${alarms ? 'alarm' : ''}`}>{alarms} alarm{alarms === 1 ? '' : 's'} logged</span>
        </div>
      </header>

      <div className="authority">
        {mine && state.pendingRequest && (
          <>
            <span>{stationName(state.pendingRequest)} requests control.</span>
            <button type="button" className="btn primary" onClick={() => dispatch({type: 'accept', by: station})}>
              Hand over control
            </button>
          </>
        )}
        {mine && !state.pendingRequest && <span>Control is held here. {stationName(other)} can request it.</span>}
        {!mine && state.pendingRequest === station && (
          <>
            <span>Request sent. Waiting for {stationName(holder)} to hand over.</span>
            <button type="button" className="btn" onClick={() => dispatch({type: 'cancelRequest'})}>
              Cancel request
            </button>
          </>
        )}
        {!mine && state.pendingRequest !== station && (
          <>
            <span>{stationName(holder)} holds control. Controls here are locked.</span>
            <button type="button" className="btn primary" onClick={() => dispatch({type: 'request', by: station})}>
              Request control
            </button>
          </>
        )}
      </div>

      <div className="grid">
        <Card title="Propulsion" className="propulsion">
          <div className="shafts">
            {(['port', 'stbd'] as Shaft[]).map((s) => (
              <div key={s} className="shaft">
                <div className="shaft-name">{shaftName[s]}</div>
                <div className="shaft-value">{state.demand[s]}%</div>
                <Slider
                  label={`${shaftName[s]} demand`}
                  value={state.demand[s]}
                  min={0}
                  max={100}
                  step={5}
                  detents={[0, 25, 50, 75, 100]}
                  orientation="vertical"
                  disabled={!live}
                  onChange={(v) => dispatch({type: 'demand', shaft: s, value: v, by: station})}
                />
              </div>
            ))}
          </div>
          <PathTable subsystem="shaft" state={state} />
        </Card>

        <Card title="Steering">
          <div className="rudder-read">
            <span>Rudder</span>
            <b>{rudderText}</b>
          </div>
          <div className="rudder-bar">
            <span className="rudder-pos" style={{left: `${((state.rudder + RUDDER_LIMIT) / (RUDDER_LIMIT * 2)) * 100}%`}} />
            <span className="rudder-mid" />
          </div>
          <div className="nudges">
            <button type="button" className="nudge" disabled={!live || state.autopilot} onClick={() => helmTurn(-5)}>Port 5 turns</button>
            <button type="button" className="nudge" disabled={!live || state.autopilot} onClick={() => helmTurn(-1)}>Port 1 turn</button>
            <button type="button" className="nudge centre" disabled={!live || state.autopilot} onClick={() => dispatch({type: 'centre', by: station})}>Centre</button>
            <button type="button" className="nudge" disabled={!live || state.autopilot} onClick={() => helmTurn(1)}>Stbd 1 turn</button>
            <button type="button" className="nudge" disabled={!live || state.autopilot} onClick={() => helmTurn(5)}>Stbd 5 turns</button>
          </div>
          <div className="helm-ratio">1 helm turn = {HELM_DEGREES_PER_ROTATION}° rudder</div>

          <div className="steer-modes">
            {!state.autopilot ? (
              <HoldButton
                label="Engage autopilot"
                disabled={!live || state.reversion || state.dock}
                onHold={() => dispatch({type: 'autopilot', on: true, by: station})}
              />
            ) : (
              <HoldButton
                label="Disengage autopilot"
                holdMs={1000}
                disabled={!live}
                onHold={() => dispatch({type: 'autopilot', on: false, by: station})}
              />
            )}

            {!state.dock ? (
              <HoldButton
                label="Engage dock mode"
                disabled={!live || state.autopilot || state.underway || state.sails !== 'retracted' || !checklistComplete('dock-approach', state.checks)}
                onHold={() => dispatch({type: 'dock', on: true, by: station})}
              />
            ) : (
              <HoldButton
                label="Disengage dock mode"
                holdMs={1000}
                disabled={!live}
                onHold={() => dispatch({type: 'dock', on: false, by: station})}
              />
            )}
            {state.dock && (
              <p className="note">
                Dock mode. Each helm turn adds {BOOSTER_PERCENT_PER_ROTATION}% bow and stern booster assist. Thruster sliders are locked.
              </p>
            )}

            {state.reversion && <p className="note">Manual reversion active. Steering is by local gear. Autopilot is locked out.</p>}
            {!state.reversion && state.reversionPending === null && (
              <button
                type="button"
                className="btn"
                disabled={!mine || state.estop}
                onClick={() => dispatch({type: 'reversionRequest', by: station})}
              >
                Request manual reversion
              </button>
            )}
            {!state.reversion && state.reversionPending === station && (
              <>
                <p className="note">Reversion requested. Waiting for {stationName(other)} to confirm.</p>
                <button type="button" className="btn" onClick={() => dispatch({type: 'reversionCancel'})}>
                  Cancel
                </button>
              </>
            )}
            {!state.reversion && state.reversionPending === other && (
              <>
                <p className="note">{stationName(other)} requests manual steering reversion. Confirm only if the local gear is ready.</p>
                <HoldButton
                  label="Confirm manual reversion"
                  holdMs={2000}
                  onHold={() => dispatch({type: 'reversionConfirm', by: station})}
                />
              </>
            )}
          </div>
          <PathTable subsystem="steering" state={state} />
        </Card>

        <Card title="Thrusters">
          {(['bow', 'stern'] as Side[]).map((side) => (
            <div key={side} className="thruster">
              <div className="thruster-head">
                <span>{sideName[side]}</span>
                <b>{state.thrust[side] === 0 ? 'Off' : `${Math.abs(state.thrust[side])}% ${state.thrust[side] < 0 ? 'port' : 'stbd'}`}</b>
              </div>
              <Slider
                label={`${sideName[side]} force`}
                value={state.thrust[side]}
                min={-100}
                max={100}
                step={5}
                detents={[-100, -50, 0, 50, 100]}
                orientation="horizontal"
                disabled={!live || state.dock}
                onChange={(v) => dispatch({type: 'thrust', side, value: v, by: station})}
              />
            </div>
          ))}
          {state.dock && <p className="note">Dock assist from rudder {state.rudder}°. Boosters follow the helm and the environment.</p>}
          <PathTable subsystem="thrusters" state={state} />
        </Card>

        <Card title="Environment">
          <div className="env-grid">
            {ENV_FIELDS.map((f) => (
              <div key={f.key} className="env-row">
                <div className="thruster-head">
                  <span>{f.label}</span>
                  <b>{state.environment[f.key]}{f.unit}</b>
                </div>
                <Slider
                  label={f.label}
                  value={state.environment[f.key]}
                  min={f.min}
                  max={f.max}
                  step={f.step}
                  detents={[]}
                  orientation="horizontal"
                  onChange={(v) => dispatch({type: 'environment', patch: {[f.key]: v}})}
                />
              </div>
            ))}
          </div>
          <div className="env-disturbance">
            Lateral disturbance {Math.round(lateralDisturbance(state.environment))}% of booster force.
            {state.dock ? ' Auto-dock is compensating.' : ' Applied in dock mode.'}
          </div>
        </Card>

        <Card title="Sails">
          <div className="thruster-head">
            <span>Sail state</span>
            <b>{SAIL_LABEL[state.sails]}</b>
          </div>
          <div className="steer-modes">
            <HoldButton
              label="Deploy sails"
              holdMs={2000}
              disabled={!live || state.sails !== 'retracted' || state.dock}
              onHold={() => dispatch({type: 'sails', mode: 'deploy', by: station})}
            />
            <HoldButton
              label="Retract sails"
              holdMs={2000}
              disabled={state.sails !== 'deployed'}
              onHold={() => dispatch({type: 'sails', mode: 'retract', by: station})}
            />
            {state.sails !== 'maintenance' ? (
              <HoldButton
                label="Enter sail maintenance"
                holdMs={2000}
                disabled={!live || state.sails !== 'retracted'}
                onHold={() => dispatch({type: 'sails', mode: 'maintenance', by: station})}
              />
            ) : (
              <HoldButton
                label="Release maintenance lock"
                holdMs={2000}
                disabled={!live}
                onHold={() => dispatch({type: 'sails', mode: 'endMaintenance', by: station})}
              />
            )}
          </div>
          {state.sails === 'deployed' && <p className="note">Sails deployed. Dock mode needs sails retracted.</p>}
          {state.sails === 'maintenance' && <p className="note">Sails locked for maintenance. Deploy is locked out.</p>}
          {state.sails !== 'deployed' && <p className="note">Retract can be held from either station, even during emergency stop.</p>}
        </Card>

        <Card title="Navigation">
          <div className="thruster-head">
            <span>Heading</span>
            <b>{state.environment.headingDeg}°</b>
          </div>
          {state.route.length === 0 ? (
            <p className="note">No route loaded.</p>
          ) : state.activeWaypoint >= state.route.length ? (
            <p className="note">Route complete.</p>
          ) : (
            <>
              <div className="thruster-head">
                <span>Next waypoint</span>
                <b>{state.route[state.activeWaypoint].name}</b>
              </div>
              <div className="thruster-head">
                <span>Course and distance</span>
                <b>{state.route[state.activeWaypoint].bearingDeg}° · {state.route[state.activeWaypoint].distanceNm} nm</b>
              </div>
              <div className="thruster-head">
                <span>Heading error</span>
                <b>
                  {Math.round(headingError(state.route[state.activeWaypoint].bearingDeg, state.environment.headingDeg))}°
                </b>
              </div>
            </>
          )}
          <div className="steer-modes">
            <button
              type="button"
              className="btn"
              disabled={!mine || state.underway || state.estop}
              onClick={() => dispatch({type: 'route', waypoints: DEMO_ROUTE, by: station})}
            >
              Load demo route
            </button>
            {!state.underway ? (
              <HoldButton
                label="Engage underway"
                disabled={!live || state.dock || state.route.length === 0 || !checklistComplete('underway-departure', state.checks)}
                onHold={() => dispatch({type: 'underway', on: true, by: station})}
              />
            ) : (
              <HoldButton
                label="Disengage underway"
                holdMs={1000}
                disabled={!live}
                onHold={() => dispatch({type: 'underway', on: false, by: station})}
              />
            )}
            {state.underway && state.waypointPending === null && (
              <button
                type="button"
                className="btn"
                disabled={!mine || state.estop}
                onClick={() => dispatch({type: 'waypointRequest', by: station})}
              >
                Request waypoint confirmation
              </button>
            )}
            {state.underway && state.waypointPending === station && (
              <p className="note">Waypoint reached. Waiting for {stationName(other)} to confirm.</p>
            )}
            {state.underway && state.waypointPending === other && (
              <>
                <p className="note">{stationName(other)} reports waypoint reached. Confirm only if the position matches.</p>
                <HoldButton
                  label="Confirm waypoint"
                  holdMs={2000}
                  disabled={state.estop}
                  onHold={() => dispatch({type: 'waypointConfirm', by: station})}
                />
              </>
            )}
          </div>
        </Card>

        <Card title="Checklists">
          {(Object.keys(PILOT_CHECKLISTS) as ChecklistId[]).map((list) => {
            const cl = PILOT_CHECKLISTS[list];
            const modeOn = list === 'underway-departure' ? state.underway : state.dock;
            return (
              <div key={list} className="checklist">
                <div className="thruster-head">
                  <span>{cl.title}</span>
                  <b>{checklistComplete(list, state.checks) ? 'Complete' : 'Open'}</b>
                </div>
                <p className="note">Draft. Not reviewed. Cannot engage {cl.mode} until the critical steps are ticked.</p>
                {cl.steps.map((step, i) => {
                  const done = !!state.checks[checkKey(list, i)];
                  return (
                    <button
                      key={i}
                      type="button"
                      className={`check-row ${done ? 'done' : ''}`}
                      aria-pressed={done}
                      disabled={modeOn}
                      onClick={() => dispatch({type: 'check', list, index: i, done: !done, by: station})}
                    >
                      <span className="check-box">{done ? '✓' : ''}</span>
                      <span>
                        {step.text}
                        {step.critical && <small> · Critical</small>}
                      </span>
                    </button>
                  );
                })}
              </div>
            );
          })}
        </Card>

        <Card title="Alarm and event log" className="status">
          <div className="log">
            {state.log.slice(-8).reverse().map((l) => (
              <div key={l.id} className={`log-row ${l.level}`}>{l.text}</div>
            ))}
          </div>
        </Card>
      </div>

      <footer className="estop-bar">
        <HoldButton
          label="Emergency stop"
          holdMs={2000}
          tone="danger"
          onHold={() => dispatch({type: 'estop', by: station})}
        />
        {state.estop && (
          <HoldButton
            label="Clear emergency stop"
            holdMs={2000}
            disabled={!mine}
            onHold={() => dispatch({type: 'clearEstop', by: station})}
          />
        )}
        {state.estop && !mine && <p className="note">Only the station holding control can clear an emergency stop.</p>}
      </footer>
    </div>
  );
}
