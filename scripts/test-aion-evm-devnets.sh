#!/usr/bin/env bash
set -Eeuo pipefail

# Local-only smoke test for the proposed AION Nova and AION Orbit EVM configs.
# This does NOT launch public networks or deploy the AION token.
NOVA_CHAIN_ID="${NOVA_CHAIN_ID:-71101}"
ORBIT_CHAIN_ID="${ORBIT_CHAIN_ID:-71102}"
NOVA_PORT="${NOVA_PORT:-18545}"
ORBIT_PORT="${ORBIT_PORT:-18546}"
NOVA_LOG="${NOVA_LOG:-/tmp/aion-nova-anvil.log}"
ORBIT_LOG="${ORBIT_LOG:-/tmp/aion-orbit-anvil.log}"

command -v anvil >/dev/null || { echo "ERROR: Foundry Anvil is required." >&2; exit 2; }
command -v cast >/dev/null || { echo "ERROR: Foundry Cast is required." >&2; exit 2; }
command -v curl >/dev/null || { echo "ERROR: curl is required." >&2; exit 2; }

nova_pid=""
orbit_pid=""
cleanup() {
  [[ -z "$nova_pid" ]] || kill "$nova_pid" 2>/dev/null || true
  [[ -z "$orbit_pid" ]] || kill "$orbit_pid" 2>/dev/null || true
}
trap cleanup EXIT

anvil --host 127.0.0.1 --port "$NOVA_PORT" --chain-id "$NOVA_CHAIN_ID" >"$NOVA_LOG" 2>&1 &
nova_pid=$!
anvil --host 127.0.0.1 --port "$ORBIT_PORT" --chain-id "$ORBIT_CHAIN_ID" >"$ORBIT_LOG" 2>&1 &
orbit_pid=$!

rpc_chain_id() {
  curl --fail --silent --show-error --max-time 2 \
    -H 'content-type: application/json' \
    --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' \
    "http://127.0.0.1:$1" | python -c 'import json,sys; print(int(json.load(sys.stdin)["result"],16))'
}

wait_for_rpc() {
  local port="$1" expected="$2" name="$3" actual=""
  for _ in $(seq 1 30); do
    if actual="$(rpc_chain_id "$port" 2>/dev/null)" && [[ "$actual" == "$expected" ]]; then
      printf 'PASS: %s RPC reachable on localhost:%s; chainId=%s\n' "$name" "$port" "$actual"
      return 0
    fi
    sleep 1
  done
  echo "FAIL: $name RPC did not report expected chainId=$expected (last='$actual')" >&2
  return 1
}

wait_for_rpc "$NOVA_PORT" "$NOVA_CHAIN_ID" "AION Nova"
wait_for_rpc "$ORBIT_PORT" "$ORBIT_CHAIN_ID" "AION Orbit"

if [[ "$NOVA_CHAIN_ID" == "$ORBIT_CHAIN_ID" ]]; then
  echo "FAIL: Nova and Orbit must have different chain IDs." >&2
  exit 1
fi

nova_block="$(cast block-number --rpc-url "http://127.0.0.1:$NOVA_PORT")"
orbit_block="$(cast block-number --rpc-url "http://127.0.0.1:$ORBIT_PORT")"
[[ "$nova_block" =~ ^[0-9]+$ && "$orbit_block" =~ ^[0-9]+$ ]] || {
  echo "FAIL: block-number response was not numeric." >&2
  exit 1
}
printf 'PASS: both isolated EVM RPCs answer block-number (Nova=%s, Orbit=%s).\n' "$nova_block" "$orbit_block"
echo "NOTE: these are temporary local Anvil nodes, not public networks. No token was deployed."
