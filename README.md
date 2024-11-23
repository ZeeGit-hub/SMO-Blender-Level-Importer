# SMO-Blender-Level-Importer
Blender plugin to import Super Mario Odyssey stages into Blender.

Credits: exelix, MonsterDruide1, ChatGPT, Zee

Requirements:
EditorCore with Super Mario Odyssey plugin & Blender 3.0+ (Not tested with 4.0+, should still work though)

This tutorial assumes that you already have EditorCore installed and set up. If not, get it here: 
https://github.com/exelix11/EditorCore
and the Odyssey plugin here:
https://github.com/exelix11/OdysseyEditor

Instructions:

1. Install OdysseyImportComplete.py from the Releases tab

2. Install the Blender plugin: In blender, go to Edit > Preferences > Install, go through the file system and select OdysseyImportComplete.py, then click Install Addon

3. Setting up the Blender plugin: Press the small arrow on the left of the SMO Level Importer tab in Preferences, a window will drop down. In the OBJ Folder field,
press on the folder icon on the right of it, then navigate to the OdysseyModels folder in the OdysseyEditor (EditorCore) once viewing the folder with all of the .objs,
press Accept.

( Optional settings: "Exclude Objects", you can type in the name of objects to exclude them from  being imported, "Enable Debug Logging", Enables advanced
debugging, ! WILL SLOW THINGS DOWN ! )

Mandatory Option: Scenario Number, Selects one of the 14 scenarios for a level.

4. Obtaining XML for level: In OdysseyEditor (EditorCore) Open a stage of choice. once open, press Level files > XXXXXX.byml. (the byml that you should choose will
look like this: ForestWorldHomeStageMap and not this: ForestWorldHomeStage_7_x_02.byml) make sure to choose the right one.
Now, click on the correct .byml, and it will open a small window. You'll see a lot of +dictionary stuff. Right click on the white space next to it, then press "Export as XML"
Save it to somewhere easily accesible for blender, name it what you'd like.

5. Finally back in Blender, press File > Import > Import SMO Level XML, this will open a file browser window, navigate to the .xml file you saved, click on it, then press
Import. Blender will be frozen temporarily, time varies on how big the stage is. Rotate the map by 90 degrees on the X axis. It will probably be massive, so scale it to .001.
Then press View > Frame Selected

Enjoy ripping levels from Super Mario Odyssey.
