"""Tests for the defect detection, classification, and standards modules."""

import pytest
import torch

from sitecheck.models import DefectType, SeverityLevel
from sitecheck.detector.model import DefectDetector, DefectCNN, NUM_CLASSES
from sitecheck.detector.classifier import DefectClassifier
from sitecheck.detector.standards import QualityStandards, StandardCode


class TestDefectCNN:
    def test_forward_shape(self):
        model = DefectCNN()
        x = torch.randn(2, 3, 224, 224)
        out = model(x)
        assert out.shape == (2, NUM_CLASSES)

    def test_single_image(self):
        model = DefectCNN()
        x = torch.randn(1, 3, 224, 224)
        out = model(x)
        assert out.shape == (1, NUM_CLASSES)


class TestDefectDetector:
    def test_detect(self):
        detector = DefectDetector()
        img = torch.randn(3, 224, 224)
        result = detector.detect(img)
        assert result.predicted_class in DefectType
        assert 0 <= result.confidence <= 1.0
        assert len(result.class_probabilities) == NUM_CLASSES

    def test_detect_batch(self):
        detector = DefectDetector()
        imgs = torch.randn(4, 3, 224, 224)
        results = detector.detect_batch(imgs)
        assert len(results) == 4


class TestDefectClassifier:
    @pytest.mark.parametrize(
        "defect_type,measurement,expected",
        [
            (DefectType.CRACKING, 0.05, SeverityLevel.COSMETIC),
            (DefectType.CRACKING, 0.2, SeverityLevel.MINOR),
            (DefectType.CRACKING, 0.5, SeverityLevel.MAJOR),
            (DefectType.CRACKING, 2.0, SeverityLevel.CRITICAL),
            (DefectType.MISALIGNMENT, 5.0, SeverityLevel.COSMETIC),
            (DefectType.MISALIGNMENT, 30.0, SeverityLevel.CRITICAL),
            (DefectType.REBAR_EXPOSURE, 10.0, SeverityLevel.MAJOR),
            (DefectType.REBAR_EXPOSURE, 100.0, SeverityLevel.CRITICAL),
            (DefectType.HONEYCOMBING, 3.0, SeverityLevel.COSMETIC),
            (DefectType.HONEYCOMBING, 50.0, SeverityLevel.CRITICAL),
        ],
    )
    def test_classify(self, defect_type, measurement, expected):
        classifier = DefectClassifier()
        result = classifier.classify(defect_type, measurement)
        assert result == expected

    def test_classify_finding_returns_model(self):
        classifier = DefectClassifier()
        finding = classifier.classify_finding(
            DefectType.CRACKING, 0.5, location="Column A1"
        )
        assert finding.severity == SeverityLevel.MAJOR
        assert finding.remediation is not None
        assert finding.standard_reference is not None


class TestQualityStandards:
    def test_by_code(self):
        qs = QualityStandards()
        specs = qs.by_code(StandardCode.ACI_318)
        assert len(specs) >= 2

    def test_by_parameter(self):
        qs = QualityStandards()
        specs = qs.by_parameter("crack width")
        assert len(specs) >= 1

    def test_check_compliance_within(self):
        qs = QualityStandards()
        result = qs.check_compliance(
            StandardCode.ACI_318, "Concrete cover - cast against earth", 75.0
        )
        assert result is not None
        compliant, spec = result
        assert compliant is True

    def test_check_compliance_outside(self):
        qs = QualityStandards()
        result = qs.check_compliance(
            StandardCode.ACI_318, "Concrete cover - cast against earth", 100.0
        )
        assert result is not None
        compliant, _ = result
        assert compliant is False

    def test_summary_counts(self):
        qs = QualityStandards()
        s = qs.summary()
        assert len(s) > 0
