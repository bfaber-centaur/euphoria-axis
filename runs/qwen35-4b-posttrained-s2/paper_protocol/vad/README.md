# VAD analysis (plan item 6)

These results are derived from the NRC VAD Lexicon v2.1 (Saif M. Mohammad, National
Research Council Canada), used under its non-commercial research terms. The lexicon is
**not redistributed** here: obtain it from NRC and cite it as its README instructs.

The files in this folder are aggregate statistics (correlations and intervals), not
lexicon entries. To reproduce: place the lexicon at `../NRC-VAD-Lexicon-v2.1/` and run
chunk 10a, which rebuilds `vad_single_token_lexicon.csv` locally (gitignored) and checks
it against `lexicon.sha256` and `token_ids_sha256` in `vad_spec.json`.
