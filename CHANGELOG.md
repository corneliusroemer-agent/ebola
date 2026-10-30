# CHANGELOG

We use this CHANGELOG to document breaking changes, new features, bug fixes,
and config value changes that may affect both the usage of the workflows and
the outputs of the workflows. See the [changelog for the ncov
repository](https://github.com/nextstrain/ncov/blob/HEAD/docs/src/reference/change_log.md)
for an example of formatting.

## 2026

* 30 October 2026: nextclade - the BDBV workflow is now the main `nextclade/Snakefile`
  (it was `nextclade/Snakefile_BDBV`), so the shared pathogen CI runs it. The unfinished
  Zaire workflow moved to `nextclade/Snakefile_zaire`. The sequence and metadata inputs
  are now set by `config.inputs` rather than hardcoded to the ingest workflow's output,
  and are combined with `augur merge`. Metadata is now keyed on an `id` column rather
  than `accession`; each input names its own id column via `config.inputs[].id_field`.
  Merging with `augur merge` orders sequences differently than the previous `cat` did,
  which perturbs the inferred tree, so this rebuild changes the BDBV reference tree
  topology slightly even though the input sequences are unchanged.

* 13 October 2026: phylogenetic - support use of cached remote inputs.
  See https://github.com/nextstrain/shared/pull/87 for more details.

* 30 September 2026: Both BDBV builds now keep ambiguous nucleotides & Ns rather
  than inferring them. Amino acid sequences are now direct translations of these
  nucleotide sequences and thus we report more X AAs.

* 30 September 2026: AA reconstruction can now be performed with `augur translate`
  by (i) removing the 'genes' entry from the ancestral config block and (ii) setting
  setting an `config.translate.{build}.reference` GenBank file.

* 30 September 2026: `config.ancestral.{build}.extra_args` is now available to pass
  through parameters to `augur ancestral`, such as `"--keep-ambiguous"`

* 03 September 2026: The config param `strain_id_field` has been replaced by
  input-specific `id_field` params. Restore previous default behavior by setting
  `id_field: accession` on each of your inputs. This change requires a minimum
  Augur version of 34.0.0.
