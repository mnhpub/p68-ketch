import type {Dispatch, ReactNode} from 'react';
import {canCommand, otherStation, RUDDER_LIMIT, stationName, type PilotAction, type PilotState, type Shaft, type Side, type Station} from './pilotState';
import {HoldButton, Slider} from './controls';

type Props = {
  station: Station;
  state: PilotState;
  dispatch: Dispatch<PilotAction>;
};

type Subsystem = 'shaft' | 'steering' | 'thrusters';
type PathName = 'network' | 'hardwired' | 'local';

const PATHS: PathName[] = ['network', 'hardwired', 'local'];
const PATH_LABEL: Record<PathName, string> = {network: 'Network', hardwired: 'Hardwired', local: 'Local manual'};

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
  const rudderNudge = (delta: number) => dispatch({type: 'rudder', value: delta === 0 ? 0 : state.rudder + delta, by: station});

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
            {state.reversion ? 'Manual reversion' : state.autopilot ? 'Autopilot' : 'Hand steering'}
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
            <button type="button" className="nudge" disabled={!live || state.autopilot} onClick={() => rudderNudge(-5)}>Port 5</button>
            <button type="button" className="nudge" disabled={!live || state.autopilot} onClick={() => rudderNudge(-1)}>Port 1</button>
            <button type="button" className="nudge centre" disabled={!live || state.autopilot} onClick={() => rudderNudge(0)}>Centre</button>
            <button type="button" className="nudge" disabled={!live || state.autopilot} onClick={() => rudderNudge(1)}>Stbd 1</button>
            <button type="button" className="nudge" disabled={!live || state.autopilot} onClick={() => rudderNudge(5)}>Stbd 5</button>
          </div>

          <div className="steer-modes">
            {!state.autopilot ? (
              <HoldButton
                label="Engage autopilot"
                disabled={!live || state.reversion}
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
                disabled={!live}
                onChange={(v) => dispatch({type: 'thrust', side, value: v, by: station})}
              />
            </div>
          ))}
          <PathTable subsystem="thrusters" state={state} />
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
