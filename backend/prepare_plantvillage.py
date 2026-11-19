import argparse
import hashlib
from pathlib import Path


DATASET_ID = "mohanty/PlantVillage"


def prepare(output_dir: Path) -> None:
    try:
        from datasets import load_dataset
    except ImportError as error:
        raise SystemExit("Install requirements-ml.txt before preparing the dataset.") from error

    if output_dir.exists() and not output_dir.is_dir():
        raise SystemExit(f"Dataset output path is not a directory: {output_dir}")

    dataset = load_dataset(
        DATASET_ID,
        "color",
        trust_remote_code=True,
    )
    labels = dataset["train"].features["label"].names
    saved = 0
    retained = 0
    for split in ("train", "test"):
        for index, row in enumerate(dataset[split]):
            class_name = labels[int(row["label"])]
            if split == "test":
                output_split = "test"
            else:
                leaf_id = row.get("leaf_id")
                if not leaf_id:
                    raise ValueError("PlantVillage row is missing the leaf_id needed for a safe split.")
                leaf_hash = hashlib.sha256(str(leaf_id).encode("utf-8")).digest()
                output_split = "validation" if int.from_bytes(leaf_hash[:8], "big") % 5 == 0 else "train"
            destination = output_dir / output_split / class_name / f"{index:06d}.jpg"
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                retained += 1
            else:
                row["image"].convert("RGB").save(destination, format="JPEG", quality=95)
                saved += 1
        print(f"Prepared {split} source split.")

    print(f"Prepared PlantVillage RGB images under {output_dir}")
    print(f"Saved {saved} images; retained {retained} existing images.")
    print("The 20% validation split is deterministic and grouped by leaf_id.")
    print("Dataset license: CC BY-SA 3.0. Preserve attribution and review share-alike obligations.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download and arrange the official PlantVillage color splits."
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--accept-cc-by-sa",
        action="store_true",
        help="Confirm that you reviewed the dataset's CC BY-SA 3.0 terms.",
    )
    args = parser.parse_args()
    if not args.accept_cc_by_sa:
        parser.error("Review the dataset license, then pass --accept-cc-by-sa.")
    prepare(args.output_dir)


if __name__ == "__main__":
    main()
