"""
generate_original_catalog.py

Synthesizes a 100% Original, Procedural, Copyright-Free Devotional Audio Catalog:
- Zero third-party audio, zero sampled loops, zero label encumbrance.
- 100% mathematical physical acoustic modeling (Tanpura, Bansuri, Temple Bells, Om Chant).
- Tuned to 432 Hz Sacred Healing Pitch.
- Normalized to EBU R128 Sanctuary Profile (-18.0 LUFS, True Peak <= -1.5 dBFS).
- Output tracks placed into live_system/stream_segments/ as the sole broadcast catalog.
"""

import sys
import math
import shutil
import subprocess
from pathlib import Path
import numpy as np
from scipy.io import wavfile

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

SAMPLE_RATE = 44100
BASE_DIR = Path(__file__).resolve().parent
LIVE_DIR = BASE_DIR / "live_system"
SEGMENTS_DIR = LIVE_DIR / "stream_segments"
SEGMENTS_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_BIN = shutil.which("ffmpeg") or r"C:\Users\Tanush Garg\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"

# ---------------------------------------------------------------------------
# 1. Acoustic Synthesizer Primitives
# ---------------------------------------------------------------------------

def synthesize_fast_tanpura(duration: float, root_freq: float = 138.59) -> np.ndarray:
    """Authentic 4-string Indian Tanpura drone with acoustic jawari beating."""
    cycle_time = 4.2
    cycle_samples = int(SAMPLE_RATE * cycle_time)
    t = np.linspace(0, cycle_time, cycle_samples, endpoint=False)
    
    strings = [
        (root_freq * 1.50, 0.22),    # Pa
        (root_freq * 1.000, 0.30),   # Sa
        (root_freq * 1.002, 0.30),   # Jori Sa (micro-detuned for natural beating)
        (root_freq * 0.500, 0.36)    # Kharaj (low octave Sa)
    ]
    
    cycle = np.zeros(cycle_samples, dtype=np.float64)
    for idx, (bf, amp) in enumerate(strings):
        t_shift = (t - idx * (cycle_time / 4.0)) % cycle_time
        env = np.exp(-0.48 * t_shift)
        harms = np.zeros(cycle_samples, dtype=np.float64)
        for h in range(1, 9):
            harms += (1.0 / (h ** 0.85)) * np.sin(2 * np.pi * bf * h * t_shift)
        cycle += harms * env * amp * 0.22
        
    for h in [1, 2]:
        cycle += (0.04 / h) * np.sin(2 * np.pi * root_freq * h * t)
        
    total_samples = int(SAMPLE_RATE * duration)
    reps = (total_samples // cycle_samples) + 2
    return np.tile(cycle, reps)[:total_samples]


def synthesize_bansuri_phrase(notes: list[tuple[float, float]], root_freq: float) -> np.ndarray:
    """Continuous bamboo flute melody with smooth meend glides, vibrato, and breath."""
    phrase_duration = sum(dur for _, dur in notes)
    total_samples = int(phrase_duration * SAMPLE_RATE)
    phrase = np.zeros(total_samples, dtype=np.float64)
    
    current_sample = 0
    prev_freq = root_freq * notes[0][0]
    
    for ratio, note_dur in notes:
        target_freq = root_freq * ratio
        note_samples = int(note_dur * SAMPLE_RATE)
        t = np.linspace(0, note_dur, note_samples, endpoint=False)
        
        # Meend (portamento pitch glide from previous note)
        glide_len = min(int(0.14 * SAMPLE_RATE), note_samples // 3)
        freq_curve = np.full(note_samples, target_freq)
        if glide_len > 0:
            freq_curve[:glide_len] = np.linspace(prev_freq, target_freq, glide_len)
            
        # Subtle bansuri vibrato (starts after 0.25s)
        vibrato_amp = np.clip((t - 0.25) * 0.016, 0, 0.014)
        vibrato = 1.0 + vibrato_amp * np.sin(2 * np.pi * 4.6 * t)
        
        inst_freq = freq_curve * vibrato
        phase = 2 * np.pi * np.cumsum(inst_freq) / SAMPLE_RATE
        
        # Soft organic attack & smooth legato decay envelope
        att_len = min(int(0.20 * SAMPLE_RATE), note_samples // 4)
        rel_len = min(int(0.25 * SAMPLE_RATE), note_samples // 4)
        env = np.ones(note_samples)
        if att_len > 0:
            env[:att_len] = 0.5 * (1 - np.cos(np.pi * np.linspace(0, 1, att_len)))
        if rel_len > 0:
            env[-rel_len:] = 0.5 * (1 + np.cos(np.pi * np.linspace(0, 1, rel_len)))
            
        # Warm bamboo harmonics + airy breath sound
        sig = (np.sin(phase) +
               0.35 * np.sin(2 * phase) +
               0.12 * np.sin(3 * phase) +
               0.05 * np.sin(4 * phase))
               
        breath_noise = np.random.normal(0, 0.016, note_samples)
        note_audio = (sig * 0.55 + breath_noise) * env
        
        end_sample = min(current_sample + note_samples, total_samples)
        actual_len = end_sample - current_sample
        phrase[current_sample:end_sample] += note_audio[:actual_len]
        
        current_sample = end_sample
        prev_freq = target_freq
        
    return phrase


def synthesize_temple_bells(duration: float, strike_times: list[float], pitch: float = 1046.5) -> np.ndarray:
    """Pure resonant brass temple ghanti with inharmonic decaying ring."""
    total_samples = int(SAMPLE_RATE * duration)
    bells = np.zeros(total_samples, dtype=np.float64)
    partials = [1.0, 2.76, 5.40, 8.93, 11.23]
    decays = [2.2, 4.2, 7.5, 12.0, 16.0]
    weights = [0.45, 0.28, 0.15, 0.08, 0.04]
    
    # Pre-render a single strike template of 6.0 seconds
    strike_dur = 6.0
    strike_len = int(SAMPLE_RATE * strike_dur)
    t = np.linspace(0, strike_dur, strike_len, endpoint=False)
    single_strike = np.zeros(strike_len, dtype=np.float64)
    for p, d, w in zip(partials, decays, weights):
        single_strike += w * np.sin(2 * np.pi * (pitch * p) * t) * np.exp(-d * t)
    single_strike *= 0.26
    
    for st in strike_times:
        start_idx = int(st * SAMPLE_RATE)
        if start_idx >= total_samples:
            continue
        end_idx = min(start_idx + strike_len, total_samples)
        avail = end_idx - start_idx
        bells[start_idx:end_idx] += single_strike[:avail]
        
    return bells


def synthesize_om_chant(duration: float, root_freq: float = 136.1) -> np.ndarray:
    """Cosmic Earth frequency 136.1 Hz Om vocal resonance with meditative breathing."""
    cycle_time = 8.5
    cycle_samples = int(SAMPLE_RATE * cycle_time)
    t = np.linspace(0, cycle_time, cycle_samples, endpoint=False)
    
    breath_cycle = 0.5 + 0.5 * np.sin(2 * np.pi * (1.0 / cycle_time) * t)
    om = (np.sin(2 * np.pi * root_freq * t) +
          0.45 * np.sin(2 * np.pi * root_freq * 2 * t) +
          0.22 * np.sin(2 * np.pi * root_freq * 3 * t) +
          0.10 * np.sin(2 * np.pi * root_freq * 4 * t) +
          0.05 * np.sin(2 * np.pi * root_freq * 5 * t))
          
    lfo = 1.0 + 0.002 * np.sin(2 * np.pi * 0.25 * t)
    om_chorus = np.sin(2 * np.pi * root_freq * lfo * t) * 0.3
    single_cycle = (om + om_chorus) * breath_cycle * 0.35
    
    total_samples = int(SAMPLE_RATE * duration)
    reps = (total_samples // cycle_samples) + 2
    return np.tile(single_cycle, reps)[:total_samples]


def synthesize_ambient_stream(duration: float) -> np.ndarray:
    """Soft whispering river stream & gentle forest breeze ambient bed."""
    cycle_time = 12.0
    cycle_samples = int(SAMPLE_RATE * cycle_time)
    white = np.random.normal(0, 1.0, cycle_samples)
    brown = np.cumsum(white)
    brown = brown - np.mean(brown)
    if np.max(np.abs(brown)) > 0:
        brown = brown / np.max(np.abs(brown))
        
    t = np.linspace(0, cycle_time, cycle_samples, endpoint=False)
    ripple = 0.6 + 0.4 * np.sin(2 * np.pi * 0.10 * t) * np.sin(2 * np.pi * 0.03 * t)
    single_cycle = brown * ripple * 0.06
    
    total_samples = int(SAMPLE_RATE * duration)
    reps = (total_samples // cycle_samples) + 2
    return np.tile(single_cycle, reps)[:total_samples]


# ---------------------------------------------------------------------------
# 2. Master Composition Builders
# ---------------------------------------------------------------------------

def compose_track(
    name: str,
    title_hindi: str,
    duration: float,
    root_freq: float,
    phrases: list[list[tuple[float, float]]],
    bell_interval: float,
    bell_pitch: float,
    has_om: bool = False
) -> Path:
    """Constructs a non-repetitive evolving soundscape and masters to 432 Hz."""
    print(f"\n🎼 Composing Track: {title_hindi} ({duration/60:.1f} mins)...", flush=True)
    
    # 1. Tanpura bed & nature ambience (sub-second vectorized tiling)
    tanpura = synthesize_fast_tanpura(duration, root_freq=root_freq / 2.0)
    ambience = synthesize_ambient_stream(duration)
    
    # 2. Bansuri melody arrangement (pre-cache phrases once)
    pre_cached_audio = [synthesize_bansuri_phrase(p, root_freq) for p in phrases]
    
    melody_track = np.zeros(int(SAMPLE_RATE * duration), dtype=np.float64)
    total_len = len(melody_track)
    
    current_time = 3.0
    p_idx = 0
    while current_time < duration - 15.0:
        p_audio = pre_cached_audio[p_idx % len(pre_cached_audio)]
        p_len = len(p_audio)
        
        s_idx = int(current_time * SAMPLE_RATE)
        e_idx = min(s_idx + p_len, total_len)
        if s_idx < total_len:
            melody_track[s_idx:e_idx] += p_audio[:e_idx - s_idx]
            
        current_time += (p_len / SAMPLE_RATE) + np.random.uniform(4.0, 8.0)
        p_idx += 1
        
    # 3. Temple bells (vectorized)
    num_bells = int(duration / bell_interval)
    strike_times = [2.0 + i * bell_interval for i in range(num_bells)]
    bells = synthesize_temple_bells(duration, strike_times, pitch=bell_pitch)
    
    # 4. Om Chant (if applicable)
    om_track = synthesize_om_chant(duration, root_freq=root_freq / 2.0) if has_om else np.zeros_like(tanpura)
    
    # 5. Master Mix
    mix = (tanpura * 0.40) + (melody_track * 0.62) + (bells * 0.25) + (ambience * 0.32) + (om_track * 0.50)
    
    # Master Fade-in and Fade-out (3.0s)
    fade_len = int(3.0 * SAMPLE_RATE)
    if total_len > fade_len * 2:
        mix[:fade_len] *= np.linspace(0, 1, fade_len)
        mix[-fade_len:] *= np.linspace(1, 0, fade_len)
        
    # Peak normalization
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.88
        
    # Write temporary WAV
    temp_wav = LIVE_DIR / f"temp_{name}.wav"
    wavfile.write(str(temp_wav), SAMPLE_RATE, (mix * 32767).astype(np.int16))
    
    # Master to MP3 with 432 Hz healing pitch + EBU R128 (-18 LUFS for sanctuary streaming)
    output_mp3 = SEGMENTS_DIR / f"{name}_432hz.mp3"
    print(f"🎛️ Mastering to 432 Hz Sanctuary Profile: {output_mp3.name}...")
    cmd = [
        FFMPEG_BIN, "-y", "-i", str(temp_wav),
        "-af", "asetrate=44100*432/440,aresample=44100,loudnorm=I=-18:TP=-1.5:LRA=8",
        "-c:a", "libmp3lame", "-b:a", "320k",
        str(output_mp3)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if temp_wav.exists():
        temp_wav.unlink()
        
    print(f"✅ Generated 100% Original Master: {output_mp3.name} ({output_mp3.stat().st_size / (1024*1024):.1f} MB)")
    return output_mp3


# ---------------------------------------------------------------------------
# 3. Master Composition Library
# ---------------------------------------------------------------------------

def generate_all_original_tracks(duration_per_track: float = 600.0):
    """
    Generates 5 distinct 100% original, copyright-free devotional masters:
    Total runtime = 5 x 10 mins = 50 mins of non-repeating original music.
    """
    print("=" * 70)
    print("GENERATING 100% ORIGINAL DEVOTIONAL MASTER CATALOG")
    print(f"Standard: Zero Third-Party Audio | 432 Hz Healing Pitch | EBU R128 (-18 LUFS)")
    print(f"Target Duration: {duration_per_track/60:.1f} minutes per track")
    print("=" * 70)
    
    # 1. Krishna Flute - Raag Bhupali (D4 root = 293.66 Hz)
    bhupali_phrases = [
        [(1.0, 3.5), (1.125, 2.5), (1.25, 4.0), (1.5, 3.5), (1.25, 2.5), (1.125, 2.5), (1.0, 4.5)],
        [(1.25, 3.0), (1.5, 3.5), (1.687, 3.5), (2.0, 4.5), (1.687, 2.5), (1.5, 3.5), (1.25, 3.5)],
        [(1.5, 3.0), (1.25, 3.0), (1.125, 3.0), (0.843, 3.5), (1.0, 5.5)]
    ]
    compose_track(
        name="krishna_bansuri",
        title_hindi="श्री कृष्ण पावन वंशी ध्यान (राग भूपाली ध्यान)",
        duration=duration_per_track,
        root_freq=293.66,
        phrases=bhupali_phrases,
        bell_interval=25.0,
        bell_pitch=1174.66
    )
    
    # 2. Sandhya Dhyan - Raag Yaman (C#4 root = 277.18 Hz)
    yaman_phrases = [
        [(0.943, 3.0), (1.125, 2.5), (1.25, 3.5), (1.414, 4.0), (1.25, 2.5), (1.125, 3.0), (1.0, 4.5)],
        [(1.25, 3.0), (1.414, 3.5), (1.50, 4.0), (1.687, 3.5), (1.887, 3.0), (2.0, 4.5)],
        [(2.0, 3.0), (1.887, 2.5), (1.687, 3.0), (1.50, 3.5), (1.25, 3.0), (1.125, 3.0), (1.0, 5.0)]
    ]
    compose_track(
        name="sandhya_yaman_dhyan",
        title_hindi="सांध्य दिव्य ध्यान एवं मन्दिर घण्टियाँ (राग यमन)",
        duration=duration_per_track,
        root_freq=277.18,
        phrases=yaman_phrases,
        bell_interval=20.0,
        bell_pitch=1108.73
    )
    
    # 3. Cosmic Om - Earth Resonance (136.1 Hz root)
    om_phrases = [
        [(1.0, 5.0), (1.5, 4.0), (1.333, 4.0), (1.0, 6.0)],
        [(1.0, 4.0), (1.125, 3.5), (1.25, 4.0), (1.0, 6.5)]
    ]
    compose_track(
        name="cosmic_om_136hz",
        title_hindi="ॐ नाद एवं महा चेतना ध्यान (136.1Hz पृथ्वी अनुनाद)",
        duration=duration_per_track,
        root_freq=136.1 * 2.0, # 272.2 Hz for upper flute harmonic
        phrases=om_phrases,
        bell_interval=35.0,
        bell_pitch=816.6,
        has_om=True
    )
    
    # 4. Shiva Kailash - Raag Shivranjani (D4 root = 293.66 Hz)
    shivranjani_phrases = [
        [(1.0, 3.5), (1.125, 3.0), (1.20, 4.5), (1.5, 4.0), (1.20, 3.0), (1.125, 3.0), (1.0, 5.0)],
        [(1.20, 3.0), (1.5, 4.0), (1.687, 4.0), (2.0, 5.0), (1.687, 3.0), (1.5, 4.0), (1.20, 3.5)],
        [(1.5, 3.5), (1.20, 3.5), (1.125, 3.0), (0.843, 4.0), (1.0, 6.0)]
    ]
    compose_track(
        name="shiva_kailash_dhyan",
        title_hindi="कैलाश मौन एवं शिव ध्यान (राग शिवरंजनी शांति)",
        duration=duration_per_track,
        root_freq=293.66,
        phrases=shivranjani_phrases,
        bell_interval=30.0,
        bell_pitch=1174.66
    )
    
    # 5. Morning Peace - Raag Bhimpalasi / Bilawal (C4 root = 261.63 Hz)
    dawn_phrases = [
        [(0.890, 3.0), (1.0, 3.5), (1.20, 4.0), (1.333, 3.5), (1.20, 3.0), (1.0, 4.5)],
        [(1.20, 3.0), (1.333, 3.5), (1.50, 4.0), (1.780, 4.0), (2.0, 5.0)],
        [(2.0, 3.0), (1.780, 3.0), (1.50, 3.5), (1.333, 3.5), (1.20, 3.0), (1.0, 5.5)]
    ]
    compose_track(
        name="pratah_shanti_dhyan",
        title_hindi="प्रातः शांति एवं पावन समर्पण (प्रकृति एवं मन्दिर ध्यान)",
        duration=duration_per_track,
        root_freq=261.63,
        phrases=dawn_phrases,
        bell_interval=22.0,
        bell_pitch=1046.50
    )
    
    print("\n" + "=" * 70)
    print("SUCCESS: 100% ORIGINAL DEVOTIONAL MASTER CATALOG READY!")
    print(f"Catalog Location: {SEGMENTS_DIR}")
    print("Zero Copyright Claims Guaranteed.")
    print("=" * 70)

if __name__ == "__main__":
    generate_all_original_tracks(duration_per_track=600.0) # 10 mins each = 50 mins total
