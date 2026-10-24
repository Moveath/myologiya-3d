The script below was used in 3DSlicer python console to generate the 3D meshes from the segmentations.

```python
shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
sceneItem = shNode.GetSceneItemID()
rootFolder = shNode.CreateFolderItem(sceneItem, "BONE_MODELS")

SMOOTHING = 0.5   # 0 = no smoothing, 1 = strong smoothing

total = 0
for segNode in slicer.util.getNodesByClass("vtkMRMLSegmentationNode"):
    seg = segNode.GetSegmentation()
    seg.SetConversionParameter("Smoothing factor", str(SMOOTHING))
    segNode.RemoveClosedSurfaceRepresentation()   # force rebuild with the smoothing setting
    segNode.CreateClosedSurfaceRepresentation()

    folder = shNode.CreateFolderItem(rootFolder, segNode.GetName())
    ok = slicer.modules.segmentations.logic().ExportAllSegmentsToModels(segNode, folder)
    n = seg.GetNumberOfSegments()
    total += n if ok else 0
    print(f"{segNode.GetName():25s} {'OK' if ok else 'FAILED'}  ({n} models)")

    segNode.GetDisplayNode().SetVisibility(False)

print(f"Done: {total} models created")
```