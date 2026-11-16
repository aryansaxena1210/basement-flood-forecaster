"""Flood rule (docs/flood_events.md): a flood day has FLOOD_CUTOFF+ complaints; flood days at most MERGE_GAP days apart form one event."""

FLOOD_CUTOFF = 100
MERGE_GAP = 2
BIG_PEAK = 500


def find_events(counts):
    """counts: {date: complaints}. Returns events, each a list of flood days in order."""
    events = []
    for d in sorted(counts):
        if counts[d] >= FLOOD_CUTOFF:
            if events and (d - events[-1][-1]).days <= MERGE_GAP:
                events[-1].append(d)
            else:
                events.append([d])
    return events
