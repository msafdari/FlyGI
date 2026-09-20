# MaleCNS data

FlyGI uses three bulk-download tables from **MaleCNS v1.0**, released on
2026-06-08:

| File | Role |
| --- | --- |
| `connectome-weights-male-cns-v1.0-minconf-0.5.feather` | Aggregated directed segment-to-segment connectivity |
| `body-annotations-male-cns-v1.0-minconf-0.5.feather` | Curated neuron annotations |
| `body-neurotransmitters-male-cns-v1.0.feather` | Per-neuron transmitter predictions |

The canonical source is the [MaleCNS download page](https://male-cns.janelia.org/download/).
The repository does not require or fetch individual-synapse tables, skeletons,
meshes, segmentation volumes, or EM imagery.

## Attribution and license

The Male CNS dataset is made available under the [Creative Commons Attribution
4.0 International license](https://creativecommons.org/licenses/by/4.0/). It
is a collaboration among FlyEM at HHMI Janelia, the University of Cambridge
Department of Zoology, the MRC Laboratory of Molecular Biology, and Google
Research. Cite the associated paper, *Sexual dimorphism in the complete
connectome of the Drosophila male central nervous system*,
[doi:10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015),
when publishing work based on these data.

FlyGI-derived runtime assets reindex neurons and may transform, sign, and
normalize edge weights. These are modifications of the source data, are not an
official MaleCNS release, and do not imply endorsement by the data creators.
The repository's MIT license applies to FlyGI code and documentation, not to
the MaleCNS source data.

## Local layout

Large inputs and generated assets are ignored by Git:

```text
data/
├── raw/                         # downloaded Feather files
├── processed/male-cns-v1.0/    # generated sparse runtime assets
└── manifests/                   # tracked provenance guidance only
```

After installing the project, the intended Milestone 1 workflow is:

```bash
flygi data fetch --release male-cns:v1.0
flygi graph build --config configs/literal_rate.yaml
flygi validate all --require-data
```

The checked-in configs intentionally contain `sha256: null`: the official
download page identifies the files but does not provide repository-maintained
SHA-256 values here. A null digest is **not** a verified hash. Do not claim a
verified download until an expected digest has been obtained through a trusted,
independent channel and recorded, or until the resulting manifest is explicitly
described as recording an observed digest rather than pre-verifying it.

Every real build must produce a manifest with source URLs, download time,
source and output SHA-256 values, schemas and dtypes, preprocessing options,
software versions, and measured graph statistics. No expected neuron count,
edge count, contact total, or digest is checked in as if it had been observed.
The configured `superclass` retention rule and `descending_neuron` group label
were inspected in the official v1.0 annotation table and remain explicit YAML
inputs, so their resulting counts are measured rather than assumed.
