# Ledger — #105 block-sendto-sendmsg

Branch: `fix/105-block-sendto` · Issue: #105 · Class: **ci**

## Goal

The test network guard also blocks `sendto` and `sendmsg`, so an unmarked test cannot send a UDP datagram without `connect()`.

## Work

- [x] Confirm `origin/main` `_BlockedSocket` does not override `sendto` or `sendmsg`
- [x] Override both in `tests/conftest.py`
- [x] Add `tests/unit/test_network_guard.py` (fails if the guard is removed; `allow_network` still works)
