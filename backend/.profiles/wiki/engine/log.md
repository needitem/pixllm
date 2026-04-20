# Engine Wiki Log

## [2026-04-16] policy | Remove runnable-program generation contract from wiki workflows
- Removed runnable sample, `.csproj`, and required output-file expectations from workflow guidance.
- Kept host-context hints only where they materially affect explanation quality, with WPF remaining the default context when needed.
- Reduced scenario pages to compact host sketches so the desktop agent stays aligned with explanation-first behavior.

## [2026-04-16] structure | Align engine wiki to LLM Wiki shape with raw-source placeholders
- Declared `D:/Pixoneer_Source/PIX_RAG_Source/backend/.profiles/wiki/raw_source/source` as the canonical immutable raw source root.
- Kept the current answer mode wiki-only so responses come from the `engine` wiki instead of raw sources.
- Added TODO placeholder pages for future ingest and accumulation work.

## [2026-04-16] desktop-ui | Make engine workflows WPF-first by default
- Reframed desktop UI workflow pages so WPF is the default shell for runnable samples and app answers.
- Added explicit WPF delivery or host-context rules to hosted view workflows and host-bound scene/vector workflows.
- Added WPF integration guidance to the remaining host-agnostic workflow pages so every workflow resolves desktop shell questions the same way.
- Aligned the remaining curated pages with the same WPF-first desktop-shell policy.
- Replaced markdown `methods/*.md` pages with `.runtime/methods_index.json` as the structured symbol verification layer.
- Removed desktop-shell policy text from the method verification layer and kept that policy in workflows/coordination only.
- Tightened runtime method extraction so `Method Page Facts` and `Runtime Usage` no longer appear as method symbols in the generated index.
- Kept `NXImageView` hosting factual by preserving the `WindowsFormsHost` requirement while demoting pure WinForms examples to explicit fallbacks.
- Updated coordination pages so wiki-level routing treats WPF as the default desktop answer shape.

## [2026-04-15] structure | Prune noisy workflow pages and add signature-level facts
- Added source-backed `required_facts` blocks to canonical workflow pages.
- Removed redundant sample/index workflow pages that only duplicated routing or sample guidance.
- Removed stale per-workflow wording that referenced the retired question-answer index.
- Kept the wiki centered on canonical workflow, methods, and coordination documents.
