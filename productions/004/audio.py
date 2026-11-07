"""Mix narration, BGM and synthesized SFX for #004 -> mix.wav (48 kHz stereo)."""
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
EV = dict(tl["events"])
SH = {}
for a, b, n in tl["shots"]:
    SH.setdefault(n, (a, b))
TE = tl["teaser_end"]

# ---------- narration
vo = np.zeros(N)
for k, s, d in tl["vo"]:
    x = load(D / f"vo_fast/{k}.wav")
    x = norm_rms(x, -16)
    place(vo, x, s)

# ---------- BGM (Signs To Nowhere) with ducking under narration
bgm = load(D / "bgm.mp3")[: N]
bgm = np.pad(bgm, (0, max(0, N - len(bgm))))
bgm = norm_rms(bgm, -27)
vo_env = np.convolve(np.abs(vo) > 0.003, np.ones(int(SR * 0.25)) / (SR * 0.25), mode="same")
duck = 1 - 0.7 * np.clip(vo_env * 3, 0, 1)
# 声の下では、こもった環境音（店内の雨・蛍光灯）も下げる。声の帯域を空けるため
amb_duck = 1 - 0.6 * np.clip(vo_env * 3, 0, 1)
bgm_level = ramp([(0, 0.5), (TE, 0.5), (TE + 0.05, 0), (TE + 0.5, 0), (TE + 1.2, 1), (EV["heels"] - 2.5, 1), (EV["heels"] - 0.1, 0.0), (DUR, 0)])
bgm = bgm * duck * bgm_level

# ---------- platform: a low station hum and a far-off room tone; a train passes under line 7
t = np.arange(N) / SR
noise = rng.normal(0, 1, N)
noise2 = rng.normal(0, 1, N)
room = lp(noise, 300) * db(-25) + bp(noise2, 1500, 5000) * db(-46) + np.sin(2 * np.pi * 50 * t) * db(-50)
room_lvl = ramp([(0, 0.7), (TE, 0.7), (TE + 0.05, 0), (TE + 1.2, 0), (TE + 1.7, 1.0), (EV["resolve"] - 0.4, 1.0), (EV["resolve"], 0.0),
                 (EV["neon"], 0), (EV["neon"] + 0.7, 0.3), (DUR, 0.2)])
rain = room * room_lvl          # (kept the name: it is the ambience bed)
hum = np.zeros(N)
# passing train: a band-passed roar that swells and fades, with rail clacks
tr = EV["train"]; n = int(SR * 4.0); tt = np.arange(n) / SR
roar = bp(rng.normal(0, 1, n), 80, 2500) * np.sin(np.pi * np.clip(tt / 4.0, 0, 1)) ** 2
clack = np.zeros(n)
for c in np.arange(0.4, 3.6, 0.21):
    m = int(SR * 0.03); i = int(c * SR)
    clack[i:i + m] += bp(rng.normal(0, 1, m), 400, 3000) * env_ad(m, 0.001, 0.008) * np.sin(np.pi * c / 4.0) ** 2
shower = np.zeros(N)
place(shower, roar * db(-22) + clack * db(-20), tr - 0.3)

sfx = np.zeros(N)
# phone vibration: one buzz (two short pulses, low and rattly)
def buzz():
    n = int(SR * 0.7); tt = np.arange(n) / SR
    g = ((tt < 0.28) | ((tt > 0.4) & (tt < 0.62))).astype(float)
    g = np.convolve(g, np.ones(200) / 200, mode="same")
    return lp(np.sign(np.sin(2 * np.pi * 165 * tt)) * 0.6 + np.sin(2 * np.pi * 330 * tt) * 0.3, 900) * g
place(sfx, buzz(), EV["buzz"], db(-18))
# notification tone (soft, generic)
def chime(fs=(1320, 990)):
    out = np.zeros(int(SR * 1.2))
    for i, f in enumerate(fs):
        n = int(SR * 0.6); tt = np.arange(n) / SR
        place(out, (np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(2 * np.pi * 2 * f * tt)) * np.exp(-tt / 0.15), i * 0.12)
    return out
place(sfx, chime(), EV["notify"], db(-32))
# taps on the glass
def tap():
    n = int(SR * 0.05); tt = np.arange(n) / SR
    return bp(rng.normal(0, 1, n), 1500, 7000) * np.exp(-tt / 0.004) + np.sin(2 * np.pi * 900 * tt) * np.exp(-tt / 0.006) * 0.3
for i in range(3):
    place(sfx, tap(), EV["taps"] + i * 0.75 + 0.02, db(-24))
place(sfx, tap(), EV["back_tap"], db(-22))
# rewind: reversed rising hiss across the black
n = int(SR * 0.35); tt = np.arange(n) / SR
rw = bp(rng.normal(0, 1, n), 800, 6000) * np.sin(np.pi * tt / 0.35) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * (20 + 120 * tt) * tt)))
place(sfx, rw, TE, db(-22))
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
for i, tt0 in enumerate((EV["heels"], EV["heels"] + 0.55, EV["heels"] + 1.1)):
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
place(sfx, neon, EV["neon"])
# シリーズ名のネオン（短く、オチより小さく）
place(sfx, neon[: int(SR * 1.3)] * np.linspace(1, 0, int(SR * 1.3)), EV["rewind"] + 0.55, db(-4))
# low piano-ish note on the line
n = int(SR * 4.5); tt = np.arange(n) / SR
low = sum((1 / (h ** 1.3)) * np.sin(2 * np.pi * 55 * h * tt) * np.exp(-tt / (2.2 / h)) for h in range(1, 7))
low *= np.minimum(1, np.arange(n) / (SR * 0.006))
place(sfx, low, EV["low"], db(-15))

hum = hum * amb_duck
rain = rain * amb_duck
shower = shower * amb_duck
mix = vo + bgm + hum + rain + shower + sfx
# gentle bus limiter
peak = np.max(np.abs(mix))
mix = np.tanh(mix / max(peak, 1e-9) * 1.3) * 0.89 if peak > 0.89 else mix
fade = ramp([(0, 1), (DUR - 0.6, 1), (DUR, 0)])
mix *= fade
# stereo: narration centre, ambience slightly widened
side = (rain + hum) * 0.0
L = mix + np.roll(rain, 240) * 0.15
R = mix + np.roll(rain, -240) * 0.15
st = np.stack([L, R], 1)
st /= max(1.0, np.max(np.abs(st)) / 0.95)
wavfile.write(D / "mix.wav", SR, (st * 32767).astype(np.int16))
print("mix ok", round(float(np.max(np.abs(st))), 3))
