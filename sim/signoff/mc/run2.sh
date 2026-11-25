#!/bin/bash
cd "$(dirname "$0")"
( python3 mcsim2.py 1 150 tt; python3 mcsim2.py 0 50 ss; python3 mcsim2.py 0 50 sf ) > lane2A.log 2>&1 &
( python3 mcsim2.py 150 300 tt; python3 mcsim2.py 0 50 ff; python3 mcsim2.py 0 50 fs ) > lane2B.log 2>&1 &
wait
