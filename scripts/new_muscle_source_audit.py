"""Reproduce the inventory and public-metadata audit of missing head muscles.

No source mesh is invented, no card flags are changed. Raw publications and
donor data remain in research/cache and are not part of the publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

from head_muscles import MUSCLE_TEMPLATES
from manifest_head import MUSCLES

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "research/cache/new-muscles"


def fetch_json(url: str, filename: str, refresh: bool) -> dict:
    target = CACHE / filename
    if refresh or not target.exists():
        with urllib.request.urlopen(url, timeout=40) as response:
            target.write_bytes(response.read())
    return json.loads(target.read_text(encoding="utf-8"))


def inventory() -> tuple[list, list]:
    missing, parts = [], []
    for base, card in MUSCLE_TEMPLATES.items():
        keys = [base] if base in {"orbicularis_oris", "transversus_menti"} else [base + "_right", base + "_left"]
        for key in keys:
            if key not in MUSCLES:
                missing.append({"id": key, "ru": card["ru"], "lat": card["lat"], "ta98": card["code"]})
            available = {part for _, part in MUSCLES.get(key, [])}
            for part, record in card.get("parts", {}).items():
                if part not in available:
                    parts.append({"muscle": key, "part": part, "ru": record["ru"], "lat": record["lat"], "ta98": record["code"]})
    return missing, parts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="Refresh official public metadata")
    parser.add_argument("--download-jena-example", action="store_true", help="Download donor01 masks only (20 MB), verify publisher MD5")
    args = parser.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    missing, parts = inventory()
    vap = []
    for uid in ["22dbb37977304b5aab9db083b51026d2", "e454a6e1c3f14982b0597f34a236dc85"]:
        url = "https://api.sketchfab.com/v3/models/" + uid
        record = fetch_json(url, uid + ".json", args.refresh)
        vap.append({
            "uid": uid, "title": record["name"], "metadata_url": url,
            "url": record["viewerUrl"], "license": record["license"],
            "downloadable_declared_by_publisher": record["isDownloadable"],
            "vertices_reported_by_publisher": record["vertexCount"],
            "triangles_reported_by_publisher": record["faceCount"],
            "local_source_mesh_obtained": False,
            "download_check": {
                "url": url + "/download", "date": "2026-10-12", "http_status": 401,
                "reason": "Official download API requires authenticated access. No viewer assets were extracted to bypass this requirement.",
            },
        })
    dataset = fetch_json("https://api.figshare.com/v2/articles/32324658", "3dface-dataset.json", args.refresh)
    example = next(f for f in dataset["files"] if f["name"] == "01.zip")
    example_path = CACHE / example["name"]
    if args.download_jena_example and not example_path.exists():
        urllib.request.urlretrieve(example["download_url"], example_path)
    checked = None
    if example_path.exists():
        checked = hashlib.file_digest(example_path.open("rb"), "md5").hexdigest()
        if checked != example["computed_md5"]:
            raise ValueError("Jena donor01 checksum mismatch")
    audit = {
        "date": "2026-10-12",
        "scope": "Only actual source models or segmentations; no speculative educational reconstructions.",
        "missing_whole_muscle_instances": missing,
        "missing_individual_part_instances": parts,
        "new_geometry_integrated": 0,
        "completion_claim": False,
        "candidates": [
            {
                "id": "visible_ape_human_head", "author": "José Saúl Martín / Visible Ape Project",
                "primary_project_url": "https://www.visibleapeproject.com/3d-human-head-and-neck",
                "type": "Existing artist-authored anatomical source model, not a scan-derived donor segmentation",
                "relevance": "The author's numbered human muscle list names depressor supercilii (5) and two masseter heads (12a/12b). Auricularis and transversus menti are not listed.",
                "status": "Source license and availability confirmed; source-file delivery requires Sketchfab authentication, mesh contents and bilateral coverage remain unverified.",
                "files": vap,
                "acceptance_requirements": [
                    "Obtain the source using the publisher's authorized download workflow.",
                    "Inspect actual objects and left/right geometry; the title and annotation list do not prove separate meshes.",
                    "Verify named muscle surfaces against two anatomical sources before integration.",
                    "Keep specimen/source coordinates distinct unless registration is independently checked.",
                ],
            },
            {
                "id": "jena_3d_face", "title": dataset["title"],
                "url": "https://doi.org/10.6084/m9.figshare.32324658", "license": dataset["license"],
                "primary_paper": "https://doi.org/10.3390/jimaging12090459",
                "status": "Real publicly downloadable muscle/bone segmentation masks acquired and inspected; not separately labeled missing muscles.",
                "limitation": "The authors deliberately segmented muscle groups and did not assign traditional individual facial-muscle boundaries. Raw CT/MRI intensities are not freely distributed. Group masks cannot prove the geometry of the nine missing muscle instances or ten missing part instances.",
                "method_locator": "Paper section 2.4 Segmentation and Figshare dataset description",
                "file_count": len(dataset["files"]), "total_bytes": sum(f["size"] for f in dataset["files"]),
                "example": {"name": example["name"], "download_url": example["download_url"], "bytes": example["size"], "publisher_md5": example["computed_md5"], "verified_md5": checked,
                    "ct_shape": [512, 512, 378], "ct_spacing_mm": [0.4877011179924011] * 3,
                    "ct_bone1_labels": {"0": 96602334, "1": 2488098},
                    "ct_bone2_labels": {"0": 83726012, "1": 1550495, "2": 2923317, "3": 10890608},
                    "ct_label_caution": "These are not individual skull-bone labels. The two stored sform matrices differ in axis signs; do not overlay without registration review.",
                    "mri_muscle_shape": [704, 704, 640], "mri_muscle_spacing_mm": [0.31818199157714844, 0.31818199157714844, 0.3200000524520874]},
            },
            {
                "id": "li_toronto_2015", "title": "Functional Analysis of the Architecture of the Oro-facial and Hyoid Musculature: A Comparative 3D Modelling Study",
                "author": "Zhi Li, University of Toronto, 2015",
                "url": "https://www.collectionscanada.gc.ca/obj/thesescanada/vol2/OTU/TC-OTU-69552.pdf",
                "locator": "Table 5.1, thesis page 54; limitations page 124",
                "relevance": "Cadaveric digitizer study reports transversus menti and a right auricularis among reconstructed muscles.",
                "status": "Thesis located, but no reusable source mesh dataset or open geometry redistribution license found.",
                "license": "Thesis title page: copyright Zhi Li 2015; not a license to redistribute the underlying 3D model.",
                "limitation": "A figure, measured fibre count or 2D projection cannot reconstruct the unpublished 3D geometry. Auricularis is not resolved into all three required external-ear muscles by the table.",
            },
            {
                "id": "mida", "url": "https://itis.swiss/virtual-population/regional-human-models/mida-model",
                "primary_paper": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4406723/", "locator": "Table 1",
                "status": "No separately named target muscles in the published segmentation list.",
                "limitation": "The list contains many facial muscles but no auricularis anterior/superior/posterior, depressor supercilii or transversus menti. Ear auricular cartilage is not ear muscle.",
            },
            {
                "id": "faceforge", "url": "https://github.com/gddickinson/FaceForge",
                "locator": "assets/config/muscles/expression_muscles.json and jaw_muscles.json",
                "status": "Same BodyParts3D-derived facial structures; no new target muscles or missing named parts.",
                "limitation": "Software animation and its simulated MRI/CT displays are not acquired imaging evidence.",
            },
            {
                "id": "anatomytool_open3d", "url": "https://anatomytool.org/sites/default/files/2025-01-03%20NAV%20Workshop%20Open%203D%20anatomie%20incl%20Open%203D%20model%20No%20video.pdf",
                "locator": "Project activities / status 1-1-2025 table",
                "status": "Published roadmap lists no head/neck muscle models at that date. This historical snapshot does not establish the current absence of all future updates.",
            },
            {
                "id": "dundee_pharynx", "url": "https://sketchfab.com/3d-models/pharynx-and-floor-of-mouth-b262c70bf9bd49c2a5428581b754f24b",
                "author": "Eve Laws / University of Dundee; anatomical approval Luke Reid",
                "license": "CC BY-NC-SA 4.0", "status": "Different anatomical scope and NC-restricted source; not exported into the open atlas.",
            },
            {
                "id": "nonhuman_dicect", "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7304424/",
                "locator": "Methods: scanning and segmentation; Table 1",
                "status": "Rejected as substitute for human geometry: segmented facial/auricular muscles belong to Eulemur flavifrons.",
                "limitation": "Homologous names do not permit transplanting an animal's muscle geometry into a human atlas.",
            },
        ],
    }
    out = ROOT / "research/new-muscle-source-audit.json"
    out.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(missing)} missing muscle instances; {len(parts)} missing part instances; 0 unverified meshes added")


if __name__ == "__main__":
    main()
