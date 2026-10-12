"""Download the BodyParts3D STL files a build needs (from the public GitHub mirror).

usage:
  python3 scripts/fetch_stl.py manifest      stl_dl     # right upper limb
  python3 scripts/fetch_stl.py manifest_leg  stl_leg    # pelvis + right lower limb
  python3 scripts/fetch_stl.py body          stl_body   # whole skeleton for the start-screen figure (skeleton_parts.json)

Source: BodyParts3D, (c) The Database Center for Life Science, CC BY-SA 2.1 Japan.
Mirror: https://github.com/Kevin-Mattheus-Moerman/BodyParts3D
"""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://raw.githubusercontent.com/Kevin-Mattheus-Moerman/BodyParts3D/main/assets/BodyParts3D_data/stl/{}.stl"
here = os.path.dirname(os.path.abspath(__file__))
which, out_dir = sys.argv[1], sys.argv[2]
if which == "body":
    ids = [fid for fid, _name, _region in json.load(open(os.path.join(here, "..", "skeleton_parts.json")))]
else:
    sys.path.insert(0, here)
    ids = __import__(which).all_ids()
os.makedirs(out_dir, exist_ok=True)
ids = sorted(set(ids))
def download(fid):
    dst = os.path.join(out_dir, f"{fid}.stl")
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return fid
    for attempt in range(5):
        try:
            with urllib.request.urlopen(BASE.format(fid), timeout=120) as r:
                data = r.read()
            # Atomic replacement prevents a interrupted download from looking complete.
            temporary = dst + '.part'
            open(temporary, "wb").write(data)
            os.replace(temporary, dst)
            break
        except Exception as e:  # rate limits (HTTP 429) and timeouts: wait and retry
            print(f"retry {fid}: {e}")
            time.sleep(3 * (attempt + 1))
    else:
        raise RuntimeError(f"failed: {fid}")
    return fid

if __name__ == '__main__':
    jobs = int(os.environ.get('DOWNLOAD_JOBS', '1'))
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for n, task in enumerate(as_completed([pool.submit(download, fid) for fid in ids]), 1):
            print(f"{n}/{len(ids)} {task.result()}", flush=True)
print("done:", len(ids), "files in", out_dir)
