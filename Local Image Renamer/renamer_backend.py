"""
Local bulk-image renamer/describer
————————————————————————————————————
FastAPI back-end + embedded Gradio UI
"""

import asyncio
import base64
import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
import textwrap
import uuid
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from io import BytesIO

import httpx
import openai
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from rapidfuzz import process, fuzz
import gradio as gr

# Load environment variables
load_dotenv()

# ────────────────────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434"
MODEL_NAME   = (
    Path(".last_model").read_text().strip()
    if Path(".last_model").exists()
    else "qwen2.5vl:latest"
)
OUT_DIR      = Path("output")
GEN_DIR      = Path("generated")
DB           = Path("files.db")
CAPTION_PROMPT = "Describe the image in factual, neutral detail. Avoid moral judgments."
SEO_PROMPT_TMPL = textwrap.dedent(
    """\
    You are an SEO assistant.
    Given the caption below, output JSON with keys:
    "keywords"  = ≤15 comma-separated keywords,
    "summary"   = <120-character abstract.
    Caption: \"\"\"{caption}\"\"\"
"""
)

# OpenAI Configuration
openai.api_key = os.getenv("OPENAI_API_KEY")
FLUX_API_KEY = os.getenv("FLUX_API_KEY")

# ────────────────────────────────────────────────────────────────────────────
# DATABASE
# ────────────────────────────────────────────────────────────────────────────
def init_db() -> None:
    con = sqlite3.connect(DB)
    con.execute(
        """CREATE TABLE IF NOT EXISTS images(
             id TEXT PRIMARY KEY,
             orig_path TEXT,
             new_path TEXT,
             caption TEXT,
             keywords TEXT,
             ts TEXT,
             group_id TEXT)"""
    )
    con.execute("CREATE INDEX IF NOT EXISTS idx_caption ON images(caption)")
    con.close()


init_db()
GEN_DIR.mkdir(exist_ok=True)

# ────────────────────────────────────────────────────────────────────────────
# FASTAPI APP
# ────────────────────────────────────────────────────────────────────────────
app = FastAPI(title="Local Image Renamer")

# serve static files (logo, generated images)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/static/generated", StaticFiles(directory="generated"), name="generated")

# ────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ────────────────────────────────────────────────────────────────────────────
async def call_ollama(image_bytes: bytes) -> str:
    """Send an image and get a caption string."""
    b64 = base64.b64encode(image_bytes).decode()
    payload = {
        "model": MODEL_NAME,
        "prompt": CAPTION_PROMPT,
        "images": [b64],
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
        r.raise_for_status()
        return r.json()["response"].strip()


async def seo_tags(caption: str) -> Dict[str, str]:
    payload = {
        "model": MODEL_NAME,
        "prompt": SEO_PROMPT_TMPL.format(caption=caption),
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
        r.raise_for_status()
        text = r.json()["response"]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # naive fallback
            parts = text.splitlines()
            return {"keywords": parts[0] if parts else "", "summary": caption[:118]}


def safe_name(s: str, ext: str) -> str:
    keep = "".join(c if c.isalnum() or c in " _-" else "_" for c in s)
    return (keep[:56] + ext).strip()


def write_metadata(path: Path, caption: str, keywords: str) -> None:
    subprocess.run(
        [
            "exiftool",
            f"-IPTC:Keywords={keywords}",
            f"-IPTC:Caption-Abstract={caption}",
            "-overwrite_original",
            str(path),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


# ────────────────────────────────────────────────────────────────────────────
# BACKGROUND JOB
# ────────────────────────────────────────────────────────────────────────────
async def process_files(file_paths: List[Path]) -> Dict[str, List[str]]:
    OUT_DIR.mkdir(exist_ok=True)
    groups: Dict[str, List[str]] = {}
    con = sqlite3.connect(DB)
    cur = con.cursor()

    for fp in file_paths:
        img_bytes = fp.read_bytes()
        caption = await call_ollama(img_bytes)
        seo = await seo_tags(caption)
        base = caption.split(",")[0][:56]  # crude base
        new_name = safe_name(base, fp.suffix.lower())

        # fuzzy duplicates
        if groups:
            match, score, gid = (
                process.extractOne(
                    new_name, [(k, k) for k in groups.keys()], scorer=fuzz.ratio
                )
                or (None, 0, None)
            )
            if score > 85:
                group_key = match
            else:
                group_key = new_name
        else:
            group_key = new_name

        # ensure uniqueness inside group
        counter = 1
        orig_stem = new_name
        while (OUT_DIR / group_key / new_name).exists():
            new_name = f"{orig_stem}_{counter:02d}{fp.suffix.lower()}"
            counter += 1

        tgt_dir = OUT_DIR / group_key
        tgt_dir.mkdir(exist_ok=True)
        tgt = tgt_dir / new_name
        shutil.copy2(fp, tgt)

        # metadata
        write_metadata(tgt, caption, seo["keywords"])

        # DB
        rec_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO images VALUES (?,?,?,?,?,?,?)",
            (
                rec_id,
                str(fp),
                str(tgt),
                caption,
                seo["keywords"],
                datetime.utcnow().isoformat(),
                group_key,
            ),
        )
        groups.setdefault(group_key, []).append(new_name)

    con.commit()
    con.close()

    # one-offs
    for k, lst in list(groups.items()):
        if len(lst) < 3:
            one_off = OUT_DIR / "one-offs"
            one_off.mkdir(exist_ok=True)
            for name in lst:
                shutil.move(str(OUT_DIR / k / name), one_off / name)
            (OUT_DIR / k).rmdir()
            groups.pop(k)
            groups.setdefault("one-offs", []).extend(lst)

    return groups


# ────────────────────────────────────────────────────────────────────────────
# IMAGE GENERATION UTILITIES
# ────────────────────────────────────────────────────────────────────────────
async def generate_dalle_image(prompt: str, model: str = "dall-e-3", size: str = "1024x1024") -> str:
    """Generate image using OpenAI DALL-E."""
    if not openai.api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    try:
        response = openai.images.generate(
            model=model,
            prompt=prompt,
            n=1,
            size=size,
            response_format="url"
        )
        return response.data[0].url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


async def generate_flux_image(prompt: str, negative_prompt: str = "", aspect_ratio: str = "1:1") -> str:
    """Generate image using Flux.1 API."""
    if not FLUX_API_KEY:
        raise HTTPException(status_code=400, detail="Flux API key not configured")
    
    try:
        response = requests.post(
            "https://api.bfl.ai/kontext/text-to-image",
            headers={"Authorization": FLUX_API_KEY},
            json={
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "aspect_ratio": aspect_ratio,
                "style": "default"
            }
        )
        response.raise_for_status()
        data = response.json()
        image_url = data.get("data", {}).get("url", "")
        if not image_url:
            raise HTTPException(status_code=500, detail="No image returned from Flux.1")
        return image_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flux generation failed: {str(e)}")


async def save_generated_image(image_url: str, filename: str) -> Path:
    """Download and save generated image."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        
        filepath = GEN_DIR / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            f.write(response.content)
        return filepath
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")


def cleanup_old_files():
    """Clean up old generated files (24 hour TTL)."""
    ttl_seconds = 86400  # 24 hours
    now = time.time()
    
    for filepath in GEN_DIR.rglob("*"):
        if filepath.is_file() and filepath.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            if now - filepath.stat().st_mtime > ttl_seconds:
                try:
                    filepath.unlink()
                except Exception:
                    pass


# ────────────────────────────────────────────────────────────────────────────
# ROUTES
# ────────────────────────────────────────────────────────────────────────────
@app.post("/upload")
async def upload(files: List[UploadFile] = File(...), bg: BackgroundTasks = None):
    tmp_dir = Path(tempfile.mkdtemp())
    paths = []
    for uf in files:
        dest = tmp_dir / uf.filename
        with dest.open("wb") as fh:
            while chunk := await uf.read(1024 * 1024):
                fh.write(chunk)
        paths.append(dest)

    groups = await process_files(paths)
    return {"status": "ok", "groups": groups}


@app.post("/generate")
async def generate_images(
    prompt_file: UploadFile = File(...),
    model: str = Form("dall-e-3"),
    image_size: str = Form("1024x1024")
):
    """Generate images from prompts using OpenAI DALL-E."""
    session_id = str(uuid.uuid4())
    session_dir = GEN_DIR / session_id
    session_dir.mkdir(parents=True)
    
    # Save uploaded prompt file
    file_path = session_dir / prompt_file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(prompt_file.file, f)
    
    # Parse prompts from file
    prompts = []
    try:
        if file_path.suffix == ".json":
            with open(file_path, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and "prompts" in data:
                    prompts = data["prompts"]
                elif isinstance(data, list):
                    prompts = data
        elif file_path.suffix == ".jsonl":
            with open(file_path, "r") as f:
                prompts = [json.loads(line)["prompt"] for line in f if line.strip()]
        else:
            with open(file_path, "r") as f:
                prompts = [line.strip() for line in f if line.strip()]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse prompts: {str(e)}")
    
    if not prompts or len(prompts) > 100:
        raise HTTPException(status_code=400, detail="Invalid number of prompts (1-100 allowed)")
    
    # Generate images
    generated_files = []
    for i, prompt in enumerate(prompts, 1):
        if len(prompt) > 500:
            raise HTTPException(status_code=400, detail=f"Prompt {i} too long (max 500 chars)")
        
        try:
            image_url = await generate_dalle_image(prompt, model, image_size)
            filename = f"img_{i:03d}.png"
            filepath = await save_generated_image(image_url, f"{session_id}/{filename}")
            generated_files.append(filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate image {i}: {str(e)}")
    
    return {
        "status": "success",
        "session_id": session_id,
        "generated_files": generated_files,
        "count": len(generated_files)
    }


@app.post("/generate-flux")
async def generate_flux(
    prompt: str = Form(...),
    negative_prompt: str = Form(""),
    aspect_ratio: str = Form("1:1")
):
    """Generate image using Flux.1 API."""
    session_id = str(uuid.uuid4())
    
    try:
        image_url = await generate_flux_image(prompt, negative_prompt, aspect_ratio)
        filename = f"flux_{session_id}.png"
        filepath = await save_generated_image(image_url, filename)
        
        return {
            "status": "success",
            "image_path": f"/static/generated/{filename}",
            "url": image_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/edit-image")
async def edit_image(
    original_image: UploadFile = File(...),
    mask_image: UploadFile = File(...),
    prompt: str = Form(...),
    model: str = Form("dall-e-2"),
    image_size: str = Form("1024x1024")
):
    """Edit image using OpenAI image editing."""
    if not openai.api_key:
        raise HTTPException(status_code=400, detail="OpenAI API key not configured")
    
    try:
        # Read image files
        orig_bytes = await original_image.read()
        mask_bytes = await mask_image.read()
        
        # Convert to base64
        orig_b64 = base64.b64encode(orig_bytes).decode("utf-8")
        mask_b64 = base64.b64encode(mask_bytes).decode("utf-8")
        
        # Call OpenAI API
        response = openai.images.edit(
            model=model,
            prompt=prompt,
            image=orig_b64,
            mask=mask_b64,
            size=image_size,
            response_format="url"
        )
        
        # Save result
        session_id = str(uuid.uuid4())
        filename = f"edited_{session_id}.png"
        filepath = await save_generated_image(response.data[0].url, filename)
        
        return {
            "status": "success",
            "image_path": f"/static/generated/{filename}",
            "url": response.data[0].url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image editing failed: {str(e)}")


# ────────────────────────────────────────────────────────────────────────────
# GRADIO UI
# ────────────────────────────────────────────────────────────────────────────
def gr_upload(file_objs):
    paths = [Path(f.name) for f in file_objs]
    files = [("files", open(p, "rb")) for p in paths]
    resp = httpx.post("http://localhost:5000/upload", files=files, timeout=None)
    resp.raise_for_status()
    return json.dumps(resp.json()["groups"], indent=2)


with gr.Blocks(title="Local Image Renamer") as demo:
    gr.Markdown("# Bulk Image Renamer & Describer")
    with gr.Row():
        files = gr.Files(
            file_types=["image"], label="Drop or select up to 1 000 images"
        )
    out = gr.JSON(label="Grouping result")
    files.change(fn=gr_upload, inputs=[files], outputs=[out])

    gr.Markdown("---")
    gr.HTML(
        '<div style="text-align:center; opacity:0.6; font-size:0.8rem;">'
        '<img src="/static/Seed_13_logo.jpg" '
        'style="height:40px; vertical-align:middle; max-height:40px;"> '
        "© 2024 Seed 13 — all rights reserved.</div>"
    )

app = gr.mount_gradio_app(app, demo, path="/gradio")


# ────────────────────────────────────────────────────────────────────────────
# STARTUP/SHUTDOWN
# ────────────────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Clean up old files on startup."""
    cleanup_old_files()


# ────────────────────────────────────────────────────────────────────────────
# ROOT (redirect)
# ────────────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def _root():
    return '<meta http-equiv="refresh" content="0; url=/gradio">'