import mss

with mss.MSS() as sct:
    for i, monitor in enumerate(sct.monitors):
        print(f"monitor[{i}]: {monitor}")