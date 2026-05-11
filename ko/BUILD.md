# 한글 버전 로컬 빌드 가이드 (Windows)

영문 원본 [`README.md`](../README.md)는 macOS 기준이라 Windows 환경에서
한글 트랙을 띄워 확인하는 절차를 별도로 정리해 둡니다. WSL 사용자는
README의 macOS 절차를 거의 그대로 따라가면 됩니다.

## 1. 사전 설치

### Ruby (필수, 3.4.5 이상)

**RubyInstaller for Windows** — <https://rubyinstaller.org/> 에서
`Ruby+Devkit 3.4.x (x64)` 설치본을 받아 설치합니다. 설치 마지막 단계에서
**"MSYS2 development toolchain 설치"** 체크박스를 꼭 켭니다 — Jekyll 일부
gem이 native 확장을 컴파일합니다.

설치 후 새 PowerShell 창에서:

```powershell
ruby -v        # 3.4.5 이상
gem -v
```

### ImageMagick (이미지 리사이징)

<https://imagemagick.org/script/download.php#windows> 에서 Windows 바이너리를
설치합니다. 설치 옵션에서 **"Add application directory to your system path"**
를 체크해야 합니다.

```powershell
magick -version
```

### Python + Jupyter (노트북 임베드용)

```powershell
pip install jupyter
```

> **WSL 사용 시:** `sudo apt install ruby-full ruby-dev imagemagick build-essential`
> + `pip install jupyter`로 끝납니다. 빌드 속도와 안정성은 WSL이 더 낫습니다.

## 2. 의존성 설치 & 서버 기동

리포 루트에서:

```powershell
cd C:\_dev\scaling-book
bundle install                          # Gemfile 기반 의존성, 첫 실행 시 몇 분
bundle exec jekyll serve --livereload   # 빌드 + 로컬 서버
```

`--livereload`를 붙이면 `.md` 저장 시 브라우저가 자동 새로고침됩니다.
첫 빌드는 1-2분, 이후 incremental은 수 초입니다.

## 3. 확인 동선

브라우저에서 `http://127.0.0.1:4000/scaling-book/` 진입 후 다음을 차례로 점검합니다.

| # | 확인 위치 | 기대 동작 |
|---|-----------|-----------|
| 1 | 영문 메인 페이지 navbar 우측 | 다크모드 토글 옆에 **한국어** 라벨이 활성(클릭 가능)으로 표시 |
| 2 | **한국어** 클릭 | `/scaling-book/ko/` 한글 0장으로 이동 |
| 3 | 한글 페이지 navbar dropdown | "Sections"이 아니라 **"섹션"** 으로 표시, 안의 챕터 라벨이 한글 |
| 4 | 한글 페이지 사이드바 TOC | "큰 그림", "각 장으로 가는 길" 클릭 시 본문 헤딩으로 점프 (anchor 매칭 확인) |
| 5 | 한글 페이지 navbar | **EN** 라벨 클릭 시 `/scaling-book/`로 복귀 |

영문의 다른 챕터(예: `/scaling-book/roofline`)에서는 한국어 라벨이
**회색/비활성**으로 보여야 정상입니다. `_data/translations.yml`에서 해당
슬러그의 `status: missing`이기 때문입니다.

## 4. 자주 만나는 트러블

| 증상 | 원인 / 해결 |
|------|-------------|
| `bundle install` 중 native gem 컴파일 실패 | MSYS2 toolchain 누락. `ridk install` 실행 후 옵션 3번(MSYS2 + MINGW dev) 선택 |
| `jekyll-imagemagick` 관련 에러 | `magick -version`이 안 잡히는 상황. PATH 재확인 후 PowerShell 창을 새로 띄우기 |
| 포트 4000 충돌 | `bundle exec jekyll serve --port 4001` |
| 사이드 TOC 클릭해도 점프 안 됨 | 본문 헤딩에 `{#anchor}`가 없거나 `toc:` 항목의 `anchor:` 값과 불일치. `slugify`가 한글을 빈 anchor로 만드는 경로에 빠진 것이니 명시 anchor를 박아야 함 |
| 한글 페이지에서 한국어 토글이 비활성 | `_data/translations.yml`에서 해당 슬러그가 `status: complete`인지 확인 |

## 5. 서버 없이 빠른 검증

```powershell
bundle exec jekyll build                # _site/ 에 정적 출력만 생성
dir _site\ko\index.html                 # 한글 페이지 생성 여부 확인
```

번역이 영문 원본과 동기화되어 있는지:

```powershell
python bin\check_translation_freshness.py
```

`exit 0`이면 모두 최신, `exit 1`이면 stale 슬러그 목록이 출력됩니다.

## 6. 새 챕터 번역 사이클

```powershell
# 1) 영문 원본의 마지막 커밋 SHA 따오기
git log -1 --format=%h -- roofline.md   # 예: 7a064c9

# 2) ko/roofline.md 작성
#    frontmatter:
#      lang: ko
#      permalink: /ko/roofline
#      source_file: roofline.md
#      source_commit: 7a064c9
#      source_updated: 2026-05-11
#      translation_status: complete
#      toc: ... (anchor: 명시)

# 3) _data/translations.yml 에서 roofline.status: complete

# 4) 라이브 미리보기 (이미 떠 있다면 자동 리빌드됨)
bundle exec jekyll serve --livereload

# 5) freshness 검증 후 커밋
python bin\check_translation_freshness.py
git add ko\roofline.md _data\translations.yml ko\TRANSLATION_STATUS.md
git commit -m "Translate chapter: roofline (한글)"
```

## 7. 참고

- 빌드는 GitHub Pages 액션이 자동으로 처리합니다([`.github/workflows/deploy.yml`](../.github/workflows/deploy.yml)). `main` 브랜치에 푸시되면 한글 페이지도 함께 배포됩니다.
- 운영/번역 워크플로우 전반은 [`TRANSLATION_STATUS.md`](TRANSLATION_STATUS.md), 아키텍처 결정 배경은 [`SETUP.md`](SETUP.md) 참고.
