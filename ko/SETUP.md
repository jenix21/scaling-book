# Korean Translation Setup

이 문서는 이 리포에 한글(`ko`) 번역 트랙을 어떻게 얹었는지를 기록합니다.
운영 워크플로우(번역 추가 절차, stale 처리)는 [`TRANSLATION_STATUS.md`](TRANSLATION_STATUS.md)
에 있고, 이 문서는 "왜 이렇게 만들었는가" + "어떤 파일을 만지고 무엇을 검증했는가"를
설명합니다.

## 설계 결정

| 결정 | 선택 | 이유 |
|------|------|------|
| URL 구조 | `/ko/<slug>` 서브디렉토리 | SEO/공유 친화, 검색엔진의 언어 분리 인식, 폴더 자체가 한글 콘텐츠 경계 |
| 영문 원본 위치 | 루트 그대로 (`roofline.md`, `tpus.md`, …) | upstream 머지 무충돌. 한글 작업이 원본을 한 글자도 건드리지 않음 |
| 짝 페이지 매칭 | 슬러그 기반 (파일명) | 영문 frontmatter에 새 필드를 박지 않아도 됨 → 영문 무손상 유지 |
| 원본 변경 추적 | 각 한글 파일 frontmatter의 `source_commit` + freshness 스크립트 | `git log -1 -- <english>`와 비교해 stale 감지. 자동 재번역 없음(인간 작업) |
| 미번역 챕터 처리 | 영문 fallback (`../<slug>`) + 스위처에서 disabled | 404 방지. 번역 진척에 따라 점진 전환 |
| Distill TOC anchor | `section.anchor` 옵션 추가 | Jekyll `slugify`가 한글을 빈 anchor로 만드는 문제 우회 |
| Giscus 댓글 | `mapping: title` 그대로 → 언어별 분리 스레드 | 한·영 독자가 같은 스레드에 섞이지 않도록 |

## 신규 파일

| 파일 | 역할 |
|------|------|
| `ko/index.md` | 0장(소개)의 완역. 다른 챕터의 frontmatter 패턴 레퍼런스. |
| `ko/dropdown.md` | navbar 한글 챕터 dropdown (`/ko/sections`). `lang: ko`라 영문 페이지에서는 숨겨짐. |
| `ko/TRANSLATION_STATUS.md` | 운영 가이드: 번역 추가 절차, stale 처리, 챕터별 상태 표. |
| `ko/SETUP.md` | 이 문서. 아키텍처 결정 기록. |
| `_data/translations.yml` | 슬러그별 `status` 단일 소스. 스위처와 freshness 스크립트가 함께 참조. |
| `_includes/language_switcher.liquid` | navbar의 EN/한국어 토글. `page.path`에서 슬러그 추출 → 짝 페이지 URL 생성. 번역 미완성이면 disabled. |
| `bin/check_translation_freshness.py` | 각 `ko/*.md`의 `source_commit`을 `git log -1 -- <english>`와 비교해 stale 보고. exit 1이면 갱신 필요. |

## 기존 파일 수정 (영문 콘텐츠 무손상)

| 파일 | 변경 | 영문 페이지 영향 |
|------|------|------------------|
| `_config.yml` | `languages:` 키 추가, `defaults`에 `path: ""→lang: en`, `path: "ko"→lang: ko` 추가 | 영문 페이지에 `page.lang = 'en'`이 자동 주입됨 — 기능 영향 없음 |
| `_includes/header.liquid` | nav 루프에 `p_lang == cur_lang` 필터, search 토글 뒤에 `{% include language_switcher.liquid %}` | 영문 페이지에서는 영문 dropdown만 표시 + 우측에 "한국어" 토글 추가 |
| `_layouts/distill.liquid` | `section.anchor` / `subsection.anchor` 옵션 인식 (없으면 기존 `slugify` 폴백) | 영문 페이지는 anchor 필드 없으므로 기존 동작 그대로 |

## 한글 페이지 frontmatter 규약

```yaml
---
layout: distill
title: "…"
lang: ko
permalink: /ko/<slug>            # 프런트 페이지는 /ko/
description: "…"

source_file: <slug>.md           # 짝이 되는 영문 원본
source_commit: <git short SHA>   # 번역 시점 영문 원본의 마지막 커밋
source_updated: YYYY-MM-DD
translation_status: complete     # complete | in_progress | stale | missing

# 한글 헤딩은 slugify에서 빈 anchor가 되므로 명시 필요
toc:
  - name: 큰 그림
    anchor: high-level-outline
---
```

본문 헤딩은 짝을 맞춰 `{#anchor}` 명시:

```markdown
## 큰 그림 {#high-level-outline}
```

내부 챕터 링크:

- 같은 `/ko/` 안의 다른 한글 챕터: `(transformers)` (상대 링크 그대로)
- 아직 미번역인 챕터: `(../transformers)` (영문 fallback)

## 검증

이번 세션에서 수행한 것:

```
$ python bin/check_translation_freshness.py; echo "exit=$?"
1 translation(s) up to date.
exit=0
```

수행하지 못한 것 (로컬 Ruby/bundler 환경 부재):

- `bundle exec jekyll serve`로 실제 빌드 후 `/scaling-book/ko/` 진입 확인
- 영문 페이지 navbar에서 "한국어" 토글이 `/scaling-book/ko/`로 이동하는지 확인
- 한글 페이지 navbar에서 "EN" 토글이 `/scaling-book/`으로 이동하는지 확인
- 한글 페이지 사이드바 TOC anchor("큰 그림" 등) 클릭 시 본문 헤딩으로 점프하는지 확인

로컬 빌드는 README의 절차(`bundle install && bundle exec jekyll serve`)로 띄워
위 네 가지를 직접 확인 부탁드립니다.

## upstream 변경에 대응하는 운영 루틴

```bash
git pull upstream main
python bin/check_translation_freshness.py
# 출력에 stale로 잡힌 슬러그만 골라 영문 diff 확인
# 한글 본문 갱신 후 frontmatter source_commit, source_updated 갱신
# _data/translations.yml에서 해당 슬러그 status는 그대로 complete 유지
```

자동 재번역은 의도적으로 없습니다 — 스크립트는 "어디가 어긋났는지"만 알리고,
실제 의미 보존은 사람이 맡습니다.

## 알려진 제약 / 후속 과제

- `<html lang="…">` 속성이 한글 페이지에서도 `en` 그대로일 수 있음. `_layouts/distill.liquid` 의 `<html>` 태그에 `lang="{{ page.lang | default: site.lang }}"`를 다는 후속 작업 권장.
- giscus의 `lang: en`이 `_config.yml`에 박혀 있어 한글 페이지 댓글 위젯 UI가 영어로 뜸. 한글 페이지에서만 `ko`로 바꾸려면 `_includes/giscus.liquid`를 `page.lang` 기반으로 분기해야 함.
- 사이트맵/RSS/Open Graph 메타는 현재 언어 구분 없음. SEO를 본격적으로 신경 쓰게 되면 `_includes/metadata.liquid`에 `hreflang` alternate 링크 추가가 필요.

## 다음 챕터 번역 추가 절차 요약

`ko/TRANSLATION_STATUS.md`에 상세 절차가 있습니다. 핵심만:

1. `roofline.md` → `ko/roofline.md` 복사 후 본문 한글로
2. frontmatter: `lang: ko`, `permalink: /ko/roofline`, `source_file: roofline.md`, `source_commit: $(git log -1 --format=%h -- roofline.md)`, `source_updated: <today>`, `translation_status: complete`
3. `_data/translations.yml`에서 `roofline.status: complete`
4. `ko/TRANSLATION_STATUS.md` 표 갱신
5. `python bin/check_translation_freshness.py` → exit 0 확인
