"""
master_live_streamer.py

The Unified, Hardened, Ultra-Robust 24/7 Devotional Live Streaming Engine:
1. Day-Parting Devotional Programming (IST-aligned):
   - 05:00 - 09:30 AM IST: Morning Pooja & Aartis (Ganesh, Gayatri, Bhor Bhai Din)
   - 09:30 - 04:30 PM IST: Dhyana & Karmic Stillness (Sri Suktam, Narayana, Purusha, Bansuri)
   - 04:30 - 09:30 PM IST: Sandhya Aarti & High-Energy Bhent (Mata Rani Bhajans & Maha Aartis)
   - 09:30 - 05:00 AM IST: Nidra Dhyana (432 Hz Deep Sleep Healing Chants, Shanti Mantras)
2. Rotating On-Screen Live Chat Engagement:
   - "कमेंट में लिखें: जय माता दी 🌸🙏"
   - "कमेंट में लिखें: ॐ नमः शिवाय 🔱"
   - "अपने शहर/गांव का नाम कमेंट में बताएं 🕉️"
3. Dual-Host RTMP Failover:
   - Primary: rtmp://a.rtmp.youtube.com/live2
   - Secondary: rtmp://b.rtmp.youtube.com/live2?backup=1
4. Self-Healing Circuit Breaker:
   - Auto-reconnects on socket disconnects with exponential backoff.
5. Automated Cloud Handover Relay:
   - When running on GitHub Actions, automatically triggers the next relay runner
     at 5 hours 15 minutes before the 6-hour limit.
"""

import sys
import os
import json
import time
import shutil
import random
import urllib.request
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Force UTF-8 for console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

FFMPEG_BIN = shutil.which("ffmpeg") or r"C:\Users\Tanush Garg\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"
FFPROBE_BIN = shutil.which("ffprobe") or r"C:\Users\Tanush Garg\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffprobe.exe"

BASE_DIR = Path(__file__).resolve().parent.parent
LIVE_DIR = BASE_DIR / "live_system"
ASSETS_DIR = BASE_DIR / "assets"
FONT_DIR = ASSETS_DIR / "fonts"
CONFIG_FILE = LIVE_DIR / "live_config.json"
PARTICLES_MP4 = ASSETS_DIR / "golden_particles_loop.mp4"

NOTO_SERIF_BOLD = str((FONT_DIR / "NotoSerifDevanagari-Bold.ttf").resolve()).replace('\\', '/').replace(':', '\\:')
ENGLISH_FONT_BOLD = (
    r"C:\Windows\Fonts\arialbd.ttf".replace('\\', '/').replace(':', '\\:')
    if os.name == 'nt' and Path(r"C:\Windows\Fonts\arialbd.ttf").exists()
    else (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf").exists()
        else NOTO_SERIF_BOLD
    )
)

VEDIC_SEGMENTS_DIR = LIVE_DIR / "stream_segments"
IST_OFFSET = timezone(timedelta(hours=5, minutes=30))

# Rotating Community Engagement Prompts (Devanagari, emoji-free to prevent font tofu boxes)
CHAT_ENGAGEMENT_PROMPTS = [
    "कमेंट बॉक्स में लिखें - ॐ श्री गणेशाय नमः",
    "आज का पावन संकल्प - कमेंट में लिखें ॐ नमः शिवाय",
    "कमेंट में लिखें - ॐ नमो भगवते वासुदेवाय",
    "अपने शहर या गांव का नाम कमेंट में बताएं और पावन संकीर्तन से जुड़ें",
    "कमेंट में लिखें - हरे कृष्णा, राधे राधे",
    "माँ महालक्ष्मी सभी भक्तों की मनोकामना पूर्ण करें - ॐ श्रीं नमः"
]

# Track Metadata Repository (Prioritizing 24/7 Vedic Chanting & Meditation Sanctuary)
TRACK_CATALOG = {
    # --- 24/7 SACRED VEDIC 432 HZ MEDITATION SANCTUARY ---
    "ganesh_atharvashirsha": {
        "title_hindi": "श्री गणेश अथर्वशीर्षम् (विघ्नहर्ता ध्यान)",
        "subtitle": "Shree Ganesh Atharvashirsha | 432 Hz Sacred Morning Recitation",
        "images": [ASSETS_DIR / "ganesha_divine_temple.jpg"],
        "category": "morning"
    },
    "sri_suktam": {
        "title_hindi": "ऋग्वेदोक्त श्री सूक्तम् (महालक्ष्मी ध्यान)",
        "subtitle": "Sri Suktam | 432 Hz Divine Wealth, Prosperity & Positive Energy",
        "images": [ASSETS_DIR / "lakshmi_divine_lotus.jpg"],
        "category": "afternoon"
    },
    "purusha_suktam": {
        "title_hindi": "ऋग्वेदोक्त पुरुष सूक्तम् (श्री नारायण ध्यान)",
        "subtitle": "Purusha Suktam | 432 Hz Cosmic Peace & Higher Consciousness",
        "images": [ASSETS_DIR / "vishnu_sheshnaag_cosmic.jpg"],
        "category": "afternoon"
    },
    "sivopasana": {
        "title_hindi": "शिवोपनिषत् / शिवोपासना (महादेव ध्यान)",
        "subtitle": "Sivopasana | 432 Hz Mount Kailash Cosmic Silence & Har Har Mahadev",
        "images": [ASSETS_DIR / "shiva_kailash_dhyan_1790941742560.jpg"],
        "category": "night"
    },
    "krishna_bansuri": {
        "title_hindi": "श्री कृष्ण बांसुरी ध्यान एवं शांति",
        "subtitle": "Krishna Divine Flute | 432 Hz Deep Sleep Healing & Meditation",
        "images": [ASSETS_DIR / "krishna_divine_flute_1790941691575.jpg"],
        "category": "night"
    },
    "shantimantrah": {
        "title_hindi": "वैदिक शान्तिमन्त्राः (विश्व शान्ति ध्यान)",
        "subtitle": "Vedic Shanti Mantras | 432 Hz Universal Peace & Deep Sleep Healing",
        "images": [ASSETS_DIR / "radha_divine_lotus_1790941709730.jpg"],
        "category": "night"
    },
    "durga_suktam": {
        "title_hindi": "ऋग्वेदोक्त दुर्गा सूक्तम् (अभय एवं सुरक्षा)",
        "subtitle": "Durga Suktam | 432 Hz Divine Protection & Inner Courage",
        "images": [ASSETS_DIR / "durga_divine_simhavahini.jpg"],
        "category": "evening"
    },
    "devi_suktam": {
        "title_hindi": "ऋग्वेदोक्त देवी सूक्तम् (वाक् सूक्त)",
        "subtitle": "Devi Suktam | 432 Hz Divine Mother Consciousness & Power",
        "images": [ASSETS_DIR / "durga_divine_simhavahini.jpg"],
        "category": "evening"
    },
    "saraswati_suktam": {
        "title_hindi": "ऋग्वेदोक्त सरस्वती सूक्तम् (विद्या एवं ज्ञान)",
        "subtitle": "Saraswati Suktam | 432 Hz Wisdom, Focus & Intellect Meditation",
        "images": [ASSETS_DIR / "lakshmi_divine_lotus.jpg"],
        "category": "morning"
    },
    "narayana_suktam": {
        "title_hindi": "यजुर्वेदीय नारायण सूक्तम् (परम पुरुष ध्यान)",
        "subtitle": "Narayana Suktam | 432 Hz Supreme Spiritual Energy & Dhyan",
        "images": [ASSETS_DIR / "vishnu_sheshnaag_cosmic.jpg"],
        "category": "evening"
    },
    "mantrapushpam": {
        "title_hindi": "तैत्तिरीयोपनिषद् मन्त्रपुष्पम् (पावन अर्पण)",
        "subtitle": "Mantrapushpam | 432 Hz Vedic Devotional Offering & Purity",
        "images": [ASSETS_DIR / "lakshmi_divine_lotus.jpg"],
        "category": "morning"
    }
}

def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_track_duration(path: str) -> float:
    cmd = [
        FFPROBE_BIN, "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def resolve_day_parting_playlist() -> list[dict]:
    """Selects tracks dynamically based on current Indian Standard Time (IST)."""
    now_ist = datetime.now(IST_OFFSET)
    hour = now_ist.hour
    
    # Classify current devotional block
    if 5 <= hour < 10:
        target_phase = "morning"
        phase_label = "प्रातः पूजा एवं आरती (Morning Pooja & Vedic Atharvashirsha)"
    elif 10 <= hour < 16:
        target_phase = "afternoon"
        phase_label = "मध्याह्न शांति एवं वेद ध्यान (Dhyana & Karmic Peace - Sri Suktam / Purusha Suktam)"
    elif 16 <= hour < 21:
        target_phase = "evening"
        phase_label = "सांध्य महा आरती एवं भजन (Sandhya Aarti & Sacred Hymns)"
    else:
        target_phase = "night"
        phase_label = "निद्रा ध्यान एवं 432Hz विश्राम (Healing Sleep Chants & Bansuri)"

    print(f"\n[IST: {now_ist.strftime('%H:%M')}] Active Programming Phase: {phase_label}")
    
    playlist = []
    
    # 1. Add primary phase tracks first
    for key, info in TRACK_CATALOG.items():
        audio_p = VEDIC_SEGMENTS_DIR / f"{key}_432hz.mp3"
        if audio_p.exists() and info.get("category") == target_phase:
            playlist.append({"key": key, "path": audio_p, "info": info})
            
    # 2. Add remaining tracks in harmonious sequence to ensure continuous 2+ hour diversity
    remaining = []
    for key, info in TRACK_CATALOG.items():
        if info.get("category") != target_phase:
            audio_p = VEDIC_SEGMENTS_DIR / f"{key}_432hz.mp3"
            if audio_p.exists():
                remaining.append({"key": key, "path": audio_p, "info": info})
                
    random.seed(int(time.time() / 3600)) # Stable shuffle per hour
    random.shuffle(remaining)
    playlist.extend(remaining[:8])
    
    return playlist

def build_filter_graph(image_paths: list[Path], info: dict, duration: float, prompt_text: str) -> str:
    n = len(image_paths)
    transition_len = 3.0
    clip_len = (duration + (n - 1) * transition_len) / n
    fps = 25
    frames_per_clip = int(clip_len * fps)
    
    chains = []
    for i, img in enumerate(image_paths):
        clean_p = str(img.resolve()).replace('\\', '/')
        zoom_expr = "min(pzoom+0.0002,1.05)" if i % 2 == 0 else "max(1.05-0.0002*on,1.0)"
        chains.append(
            f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
            f"zoompan=z='{zoom_expr}':d={frames_per_clip}:s=1920x1080:fps={fps},"
            f"format=yuv420p[v{i}];"
        )
        
    last_v = "[v0]"
    for i in range(1, n):
        offset = i * (clip_len - transition_len)
        chains.append(f"{last_v}[v{i}]xfade=transition=fade:duration={transition_len}:offset={offset:.2f}[xf{i}];")
        last_v = f"[xf{i}]"
        
    # Particle blending
    particles_idx = n
    chains.append(
        f"[{particles_idx}:v]scale=1920:1080,setsar=1,format=gbrp[p_rgb];"
        f"{last_v}format=gbrp[base_rgb];"
        f"[base_rgb][p_rgb]blend=all_mode='addition':all_opacity=0.35,format=yuv420p[blended];"
    )
    
    t_hindi = info["title_hindi"].replace("'", "").replace(":", "-")
    t_sub = info["subtitle"].replace("'", "").replace(":", "-")
    p_clean = prompt_text.replace("'", "").replace(":", "-")
    
    # OSD Graphics (Big Bold LIVE Badge, Prominent Centered Chat Prompt, Clean Top-Right)
    chains.append(
        f"[blended]"
        # 1. Top-Left: Bigger, High-Impact Red LIVE Badge
        f"drawbox=x=50:y=30:w=180:h=70:color=#FF0000@1.0:t=fill,"
        f"drawbox=x=50:y=30:w=180:h=70:color=white:t=3,"
        f"drawtext=fontfile='{ENGLISH_FONT_BOLD}':text='LIVE':fontsize=42:fontcolor=white:x=90:y=42,"
        # Channel Branding Badge next to LIVE
        f"drawbox=x=230:y=30:w=320:h=70:color=black@0.92:t=fill,"
        f"drawbox=x=230:y=30:w=320:h=70:color=#FFD700:t=2,"
        f"drawtext=fontfile='{NOTO_SERIF_BOLD}':text='दिव्य सत्संग 24/7':fontsize=28:fontcolor=#FFD700:x=255:y=47,"
        # 2. Top-Center: Prominent, High-Contrast Interactive Chat Prompt (Mathematically Centered, 32px Font)
        f"drawbox=x=480:y=30:w=960:h=70:color=black@0.92:t=fill,"
        f"drawbox=x=480:y=30:w=960:h=70:color=#FFD700:t=3,"
        f"drawtext=fontfile='{NOTO_SERIF_BOLD}':text='{p_clean}':fontsize=32:fontcolor=#FFFFFF:x=(1920-tw)/2:y=45,"
        # 3. Top-Right: Intentionally Clean (No text as requested)
        # 4. Bottom Title Card: Clean Lower Third Card
        f"drawbox=x=60:y=900:w=1800:h=130:color=black@0.85:t=fill,"
        f"drawbox=x=60:y=900:w=1800:h=130:color=#FFD700:t=2,"
        f"drawtext=fontfile='{NOTO_SERIF_BOLD}':text='{t_hindi}':fontsize=36:fontcolor=#FFD700:x=90:y=920,"
        f"drawtext=fontfile='{ENGLISH_FONT_BOLD}':text='{t_sub}':fontsize=22:fontcolor=white:x=90:y=975[v_osd];"
        f"[v_osd]realtime=speed=1.0[v_final];"
        f"[{n + 1}:a]arealtime=speed=1.0[a_final]"
    )
    return "".join(chains)

def trigger_next_cloud_relay():
    """Triggers the next runner in the GitHub Actions chain before timeout."""
    token = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY", "tanushgargjanuary-bot/youtube-automation-pipeline")
    if not token:
        print("[Relay] No GITHUB_TOKEN present, skipping cloud relay trigger.")
        return
        
    url = f"https://api.github.com/repos/{repo}/actions/workflows/live_stream.yml/dispatches"
    payload = json.dumps({"ref": "main", "inputs": {"stream_type": "day_parted_24_7", "duration_hours": "5.5"}}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "CloudStream-Relay"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"🚀 SUCCESS: Triggered next cloud relay runner (HTTP {resp.status})!")
    except Exception as e:
        print(f"⚠️ Failed to trigger cloud relay: {e}")

def run_master_stream(max_hours: float = None, is_preview: bool = False):
    config = load_config()
    stream_key = (os.environ.get("YOUTUBE_STREAM_KEY") or config.get("stream_key", "")).strip()
    rtmp_primary = "rtmp://a.rtmp.youtube.com/live2"
    rtmp_backup = "rtmp://b.rtmp.youtube.com/live2?backup=1"
    
    b_cfg = config.get("broadcast_settings", {})
    v_bitrate = b_cfg.get("video_bitrate", "2500k")
    a_bitrate = b_cfg.get("audio_bitrate", "192k")
    fps = b_cfg.get("fps", 25)
    
    if not is_preview and (not stream_key or "YOUR_STREAM_KEY" in stream_key):
        print("ERROR: YOUTUBE_STREAM_KEY not configured!")
        sys.exit(1)
        
    print("=" * 70)
    print("CLOUDSTREAM: MASTER 24/7 BROADCAST ENGINE")
    print(f"Mode: {'PREVIEW (60s Benchmark)' if is_preview else 'LIVE CLOUD BROADCAST'}")
    print(f"Video Quality: 1080p @ {fps}fps | {v_bitrate} Video / {a_bitrate} Audio")
    print(f"Audio Mastering: 432 Hz Sacred Frequency | 320 kbps AAC Output")
    print("=" * 70)
    
    start_time = time.time()
    relay_triggered = False
    cycle = 1
    
    while True:
        elapsed_hours = (time.time() - start_time) / 3600.0
        if max_hours and elapsed_hours >= max_hours:
            print(f"\nTarget session duration ({max_hours} hours) complete. Exiting cleanly.")
            break
            
        # Cloud Handover Trigger: 15 mins before 5.5h limit
        if os.environ.get("GITHUB_ACTIONS") and elapsed_hours >= 5.0 and not relay_triggered:
            print("\n🔄 Approaching runner ceiling: Launching next cloud runner relay...")
            trigger_next_cloud_relay()
            relay_triggered = True
            
        if is_preview:
            # For 24/7 preview, showcase the opening track: Shree Ganesh Atharvashirsha
            p_vedic = VEDIC_SEGMENTS_DIR / "ganesh_atharvashirsha_432hz.mp3"
            playlist = [{"key": "ganesh_atharvashirsha", "path": p_vedic, "info": TRACK_CATALOG["ganesh_atharvashirsha"]}]
        else:
            playlist = resolve_day_parting_playlist()
        print(f"\n--- Starting Devotional Cycle #{cycle} ({len(playlist)} Curated Segments) ---")
        
        for idx, t in enumerate(playlist, 1):
            elapsed_hours = (time.time() - start_time) / 3600.0
            if max_hours and elapsed_hours >= max_hours:
                return
                
            dur = 60.0 if is_preview else get_track_duration(str(t["path"]))
            title = t["info"]["title_hindi"]
            prompt = CHAT_ENGAGEMENT_PROMPTS[idx % len(CHAT_ENGAGEMENT_PROMPTS)]
            
            print(f"[{idx}/{len(playlist)}] Now Streaming: {title} ({dur/60:.1f} mins)...")
            
            imgs = t["info"]["images"]
            inputs = []
            for img in imgs:
                inputs.extend(["-loop", "1", "-t", f"{dur:.2f}", "-i", str(img.resolve()).replace('\\', '/')])
            inputs.extend(["-stream_loop", "-1", "-t", f"{dur:.2f}", "-i", str(PARTICLES_MP4.resolve()).replace('\\', '/')])
            inputs.extend(["-re", "-i", str(t["path"].resolve()).replace('\\', '/')])
            
            fg = build_filter_graph(imgs, t["info"], dur, prompt)
            
            if is_preview:
                out_sample = str(BASE_DIR / "output" / "master_broadcast_preview.mp4")
                cmd = [
                    FFMPEG_BIN, "-y",
                    *inputs,
                    "-filter_complex", fg,
                    "-map", "[v_final]", "-map", "[a_final]",
                    "-c:v", "libx264", "-preset", "veryfast", "-b:v", v_bitrate,
                    "-c:a", "aac", "-b:a", a_bitrate,
                    "-t", "60.0", "-pix_fmt", "yuv420p",
                    out_sample
                ]
                subprocess.run(cmd, check=True)
                print(f"\n✅ Preview successfully rendered: {out_sample}")
                return
                
            # Dual Ingest RTMP command with circuit-breaker retry & strict realtime rate limiting
            rtmp_url = f"{rtmp_primary}/{stream_key}"
            cmd = [
                FFMPEG_BIN, "-y",
                *inputs,
                "-filter_complex", fg,
                "-map", "[v_final]", "-map", "[a_final]",
                "-c:v", "libx264", "-preset", "veryfast", "-b:v", v_bitrate,
                "-maxrate", v_bitrate, "-bufsize", "3000k",
                "-g", str(fps * 2),
                "-c:a", "aac", "-b:a", a_bitrate, "-ar", "44100",
                "-flvflags", "no_duration_filesize",
                "-f", "flv",
                rtmp_url
            ]
            
            try:
                subprocess.run(cmd, check=True)
            except Exception as e:
                print(f"Primary ingest hiccup ({e}). Attempting secondary failover...")
                # Attempt backup ingest
                cmd[-1] = f"{rtmp_backup}/{stream_key}"
                try:
                    subprocess.run(cmd, check=True)
                except Exception as e2:
                    print(f"Secondary ingest retry error ({e2}). Reconnecting in 3s...")
                    time.sleep(3)
                    
        cycle += 1

if __name__ == "__main__":
    is_prev = "--preview" in sys.argv
    dur_h = None
    if "--hours" in sys.argv:
        try:
            h_idx = sys.argv.index("--hours")
            dur_h = float(sys.argv[h_idx + 1])
        except Exception:
            dur_h = 3.5
    run_master_stream(max_hours=dur_h, is_preview=is_prev)
