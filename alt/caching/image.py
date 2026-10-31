import requests
import os
from pathlib import Path
import pickle
import zstandard as zstd
from PIL import Image
import io
import time
from alt import data
from alt.data import network_requests, version
from data import version as versionshift
import platform

not_animated_types = [".png", ".jpg", ".jpeg", ".bmp", ".ico"]


def compress_bytes_to_acf(file_bytes, output_path, compression_level=3):
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            fmt = (img.format or "UNKNOWN").encode("utf-8")
    except Exception:
        fmt = b"UNKNOWN"

    header = bytes([len(fmt)]) + fmt
    full_data = header + file_bytes

    cctx = zstd.ZstdCompressor(level=compression_level)
    compressed_data = cctx.compress(full_data)

    with open(output_path, "wb") as f:
        f.write(compressed_data)


def decompress_acf_to_bytes(acf_bytes):
    dctx = zstd.ZstdDecompressor()
    decompressed_data = dctx.decompress(acf_bytes)

    fmt_len = decompressed_data[0]
    fmt = decompressed_data[1 : 1 + fmt_len].decode("utf-8")
    original_bytes = decompressed_data[1 + fmt_len :]

    return original_bytes, fmt

def load_not_animated_and_cache(source: str, localfile, randomindex):
    file = Path(os.path.expandvars(r"%TEMP%\Shift\images.arcf")) # .arcf - Alt Routing Caching File

    file.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    if file.exists():
        with file.open("rb") as f:
            try:
                data = pickle.load(f)
            except Exception:
                data = {}
    else:
        with file.open("wb") as f:
            pickle.dump(data, f)

    if data and source in data:
        cache_file = data[source]
        with open(cache_file, "rb") as f:
            info = decompress_acf_to_bytes(f.read())
            return 1, info[0]

    if not source.startswith("https://") and not localfile:
        return 0, "It isn't safety. Use https://"
    elif localfile and source.startswith("local://"):
        type_file = None

        for type in not_animated_types:
            if source.endswith(type):
                type_file = type
                break

        if type_file is None:
            return 0, "Alt doesn't support this type of the file"

        file = Path(source[len("local://"):])

        if not file.exists():
            return 0, "File doesn't exist"

        with file.open("rb") as f:
            return f.read()

    index = len(network_requests)

    network_requests.append({
        "endpoint": source,
        "created_by": "Alt.CachingService",
        "when": time.time(),
        "status": 0,
        "method": "GET"
    })

    accept = ""

    for type in not_animated_types:
        accept += f"image/{type[1:]} "

    request = requests.get(
        source,
        headers={
            "User-Agent": f"Shift/{versionshift}, Alt/{version}, {platform.system()}/{platform.release()}",
            "Accept": accept,
            "Alt_Type-Script": "Local" if localfile is None else "Global",
            "Alt_Created_By": "Alt.CachingService",
        }
    )

    network_requests[index] = {
        "endpoint": source,
        "created_by": "Alt.CachingService",
        "when": network_requests[index]["when"],
        "status": request.status_code,
        "method": "GET",
        "ping": (time.time()-network_requests[index]["when"])*1000,
        "headers": request.headers,
        "json": None,
        "text": request.text,
        "content": request.content
    }

    if request.status_code != 200:
        return 0, f"{source} return status {request.status_code}()"

    can_cache = True
    image = Image.open(io.BytesIO(request.content))
    type_request_file = image.format.lower()
    allowed = False

    for type in not_animated_types:
        if type_request_file == type.lstrip("."):
            allowed = True
            break

    if not allowed:
        return 0, f"{source} returns unsupported type"

    # If header "CachingService" has "NotAllowedCaching" then cache isn't allowed
    # For example: "CachingService: AllowedCaching SolutionBrowser"

    if request.headers.get("CachingService") is not None:
        if "NotAllowedCaching" in request.headers["CachingService"]:
            can_cache = False

    # If header "CachingService" has "NeedCache" then cache needs to save
    # CachingService decides to save cache or not if cache doesn't need to save

    if "NeedCache" in request.headers.get("CachingService", "") or can_cache and len(request.content)/1024 > 1024:
        if not can_cache:
            return 0, f"{source} doesn't allowed cache and require to save cache. Administrator of this source has to set true values"

        path = os.path.expandvars(f"%TEMP%/Shift/images/{time.time()}_{randomindex}.acf") # acf - Alt Caching File

        Path(path).parent.mkdir(parents=True, exist_ok=True)

        compress_bytes_to_acf(request.content, path)

        read = file.open("rb")
        data = pickle.load(read)

        if data is None:
            data = {}

        data[source] = path

        with file.open("wb") as f:
            pickle.dump(data, f)

    return 1, request.content









    return request.content