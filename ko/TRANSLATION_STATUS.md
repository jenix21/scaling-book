# Korean Translation Status

This directory holds the Korean (`ko`) translation of the book. **The English
files at the repo root remain the source of truth and continue to receive
upstream updates.** Korean files mirror them one-for-one by filename slug.

## Layout

```
scaling-book/
├── roofline.md, tpus.md, …          ← English originals (do not edit when translating)
├── ko/
│   ├── index.md, roofline.md, …     ← Korean mirror, one file per English source
│   └── TRANSLATION_STATUS.md
├── _data/translations.yml           ← per-slug status registry
└── bin/check_translation_freshness.py
```

URLs:

| Language | URL |
|----------|-----|
| English  | `https://jax-ml.github.io/scaling-book/<slug>` |
| Korean   | `https://jax-ml.github.io/scaling-book/ko/<slug>` |

The front page is `/` (EN) and `/ko/` (KO).

## Adding or updating a translation

1. Pick a `missing` or `stale` slug from the table below.
2. Copy the English source (e.g. `roofline.md`) into `ko/` with the same filename.
3. Translate the body. Internal chapter links that point at an as-yet-untranslated
   chapter should use `../<slug>` so they fall back to the English page.
4. Set the following frontmatter fields on the Korean file:
   - `lang: ko`
   - `permalink: /ko/<slug>` (`/ko/` for the front page)
   - `source_file: <slug>.md`
   - `source_commit: <git short SHA of the English file at translation time>`
   - `source_updated: YYYY-MM-DD`
   - `translation_status: complete`
5. Flip the slug's `status` to `complete` in `_data/translations.yml`.
6. Run `python bin/check_translation_freshness.py` — the script reports any
   Korean file whose `source_commit` no longer matches `git log -1 -- <english>`.

## Keeping translations in sync with upstream

When upstream changes an English chapter, the script flags the Korean file as
stale. Flow:

```
git pull upstream main
python bin/check_translation_freshness.py
# -> prints the slugs whose source_commit is now behind
# Re-read the English diff, update the Korean file, bump source_commit + source_updated.
```

There is no automated re-translation step — staleness is surfaced, fixing it
is a human task.

## Distill TOC anchor caveat

`_layouts/distill.liquid` builds sidebar TOC links via Jekyll's `slugify`
filter, which strips non-ASCII. Korean pages must give each `toc:` entry an
explicit `anchor:` field and put `{#that-anchor}` on the corresponding heading
in the body. The layout reads `section.anchor` when present:

```yaml
toc:
  - name: 큰 그림
    anchor: high-level-outline
```

```markdown
## 큰 그림 {#high-level-outline}
```

## Comments (Giscus)

`_config.yml` keys Giscus by `mapping: title`, so Korean and English pages
land on separate discussion threads. This is intentional — each language gets
its own comment stream rather than mixing them on the English thread.

## Status

| Slug | English title | Korean title | Status |
|------|---------------|--------------|--------|
| index | How to Scale Your Model | 모델을 어떻게 스케일링할 것인가 | complete |
| roofline | All About Rooflines | 루프라인의 모든 것 | missing |
| tpus | How to Think About TPUs | TPU를 어떻게 생각할 것인가 | missing |
| sharding | Sharded Matrices and How to Multiply Them | 샤딩된 행렬과 그것을 곱하는 법 | missing |
| transformers | All the Transformer Math You Need to Know | 알아야 할 트랜스포머 수학 전부 | missing |
| training | How to Parallelize a Transformer for Training | 학습을 위해 트랜스포머를 병렬화하는 법 | missing |
| applied-training | Training LLaMA 3 on TPUs | TPU에서 LLaMA 3 학습하기 | missing |
| inference | All About Transformer Inference | 트랜스포머 추론의 모든 것 | missing |
| applied-inference | Serving LLaMA 3 on TPUs | TPU에서 LLaMA 3 서빙하기 | missing |
| profiling | How to Profile TPU Code | TPU 코드 프로파일링 하는 법 | missing |
| jax-stuff | Programming TPUs in JAX | JAX로 TPU 프로그래밍하기 | missing |
| conclusion | Conclusions and Further Reading | 결론과 더 읽을거리 | missing |
| gpus | How to Think About GPUs | GPU를 어떻게 생각할 것인가 | missing |
