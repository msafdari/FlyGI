import sys, importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT/'src'))
spec = importlib.util.spec_from_file_location('b', ROOT/'scripts/evaluate_random_baseline.py')
b = importlib.util.module_from_spec(spec); sys.modules['b']=b; spec.loader.exec_module(b)
import numpy as np
from flygi.encoding.features import latest_grid
rt = b.load_arc_runtime()
g = b.discover_games(rt, ROOT/'environment_files', ['sb26'])[0]
arc = b._new_offline_arcade(rt, ROOT/'environment_files')
sc = arc.open_scorecard(tags=['diag'], opaque={})
seed,_ = b.derived_run_seeds(0, g.game_id)
env = arc.make(g.game_id, seed=seed, scorecard_id=sc, save_recording=False, include_frame_data=False)
def act(i, payload=None):
    a = rt.GameAction.from_id(i)
    if payload: a.set_data(payload)
    env.step(a, data=payload or {}, reasoning=None)
    return env.observation_space
def st():
    fr = env.observation_space
    return fr.levels_completed, str(fr.state)
steps = json.load(open('/tmp/fap_ext/sb26/p11.json'))
for s in steps:
    if s['action']==6: act(6, {'x':s['x'],'y':s['y']})
    else: act(s['action'])
print('after replay:', st())

BTN = {'f':(6,58),'b':(13,58),'c':(20,58),'8':(27,58),'9':(34,58),'e':(41,58),'H8':(48,58),'H9':(55,58)}
RS = [(22,26),(28,26),(34,26),(40,26)]
SS = [(22,40),(28,40),(34,40),(40,40)]
def attempt(name, rootfill, subfill):
    for btn, slot in rootfill:
        act(6, {'x':BTN[btn][0],'y':BTN[btn][1]})
        act(6, {'x':RS[slot][0],'y':RS[slot][1]})
    for btn, slot in subfill:
        act(6, {'x':BTN[btn][0],'y':BTN[btn][1]})
        act(6, {'x':SS[slot][0],'y':SS[slot][1]})
    act(5)
    sc_, state = st()
    print(name, '->', sc_, state)
    if sc_>=8 or 'WIN' in state:
        print('SOLVED', name); json.dump({'winner':name}, open('/tmp/fap_ext/sb26/level8_winner.json','w')); sys.exit(0)
    act(0)
    g2 = np.asarray(latest_grid(env.observation_space), dtype=np.int16)
    print('  reset ->', st(), 'timer-remaining', int((g2[53]==2).sum()))

attempt('cand1 root=[8,b,c,H9] sub=[9,e,f,H8]', [('8',0),('b',1),('c',2),('H9',3)], [('9',0),('e',1),('f',2),('H8',3)])
attempt('cand2 root=[H9,9,e,f] sub=[8,b,c,H8]', [('H9',0),('9',1),('e',2),('f',3)], [('8',0),('b',1),('c',2),('H8',3)])
attempt('cand3 root=[8,H9,e,f] sub=[b,c,9,H8]', [('8',0),('H9',1),('e',2),('f',3)], [('b',0),('c',1),('9',2),('H8',3)])
attempt('cand4 root=[8,b,H9,f] sub=[c,9,e,H8]', [('8',0),('b',1),('H9',2),('f',3)], [('c',0),('9',1),('e',2),('H8',3)])
