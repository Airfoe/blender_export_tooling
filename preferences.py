import bpy  # type: ignore
from .constants import get_operator
from .operators import USD_OT_DownloadUSDView


class Airfoe_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    root_directory: bpy.props.StringProperty(subtype="DIR_PATH", default="X:\\")#type: ignore
    usdview_path:bpy.props.StringProperty(subtype="DIR_PATH", default ="C:\\Users\\Fxnarji\\Documents\\test\\") #type: ignore

    def draw(self, context):
        layout = self.layout
        job = USD_OT_DownloadUSDView.DOWNLOAD_JOB
        usd_download_running = job is not None and not job.done and not job.cancel

        box = layout.box()
        box.prop(context.scene.export_hook_settings, "export_type", text="USD File Format")
        box.prop(self, "root_directory", text = "Global Root Directory")
        box.prop(context.scene.export_hook_settings, "export_root_directory", text = "Export Directory")

        box=layout.box()
        box.label(text="USD View")
        box.prop(self, "usdview_path", text = "Path")
        if usd_download_running:
            done_mb = job.bytes_done / (1024 * 1024)
            total_mb = job.bytes_total / (1024 * 1024)

            status = "{}... [{:.1f} / {:.1f} MB]".format(
                job.phase,
                done_mb,
                total_mb,
            )
            box.progress(factor = job.progress, type = "BAR", text=status)
            box.operator(USD_OT_DownloadUSDView.USD_OT_CancelDownload.bl_idname, text = "Cancel Download", icon = "CANCEL")
        else:
            box.operator(USD_OT_DownloadUSDView.USD_OT_DownloadUSDView.bl_idname, text = "Download Nvidias USD View", icon = "IMPORT")

