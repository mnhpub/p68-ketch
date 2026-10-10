import {useReducer, useState} from 'react';
import PilotingConsole from './piloting/PilotingConsole';
import {initialPilotState, pilotReducer, stationName, type Station} from './aggregates/pilot';
import './piloting/piloting.css';

// Concept screen for the two-crew helm. The demo bar is for review only. In a
// real system, a network fault is an alarm from the equipment, not a button.
export default function PilotingView() {
  const [state, dispatch] = useReducer(pilotReducer, initialPilotState);
  const [station, setStation] = useState<Station>('bridge');

  return (
    <section className="piloting">
      <div className="explorer-head">
        <span className="eyebrow">HELM / TWO-CREW CONCEPT</span>
        <h1>Piloting controls.</h1>
        <p>
          Two helm stations, on the bridge and in the outdoor pilot house, share one control state. Only one station holds control at a time. Changes that move the
          vessel or change control need a press-and-hold, and some need the other station to confirm.
        </p>
      </div>

      <div className="concept-banner">
        CONCEPT INTERFACE. NOT CONNECTED TO ANY VESSEL SYSTEM. NO COMMANDS ARE SENT TO EQUIPMENT.
      </div>

      <div className="demo-bar">
        <span>Viewing as</span>
        {(['bridge', 'pilothouse'] as Station[]).map((s) => (
          <button key={s} type="button" className={station === s ? 'active' : ''} onClick={() => setStation(s)}>
            {stationName(s)}
          </button>
        ))}
        <button
          type="button"
          className={state.networkFault ? 'active' : ''}
          onClick={() => dispatch({type: 'networkFault', on: !state.networkFault})}
        >
          {state.networkFault ? 'Restore primary network' : 'Simulate primary network loss'}
        </button>
        <button type="button" onClick={() => dispatch({type: 'reset'})}>Reset demo</button>
      </div>

      <PilotingConsole station={station} state={state} dispatch={dispatch} />
    </section>
  );
}
