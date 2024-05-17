"""
Example upload of a dataset to posthog-llm sending input in chatml format
and no session ID.
"""
import os
from pathlib import Path
import json
import posthog


posthog.api_key = os.environ.get("POSTHOG_API_KEY")
posthog.host = os.environ.get("POSTHOG_HOST")


def task(
    distinct_id,
    input,
    output,
    event="llm-task",
    timestamp=None,
    session_id=None,
    properties=None,
):
    props = properties if properties else {}
    props["$llm_input"] = input
    props["$llm_output"] = output

    if session_id:
        props["$session_id"] = session_id

    posthog.capture(
        distinct_id=distinct_id,
        event=event,
        properties=props,
        timestamp=timestamp,
        disable_geoip=False,
    )


def chunker(seq, size):
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def as_chatml(turns):
    ret = []
    for human, ai in turns:
        ret.append({"role": "user", "content": human})
        if ai is not None:
            ret.append({"role": "assistant", "content": ai})
    return ret


# example data from sharegpt dataset
with open(Path(__file__).parent / "example_data.json") as f:
    data = json.load(f)


for itm in data:
    turns = []
    for human, ai in chunker(itm["turns"], 2):
        turns.append([human["content"], None])
        task(
            itm["id"],
            input=as_chatml(turns),
            output=ai["content"],
            properties={"model": itm["model"]},
        )
        turns[-1][1] = ai["content"]
