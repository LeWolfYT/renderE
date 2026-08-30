import struct
from PIL import Image
import threading as th
from io import BytesIO
import rendereglobals as rg

def loadmv(data):
    def read_u32(offset):
        return struct.unpack(">I", data[offset:offset+4])[0]

    def read_u64(offset):
        return struct.unpack(">Q", data[offset:offset+8])[0]
    width = read_u32(0)
    height = read_u32(4)
    fsize = read_u64(8)
    nframes = read_u32(16)
    bpf = width * height * 4
    
    frames = []

    def process_one(frameix, raw):
        if len(raw) < bpf:
            raw += b"\x00" * (bpf - len(raw)) #padding because apparently that's a thing

        frame_bytes = bytearray(raw)
        for i in range(0, len(frame_bytes), 4):
            r, g, b, a = frame_bytes[i:i+4]
            frame_bytes[i:i+4] = bytes([b, g, r, a])

        img = Image.frombuffer("RGBA", (width, height), bytes(frame_bytes), "raw", "BGRA", 0, 1)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        arr = BytesIO()
        img.save(arr, format="PNG")
        arr = arr.getvalue()
        img = rg.rl.load_image_from_memory('.png', arr, len(arr))
        rg.rl.image_alpha_premultiply(img)
        frames.append((img, frameix))

    ts = []
    for frameix in range(1, nframes + 1):
        start = (frameix - 1) * bpf
        frame_start = start + 32
        if frame_start >= len(data):
            print(f"frame {frameix} data is out of range")
            break
        t = th.Thread(target=process_one, args=(frameix, data[frame_start:frame_start + bpf]))
        ts.append(t)
        t.start()
    
    for t in ts:
        t.join()
    
    return [f[0] for f in sorted(frames, key=lambda x: x[1])]