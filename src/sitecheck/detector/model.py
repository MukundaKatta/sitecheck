"""CNN-based construction defect detector."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from sitecheck.models import DefectType


# Class index mapping
DEFECT_CLASSES: list[DefectType] = [
    DefectType.CRACKING,
    DefectType.MISALIGNMENT,
    DefectType.WATER_DAMAGE,
    DefectType.REBAR_EXPOSURE,
    DefectType.HONEYCOMBING,
]

CLASS_TO_IDX: dict[DefectType, int] = {d: i for i, d in enumerate(DEFECT_CLASSES)}
NUM_CLASSES = len(DEFECT_CLASSES)


class DefectCNN(nn.Module):
    """Lightweight CNN for construction defect classification.

    Accepts 3-channel images of size 224x224 and outputs logits for
    5 defect classes.

    Architecture
    ------------
    - 3 convolutional blocks (conv -> batch-norm -> ReLU -> max-pool)
    - Adaptive average pool -> flatten
    - 2 fully-connected layers with dropout
    """

    def __init__(self, num_classes: int = NUM_CLASSES, dropout: float = 0.3) -> None:
        super().__init__()

        self.features = nn.Sequential(
            # Block 1: 224x224 -> 112x112
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            # Block 2: 112x112 -> 56x56
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            # Block 3: 56x56 -> 28x28
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )

        self.pool = nn.AdaptiveAvgPool2d((4, 4))

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 4 * 4, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(256, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass: (B, 3, 224, 224) -> (B, num_classes) logits."""
        x = self.features(x)
        x = self.pool(x)
        x = self.classifier(x)
        return x


@dataclass
class DetectionResult:
    """Output of DefectDetector.detect()."""

    predicted_class: DefectType
    confidence: float
    class_probabilities: dict[DefectType, float]


@dataclass
class DefectDetector:
    """High-level defect detection wrapper around DefectCNN.

    Parameters
    ----------
    model_path : str | None
        Path to a saved state dict.  If None the model is initialised
        with random weights (useful for simulation / testing).
    device : str
        ``"cpu"`` or ``"cuda"``.
    confidence_threshold : float
        Minimum softmax probability to accept a detection.
    """

    model_path: Optional[str] = None
    device: str = "cpu"
    confidence_threshold: float = 0.5
    _model: DefectCNN = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._model = DefectCNN()
        if self.model_path is not None:
            state = torch.load(self.model_path, map_location=self.device)
            self._model.load_state_dict(state)
        self._model.to(self.device)
        self._model.eval()

    def detect(self, image: torch.Tensor) -> DetectionResult:
        """Classify a single image tensor of shape (3, 224, 224).

        Returns a :class:`DetectionResult` with class probabilities.
        """
        if image.dim() == 3:
            image = image.unsqueeze(0)  # add batch dim

        image = image.to(self.device)
        with torch.no_grad():
            logits = self._model(image)
            probs = F.softmax(logits, dim=1).squeeze(0)

        class_probs = {
            DEFECT_CLASSES[i]: float(probs[i]) for i in range(NUM_CLASSES)
        }
        best_idx = int(torch.argmax(probs))
        return DetectionResult(
            predicted_class=DEFECT_CLASSES[best_idx],
            confidence=float(probs[best_idx]),
            class_probabilities=class_probs,
        )

    def detect_batch(self, images: torch.Tensor) -> list[DetectionResult]:
        """Classify a batch of images of shape (B, 3, 224, 224)."""
        images = images.to(self.device)
        with torch.no_grad():
            logits = self._model(images)
            probs = F.softmax(logits, dim=1)

        results: list[DetectionResult] = []
        for i in range(probs.shape[0]):
            p = probs[i]
            class_probs = {
                DEFECT_CLASSES[j]: float(p[j]) for j in range(NUM_CLASSES)
            }
            best_idx = int(torch.argmax(p))
            results.append(
                DetectionResult(
                    predicted_class=DEFECT_CLASSES[best_idx],
                    confidence=float(p[best_idx]),
                    class_probabilities=class_probs,
                )
            )
        return results

    def is_defect(self, result: DetectionResult) -> bool:
        """Check whether the detection confidence exceeds the threshold."""
        return result.confidence >= self.confidence_threshold
