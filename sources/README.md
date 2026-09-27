# Local source cache

Repository clones live below `sources/<provider>/<owner>/<repository>/`.
Everything in this directory is ignored by Git except this policy file.

Source clones are disposable local cache:

- Do not place analysis reports here.
- Do not modify a source repository merely to analyze it.
- Do not run or install untrusted repository code by default.
- Re-clone from the canonical URL in `registry/repositories.yaml` when another computer needs the source.
- Delete cached clones only when the user explicitly decides to clean them up.

