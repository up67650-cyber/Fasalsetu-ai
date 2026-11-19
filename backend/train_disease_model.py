import argparse
import json
from pathlib import Path

import tensorflow as tf

from .disease_guidance import PLANTVILLAGE_CLASSES


IMAGE_SIZE = (224, 224)
SEED = 42


def build_model(class_count: int, imagenet_weights: bool) -> tf.keras.Model:
    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3), name="leaf_image")
    x = tf.keras.layers.Rescaling(
        scale=1 / 127.5,
        offset=-1,
        name="mobilenet_v2_preprocessing",
    )(inputs)
    augmentation = tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.08),
            tf.keras.layers.RandomZoom(0.1),
        ],
        name="training_augmentation",
    )
    base = tf.keras.applications.MobileNetV2(
        input_shape=(*IMAGE_SIZE, 3),
        include_top=False,
        weights="imagenet" if imagenet_weights else None,
        name="mobilenetv2_backbone",
    )
    base.trainable = False
    x = augmentation(x)
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.25)(x)
    outputs = tf.keras.layers.Dense(class_count, activation="softmax", name="disease_classes")(x)
    model = tf.keras.Model(inputs, outputs, name="fasalsetu_mobilenetv2")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def train(dataset_dir: Path, output_dir: Path, imagenet_weights: bool, epochs: int) -> None:
    train_dir = dataset_dir / "train"
    validation_dir = dataset_dir / "validation"
    test_dir = dataset_dir / "test"
    if not train_dir.is_dir() or not validation_dir.is_dir() or not test_dir.is_dir():
        raise SystemExit(
            "Expected dataset folders: <dataset-dir>\\train, \\validation, and \\test."
        )
    if output_dir.exists() and (
        not output_dir.is_dir() or any(output_dir.iterdir())
    ):
        raise SystemExit(f"Refusing to overwrite non-empty model directory: {output_dir}")

    train_data = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        image_size=IMAGE_SIZE,
        batch_size=32,
        seed=SEED,
    )
    validation_data = tf.keras.utils.image_dataset_from_directory(
        validation_dir,
        image_size=IMAGE_SIZE,
        batch_size=32,
        shuffle=False,
    )
    test_data = tf.keras.utils.image_dataset_from_directory(
        test_dir,
        image_size=IMAGE_SIZE,
        batch_size=32,
        shuffle=False,
    )
    classes = train_data.class_names
    if (
        test_data.class_names != classes
        or validation_data.class_names != classes
        or set(classes) != set(PLANTVILLAGE_CLASSES)
    ):
        raise SystemExit(
            "Training and test directories must contain the same 38 PlantVillage classes."
        )

    autotune = tf.data.AUTOTUNE
    train_data = train_data.prefetch(autotune)
    validation_data = validation_data.prefetch(autotune)
    test_data = test_data.prefetch(autotune)
    model = build_model(len(classes), imagenet_weights)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "model.keras"
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=3,
            restore_best_weights=True,
        ),
        tf.keras.callbacks.ModelCheckpoint(
            filepath=model_path,
            monitor="val_accuracy",
            mode="max",
            save_best_only=True,
        ),
    ]
    model.fit(
        train_data,
        validation_data=validation_data,
        epochs=epochs,
        callbacks=callbacks,
    )

    base = model.get_layer("mobilenetv2_backbone")
    base.trainable = True
    for layer in base.layers[:-30]:
        layer.trainable = False
    for layer in base.layers:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(
        train_data,
        validation_data=validation_data,
        epochs=max(1, min(epochs, 8)),
        callbacks=callbacks,
    )

    best_model = tf.keras.models.load_model(model_path, compile=False, safe_mode=True)
    evaluation = best_model.evaluate(test_data, return_dict=True, verbose=0)
    metadata = {
        "model_name": "FasalSetu MobileNetV2 PlantVillage transfer-learning classifier",
        "architecture": "MobileNetV2",
        "dataset": "PlantVillage",
        "dataset_source": "https://huggingface.co/datasets/mohanty/PlantVillage",
        "dataset_license": "CC-BY-SA-3.0",
        "dataset_attribution": "Mohanty, Hughes & Salathé (2016), https://doi.org/10.3389/fpls.2016.01419",
        "model_license_review": "Review PlantVillage share-alike and pretrained-backbone terms before redistribution.",
        "validation_split": "Deterministic 20% of training leaf_id groups; official test split retained.",
        "image_size": 224,
        "preprocessing": "internal_mobilenet_v2_minus1_to_1",
        "pretrained_imagenet_backbone": imagenet_weights,
        "classes": classes,
        "test_metrics": {key: float(value) for key, value in evaluation.items()},
        "warning": "PlantVillage images are controlled-condition images; test metrics do not establish field accuracy.",
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(metadata["test_metrics"], indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train a MobileNetV2 classifier on a locally prepared PlantVillage dataset."
    )
    parser.add_argument("--dataset-dir", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).with_name("models") / "plant_disease_mobilenetv2",
    )
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument(
        "--imagenet-weights",
        action="store_true",
        help="Download official Keras ImageNet MobileNetV2 weights for transfer learning.",
    )
    args = parser.parse_args()
    if args.epochs < 1:
        parser.error("--epochs must be at least 1")
    train(args.dataset_dir, args.output_dir, args.imagenet_weights, args.epochs)


if __name__ == "__main__":
    main()
