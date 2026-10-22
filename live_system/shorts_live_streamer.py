"""
shorts_live_streamer.py

Dedicated 9:16 Vertical YouTube Shorts 24/7 Live Streaming Engine:
1. Native 1080x1920 Vertical Aspect Ratio for YouTube mobile Shorts Feed.
2. Mobile UI Safe-Zone Compliance:
   - Top 10%: Red LIVE badge & channel brand.
   - Upper-Middle (y=210..295): Prominent Devanagari interactive chat prompt.
   - Center (y=300..1120): Unobstructed Sacred Deity Darshan.
   - Lower-Middle (y=1120..1260): Devanagari hymn title card.
   - Bottom 35% (y=1260..1920): Clear for YouTube mobile chat & Subscribe overlay.
3. 432 Hz Sacred Vedic Chanting & Meditation Sanctuary.
4. Auto-relay chaining before 5.5 hours via GitHub Actions API.
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

CHAT_ENGAGEMENT_PROMPTS = [
    "कमेंट बॉक्स में लिखें - ॐ श्री गणेशाय नमः",
    "आज का पावन संकल्प - कमेंट में लिखें ॐ नमः शिवाय",
    "कमेंट में लिखें - ॐ नमो भगवते वासुदेवाय",
    "अपने शहर या गांव का नाम कमेंट में बताएं",
    "कमेंट में लिखें - हरे कृष्णा, राधे राधे",
    "माँ महालक्ष्मी का पावन आशीर्वाद - ॐ श्रीं नमः"
]

SHORTS_CATALOG = {
    "ganesh_atharvashirsha": {
        "title_hindi": "श्री गणेश अथर्वशीर्षम् (विघ्नहर्ता ध्यान)",
        "subtitle": "Shree Ganesh Atharvashirsha | 432 Hz",
        "images": [ASSETS_DIR / "ganesha_divine_temple.jpg"]
    },
    "sri_suktam": {
        "title_hindi": "ऋग्वेदोक्त श्री सूक्तम् (महालक्ष्मी ध्यान)",
        "subtitle": "Sri Suktam | Divine Wealth & Peace | 432 Hz",
        "images": [ASSETS_DIR / "lakshmi_divine_lotus.jpg"]
    },
    "purusha_suktam": {
        "title_hindi": "ऋग्वेदोक्त पुरुष सूक्तम् (नारायण ध्यान)",
        "subtitle": "Purusha Suktam | Cosmic Consciousness | 432 Hz",
        "images": [ASSETS_DIR / "vishnu_sheshnaag_cosmic.jpg"]
    },
    "krishna_bansuri": {
        "title_hindi": "श्री कृष्ण बांसुरी ध्यान एवं शांति",
        "subtitle": "Krishna Divine Flute | Deep Meditation | 432 Hz",
        "images": [ASSETS_DIR / "krishna_divine_flute_1790941691575.jpg"]
    },
    "saraswati_suktam": {
        "title_hindi": "ऋग्वेदोक्त सरस्वती सूक्तम् (विद्या एवं ज्ञान)",
        "subtitle": "Saraswati Suktam | Wisdom & Intellect | 432 Hz",
        "images": [ASSETS_DIR / "lakshmi_divine_lotus.jpg"]
    },
    "narayana_suktam": {
        "title_hindi": "यजुर्वेदीय नारायण सूक्तम् (परम पुरुष ध्यान)",
        "subtitle": "Narayana Suktam | Supreme Energy | 432 Hz",
        "images": [ASSETS_DIR / "vishnu_sheshnaag_cosmic.jpg"]
    },
    "mantrapushpam": {
        "title_hindi": "तैत्तिरीयोपनिषद् मन्त्रपुष्पम् (पावन अर्पण)",
        "subtitle": "Mantrapushpam | Devotional Offering | 432 Hz",
        "images": [ASSETS_DIR / "lakshmi_divine_lotus.jpg"]
    }
}

def get_track_duration(path: str) -> float:
    cmd = [
        FFPROBE_BIN, "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def build_vertical_filter_graph(image_paths: list[Path], info: dict, duration: float, prompt_text: str) -> str:
    n = len(image_paths)
    transition_len = 3.0
    clip_len = (duration + (n - 1) * transition_len) / n
    fps = 25
    frames_per_clip = int(clip_len * fps)
    
    chains = []
    for i, img in enumerate(image_paths):
        clean_p = str(img.resolve()).replace('\\', '/')
        zoom_expr = "min(pzoom+0.0002,1.04)" if i % 2 == 0 else "max(1.04-0.0002*on,1.0)"
        chains.append(
            f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='{zoom_expr}':d={frames_per_clip}:s=1080x1920:fps={fps},"
            f"format=yuv420p[v{i}];"
        )
        
    last_v = "[v0]"
    for i in range(1, n):
        offset = i * (clip_len - transition_len)
        chains.append(f"{last_v}[v{i}]xfade=transition=fade:duration={transition_len}:offset={offset:.2f}[xf{i}];")
        last_v = f"[xf{i}]"
        
    # Particle blending scaled to 1080x1920
    particles_idx = n
    chains.append(
        f"[{particles_idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,format=gbrp[p_rgb];"
        f"{last_v}format=gbrp[base_rgb];"
        f"[base_rgb][p_rgb]blend=all_mode='addition':all_opacity=0.35,format=yuv420p[blended];"
    )
    
    t_hindi = info["title_hindi"].replace("'", "").replace(":", "-")
    t_sub = info["subtitle"].replace("'", "").replace(":", "-")
    p_clean = prompt_text.replace("'", "").replace(":", "-")
    
    # Vertical Safe-Zone OSD (Optimized for Mobile Shorts Swipe Feed)
    chains.append(
        f"[blended]"
        # 1. Top Bar: Red LIVE Badge + Channel Name (y=100)
        f"drawbox=x=80:y=100:w=180:h=75:color=#FF0000@1.0:t=fill,"
        f"drawbox=x=80:y=100:w=180:h=75:color=white:t=3,"
        f"drawtext=fontfile='{ENGLISH_FONT_BOLD}':text='LIVE':fontsize=44:fontcolor=white:x=120:y=115,"
        f"drawbox=x=280:y=100:w=480:h=75:color=black@0.90:t=fill,"
        f"drawbox=x=280:y=100:w=480:h=75:color=#FFD700:t=2,"
        f"drawtext=fontfile='{NOTO_SERIF_BOLD}':text='दिव्य सत्संग 24/7':fontsize=32:fontcolor=#FFD700:x=315:y=120,"
        # 2. Upper-Middle Safe Zone: Interactive Live Chat Prompt (y=210..295)
        f"drawbox=x=80:y=210:w=920:h=85:color=black@0.92:t=fill,"
        f"drawbox=x=80:y=210:w=920:h=85:color=#FFD700:t=3,"
        f"drawtext=fontfile='{NOTO_SERIF_BOLD}':text='{p_clean}':fontsize=34:fontcolor=#FFFFFF:x=(1080-tw)/2:y=232,"
        # 3. Lower-Middle Title Card (y=1120..1260) - Bottom 35% left clear for YouTube UI
        f"drawbox=x=60:y=1120:w=960:h=140:color=black@0.90:t=fill,"
        f"drawbox=x=60:y=1120:w=960:h=140:color=#FFD700:t=2,"
        f"drawtext=fontfile='{NOTO_SERIF_BOLD}':text='{t_hindi}':fontsize=36:fontcolor=#FFD700:x=(1080-tw)/2:y=1142,"
        f"drawtext=fontfile='{ENGLISH_FONT_BOLD}':text='{t_sub}':fontsize=24:fontcolor=white:x=(1080-tw)/2:y=1205[v_osd];"
        f"[v_osd]realtime=speed=1.0[v_final];"
        f"[{n + 1}:a]arealtime=speed=1.0[a_final]"
    )
    return "".join(chains)

def trigger_next_shorts_relay():
    """Triggers the next runner in the GitHub Actions chain before timeout."""
    token = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY", "tanushgargjanuary-bot/youtube-automation-pipeline")
    if not token:
        print("[Relay] No token present, skipping cloud relay trigger.")
        return
        
    url = f"https://api.github.com/repos/{repo}/actions/workflows/shorts_live.yml/dispatches"
    payload = json.dumps({"ref": "main"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "ShortsLive-Relay"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"🚀 SUCCESS: Triggered next Shorts cloud relay runner (HTTP {resp.status})!")
    except Exception as e:
        print(f"⚠️ Failed to trigger Shorts cloud relay: {e}")

def run_shorts_live_stream(max_hours: float = None, is_preview: bool = False):
    stream_key = (os.environ.get("YOUTUBE_SHORTS_STREAM_KEY") or os.environ.get("YOUTUBE_STREAM_KEY") or "").strip()
    rtmp_primary = "rtmp://a.rtmp.youtube.com/live2"
    rtmp_backup = "rtmp://b.rtmp.youtube.com/live2?backup=1"
    
    # 9:16 vertical broadcast bitrate: 3000k video, 192k audio, 25fps
    v_bitrate = "3000k"
    a_bitrate = "192k"
    fps = 25
    
    if not is_preview and not stream_key:
        print("ERROR: YOUTUBE_SHORTS_STREAM_KEY or YOUTUBE_STREAM_KEY not configured!")
        sys.exit(1)
        
    print("=" * 70)
    print("CLOUD BROADCAST: VERTICAL 9:16 MOBILE 24/7 STREAM RELAY")
    print(f"Mode: {'PREVIEW (60s Benchmark)' if is_preview else 'LIVE MOBILE FEED BROADCAST'}")
    print(f"Resolution: 1080x1920 (9:16 Vertical) @ {fps}fps")
    print(f"Video Bitrate: {v_bitrate} | Audio Bitrate: {a_bitrate} (432 Hz Mastered)")
    print("=" * 70)
    
    # Build playlist from catalog
    playlist = []
    for k, info in SHORTS_CATALOG.items():
        p = VEDIC_SEGMENTS_DIR / f"{k}_432hz.mp3"
        if p.exists():
            playlist.append({"key": k, "path": p, "info": info})
            
    if not playlist:
        print("No valid audio files found in stream_segments!")
        sys.exit(1)
        
    start_time = time.time()
    relay_triggered = False
    cycle = 1
    
    while True:
        elapsed_hours = (time.time() - start_time) / 3600.0
        if max_hours and elapsed_hours >= max_hours:
            print(f"\nTarget session duration ({max_hours} hours) complete. Exiting cleanly.")
            break
            
        if os.environ.get("GITHUB_ACTIONS") and elapsed_hours >= 5.0 and not relay_triggered:
            print("\n🔄 Approaching runner ceiling: Launching next Shorts cloud runner relay...")
            trigger_next_shorts_relay()
            relay_triggered = True
            
        print(f"\n--- Starting Shorts Devotional Cycle #{cycle} ({len(playlist)} Segments) ---")
        
        for idx, t in enumerate(playlist, 1):
            elapsed_hours = (time.time() - start_time) / 3600.0
            if max_hours and elapsed_hours >= max_hours:
                return
                
            dur = 60.0 if is_preview else get_track_duration(str(t["path"]))
            title = t["info"]["title_hindi"]
            prompt = CHAT_ENGAGEMENT_PROMPTS[idx % len(CHAT_ENGAGEMENT_PROMPTS)]
            
            print(f"[{idx}/{len(playlist)}] Now Streaming Shorts Feed: {title} ({dur/60:.1f} mins)...")
            
            imgs = t["info"]["images"]
            inputs = []
            for img in imgs:
                inputs.extend(["-loop", "1", "-t", f"{dur:.2f}", "-i", str(img.resolve()).replace('\\', '/')])
            inputs.extend(["-stream_loop", "-1", "-t", f"{dur:.2f}", "-i", str(PARTICLES_MP4.resolve()).replace('\\', '/')])
            inputs.extend(["-re", "-i", str(t["path"].resolve()).replace('\\', '/')])
            
            fg = build_vertical_filter_graph(imgs, t["info"], dur, prompt)
            
            if is_preview:
                out_sample = str(BASE_DIR / "output" / "shorts_broadcast_preview.mp4")
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
                print(f"\n✅ Shorts Preview successfully rendered: {out_sample}")
                return
                
            rtmp_url = f"{rtmp_primary}/{stream_key}"
            cmd = [
                FFMPEG_BIN, "-y",
                *inputs,
                "-filter_complex", fg,
                "-map", "[v_final]", "-map", "[a_final]",
                "-c:v", "libx264", "-preset", "veryfast", "-b:v", v_bitrate,
                "-maxrate", v_bitrate, "-bufsize", "4000k",
                "-g", str(fps * 2),
                "-c:a", "aac", "-b:a", a_bitrate, "-ar", "44100",
                "-flvflags", "no_duration_filesize",
                "-f", "flv",
                rtmp_url
            ]
            
            try:
                subprocess.run(cmd, check=True)
            except Exception as e:
                print(f"Primary Shorts ingest hiccup ({e}). Attempting secondary failover...")
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
            dur_h = 5.5
    run_shorts_live_stream(max_hours=dur_h, is_preview=is_prev)
