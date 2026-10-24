"""Bounded source research, never an application/model generator."""
import argparse
import hashlib
import io
import json
import pathlib
import time
import urllib.request
import zipfile


class RemoteZip(io.RawIOBase):
    """Read only requested ZIP ranges; refuse servers that return the whole archive."""
    def __init__(self, url, budget=8_000_000):
        self.url, self.pos, self.used, self.budget = url, 0, 0, budget
        self.started = time.monotonic()
        request = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(request, timeout=15) as response:
            self.size = int(response.headers["Content-Length"])
            self.headers = dict(response.headers)

    def seekable(self):
        return True

    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        return self.pos

    def tell(self):
        return self.pos

    def read(self, size=-1):
        size = min(self.size - self.pos, size if size >= 0 else self.size)
        if not size:
            return b""
        if self.used + size > self.budget or time.monotonic() - self.started > 90:
            raise TimeoutError("Bounded archive inspection budget exceeded")
        start = self.pos
        request = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{start+size-1}"})
        with urllib.request.urlopen(request, timeout=15) as response:
            if response.status != 206 or not response.headers.get("Content-Range", "").startswith(f"bytes {start}-"):
                raise ValueError("Server ignored byte range; full archive download refused")
            result = response.read(size + 1)
        if len(result) != size:
            raise ValueError("Unexpected range size")
        self.used += size
        self.pos += size
        return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run")
    args = parser.parse_args()
    run = pathlib.Path(args.run)
    cache = pathlib.Path("research/cache/stage6-sources")
    cache.mkdir(parents=True, exist_ok=True)
    url = "https://dbarchive.biosciencedbc.jp/data/bodyparts3d/20110915/BodyParts3D_3.0_obj_95.zip"
    source = RemoteZip(url)
    with zipfile.ZipFile(source) as archive:
        entries = [dict(name=i.filename, bytes=i.file_size, compressed=i.compress_size, crc=i.CRC) for i in archive.infolist()]
        with (run / "official-archive-index.json").open("x", encoding="utf8") as out:
            json.dump(dict(url=url,archiveBytes=source.size,headers=source.headers,entries=entries),out,indent=2)
        downloads = []
        for fma in ("FMA23464", "FMA23465", "FMA23467", "FMA23468"):
            names = [n for n in archive.namelist() if pathlib.PurePosixPath(n).name == fma + ".obj"]
            if len(names) != 1:
                raise ValueError((fma, names))
            data = archive.read(names[0])  # zipfile checks the archive CRC.
            target = cache / (fma + ".obj")
            with target.open("xb") as out:
                out.write(data)
            downloads.append(dict(id=fma,url=url,entry=names[0],file=target.as_posix(),
                                  bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
            with (run / (fma + "-official.json")).open("x",encoding="utf8") as out:
                json.dump(downloads[-1],out,indent=2)
        result = dict(status="passed",rangeBytesRead=source.used,archiveBytes=source.size,entries=len(entries),downloads=downloads)
        with (run / "official-extraction.json").open("x",encoding="utf8") as out:
            json.dump(result,out,indent=2)
        print(json.dumps({k:v for k,v in result.items() if k!="downloads"}))


if __name__ == "__main__":
    main()
