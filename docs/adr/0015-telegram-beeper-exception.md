# ADR-0015 — Telegram operator beeper: an accepted exception to "local only"

Date: 2026-08-08. Status: accepted.

## Context

During the twenty minutes of generation on stage the operator cannot watch a
terminal, and the failure the beeper must signal is precisely the conference
WiFi dropping. The golden rule says no cloud API.

## Decision

- Notifications go to the operator's phone through Telegram, OFF by default
  (`TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` both required; without them
  every call is a silent no-op, zero bytes on the network).
- What stays local is the FACTORY of the work; this is the operator's PAGER.
  Its value is being out of band (cellular).
- The protection is MECHANICAL: messages are composed from STRUCTURED FIELDS
  (phase, percentage, durations, counters, error class). There is
  deliberately no generic `notify.text()`. A second curtain strips everything
  between quotation marks and bounds messages to 200 characters; our own
  notes cite the bible and the chapter and would have exported the work.
- Rate: one progress beat per 5 minutes at most; start, failure, cancel and
  ready pass with priority. Sending runs in a thread; generation never waits
  on the network.

## Consequences

- `notify._assainir` is tested on the three real cases that cite the work.
- Any new notification is a new typed function, never a string passthrough.
