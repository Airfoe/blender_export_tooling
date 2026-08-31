import bpy  # type: ignore
from .constants import get_operator
from .operators import USD_OT_DownloadUSDView
from .project import paths

class Airfoe_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    root_directory: bpy.props.StringProperty(subtype="DIR_PATH", default="D:\\ShowcaseProject")#type: ignore

    show_source_paths: bpy.props.BoolProperty(default=False) #type: ignore
    source_environment_path:bpy.props.StringProperty(default=r"{ROOT}\3D\Environment\{NAME}") #type: ignore
    source_props_path:bpy.props.StringProperty(default=r"{ROOT}\3D\Props\{NAME}") #type: ignore
    source_char_path:bpy.props.StringProperty(default=r"{ROOT}\3D\chars\{NAME}") #type: ignore


    show_export_paths: bpy.props.BoolProperty(default=False) #type: ignore
    export_environment_path:bpy.props.StringProperty(default=r"{ROOT}\_export\{NAME}") #type: ignore
    export_props_path:bpy.props.StringProperty(default=r"{ROOT}\_export\props\{NAME}") #type: ignore
    export_char_path:bpy.props.StringProperty(default=r"{ROOT}\_export\chars\{NAME}") #type: ignore



    preview_export_paths: bpy.props.BoolProperty(default=False) #type: ignore
    preview_source_paths: bpy.props.BoolProperty(default=False) #type: ignore


    usdview_path:bpy.props.StringProperty(subtype="DIR_PATH", default ="C:\\Users\\Fxnarji\\Documents\\test\\") #type: ignore

    def draw(self, context):
        self.context = context
        layout = self.layout
        self.draw_project_settings(layout)
        self.draw_usdview(layout)



    def draw_project_settings(self, layout):
        box = layout.box()
        box.prop(self.context.scene.export_hook_settings, "export_type", text="USD File Format")
        box.prop(self, "root_directory", text = "Global Root Directory")

        box = layout.box()
        row = box.row()
        row.prop(self, "show_source_paths", text = "", icon='RIGHTARROW_THIN' if not self.show_source_paths else 'DOWNARROW_HLT')
        row.label(text = "Source Paths")

        if self.show_source_paths:
            split = box.split(factor=0.2)
            split.label(text = "Environments", icon = "SCENE_DATA")
            split.prop(self, "source_environment_path", text = "")


            split = box.split(factor=0.2)
            split.label(text = "Props", icon = "OUTLINER_OB_GROUP_INSTANCE")
            split.prop(self, "source_props_path", text = "")

            split = box.split(factor=0.2)
            split.label(text = "Characters", icon = "USER")
            split.prop(self, "source_char_path", text = "")

            box.prop(self, "preview_source_paths", text = "Preview Source Paths", icon='HIDE_OFF')

            if self.preview_source_paths:
                path = box.box()
                path.label(text = paths.source_environment_path)

                path = box.box()
                path.label(text = paths.source_props_path)

                path = box.box()
                path.label(text = paths.source_char_path)

        box = layout.box()
        row = box.row()
        row.prop(self, "show_export_paths", text = "", icon='RIGHTARROW_THIN' if not self.show_export_paths else 'DOWNARROW_HLT')
        row.label(text = "Export Paths")

        if self.show_export_paths:
            split = box.split(factor=0.2)
            split.label(text = "Environments", icon = "SCENE_DATA")
            split.prop(self, "export_environment_path", text = "")

            split = box.split(factor=0.2)
            split.label(text = "Props", icon = "OUTLINER_OB_GROUP_INSTANCE")
            split.prop(self, "export_props_path", text = "")

            split = box.split(factor=0.2)
            split.label(text = "Characters", icon = "USER")
            split.prop(self, "export_char_path", text = "")
            box.prop(self, "preview_export_paths", text = "Preview Export Paths", icon='HIDE_OFF')

            if self.preview_export_paths:

                path = box.box()
                path.label(text = paths.export_environment_path)

                path = box.box()
                path.label(text = paths.export_props_path)

                path = box.box()
                path.label(text = paths.export_char_path)

    def draw_usdview(self, layout):
        job = USD_OT_DownloadUSDView.DOWNLOAD_JOB
        usd_download_running = job is not None and not job.done and not job.cancel


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
            box.operator(USD_OT_DownloadUSDView.USD_OT_DownloadUSDView.bl_idname, text = "Download Nvidia USD View", icon = "IMPORT")

