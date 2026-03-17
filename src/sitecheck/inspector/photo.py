"""Photo documentation organiser for defect evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from sitecheck.models import DefectType, SeverityLevel


@dataclass
class PhotoMetadata:
    """Metadata for a single inspection photograph."""

    photo_id: str
    filename: str
    timestamp: datetime = field(default_factory=datetime.now)
    location: str = ""
    defect_type: Optional[DefectType] = None
    severity: Optional[SeverityLevel] = None
    finding_id: Optional[str] = None
    annotations: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    @property
    def extension(self) -> str:
        return Path(self.filename).suffix.lower()

    def add_annotation(self, text: str) -> None:
        self.annotations.append(text)


@dataclass
class PhotoDocumentor:
    """Organises and catalogues inspection photographs.

    Photos are grouped by defect type, severity, and location for
    easy retrieval and report inclusion.
    """

    project_name: str = "Unnamed Project"
    _photos: list[PhotoMetadata] = field(default_factory=list)
    _counter: int = field(default=0, init=False)

    def add_photo(
        self,
        filename: str,
        location: str = "",
        defect_type: Optional[DefectType] = None,
        severity: Optional[SeverityLevel] = None,
        finding_id: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> PhotoMetadata:
        """Register a new photo and return its metadata."""
        self._counter += 1
        photo = PhotoMetadata(
            photo_id=f"PHT-{self._counter:04d}",
            filename=filename,
            location=location,
            defect_type=defect_type,
            severity=severity,
            finding_id=finding_id,
            tags=tags or [],
        )
        self._photos.append(photo)
        return photo

    def get_photo(self, photo_id: str) -> Optional[PhotoMetadata]:
        for p in self._photos:
            if p.photo_id == photo_id:
                return p
        return None

    def by_defect_type(self, defect_type: DefectType) -> list[PhotoMetadata]:
        return [p for p in self._photos if p.defect_type == defect_type]

    def by_severity(self, severity: SeverityLevel) -> list[PhotoMetadata]:
        return [p for p in self._photos if p.severity == severity]

    def by_finding(self, finding_id: str) -> list[PhotoMetadata]:
        return [p for p in self._photos if p.finding_id == finding_id]

    def by_location(self, location_keyword: str) -> list[PhotoMetadata]:
        kw = location_keyword.lower()
        return [p for p in self._photos if kw in p.location.lower()]

    @property
    def total_photos(self) -> int:
        return len(self._photos)

    def summary(self) -> dict[str, int]:
        """Return a count of photos by defect type."""
        counts: dict[str, int] = {}
        for p in self._photos:
            key = p.defect_type.value if p.defect_type else "unclassified"
            counts[key] = counts.get(key, 0) + 1
        return counts

    def generate_directory_structure(self, base_dir: str = "photos") -> dict[str, list[str]]:
        """Propose a directory structure for organising photo files.

        Returns a mapping of directory path -> list of filenames.
        """
        structure: dict[str, list[str]] = {}
        for p in self._photos:
            defect_dir = p.defect_type.value if p.defect_type else "general"
            severity_dir = p.severity.value if p.severity else "ungraded"
            dir_path = f"{base_dir}/{defect_dir}/{severity_dir}"
            structure.setdefault(dir_path, []).append(p.filename)
        return structure
