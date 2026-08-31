# Pipeline Addon für Semesterprojekt.

# How to Install:
In Blender, add a remote repository with this URL:
`extensions.airfoe.com`
Then look for Airfoe Blender Tooling, and download from there.

## Configuration
In Edit > preferences > Add-Ons, look for Airfoe Blender Tooling. This is where you can set
- USD file Format (either USDC or USDA)
- Project Source Directory (Paths for Environments, Props, Characters)
- Project Export Directory (Paths for Environments, Props, Characters)
- Download location for Nvidias USDView (optional dependency)

## How to make a new Scene
- open Empty file
- click on `Set as Scene`
- make a GEO and a LAYOUT collection
The GEO collection should be all level specific Geometry. The Layout collection should house all instances to Assets.
Export the GEO collection first, as the LAYOUT usda file will link the GEO usda file into it.

## How to make an Asset
The easiest way to add an Asset is when you are already in a Scene. Simply add one (or many) objects, select them all and click Make Asset.
This will move your selected objects to a seperate Blend file, and link it back into the scene file as an instance. When inside the file, click `Set as Asset`. You can then optionally set
- a high poly collection
- the Parent Class of the Unreal Engine Blueprint

## Collider Tools:
### Make Collider Objects:
Uses Unreal Engines UCX to parent selected objects to the active one and mark them as collider. This assumes that the selected objects are already convex.

### Make Quick Collisions:
Will generate a convex hull for a collider

### Show / Hide Colliders:
As the name says

## misc tools
### Group Objects
Will create a new Empty, parent all selected objects to it. This will act as a hirarchy in USD and later in the unreal import.

### Guide | Render | Proxy | Clear
Set the USD Purpose of selected objects

### Open Asset
Will open the associated Blender file of the currently selected linked library

### Make Asset
Will Create a new asset from the selected Object(s). For more info, see above.

### Fix Texture Paths:
Quick throwaway utility to fix absolute paths. 

### USD Tools
If you downloaded USD View from Nvidia via the addons preferences, here you can inspect the exported usd files

Developed by Fynn Luft. 
Claude Code was used in some instances and marked as such in the Code. Github Copilot was used as fancy autocomplete.
