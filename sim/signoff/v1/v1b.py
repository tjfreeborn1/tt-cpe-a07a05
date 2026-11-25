"""V1b: single-branch resistor tolerance sweep (+-5, 10, 15 %) using v1sim's verified transforms."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v1sim
part, n = int(sys.argv[1]), int(sys.argv[2])
S = [dict(name=f'br_{b}_{k}', br=b, kb=k) for b in v1sim.BR for k in (0.85, 0.9, 0.95, 1.05, 1.1, 1.15)]
for sc in S[part::n]:
    if not os.path.exists(f'{v1sim.OUT}/{sc["name"]}.npz'): v1sim.run(sc)
