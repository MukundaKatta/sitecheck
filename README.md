# SiteCheck

Construction Defect Detector -- an AI-powered inspection tool for identifying and classifying structural defects on construction sites.

## Features

- **Defect Detection**: CNN-based detector trained to identify cracking, misalignment, water damage, rebar exposure, and honeycombing.
- **Severity Grading**: Classifies defects into severity tiers (cosmetic, minor, major, critical) with reference to industry standards.
- **Standards Compliance**: Built-in ACI 318, ACI 301, ASTM C150, ASTM E119, and ASTM C33 tolerance references.
- **Inspection Checklists**: Trade-specific checklists for concrete, masonry, steel, wood, plumbing, and electrical work.
- **Report Generation**: Comprehensive inspection reports with findings, photos, and remediation recommendations.
- **Photo Documentation**: Organises defect evidence with metadata and annotations.

## Installation

```bash
pip install -e .
```

## Dependencies

- torch
- numpy
- pydantic
- click
- rich

## Usage

```bash
# Run an inspection simulation
sitecheck simulate --defects 10

# Classify a defect
sitecheck classify --type cracking --width 0.5

# Check standards compliance
sitecheck standards --code ACI-318

# Generate a full inspection report
sitecheck report

# View checklist for a trade
sitecheck checklist --trade concrete
```

## Project Structure

```
src/sitecheck/
  cli.py              - Command-line interface
  models.py           - Pydantic data models
  simulator.py        - Defect simulation engine
  report.py           - Report generation
  detector/
    model.py           - CNN defect detector
    classifier.py      - Severity grading
    standards.py       - ACI/ASTM tolerance references
  inspector/
    checklist.py       - Trade-specific inspection checklists
    report_gen.py      - Inspection report generator
    photo.py           - Photo documentation organiser
```

## Author

Mukunda Katta
