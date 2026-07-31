import bpy #type: ignore
import threading
import urllib.request
import zipfile
from pathlib import Path
import os
import shutil
from ..constants import get_preferences, get_operator


    
FILENAME = "usd.py312.windows-x86_64.usdview.release-v25.08.71e038c1.zip"
DISPLAYNAME = "usdview.windows-x86_64"
BUNDLE_URL = (
    f"https://developer.nvidia.com/downloads/usd/usd_binaries/25.08/{FILENAME}"
)

DOWNLOAD_JOB = None

class DownloadJob:
    def __init__(self):
        self.phase = "Starting"
        self.progress = 0.0
        self.bytes_done = 0
        self.bytes_total = 0
        self.result_path = None
        self.error = None
        self.cancel = False
        self.done = False

def download(job: DownloadJob, url):
    download_path = get_preferences().usdview_path
    zip_path = download_path + DISPLAYNAME + ".zip"
    part_path = download_path + DISPLAYNAME + ".part"

    print("Downloading")

    try:
        job.phase = "Downloading..."
        req = urllib.request.Request(url, headers={"User-Agent": "BlenderPipeline"})
        with urllib.request.urlopen(req) as resp:
            job.bytes_total = int(resp.headers.get("Content-Length", 0))
            with open(part_path, "wb") as f:
                while True:
                    if job.cancel:
                        job.phase = "Cancelling"
                        cleanup(part_path=part_path)
                        return
                    chunk = resp.read( 1 << 20) #1 mb per read
                    if not chunk:
                        break
                    f.write(chunk)
                    job.bytes_done += len(chunk)
                    if job.bytes_total:
                        job.progress = job.bytes_done / job.bytes_total
                        print(f"[{job.bytes_done} / {job.bytes_total} - {job.progress}%]")

        os.replace(part_path, zip_path)
        return zip_path, part_path
                    
    except Exception as e:
        print(e)


def extract(job: DownloadJob, zip_path):
    job.phase = "Extracting"
    job.progress = 0.0

    cache = get_preferences().usdview_path + "USDView"

    with zipfile.ZipFile(zip_path) as zf:
        members = zf.infolist()

        job.bytes_total = sum(info.file_size for info in members)
        job.bytes_done = 0

        for info in members:
            if job.cancel:
                cleanup(zip_path=zip_path, extract_path=cache)
                return False

            zf.extract(info, cache)

            job.bytes_done += info.file_size
            job.progress = (job.bytes_done / job.bytes_total)

    return True


def download_and_extract(job: DownloadJob, url):
    zip_path, part_path = download(job, url)
    if zip_path is None:
        job.done = True
        return
    
    completed = extract(job, zip_path)

    if not completed:
        job.done = True
        return

    job.done = completed
    cleanup(zip_path)

def cleanup(part_path=None, zip_path=None, extract_path=None):
    for path in (part_path, zip_path):
        if path:
            try:
                Path(path).unlink(missing_ok=True)
            except OSError:
                pass

    if extract_path:
        try:
            shutil.rmtree(extract_path, ignore_errors=True)
        except OSError:
            pass


def redraw_window_manager(context):
    wm = context.window_manager
    for window in wm.windows:
        screen = window.screen
        if not screen:
            continue

        for area in screen.areas:
            if area.type == 'PREFERENCES':
                area.tag_redraw()

class USD_OT_DownloadUSDView(bpy.types.Operator):
    bl_idname = get_operator("download_usdview")
    bl_label = "Downloads USD View"

    timer = None

    def invoke(self, context, event):
        global DOWNLOAD_JOB
        if DOWNLOAD_JOB is not None and not DOWNLOAD_JOB.done:
            return{"CANCELLED"}
        
        DOWNLOAD_JOB = DownloadJob()

        threading.Thread(
            target=download_and_extract,
            args=(DOWNLOAD_JOB, BUNDLE_URL),
            daemon=True,
        ).start()

        wm = context.window_manager
        self.timer = wm.event_timer_add(0.1, window = context.window)
        wm.modal_handler_add(self)
        redraw_window_manager(context)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        job = DOWNLOAD_JOB

        if event.type == "ESC" and job is not None:
            job.cancel = True

        if event.type == "TIMER":
            redraw_window_manager(context)
            if job is None or job.done:
                return self.finish(context)
            
        return {"PASS_THROUGH"}

    def finish(self, context):
        wm = context.window_manager
        if self.timer:
            wm.event_timer_remove(self.timer)
            self.timer = None
        redraw_window_manager(context)

        job = DOWNLOAD_JOB
        if job is None:
            return {"CANCELLED"}

        self.report({"INFO"}, "Download complete!")
        return{"FINISHED"}


class USD_OT_CancelDownload(bpy.types.Operator):
    bl_idname = get_operator("cancel_usdview_download")
    bl_label = "Cancel"
 
    def execute(self, context):
        if DOWNLOAD_JOB is not None and not DOWNLOAD_JOB.done:
            DOWNLOAD_JOB.cancel = True
            if DOWNLOAD_JOB.error:
                self.report({"ERROR"}, DOWNLOAD_JOB.error)
                return {"CANCELLED"}

            if DOWNLOAD_JOB.cancel:
                self.report({"INFO"}, "Download cancelled.")
                return {"CANCELLED"}

            self.report({"INFO"}, "Download complete!")
            return {"FINISHED"}
        return {'FINISHED'}
