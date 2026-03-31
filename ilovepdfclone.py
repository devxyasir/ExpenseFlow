from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import Flowable

# ─── Color Palette ───────────────────────────────────────────────────────────
DARK_BG      = colors.HexColor("#0F172A")
ACCENT       = colors.HexColor("#6366F1")
ACCENT2      = colors.HexColor("#8B5CF6")
SUCCESS      = colors.HexColor("#10B981")
WARNING      = colors.HexColor("#F59E0B")
DANGER       = colors.HexColor("#EF4444")
CODE_BG      = colors.HexColor("#1E293B")
CODE_TEXT    = colors.HexColor("#E2E8F0")
HEADER_TEXT  = colors.white
BODY_TEXT    = colors.HexColor("#1E293B")
MUTED        = colors.HexColor("#64748B")
LIGHT_BORDER = colors.HexColor("#E2E8F0")
SECTION_BG   = colors.HexColor("#F8FAFC")
PURPLE_LIGHT = colors.HexColor("#EDE9FE")
GREEN_LIGHT  = colors.HexColor("#D1FAE5")
BLUE_LIGHT   = colors.HexColor("#DBEAFE")
ORANGE_LIGHT = colors.HexColor("#FEF3C7")

W, H = A4

# ─── Custom Flowables ─────────────────────────────────────────────────────────

class ColoredRect(Flowable):
    def __init__(self, width, height, fill_color, radius=4):
        super().__init__()
        self.width = width
        self.height = height
        self.fill_color = fill_color
        self.radius = radius

    def draw(self):
        self.canv.setFillColor(self.fill_color)
        self.canv.roundRect(0, 0, self.width, self.height, self.radius, fill=1, stroke=0)


class SectionHeader(Flowable):
    """Full-width colored section header bar."""
    def __init__(self, text, bg=ACCENT, fg=colors.white, font_size=14, height=36):
        super().__init__()
        self.text = text
        self.bg = bg
        self.fg = fg
        self.font_size = font_size
        self.height = height
        self.width = W - 40*mm

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=0)
        c.setFillColor(self.fg)
        c.setFont("Helvetica-Bold", self.font_size)
        c.drawString(12, self.height / 2 - self.font_size / 2 + 1, self.text)


class CodeBlock(Flowable):
    """Dark code block with monospace text and optional label."""
    def __init__(self, code, label="", width=None):
        super().__init__()
        self.code = code
        self.label = label
        self.block_width = width or (W - 40*mm)
        self.padding = 10
        self.line_height = 13
        self.lines = code.strip().split("\n")
        content_h = len(self.lines) * self.line_height + self.padding * 2
        self.height = content_h + (16 if label else 0)

    def draw(self):
        c = self.canv
        bw, bh = self.block_width, self.height

        # Background
        c.setFillColor(CODE_BG)
        c.roundRect(0, 0, bw, bh, 5, fill=1, stroke=0)

        # Top label bar
        if self.label:
            c.setFillColor(colors.HexColor("#334155"))
            c.roundRect(0, bh - 16, bw, 16, 5, fill=1, stroke=0)
            c.setFillColor(colors.HexColor("#94A3B8"))
            c.setFont("Helvetica", 7)
            c.drawString(10, bh - 11, self.label)

        # Code lines
        c.setFont("Courier", 8)
        y = bh - (16 if self.label else 0) - self.padding - 9
        for line in self.lines:
            # Basic syntax highlight hints
            stripped = line.strip()
            if stripped.startswith("#"):
                c.setFillColor(colors.HexColor("#6B7280"))
            elif stripped.startswith("def ") or stripped.startswith("class ") or stripped.startswith("import ") or stripped.startswith("from "):
                c.setFillColor(colors.HexColor("#818CF8"))
            elif stripped.startswith("pip ") or stripped.startswith("$") or stripped.startswith("//"):
                c.setFillColor(colors.HexColor("#34D399"))
            else:
                c.setFillColor(CODE_TEXT)
            c.drawString(self.padding, y, line[:95])
            y -= self.line_height
            if y < self.padding:
                break

    def wrap(self, availW, availH):
        return self.block_width, self.height


class Callout(Flowable):
    """Colored callout box with icon + text."""
    def __init__(self, text, kind="info", width=None):
        super().__init__()
        self.text = text
        self.kind = kind
        self.box_width = width or (W - 40*mm)
        configs = {
            "info":    (BLUE_LIGHT,   colors.HexColor("#1D4ED8"), "ℹ"),
            "tip":     (GREEN_LIGHT,  SUCCESS,                    "✓"),
            "warning": (ORANGE_LIGHT, WARNING,                    "⚠"),
            "danger":  (colors.HexColor("#FEE2E2"), DANGER,       "✗"),
        }
        self.bg, self.border, self.icon = configs.get(kind, configs["info"])
        self.height = 38

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self.box_width, self.height, 5, fill=1, stroke=0)
        c.setStrokeColor(self.border)
        c.setLineWidth(2)
        c.line(0, 0, 0, self.height)

        c.setFillColor(self.border)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(10, self.height / 2 - 5, self.icon)

        c.setFillColor(BODY_TEXT)
        c.setFont("Helvetica", 8.5)
        # wrap text
        words = self.text.split()
        line, lines = "", []
        for w in words:
            test = (line + " " + w).strip()
            if c.stringWidth(test, "Helvetica", 8.5) < self.box_width - 40:
                line = test
            else:
                lines.append(line)
                line = w
        lines.append(line)
        y = self.height / 2 + (len(lines) - 1) * 5.5 - 5
        for l in lines:
            c.drawString(28, y, l)
            y -= 11

    def wrap(self, aW, aH):
        return self.box_width, self.height


class BadgeRow(Flowable):
    """Row of colored technology badges."""
    def __init__(self, badges, width=None):
        super().__init__()
        self.badges = badges  # list of (label, bg_color, text_color)
        self.box_width = width or (W - 40*mm)
        self.height = 24

    def draw(self):
        c = self.canv
        x = 0
        for label, bg, fg in self.badges:
            w = c.stringWidth(label, "Helvetica-Bold", 8) + 16
            c.setFillColor(bg)
            c.roundRect(x, 4, w, 16, 4, fill=1, stroke=0)
            c.setFillColor(fg)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(x + 8, 9, label)
            x += w + 8

    def wrap(self, aW, aH):
        return self.box_width, self.height


# ─── Styles ───────────────────────────────────────────────────────────────────

def make_styles():
    base = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        "cover_title": ps("cover_title",
            fontName="Helvetica-Bold", fontSize=38, textColor=colors.white,
            leading=46, alignment=TA_LEFT, spaceAfter=8),

        "cover_sub": ps("cover_sub",
            fontName="Helvetica", fontSize=16, textColor=colors.HexColor("#A5B4FC"),
            leading=22, alignment=TA_LEFT, spaceAfter=6),

        "cover_meta": ps("cover_meta",
            fontName="Helvetica", fontSize=10, textColor=colors.HexColor("#94A3B8"),
            alignment=TA_LEFT),

        "h1": ps("h1",
            fontName="Helvetica-Bold", fontSize=22, textColor=BODY_TEXT,
            spaceBefore=18, spaceAfter=8, leading=28),

        "h2": ps("h2",
            fontName="Helvetica-Bold", fontSize=15, textColor=ACCENT,
            spaceBefore=14, spaceAfter=5, leading=20),

        "h3": ps("h3",
            fontName="Helvetica-Bold", fontSize=11, textColor=BODY_TEXT,
            spaceBefore=10, spaceAfter=4, leading=16),

        "body": ps("body",
            fontName="Helvetica", fontSize=9.5, textColor=BODY_TEXT,
            leading=16, spaceAfter=6, alignment=TA_LEFT),

        "body_sm": ps("body_sm",
            fontName="Helvetica", fontSize=8.5, textColor=BODY_TEXT,
            leading=14, spaceAfter=4),

        "bullet": ps("bullet",
            fontName="Helvetica", fontSize=9, textColor=BODY_TEXT,
            leading=15, leftIndent=14, spaceAfter=3,
            bulletIndent=4, bulletFontName="Helvetica"),

        "muted": ps("muted",
            fontName="Helvetica", fontSize=8, textColor=MUTED,
            leading=12, spaceAfter=3),

        "toc_h": ps("toc_h",
            fontName="Helvetica-Bold", fontSize=10, textColor=ACCENT,
            leading=14, spaceAfter=2),

        "toc_item": ps("toc_item",
            fontName="Helvetica", fontSize=9, textColor=BODY_TEXT,
            leading=14, leftIndent=12, spaceAfter=1),
    }

# ─── Page Template ────────────────────────────────────────────────────────────

def make_on_page(doc_ref):
    def on_page(canvas, doc):
        canvas.saveState()
        is_cover = doc.page == 1

        if is_cover:
            # Full dark cover background
            canvas.setFillColor(DARK_BG)
            canvas.rect(0, 0, W, H, fill=1, stroke=0)

            # Decorative gradient bands (simulated)
            for i, alpha in enumerate([(0.08, ACCENT), (0.05, ACCENT2), (0.04, SUCCESS)]):
                canvas.setFillColor(alpha[1])
                canvas.setFillAlpha(alpha[0])
                canvas.roundRect(W * 0.6 + i * 20, H * 0.1 + i * 30,
                                 W * 0.7, H * 0.9, 40, fill=1, stroke=0)
            canvas.setFillAlpha(1.0)

            # Top accent bar
            canvas.setFillColor(ACCENT)
            canvas.rect(0, H - 6, W, 6, fill=1, stroke=0)

            # Bottom strip
            canvas.setFillColor(colors.HexColor("#1E293B"))
            canvas.rect(0, 0, W, 28, fill=1, stroke=0)
            canvas.setFillColor(colors.HexColor("#475569"))
            canvas.setFont("Helvetica", 7.5)
            canvas.drawString(20*mm, 10, "© 2026 devxyasir — Developer Guide")
            canvas.drawRightString(W - 20*mm, 10, "CONFIDENTIAL · ALL RIGHTS RESERVED")

        else:
            # Header bar
            canvas.setFillColor(DARK_BG)
            canvas.rect(0, H - 22, W, 22, fill=1, stroke=0)

            canvas.setFillColor(ACCENT)
            canvas.rect(0, H - 22, 4, 22, fill=1, stroke=0)

            canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 7.5)
            canvas.drawString(12*mm, H - 14, "devxyasir — Developer Blueprint")
            canvas.setFont("Helvetica", 7.5)
            canvas.drawRightString(W - 12*mm, H - 14, "Full Stack PDF Platform")

            # Footer
            canvas.setFillColor(SECTION_BG)
            canvas.rect(0, 0, W, 20, fill=1, stroke=0)
            canvas.setStrokeColor(LIGHT_BORDER)
            canvas.setLineWidth(0.5)
            canvas.line(0, 20, W, 20)

            canvas.setFillColor(MUTED)
            canvas.setFont("Helvetica", 7)
            canvas.drawString(20*mm, 7, "devxyasir · Developer Guide")
            canvas.drawCentredString(W / 2, 7, f"Page {doc.page}")
            canvas.drawRightString(W - 20*mm, 7, "Free & Open Source Stack")

        canvas.restoreState()
    return on_page


# ─── Content Builder ─────────────────────────────────────────────────────────

def build_doc():
    S = make_styles()
    story = []
    gap = lambda n=6: Spacer(1, n)
    hr = lambda: HRFlowable(width="100%", thickness=0.5, color=LIGHT_BORDER, spaceAfter=6, spaceBefore=6)
    full_w = W - 40*mm

    def section(title, color=ACCENT):
        story.append(gap(10))
        story.append(SectionHeader(title, bg=color))
        story.append(gap(8))

    def h2(text):
        story.append(Paragraph(text, S["h2"]))

    def h3(text):
        story.append(Paragraph(text, S["h3"]))

    def body(text):
        story.append(Paragraph(text, S["body"]))

    def bullets(items):
        for item in items:
            story.append(Paragraph(f"• {item}", S["bullet"]))

    def code(text, label=""):
        story.append(gap(4))
        story.append(CodeBlock(text, label=label))
        story.append(gap(6))

    def callout(text, kind="info"):
        story.append(gap(4))
        story.append(Callout(text, kind=kind))
        story.append(gap(6))

    def table(data, col_widths=None, header_bg=ACCENT):
        col_widths = col_widths or [full_w / len(data[0])] * len(data[0])
        style = TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0),  header_bg),
            ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, 0),  8.5),
            ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",     (0, 1), (-1, -1), 8),
            ("TEXTCOLOR",    (0, 1), (-1, -1), BODY_TEXT),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SECTION_BG]),
            ("GRID",         (0, 0), (-1, -1), 0.4, LIGHT_BORDER),
            ("ALIGN",        (0, 0), (-1, -1), "LEFT"),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",   (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
            ("LEFTPADDING",  (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("ROUNDEDCORNERS", [4]),
        ])
        t = Table(data, colWidths=col_widths, style=style, repeatRows=1)
        story.append(gap(4))
        story.append(t)
        story.append(gap(8))

    # ══════════════════════════════════════════════════════════════
    # COVER PAGE
    # ══════════════════════════════════════════════════════════════
    story.append(Spacer(1, 52*mm))
    story.append(Paragraph("iLovePDF Clone", S["cover_title"]))
    story.append(Paragraph("Full-Stack Developer Blueprint", S["cover_sub"]))
    story.append(gap(6))
    story.append(HRFlowable(width=80*mm, thickness=2, color=ACCENT, spaceAfter=14))
    story.append(Paragraph("Build every PDF tool from scratch · 100% Free & Open Source", S["cover_meta"]))
    story.append(gap(4))
    story.append(Paragraph("React · FastAPI · PyMuPDF · pikepdf · Tesseract · Ollama · LibreOffice", S["cover_meta"]))
    story.append(gap(16))
    story.append(BadgeRow([
        ("Python 3.11+", ACCENT, colors.white),
        ("React 18", SUCCESS, colors.white),
        ("FastAPI", colors.HexColor("#009688"), colors.white),
        ("Open Source", WARNING, DARK_BG),
        ("Self-Hosted", ACCENT2, colors.white),
    ]))
    story.append(Spacer(1, 60*mm))
    story.append(Paragraph("Version 1.0 · 2026 · Complete Developer Reference", S["cover_meta"]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════
    story.append(SectionHeader("📋  Table of Contents", bg=DARK_BG))
    story.append(gap(10))

    toc = [
        ("1", "Tech Stack Overview", "Chosen libraries & why"),
        ("2", "Project Architecture", "Folder structure, API design, job queue"),
        ("3", "Tool 01 — Merge PDF", "Combine multiple PDFs into one"),
        ("4", "Tool 02 — Split PDF", "Extract page ranges or individual pages"),
        ("5", "Tool 03 — Compress PDF", "Reduce file size (3 strategies)"),
        ("6", "Tool 04 — Rotate PDF", "Rotate specific or all pages"),
        ("7", "Tool 05 — Add Page Numbers", "Customisable numbering overlay"),
        ("8", "Tool 06 — Watermark", "Text & image watermarks"),
        ("9", "Tool 07 — Edit PDF", "Add text, images, shapes (canvas UI)"),
        ("10", "Tool 08 — Annotate PDF", "Highlights, sticky notes, freehand"),
        ("11", "Tool 09 — Sign PDF", "Draw / type / upload signature"),
        ("12", "Tool 10 — Redact PDF", "Permanently remove sensitive content"),
        ("13", "Tool 11 — Word ↔ PDF", "LibreOffice headless + pdf2docx"),
        ("14", "Tool 12 — Excel ↔ PDF", "LibreOffice + pdfplumber + openpyxl"),
        ("15", "Tool 13 — Image ↔ PDF", "img2pdf + PyMuPDF renderer"),
        ("16", "Tool 14 — Protect / Unlock", "Password encryption & decryption"),
        ("17", "Tool 15 — OCR", "Tesseract: scanned PDF → searchable"),
        ("18", "Tool 16 — AI Summarizer", "Ollama local LLM, no API key needed"),
        ("19", "Tool 17 — AI Translator", "LibreTranslate self-hosted"),
        ("20", "Tool 18 — Repair PDF", "Recover corrupted PDFs"),
        ("21", "Deployment Guide", "Docker Compose, Nginx, production tips"),
        ("22", "Frontend Architecture", "React components, canvas editor, upload flow"),
    ]

    # 2-column ToC
    left_items, right_items = toc[:11], toc[11:]
    def toc_row(num, title, desc):
        return [
            Paragraph(f"<font color='#6366F1'><b>{num}.</b></font>  <b>{title}</b>", S["toc_item"]),
            Paragraph(desc, S["muted"]),
        ]

    combined = []
    for i in range(max(len(left_items), len(right_items))):
        left = toc_row(*left_items[i]) if i < len(left_items) else ["", ""]
        right = toc_row(*right_items[i]) if i < len(right_items) else ["", ""]
        combined.append(left + right)

    toc_style = TableStyle([
        ("FONTNAME",  (0,0), (-1,-1), "Helvetica"),
        ("FONTSIZE",  (0,0), (-1,-1), 8.5),
        ("VALIGN",    (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",(0,0), (-1,-1), 4),
        ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ("LEFTPADDING",(0,0), (-1,-1), 4),
        ("LINEAFTER", (1,0), (1,-1), 0.5, LIGHT_BORDER),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.white, SECTION_BG]),
    ])
    col_w = full_w / 4
    t = Table(combined, colWidths=[col_w*1.1, col_w*0.9, col_w*1.1, col_w*0.9], style=toc_style)
    story.append(t)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # SECTION 1 — TECH STACK
    # ══════════════════════════════════════════════════════════════
    section("1 · Tech Stack Overview", DARK_BG)
    callout("Every library listed here is 100% free, open-source and self-hostable. No paid API keys required.", "tip")

    table([
        ["Layer", "Technology", "Purpose", "Install"],
        ["PDF Engine", "PyMuPDF (fitz)", "Read, write, render, annotate PDFs", "pip install pymupdf"],
        ["PDF Engine", "pikepdf", "Low-level PDF manipulation & encryption", "pip install pikepdf"],
        ["Text Extraction", "pdfplumber", "Tables, text with layout preservation", "pip install pdfplumber"],
        ["Office Convert", "LibreOffice", "Word/Excel/PPT ↔ PDF (headless CLI)", "apt install libreoffice"],
        ["PDF→Word", "pdf2docx", "Convert PDF layout to .docx", "pip install pdf2docx"],
        ["Image→PDF", "img2pdf", "Lossless image to PDF embedding", "pip install img2pdf"],
        ["OCR", "Tesseract + pytesseract", "Scanned image text recognition", "apt install tesseract-ocr"],
        ["AI Local LLM", "Ollama (llama3/mistral)", "Summarize, translate — fully offline", "ollama.com"],
        ["Translation", "LibreTranslate", "Self-hosted translation API", "pip install libretranslate"],
        ["Backend API", "FastAPI + Uvicorn", "Async REST API server", "pip install fastapi uvicorn"],
        ["Task Queue", "Celery + Redis", "Background job processing", "pip install celery redis"],
        ["Frontend", "React + Tailwind CSS", "UI components & canvas editor", "npm create vite@latest"],
        ["File Storage", "MinIO / Local disk", "Store uploads & results", "Self-hosted S3 compatible"],
        ["Containerize", "Docker + Compose", "Reproducible deployment", "docker.com"],
    ], col_widths=[full_w*0.14, full_w*0.2, full_w*0.36, full_w*0.3])

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # SECTION 2 — ARCHITECTURE
    # ══════════════════════════════════════════════════════════════
    section("2 · Project Architecture", DARK_BG)
    body("The platform follows a clean separation of concerns: React frontend → FastAPI backend → Celery workers for heavy PDF processing.")

    code("""ilovepdf-clone/
├── backend/
│   ├── main.py              # FastAPI entrypoint
│   ├── routers/
│   │   ├── merge.py
│   │   ├── split.py
│   │   ├── compress.py
│   │   ├── convert.py
│   │   ├── ocr.py
│   │   └── ai_tools.py
│   ├── workers/
│   │   ├── celery_app.py    # Celery setup
│   │   └── tasks.py         # All background tasks
│   ├── utils/
│   │   ├── pdf_utils.py     # Shared PDF helpers
│   │   └── storage.py       # File save/retrieve
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadZone.jsx
│   │   │   ├── ToolCard.jsx
│   │   │   ├── PdfCanvas.jsx  # Canvas editor
│   │   │   └── ProgressBar.jsx
│   │   ├── pages/
│   │   │   ├── Merge.jsx
│   │   │   ├── Split.jsx
│   │   │   └── ...
│   │   └── App.jsx
├── docker-compose.yml
└── nginx.conf""", "Project Structure")

    h2("API Design Pattern")
    body("Every tool follows the same REST pattern:")

    code("""# Upload → Process → Download
POST /api/merge         → returns job_id
GET  /api/jobs/{job_id} → returns { status, progress }
GET  /api/download/{job_id} → streams result file

# FastAPI example
from fastapi import FastAPI, UploadFile, File
from workers.tasks import merge_task

app = FastAPI()

@app.post("/api/merge")
async def merge_pdfs(files: list[UploadFile] = File(...)):
    paths = [save_upload(f) for f in files]
    job = merge_task.delay(paths)
    return {"job_id": job.id}""", "FastAPI Router Pattern")

    h2("Celery Worker Setup")
    code("""# celery_app.py
from celery import Celery

app = Celery(
    "pdf_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)
app.conf.task_time_limit = 300  # 5 min max per task

# Start with:
# celery -A workers.celery_app worker --concurrency=4""", "Celery Configuration")

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # TOOLS — ORGANIZE
    # ══════════════════════════════════════════════════════════════
    section("3 · Tool 01 — Merge PDF", SUCCESS)
    body("Combine two or more PDF files into a single document, preserving all pages in user-defined order.")
    callout("Best Library: pikepdf — faster than pypdf for large files, handles encrypted PDFs gracefully.", "tip")

    h2("How It Works")
    bullets([
        "User uploads N PDFs via drag-and-drop, reorders them in the UI",
        "Frontend sends ordered file list to POST /api/merge",
        "Backend saves uploads to /tmp/, queues Celery task with file paths in order",
        "Worker opens each PDF and appends all pages into a new pikepdf.Pdf object",
        "Saves the merged PDF and sends download link back via WebSocket",
    ])

    code("""import pikepdf
from celery import shared_task

@shared_task
def merge_task(file_paths: list[str], output_path: str) -> str:
    merged = pikepdf.Pdf.new()

    for path in file_paths:
        with pikepdf.open(path) as pdf:
            merged.pages.extend(pdf.pages)

    merged.save(output_path)
    return output_path

# Handle encrypted PDFs:
# with pikepdf.open(path, password="secret") as pdf: ...""", "merge.py — Celery Task")

    section("4 · Tool 02 — Split PDF", SUCCESS)
    body("Extract specific pages or ranges from a PDF into separate files.")
    bullets([
        "Page Range Mode: '1-3, 5, 7-9' → parse ranges, extract each group into a separate PDF",
        "Every Page Mode: split each page into its own file → zip all and return",
        "Split Every N Pages: chunk PDF into equal-sized parts",
    ])

    code("""import pikepdf, re

def parse_ranges(range_str: str, total: int) -> list[list[int]]:
    groups = []
    for part in range_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            groups.append(list(range(int(start)-1, int(end))))
        else:
            groups.append([int(part)-1])
    return groups

@shared_task
def split_task(input_path: str, range_str: str) -> list[str]:
    src = pikepdf.open(input_path)
    groups = parse_ranges(range_str, len(src.pages))
    outputs = []

    for i, page_indices in enumerate(groups):
        out = pikepdf.Pdf.new()
        for idx in page_indices:
            out.pages.append(src.pages[idx])
        path = f"/tmp/split_part_{i+1}.pdf"
        out.save(path)
        outputs.append(path)

    return outputs  # zip these before sending""", "split.py")

    section("5 · Tool 03 — Compress PDF", SUCCESS)
    body("Reduce PDF file size using three progressive strategies.")

    table([
        ["Mode", "Strategy", "Quality", "Typical Saving"],
        ["Low",    "Re-save with garbage collection (remove dead objects)", "Lossless", "5–15%"],
        ["Medium", "Downsample embedded images to 150 DPI", "Visually identical", "30–60%"],
        ["High",   "Render each page as 72 DPI image → reassemble", "Lossy", "60–85%"],
    ], col_widths=[full_w*0.1, full_w*0.45, full_w*0.2, full_w*0.25], header_bg=SUCCESS)

    code("""import fitz  # PyMuPDF

@shared_task
def compress_task(input_path: str, mode: str, output_path: str) -> str:
    doc = fitz.open(input_path)

    if mode == "low":
        # Lossless: strip dead objects & compress streams
        doc.save(output_path, garbage=4, deflate=True, clean=True)

    elif mode == "medium":
        # Downsample images to 150 DPI
        for page in doc:
            for img_ref in page.get_images(full=True):
                xref = img_ref[0]
                img = doc.extract_image(xref)
                if img["width"] > 800:
                    # Re-embed at lower quality via PIL
                    from PIL import Image
                    import io
                    pil = Image.open(io.BytesIO(img["image"]))
                    buf = io.BytesIO()
                    pil.save(buf, "JPEG", quality=60)
                    doc.update_stream(xref, buf.getvalue())
        doc.save(output_path, garbage=4, deflate=True)

    elif mode == "high":
        # Render pages at low DPI → new PDF (lossy)
        out = fitz.open()
        for page in doc:
            mat = fitz.Matrix(72/72, 72/72)  # 72 DPI
            pix = page.get_pixmap(matrix=mat)
            img_page = out.new_page(width=page.rect.width, height=page.rect.height)
            img_page.insert_image(page.rect, pixmap=pix)
        out.save(output_path, deflate=True)

    return output_path""", "compress.py")

    section("6 · Tool 04 — Rotate PDF", SUCCESS)
    body("Rotate all pages or specific pages by 90°, 180°, or 270°. No re-rendering — just metadata update.")

    code("""import pikepdf

@shared_task
def rotate_task(input_path: str, pages: list[int],
                angle: int, output_path: str) -> str:
    # angle must be 90, 180, or 270
    with pikepdf.open(input_path) as pdf:
        targets = pages if pages else range(len(pdf.pages))
        for i in targets:
            pdf.pages[i].rotate(angle, relative=True)
        pdf.save(output_path)
    return output_path""", "rotate.py")

    section("7 · Tool 05 — Add Page Numbers", SUCCESS)
    body("Stamp page numbers onto each page at a configurable position, font, color and starting value.")

    code("""import fitz

POSITIONS = {
    "bottom-center": lambda r: (r.width/2, r.height - 25),
    "bottom-right":  lambda r: (r.width - 40, r.height - 25),
    "top-center":    lambda r: (r.width/2, 20),
}

@shared_task
def page_numbers_task(input_path: str, output_path: str,
                      start: int = 1, position: str = "bottom-center",
                      font_size: int = 11) -> str:
    doc = fitz.open(input_path)
    for i, page in enumerate(doc):
        number = str(start + i)
        x, y = POSITIONS[position](page.rect)
        page.insert_text(
            (x - fitz.get_text_length(number, fontsize=font_size)/2, y),
            number,
            fontsize=font_size,
            color=(0.2, 0.2, 0.2)
        )
    doc.save(output_path)
    return output_path""", "page_numbers.py")

    section("8 · Tool 06 — Watermark PDF", SUCCESS)
    bullets([
        "Text watermark: Diagonal semi-transparent text stamped across each page",
        "Image watermark: PNG/JPG logo embedded at specified opacity and position",
        "Configurable: opacity, font size, rotation angle, color, position",
    ])

    code("""import fitz

@shared_task
def watermark_text_task(input_path: str, output_path: str,
                        text: str = "CONFIDENTIAL",
                        opacity: float = 0.15,
                        angle: int = 45) -> str:
    doc = fitz.open(input_path)
    for page in doc:
        r = page.rect
        # Insert at page center, rotated
        page.insert_text(
            (r.width * 0.18, r.height * 0.55),
            text,
            fontsize=52,
            color=(0.6, 0.1, 0.1),
            rotate=angle,
            render_mode=3,  # transparent fill
            overlay=True
        )
    doc.save(output_path)
    return output_path

@shared_task
def watermark_image_task(input_path, output_path, img_path,
                         opacity=0.15, position="center"):
    doc = fitz.open(input_path)
    for page in doc:
        rect = page.rect.inflate(-50, -50)  # slight margin
        page.insert_image(rect, filename=img_path, overlay=True)
    doc.save(output_path)
    return output_path""", "watermark.py")

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # EDIT & ANNOTATE
    # ══════════════════════════════════════════════════════════════
    section("9 · Tool 07 — Edit PDF", ACCENT)
    body("The most complex tool. PDF pages are rendered as images and displayed on an HTML canvas. Users interact visually; edits are sent as JSON to the backend for application.")

    h2("Canvas-based Editing Flow")
    code("""# STEP 1 — Backend renders pages as images for the canvas editor
import fitz

@app.get("/api/preview/{job_id}/{page_num}")
async def render_page(job_id: str, page_num: int, dpi: int = 150):
    doc = fitz.open(get_file_path(job_id))
    page = doc[page_num - 1]
    mat = fitz.Matrix(dpi/72, dpi/72)
    pix = page.get_pixmap(matrix=mat)
    return Response(content=pix.tobytes("png"), media_type="image/png")

# STEP 2 — Frontend sends edit operations as JSON
# {
#   "page": 1,
#   "edits": [
#     {"type": "text", "x": 100, "y": 200, "content": "Hello", "size": 12},
#     {"type": "image", "x": 50, "y": 50, "x2": 200, "y2": 150, "src": "base64..."},
#     {"type": "rect", "x1": 10, "y1": 10, "x2": 100, "y2": 50, "color": "#ff0000"}
#   ]
# }

# STEP 3 — Backend applies all edits to the real PDF
@shared_task
def apply_edits_task(input_path: str, output_path: str,
                     all_edits: list[dict]) -> str:
    doc = fitz.open(input_path)
    for edit in all_edits:
        page = doc[edit["page"] - 1]
        if edit["type"] == "text":
            page.insert_text(
                (edit["x"], edit["y"]),
                edit["content"],
                fontsize=edit.get("size", 11),
                color=hex_to_rgb(edit.get("color", "#000000"))
            )
        elif edit["type"] == "image":
            import base64, io
            img_bytes = base64.b64decode(edit["src"].split(",")[1])
            rect = fitz.Rect(edit["x"], edit["y"], edit["x2"], edit["y2"])
            page.insert_image(rect, stream=img_bytes)
        elif edit["type"] == "rect":
            rect = fitz.Rect(edit["x1"], edit["y1"], edit["x2"], edit["y2"])
            page.draw_rect(rect, color=hex_to_rgb(edit["color"]), width=1.5)
    doc.save(output_path)
    return output_path""", "edit.py")

    section("10 · Tool 08 — Annotate PDF", ACCENT)
    bullets([
        "Highlight: Draw colored transparent rect over selected text area → /Highlight annotation",
        "Sticky Note: Click to place a /Text popup annotation at any coordinate",
        "Freehand Draw: Capture mouse path coordinates → /Ink annotation",
        "All annotations are standards-compliant and viewable in Adobe Reader",
    ])

    code("""import fitz

def add_highlight(page, coords: tuple, color=(1, 1, 0)):
    rect = fitz.Rect(*coords)
    annot = page.add_highlight_annot(rect)
    annot.set_colors(stroke=color)
    annot.update()

def add_sticky_note(page, point: tuple, content: str, author="User"):
    annot = page.add_text_annot(fitz.Point(*point), content)
    annot.set_info(title=author)
    annot.update()

def add_freehand(page, ink_list: list[list[tuple]]):
    # ink_list = list of strokes, each stroke = list of (x,y) points
    annot = page.add_ink_annot(ink_list)
    annot.set_border(width=1.5)
    annot.set_colors(stroke=(0.1, 0.1, 0.8))
    annot.update()""", "annotate.py")

    section("11 · Tool 09 — Sign PDF", ACCENT)
    bullets([
        "Draw Mode: HTML canvas with mouse events → export as transparent PNG → embed in PDF",
        "Type Mode: Render cursive font text on server → embed as image at chosen position",
        "Upload Mode: User uploads PNG/JPG of handwritten signature → embed at position",
    ])

    code("""import fitz, base64

@shared_task
def sign_task(input_path: str, output_path: str,
              sig_base64: str, page_num: int,
              x: float, y: float, w: float, h: float) -> str:
    doc = fitz.open(input_path)
    page = doc[page_num - 1]

    # Decode base64 PNG from canvas
    img_data = base64.b64decode(sig_base64.split(",")[1])
    rect = fitz.Rect(x, y, x + w, y + h)

    # Insert with transparency support
    page.insert_image(rect, stream=img_data, keep_proportion=True)
    doc.save(output_path)
    return output_path""", "sign.py")

    section("12 · Tool 10 — Redact PDF", ACCENT)
    callout("IMPORTANT: add_redact_annot() + apply_redactions() permanently destroys the underlying data — not just covers it. The text/image content is gone from the file.", "warning")

    code("""import fitz

@shared_task
def redact_task(input_path: str, output_path: str,
                redactions: list[dict]) -> str:
    doc = fitz.open(input_path)

    for r in redactions:
        page = doc[r["page"] - 1]
        rect = fitz.Rect(r["x1"], r["y1"], r["x2"], r["y2"])
        # Add black fill redaction annotation
        annot = page.add_redact_annot(rect)
        annot.set_colors(fill=(0, 0, 0))
        annot.update()

    # CRITICAL: This permanently removes underlying content
    doc.apply_redactions()
    doc.save(output_path)
    return output_path""", "redact.py — PERMANENT DATA REMOVAL")

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # CONVERSION
    # ══════════════════════════════════════════════════════════════
    section("13 · Tool 11 — Word ↔ PDF", WARNING)
    h2("Word → PDF (LibreOffice Headless)")
    callout("LibreOffice handles .docx, .odt, .rtf, .doc — completely free, no Microsoft Office needed.", "tip")

    code("""import subprocess, os

def word_to_pdf(input_path: str, output_dir: str) -> str:
    # LibreOffice headless mode — runs as CLI
    result = subprocess.run([
        "libreoffice", "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        input_path
    ], capture_output=True, timeout=60)

    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())

    # Output filename mirrors input with .pdf extension
    base = os.path.splitext(os.path.basename(input_path))[0]
    return os.path.join(output_dir, f"{base}.pdf")""", "word_to_pdf.py")

    h2("PDF → Word (pdf2docx)")
    code("""from pdf2docx import Converter

def pdf_to_word(input_path: str, output_path: str,
                start: int = 0, end: int = None) -> str:
    cv = Converter(input_path)
    cv.convert(output_path, start=start, end=end)
    cv.close()
    return output_path

# pdf2docx maps:
# - Text blocks → Word paragraphs
# - Tables → Word tables
# - Images → inline images
# - Columns → Word columns (best effort)""", "pdf_to_word.py")

    section("14 · Tool 12 — Excel ↔ PDF", WARNING)
    code("""# Excel → PDF: same LibreOffice headless approach
def excel_to_pdf(input_path: str, output_dir: str) -> str:
    subprocess.run([
        "libreoffice", "--headless",
        "--convert-to", "pdf",
        "--outdir", output_dir,
        input_path
    ], timeout=60)
    base = os.path.splitext(os.path.basename(input_path))[0]
    return os.path.join(output_dir, f"{base}.pdf")

# PDF → Excel: extract tables then write xlsx
import pdfplumber, openpyxl

def pdf_to_excel(pdf_path: str, xlsx_path: str) -> str:
    wb = openpyxl.Workbook()
    ws = wb.active
    row_num = 1

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    ws.append([cell or "" for cell in row])
                    row_num += 1
                ws.append([])  # blank row between tables
                row_num += 1

    wb.save(xlsx_path)
    return xlsx_path""", "excel_convert.py")

    section("15 · Tool 13 — Image ↔ PDF", WARNING)
    code("""# Multiple Images → PDF (lossless with img2pdf)
import img2pdf, fitz
from PIL import Image

def images_to_pdf(img_paths: list[str], output_path: str) -> str:
    # img2pdf embeds JPEGs directly without re-encoding (truly lossless)
    with open(output_path, "wb") as f:
        f.write(img2pdf.convert(img_paths))
    return output_path

# PDF → Images (per-page PNG/JPG export)
def pdf_to_images(pdf_path: str, output_dir: str,
                  dpi: int = 150, fmt: str = "png") -> list[str]:
    doc = fitz.open(pdf_path)
    outputs = []
    mat = fitz.Matrix(dpi/72, dpi/72)

    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out_path = f"{output_dir}/page_{i+1}.{fmt}"
        pix.save(out_path)
        outputs.append(out_path)

    return outputs""", "image_convert.py")

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # SECURITY
    # ══════════════════════════════════════════════════════════════
    section("16 · Tool 14 — Protect & Unlock PDF", DANGER)
    bullets([
        "Protect: AES-256 encryption with user password (open) and owner password (restrict editing)",
        "Unlock: Open encrypted PDF with password → save without encryption",
        "Permission Flags: restrict printing, copying, annotations independently",
    ])

    code("""import pikepdf

def protect_pdf(input_path: str, output_path: str,
                user_pass: str, owner_pass: str,
                allow_print: bool = True) -> str:
    permissions = pikepdf.Permissions(
        print_highres=allow_print,
        modify_annotation=False,
        extract=False,
    )
    with pikepdf.open(input_path) as pdf:
        pdf.save(
            output_path,
            encryption=pikepdf.Encryption(
                owner=owner_pass,
                user=user_pass,
                R=6,  # AES-256 (PDF 2.0)
                allow=permissions
            )
        )
    return output_path

def unlock_pdf(input_path: str, output_path: str, password: str) -> str:
    with pikepdf.open(input_path, password=password) as pdf:
        pdf.save(output_path)
    return output_path""", "security.py")

    # ══════════════════════════════════════════════════════════════
    # OCR
    # ══════════════════════════════════════════════════════════════
    section("17 · Tool 15 — OCR (Scanned PDF → Searchable)", ACCENT2)
    body("Convert scanned, non-selectable PDFs into fully searchable PDFs by adding an invisible text layer over the page images.")
    callout("Tesseract supports 100+ languages. Install language packs: apt install tesseract-ocr-ara for Arabic.", "info")

    code("""import fitz, pytesseract
from PIL import Image
import io

@shared_task
def ocr_task(input_path: str, output_path: str,
             lang: str = "eng") -> str:
    doc = fitz.open(input_path)
    out_doc = fitz.open()

    for page_num, page in enumerate(doc):
        # 1) Render page to high-DPI image
        mat = fitz.Matrix(300/72, 300/72)  # 300 DPI for accuracy
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # 2) Run Tesseract → get hOCR (HTML with positions)
        hocr = pytesseract.image_to_pdf_or_hocr(
            img, lang=lang, extension="hocr"
        )

        # 3) Create searchable PDF page from hOCR output
        # Use ocrmypdf as higher-level alternative:
        # import ocrmypdf
        # ocrmypdf.ocr(input_path, output_path, language=lang)

        # 4) Simpler approach with pytesseract direct:
        pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension="pdf")
        ocr_page = fitz.open("pdf", pdf_bytes)
        out_doc.insert_pdf(ocr_page)

    out_doc.save(output_path)
    return output_path

# RECOMMENDED: Use ocrmypdf (wraps Tesseract + pikepdf perfectly)
# pip install ocrmypdf
# ocrmypdf.ocr("scanned.pdf", "searchable.pdf", language="eng")""", "ocr.py")

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # AI TOOLS
    # ══════════════════════════════════════════════════════════════
    section("18 · Tool 16 — AI Summarizer (Ollama Local LLM)", ACCENT2)
    body("Extract text from the PDF, then pass it to a locally-running Ollama LLM for summarization. Completely offline — no API key, no data sent to any cloud.")

    callout("Install Ollama: curl -fsSL https://ollama.com/install.sh | sh  →  ollama pull llama3", "tip")

    code("""import fitz, ollama

def extract_text(pdf_path: str, max_chars: int = 8000) -> str:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
        if len(text) > max_chars:
            break
    return text[:max_chars]

@shared_task
def summarize_task(pdf_path: str, style: str = "concise") -> str:
    text = extract_text(pdf_path)

    prompts = {
        "concise": f"Summarize in 3-5 bullet points:\\n\\n{text}",
        "detailed": f"Write a detailed summary with sections:\\n\\n{text}",
        "executive": f"Write a 2-paragraph executive summary:\\n\\n{text}",
    }

    response = ollama.chat(
        model="llama3",  # or mistral, gemma, phi3 — all free
        messages=[{"role": "user", "content": prompts[style]}]
    )
    return response["message"]["content"]""", "ai_summarizer.py")

    section("19 · Tool 17 — AI Translator (LibreTranslate)", ACCENT2)
    body("Self-hosted translation API. Translate PDF content while preserving page layout and positioning.")

    code("""# Start LibreTranslate server:
# pip install libretranslate
# libretranslate --host 0.0.0.0 --port 5000

import requests, fitz

LIBRE_URL = "http://localhost:5000/translate"

def translate_text(text: str, source: str, target: str) -> str:
    resp = requests.post(LIBRE_URL, json={
        "q": text, "source": source, "target": target, "format": "text"
    })
    return resp.json()["translatedText"]

@shared_task
def translate_pdf_task(input_path: str, output_path: str,
                       source: str = "en", target: str = "ar") -> str:
    doc = fitz.open(input_path)

    for page in doc:
        # Get all text blocks with their positions
        blocks = page.get_text("blocks")
        for block in blocks:
            x0, y0, x1, y1, text, *_ = block
            if not text.strip():
                continue

            # Translate the block text
            translated = translate_text(text.strip(), source, target)

            # Cover original text with white rect
            page.draw_rect(fitz.Rect(x0, y0, x1, y1),
                           color=(1,1,1), fill=(1,1,1))

            # Insert translated text at same position
            page.insert_textbox(
                fitz.Rect(x0, y0, x1, y1+20),
                translated,
                fontsize=9,
                align=fitz.TEXT_ALIGN_RIGHT if target == "ar" else fitz.TEXT_ALIGN_LEFT
            )

    doc.save(output_path)
    return output_path

# Supported language pairs: 30+ including Arabic, French, Spanish, German, Chinese""", "ai_translator.py")

    section("20 · Tool 18 — Repair PDF", DANGER)
    body("Attempt to recover and rebuild corrupted or damaged PDF files.")

    code("""import pikepdf, fitz, subprocess

def repair_pdf(input_path: str, output_path: str) -> dict:
    # Strategy 1: pikepdf (handles xref table corruption)
    try:
        with pikepdf.open(input_path, suppress_warnings=True) as pdf:
            pdf.save(output_path)
        return {"method": "pikepdf", "success": True}
    except Exception:
        pass

    # Strategy 2: qpdf CLI (external tool)
    try:
        result = subprocess.run([
            "qpdf", "--recover", input_path, output_path
        ], capture_output=True)
        if result.returncode == 0:
            return {"method": "qpdf", "success": True}
    except FileNotFoundError:
        pass

    # Strategy 3: PyMuPDF (best at partial recovery)
    try:
        doc = fitz.open(input_path)
        doc.save(output_path, garbage=4, clean=True)
        return {"method": "pymupdf", "success": True}
    except Exception as e:
        return {"method": "none", "success": False, "error": str(e)}""", "repair.py")

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════
    # DEPLOYMENT
    # ══════════════════════════════════════════════════════════════
    section("21 · Deployment Guide (Docker Compose)", DARK_BG)
    body("One-command deployment of the entire stack: FastAPI, Celery workers, Redis, and the React frontend via Nginx.")

    code("""# docker-compose.yml
version: "3.9"

services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - REDIS_URL=redis://redis:6379/0
      - UPLOAD_DIR=/data/uploads
      - OUTPUT_DIR=/data/outputs
    volumes:
      - pdf_data:/data
    depends_on: [redis]
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2

  worker:
    build: ./backend
    environment:
      - REDIS_URL=redis://redis:6379/0
      - UPLOAD_DIR=/data/uploads
      - OUTPUT_DIR=/data/outputs
    volumes:
      - pdf_data:/data
    depends_on: [redis]
    command: celery -A workers.celery_app worker --concurrency=4 --loglevel=info

  frontend:
    build: ./frontend
    ports: ["80:80"]
    depends_on: [backend]

volumes:
  pdf_data:""", "docker-compose.yml")

    code("""# backend/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    libreoffice tesseract-ocr qpdf \\
    tesseract-ocr-ara tesseract-ocr-fra \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# frontend/Dockerfile
# FROM node:20-alpine as build
# WORKDIR /app
# COPY package*.json .
# RUN npm ci
# COPY . .
# RUN npm run build
# FROM nginx:alpine
# COPY --from=build /app/dist /usr/share/nginx/html
# COPY nginx.conf /etc/nginx/conf.d/default.conf""", "Dockerfiles")

    code("""# requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-multipart==0.0.12
celery==5.4.0
redis==5.1.1
pymupdf==1.24.13
pikepdf==9.4.2
pdfplumber==0.11.4
pdf2docx==0.5.8
img2pdf==0.5.1
pytesseract==0.3.13
openpyxl==3.1.5
Pillow==11.0.0
ollama==0.4.2
requests==2.32.3
ocrmypdf==16.6.1""", "requirements.txt")

    section("22 · Frontend Architecture (React)", DARK_BG)
    body("The frontend is built with React + Vite + Tailwind. Each tool has a dedicated page with a shared upload zone, progress tracking, and download flow.")

    code("""// src/components/UploadZone.jsx
import { useCallback } from "react"
import { useDropzone } from "react-dropzone"

export function UploadZone({ onFiles, accept = { "application/pdf": [".pdf"] }, multiple = true }) {
  const onDrop = useCallback(files => onFiles(files), [])
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept, multiple })

  return (
    <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-12 text-center
      cursor-pointer transition-colors
      ${isDragActive ? "border-indigo-500 bg-indigo-50" : "border-gray-300 hover:border-indigo-400"}`}>
      <input {...getInputProps()} />
      <p className="text-2xl mb-2">📄</p>
      <p className="font-semibold text-gray-700">Drop PDF here or click to browse</p>
      <p className="text-sm text-gray-400 mt-1">Max 100MB per file</p>
    </div>
  )
}

// src/hooks/useJobPoller.js
import { useState, useEffect } from "react"

export function useJobPoller(jobId) {
  const [status, setStatus] = useState(null)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (!jobId) return
    const interval = setInterval(async () => {
      const res = await fetch(\`/api/jobs/\${jobId}\`)
      const data = await res.json()
      setStatus(data.status)
      setProgress(data.progress)
      if (data.status === "done" || data.status === "error") clearInterval(interval)
    }, 1500)
    return () => clearInterval(interval)
  }, [jobId])

  return { status, progress }
}""", "React Components")

    story.append(gap(10))

    # Final summary table
    section("Quick Reference — All 18 Tools", DARK_BG)
    table([
        ["#", "Tool", "Primary Library", "Difficulty"],
        ["01", "Merge PDF", "pikepdf", "⭐ Easy"],
        ["02", "Split PDF", "pikepdf", "⭐ Easy"],
        ["03", "Compress PDF", "PyMuPDF + Pillow", "⭐⭐ Medium"],
        ["04", "Rotate PDF", "pikepdf", "⭐ Easy"],
        ["05", "Page Numbers", "PyMuPDF", "⭐ Easy"],
        ["06", "Watermark", "PyMuPDF", "⭐ Easy"],
        ["07", "Edit PDF", "PyMuPDF + React Canvas", "⭐⭐⭐ Hard"],
        ["08", "Annotate PDF", "PyMuPDF", "⭐⭐ Medium"],
        ["09", "Sign PDF", "PyMuPDF + Canvas", "⭐⭐ Medium"],
        ["10", "Redact PDF", "PyMuPDF", "⭐⭐ Medium"],
        ["11", "Word ↔ PDF", "LibreOffice + pdf2docx", "⭐⭐ Medium"],
        ["12", "Excel ↔ PDF", "LibreOffice + pdfplumber", "⭐⭐ Medium"],
        ["13", "Image ↔ PDF", "img2pdf + PyMuPDF", "⭐ Easy"],
        ["14", "Protect/Unlock", "pikepdf", "⭐ Easy"],
        ["15", "OCR", "Tesseract + ocrmypdf", "⭐⭐ Medium"],
        ["16", "AI Summarizer", "Ollama (llama3)", "⭐⭐ Medium"],
        ["17", "AI Translator", "LibreTranslate", "⭐⭐ Medium"],
        ["18", "Repair PDF", "pikepdf + qpdf", "⭐⭐ Medium"],
    ], col_widths=[full_w*0.06, full_w*0.28, full_w*0.4, full_w*0.26])

    callout("Start with Merge, Split, and Compress (all Easy). Add the canvas-based editor last as it's the most complex piece.", "tip")
    callout("Total estimated build time for a solo developer: 3–5 months for a full production-ready clone.", "info")

    return story


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    output = "ilovepdf_developer_blueprint.pdf"

    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=30*mm, bottomMargin=24*mm,
        title="devxyasir — Developer Blueprint",
        author="Developer Guide",
    )

    story = build_doc()
    on_page_fn = make_on_page(doc)
    doc.build(story, onFirstPage=on_page_fn, onLaterPages=on_page_fn)
    print(f"✅  PDF generated: {output}")


if __name__ == "__main__":
    main()