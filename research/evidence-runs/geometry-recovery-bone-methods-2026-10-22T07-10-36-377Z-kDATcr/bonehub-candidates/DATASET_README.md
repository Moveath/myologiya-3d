---
pretty_name: Visible Human Full-Skeleton 3D Bone Models
license: cc-by-4.0
task_categories:
  - image-segmentation
  - mask-generation
tags:
  - medical-imaging
  - ct-scan
  - visible-human-project
  - segmentation
  - bone-segmentation
  - skeletal-anatomy
  - musculoskeletal
  - anatomy
  - orthopedics
  - biomechanics
  - 3d-models
  - mesh
  - stl
  - cad
  - iges
  - step
  - nurbs
size_categories:
  - n<1K
annotations_creators:
  - expert-generated
  - machine-generated
viewer: false
---

# Visible Human Full-Skeleton 3D Bone Models

**[🌐 View the interactive 3D demo here](https://bonehub.github.io/Educational-Atlas/)**

This dataset contains CT segmentation labels, STL meshes, and NURBS CAD surfaces (IGES and STEP) for **142 (male) and 143 (female) individually labeled bones** from two subjects — the most anatomically complete full-skeleton labeling of the NLM Visible Human dataset publicly available.

<p align="center">
  <img src="./visible_human_3d_models/CT/Segmentation/preview.png" alt="Preview of full-skeleton segmentation for the Visible Human Male and Female subjects" width="600">
</p>
<p align="center"><em>Rendered preview of the segmented full-skeleton bone models — Visible Human Male and Female.</em></p>

## Dataset Summary

Both subjects — Visible Human Male and Female — were segmented from their aligned whole-body CT volumes. Bones are labeled individually rather than as grouped regions: every vertebra, rib, carpal, metacarpal, tarsal and metatarsal is its own label. The exceptions are the phalanges, the skull, the sternum, and the sacrum, whose label (`SACRUM`) also includes the coccyx (see [Known Issues & Limitations](#known-issues--limitations)). The female subject has one more label than the male because she has a sixth lumbar vertebra (`VERTEBRA_L6`).

Each bone is provided as:

- a **voxel segmentation label**,
- a corresponding **STL surface mesh**, and
- a corresponding **NURBS CAD surface** in both **IGES** and **STEP** format,

so the data is readily usable for ML segmentation training, biomechanical MSK/FE modeling, or CAD-based work (implant design, prosthetics, 3D printing) without needing to convert between formats or isolate individual bones by hand.

All models are currently derived from CT. The Visible Human Project also provides MRI and whole-body cryosection images of the same subjects. The cryosection images show soft tissues (muscles, tendons, ligaments and organs) that CT does not resolve well. Segmentations from these modalities may be added in the future.

## Source Data & Provenance

The underlying CT imagery originates from the National Library of Medicine's **Visible Human Project**, as aligned and redistributed by the University of Denver Center for Orthopaedic Biomechanics:

> Andreassen, T.E., Hume, D.R., Hamilton, L.D. *et al.* Three Dimensional Lower Extremity Musculoskeletal Geometry of the Visible Human Female and Male. *Sci Data* **10**, 34 (2023). https://doi.org/10.1038/s41597-022-01905-2

Data files were obtained directly from [Digital Commons @ DU](https://digitalcommons.du.edu/visiblehuman/) — specifically the **Aligned CT (DICOM)** series for both subjects.

That source release is licensed **CC BY 4.0** and covers fewer bones, some of them grouped — the metatarsals and phalanges of each foot, for example, form a single geometry rather than separate bones — giving 28 bone geometries per subject, from the pelvis to the feet. This dataset is an independent derivative that labels the bones individually (see above) — 142 labels for the male and 143 for the female — over the whole body rather than the lower extremity alone.

### Subjects

Two cadaveric subjects included in this dataset:

| Index | Subject | Sex | Age | Height | Weight | BMI |
|---|---|---|---|---|---|---|
| 1 | Visible Human Male | M | 39 | 180 cm (71 in) | 90 kg | 27.8 |
| 2 | Visible Human Female | F | 59 | 157 cm (62 in) | 88 kg | 35.7 |

## How This Dataset Was Created

1. **Format conversion.** The source DICOM series were loaded in [3D Slicer](https://www.slicer.org/) and converted to NIfTI (`.nii.gz`).
2. **Segmentation.** Each subject was segmented by two trained human annotators using the [nnInteractive](https://arxiv.org/abs/2503.08373) promptable deep-learning segmentation framework, via the [SlicerNNInteractive](https://github.com/coendevente/SlicerNNInteractive) 3D Slicer extension — i.e. model-assisted, human-verified segmentation rather than fully manual or fully automatic.
3. **Mesh reconstruction.** 3D surface meshes were exported from the finished segmentations in 3D Slicer (smoothing factor 0.5) and saved as STL without further post-processing. See [`CT/Mesh/README.md`](./visible_human_3d_models/CT/Mesh/README.md) for the export script.
4. **CAD conversion.** The STL meshes were converted to NURBS surfaces in Rhino3D using the open-source [Mesh2NURBS-Rhino3D](https://github.com/BoneHub/Mesh2NURBS-Rhino3D) pipeline, which removes isolated mesh islands before remeshing, and exported in IGES and STEP format. Settings for each anatomy folder and a script to reproduce the conversion are in [`CT/NURBS/README.md`](./visible_human_3d_models/CT/NURBS/README.md).

## Dataset Structure

```
visible_human_3d_models/CT/
├── metadata.json                                # subject sex, age, height, weight, BMI
├── Image/<subject>.nii.gz                       # aligned whole-body CT volume
├── Segmentation/<subject>/<anatomy>.seg.nrrd    # 3D Slicer segmentation, one label per bone
├── Mesh/<subject>/<anatomy>/<BONE>.stl          # surface mesh per bone
└── NURBS/<subject>/<anatomy>/<BONE>.iges|.step  # NURBS CAD surface per bone
```

`<subject>` is `01_Male` or `02_Female`. `<anatomy>` is one of `SKULL`, `SPINAL_COLUMN`, `THORAX`, `UPPER_EXTREMITY_LEFT/RIGHT`, `LOWER_EXTREMITY_LEFT/RIGHT`, `HAND_LEFT/RIGHT`, `FOOT_LEFT/RIGHT`. The hand and foot are stored as separate categories for convenience; see [Known Issues & Limitations](#known-issues--limitations).

## Intended Uses

- Training/evaluating deep-learning models for fine-grained skeletal CT segmentation (per-bone rather than region-level)
- Biomechanical simulation and finite element analysis (FEA) requiring individual bone geometry
- CAD-based orthopedic implant, prosthetic, or surgical-guide design
- 3D printing of individual anatomical bone models
- Anatomy education and reference

## Known Issues & Limitations

- **Incomplete elbow region.** The elbow region is not fully captured in the source CT data (missing or truncated image data at this level). As a result, the distal humerus and the proximal radius and ulna are incomplete, and the elbow joint cannot be reconstructed in full. This comes from the original image acquisition, not from the segmentation, and cannot be corrected in this derivative dataset.
- **Combined phalanges.** The proximal, middle and distal phalanges of each digit are not segmented individually. They form a single label per finger or toe, so the interphalangeal joints are not represented as separate bone geometries.
- **Combined cranium and maxilla.** The cranium and the maxilla form a single label (`SKULL_CRANIAL_MAXILLA`). The individual cranial and facial bones are not separated; the mandible (`SKULL_MANDIBLE`) is the only other skull label.
- **Combined sacrum and coccyx.** The coccyx is not labeled separately; it is part of the `SACRUM` label.
- **Undivided sternum.** The manubrium, body and xiphoid process of the sternum form a single label (`STERNUM`).
- **Hyoid bone not included.** The hyoid bone is not segmented.
- **Sesamoid bones not included.** The patella is the only sesamoid bone in the dataset. Other sesamoid bones, such as those of the first metatarsophalangeal and first metacarpophalangeal joints, are not segmented.
- **Costal cartilages not included.** Only bone is segmented, so the costal cartilages are absent and there is no geometric connection between the ribs and the sternum. Models of the thorax that need the costochondral and sternocostal connections, such as finite element models, must add these cartilages themselves.
- **Non-standard regional grouping.** In standard anatomical terminology, the hand is part of the upper extremity and the foot is part of the lower extremity. Here the hand and foot bones are stored in separate anatomy folders (`HAND_LEFT/RIGHT`, `FOOT_LEFT/RIGHT`), apart from `UPPER_EXTREMITY_LEFT/RIGHT` and `LOWER_EXTREMITY_LEFT/RIGHT`. This grouping is for organizing the data only and does not follow anatomical definitions. To get a complete extremity, combine the matching extremity and hand/foot folders.
- **Annotator judgment.** Segmentation reflects the judgment of the annotators; no inter-rater reliability figures are provided.

## Licensing & Attribution

This dataset is released under **CC BY 4.0**, consistent with the source dataset's license. If you use this dataset, please cite **both**:

1. The original Visible Human 3D geometry paper (Andreassen et al., 2023 — see above), since this work derives from their aligned CT release.
2. This dataset (citation below).

## Citation

```bibtex
@misc{seyedhamidrezaalaviVisiblehuman3dModels,
  title = {Visible-Human-3d-Models},
  author = {Seyed Hamidreza Alavi and Malte Asseln},
  year = 2026,
  publisher = {Hugging Face},
  doi = {10.57967/HF/10464},
  url = {https://huggingface.co/datasets/BoneHub/visible-human-3d-models},
}
```

```bibtex
@article{andreassen2023visible,
  title={Three Dimensional Lower Extremity Musculoskeletal Geometry of the Visible Human Female and Male},
  author={Andreassen, Thor E. and Hume, Donald R. and Hamilton, Landon D. and Walker, Karen E. and Higinbotham, Sean E. and Shelburne, Kevin B.},
  journal={Scientific Data},
  volume={10},
  pages={34},
  year={2023},
  doi={10.1038/s41597-022-01905-2}
}
```

## Contact

This repository is maintained by: **Hamid Alavi** and **Malte Asseln**

Affiliation: Department of Biomechanical Engineering, University of Twente, The Netherlands.

Email: [hamid.alavi@utwente.nl](mailto:hamid.alavi@utwente.nl)

Email: [m.asseln@utwente.nl](mailto:m.asseln@utwente.nl)