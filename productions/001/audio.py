"""Mix narration, BGM and synthesized SFX for ep001 -> mix.wav (48 kHz stereo)."""
import json, subprocess, pathlib
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

D = pathlib.Path(__file__).resolve().parent
SR = 48000
import json as _j
DUR = _j.load(open(pathlib.Path(__file__).resolve().parent/"timeline.json"))["total"]
N = int(DUR * SR)
rng = np.random.default_rng(3)


def bp(x, lo, hi, order=4):
    sos = butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, x)


def lp(x, f):
    return sosfilt(butter(4, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f):
    return sosfilt(butter(2, f, btype="high", fs=SR, output="sos"), x)


def db(v):
    return 10 ** (v / 20)


def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-np.maximum(t - a, 0) / d)


def place(buf, x, t, gain=1.0):
    i = int(t * SR)
    j = min(len(buf), i + len(x))
    if j > i:
        buf[i:j] += x[: j - i] * gain


def load(path):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).copy()


def ramp(times_vals):
    t = np.arange(N) / SR
    ts, vs = zip(*times_vals)
    return np.interp(t, ts, vs)


def norm_rms(x, target_db):
    r = np.sqrt(np.mean(x[np.abs(x) > 1e-4] ** 2)) + 1e-9
    return x * db(target_db) / r


tl = json.loads((D / "timeline.json").read_text())

# ---------- narration
vo = np.zeros(N)
for k, s, d in tl["vo"]:
    x = load(D / f"vo/{k}.wav")
    x = norm_rms(x, -18)
    place(vo, x, s, 1.0 if k != 8 else 0.95)

# ---------- BGM (Signs To Nowhere) with ducking under narration
bgm = load(D / "bgm.mp3")[: N]
bgm = np.pad(bgm, (0, max(0, N - len(bgm))))
bgm = norm_rms(bgm, -27)
vo_env = np.convolve(np.abs(vo) > 0.003, np.ones(int(SR * 0.25)) / (SR * 0.25), mode="same")
duck = 1 - 0.45 * np.clip(vo_env * 3, 0, 1)
bgm_level = ramp([(0, 0), (0.8, 1), (50.51400000000001, 1), (52.91400000000001, 0.0), (63.14, 0)])
bgm = bgm * duck * bgm_level

# ---------- room tone: fluorescent hum inside the store (0-49s)
t = np.arange(N) / SR
hum = (np.sin(2 * np.pi * 100 * t) + 0.4 * np.sin(2 * np.pi * 200 * t) + 0.15 * np.sin(2 * np.pi * 300 * t)) * db(-46)
hum *= ramp([(0, 0), (0.5, 1), (46.414333000000006, 1), (47.21433300000001, 0), (63.14, 0)])

# ---------- rain: muffled inside, open outside, gone in the silence beat, faint at the end
noise = rng.normal(0, 1, N)
rain_out = bp(noise, 900, 7000) * db(-30)
rain_in = lp(noise, 900) * db(-34)
# droplets
drops = np.zeros(N)
for _ in range(900):
    tt = rng.uniform(0, DUR)
    n = int(SR * 0.012)
    place(drops, bp(rng.normal(0, 1, n), 2500, 9000) * env_ad(n, 0.0005, 0.003), tt, db(-30) * rng.uniform(0.3, 1))
rain = rain_in * ramp([(0, 0), (0.6, 1), (46.71433300000001, 1), (47.31433300000001, 0), (63.14, 0)]) \
    + (rain_out + drops) * ramp([(0, 0), (46.51433300000001, 0), (47.414333000000006, 1.25), (55.56400000000001, 1.0), (56.964000000000006, 0.0), (57.864000000000004, 0), (58.56400000000001, 0.35), (63.14, 0.25)])

sfx = np.zeros(N)
# scanner beep
def beep(f=2350, dur=0.11):
    n = int(SR * dur); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * f * tt) * np.minimum(1, (n - np.arange(n)) / (SR * 0.01)) * np.minimum(1, np.arange(n) / (SR * 0.004))
place(sfx, beep(), 17.757, db(-20))

# alert chime (two tones, falling)
def chime():
    out = np.zeros(int(SR * 1.2))
    for i, f in enumerate((988, 784)):
        n = int(SR * 0.8); tt = np.arange(n) / SR
        tone = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)) * np.exp(-tt / 0.25)
        place(out, tone, i * 0.28)
    return out
place(sfx, chime(), 23.824, db(-22))
place(sfx, chime(), 24.824, db(-27))
place(sfx, chime(), 32.632333, db(-24))
# receipt printer
n = int(SR * 1.7); tt = np.arange(n) / SR
printer = bp(rng.normal(0, 1, n), 600, 4000) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 38 * tt))) * np.minimum(1, (n - np.arange(n)) / (SR * 0.05))

# automatic door: motor + whoosh
n = int(SR * 1.4); tt = np.arange(n) / SR
door = (np.sin(2 * np.pi * (110 + 40 * tt) * tt) * 0.5 + bp(rng.normal(0, 1, n), 300, 2500)) * np.sin(np.pi * tt / 1.4)
place(sfx, door, 46.61433300000001, db(-28))
# heels: three steps, wet pavement, a little space
def heel():
    n = int(SR * 0.35); tt = np.arange(n) / SR
    click = bp(rng.normal(0, 1, n), 1800, 6000) * np.exp(-tt / 0.006)
    knock = np.sin(2 * np.pi * 210 * tt) * np.exp(-tt / 0.025) * 0.6
    x = click + knock
    tail = np.zeros(n)
    for dly, g in ((0.045, 0.35), (0.09, 0.2), (0.15, 0.1)):
        k = int(dly * SR); tail[k:] += x[: n - k] * g
    return x + lp(tail, 3000)
for i, tt0 in enumerate((53.01400000000001, 53.61400000000001, 54.21400000000001)):
    place(sfx, heel(), tt0, db(-12 - i * 1.5))
# neon: crackle on flicker, then hum
n = int(SR * 5.8); tt = np.arange(n) / SR
buzz = np.sign(np.sin(2 * np.pi * 120 * tt)) * 0.3 + np.sin(2 * np.pi * 240 * tt) * 0.3
buzz = lp(buzz, 1800)
fl = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1]
gate = np.array([1.0 if tt_ > 0.6 else fl[int(tt_ / 0.05) % len(fl)] for tt_ in tt])
gate = np.convolve(gate, np.ones(96) / 96, mode="same")
crack = bp(rng.normal(0, 1, n), 2000, 8000) * (np.abs(np.diff(np.r_[0, gate])) * 400).clip(0, 1)
neon = buzz * gate * np.r_[np.ones(int(SR * 0.6)), np.linspace(1, 0.35, n - int(SR * 0.6))] * db(-30) + crack * db(-20)
place(sfx, neon, 57.964000000000006)
# low piano-ish note on the line
n = int(SR * 4.5); tt = np.arange(n) / SR
low = sum((1 / (h ** 1.3)) * np.sin(2 * np.pi * 55 * h * tt) * np.exp(-tt / (2.2 / h)) for h in range(1, 7))
low *= np.minimum(1, np.arange(n) / (SR * 0.006))
place(sfx, low, 58.714000000000006, db(-17))

mix = vo + bgm + hum + rain + sfx
# gentle bus limiter
peak = np.max(np.abs(mix))
mix = np.tanh(mix / max(peak, 1e-9) * 1.3) * 0.89 if peak > 0.89 else mix
fade = ramp([(0, 0), (0.3, 1), (62.54, 1), (63.14, 0)])
mix *= fade
# stereo: narration centre, ambience slightly widened
side = (rain + hum) * 0.0
L = mix + np.roll(rain, 240) * 0.15
R = mix + np.roll(rain, -240) * 0.15
st = np.stack([L, R], 1)
st /= max(1.0, np.max(np.abs(st)) / 0.95)
wavfile.write(D / "mix.wav", SR, (st * 32767).astype(np.int16))
print("mix ok", round(float(np.max(np.abs(st))), 3))
