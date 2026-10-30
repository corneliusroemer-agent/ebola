# Nextclade

Previously, all "official" Nextclade workflows lived in a [central GitHub repository](https://github.com/neherlab/nextclade_data_workflows).
The new standard would be to include the Nextclade workflow within the pathogen repo.

This workflow is used to create the Nextclade datasets for this pathogen.
All official Nextclade datasets are available at https://github.com/nextstrain/nextclade_data.

> [!IMPORTANT]
> Only the BDBV dataset is built by this workflow today. `Snakefile_zaire` and the
> `rules/` modules are an unfinished second workflow aimed at a Zaire ebolavirus
> dataset: `rules/preprocess.smk` has no rules yet, so nothing produces its
> `data/{build}/metadata.tsv` input and the build cannot run. Finishing it means
> following the
> [Nextclade dataset creation guide](https://github.com/nextstrain/nextclade_data/blob/@/docs/dataset-creation-guide.md),
> with [mpox](https://github.com/nextstrain/mpox) as a worked example.

## Workflow Usage

The workflow can be run from the top level pathogen repo directory:
```
nextstrain build nextclade
```

Alternatively, the workflow can also be run from within the nextclade directory:
```
cd nextclade
nextstrain build .
```

This produces the default outputs of the nextclade workflow:

- nextclade_dataset(s) = datasets/<build_name>/*

## Defaults

The defaults directory contains all of the default configurations for the Nextclade workflow.

[defaults/config.yaml](defaults/config.yaml) contains all of the default configuration parameters
used for the Nextclade workflow. Use Snakemake's `--configfile`/`--config`
options to override these default values.

## Snakefile and rules

The main [Snakefile](Snakefile) builds the BDBV dataset and defines all of its rules
inline. It is the entry point the
[shared pathogen CI](https://github.com/nextstrain/.github/blob/master/.github/workflows/pathogen-repo-ci.yaml)
looks for.

The rules directory contains separate Snakefiles (`*.smk`) as modules, used only by the
unfinished [Snakefile_zaire](Snakefile_zaire) described above.

The `workdir` is hardcoded to be the nextclade directory so all filepaths for
inputs/outputs should be relative to the nextclade directory.

## Inputs

`inputs` in [defaults/config.yaml](defaults/config.yaml) lists the sequence and metadata
files to build from; they are merged with `augur merge` before filtering. Each input's
`id_field` names the metadata column holding its id, and the merged metadata is keyed on
`id` whatever the inputs called it, so inputs that disagree can still be combined.

The default is the open and restricted output of the ingest workflow, so
`nextstrain build ingest` has to have run first. Override `inputs` with `--configfile` to
build from somewhere else.

## Build configs

The build-configs directory contains custom configs and rules that override and/or
extend the default workflow.

- [ci](build-configs/ci/) - build that runs in CI, from the phylogenetic workflow's
  [example data](../phylogenetic/example_data/) instead of the ingest workflow's output
- [test-dataset](build-configs/test-dataset/) - build to test new Nextclade dataset
