# Ubuntu 26.04 러너 이행이 이 레포에 미치는 영향 — 조사 보고

- 작성: 2026-09-28. 조사만 했고 레포 변경·dispatch·브랜치 생성은 없다.
- 기준 커밋: `origin/main` = `9f65878` (로컬 main `ed76912` 보다 발행 커밋 1 개 앞섬.
  차이는 `logs/build.jsonl`·`status.json` 뿐이라 워크플로·설정은 같다.)
- 대상 원문 고정:
  - Playwright 태그 `v1.62.0` = `e3950d9c140d007bd52853b45813c6274b24e36f`
  - actions/runner-images `main` = `7ef9dd0112f1827264dbca2dff8b13eb9f1a5534`
  - astral-sh/uv 태그 `0.12.19` (run 로그의 setup-uv 가 받은 버전)

---

## ⚠ 선행 실측과 전제의 차이 (먼저 읽을 것)

**전제 4 가 열려 있던 항목인데, 답이 "러너의 시스템 파이썬"이다.** 그래서 [D] 가
"영향 없음" 한 줄로 끝나지 않는다. 이 발견이 브라우저 건과 별개인 두 번째 영향
경로다.

전제 1~3 은 실물과 같다.

## 0. 선행 실측

| # | 항목 | 실물 | 전제와 |
|---|---|---|---|
| 1 | runs-on | `ci.yml:48`·`publish.yml:52` 모두 `ubuntu-latest` | 같음 |
| 2 | 브라우저 캐시 키 | 식 `playwright-${{ runner.os }}-${{ runner.arch }}-${{ steps.browser.outputs.version }}` (`ci.yml:101`, `publish.yml:117`). 실제 값 `playwright-Linux-X64-1.62.0`. OS 버전 없음 | 같음 |
| 3 | playwright 고정·설치 | `pyproject.toml:24` `"playwright==1.62.0"`. 설치 `uv run playwright install --only-shell chromium` (`ci.yml:105`, `publish.yml:121`) | 같음 |
| 4 | 파이썬 출처 | **러너 시스템 파이썬 `/usr/bin/python3.12` (3.12.3)** | 전제는 열린 질문. 답은 시스템 쪽 |

4 의 근거 [실측]:
- `.python-version` = `3.12`. `pyproject.toml:6` `requires-python = ">=3.12"`.
- setup-uv 스텝은 `enable-cache: true` 만 준다. `python-version` 입력은 없다
  (`ci.yml:56-59`, `publish.yml:72-75`).
- publish run 36360030875 (2026-09-27) 로그:
  ```
  Using CPython 3.12.3 interpreter at: /usr/bin/python3.12
  Creating virtual environment at: .venv
  Cache hit for: setup-uv-2-x86_64-unknown-linux-gnu-ubuntu-24.04-3.12.3-pruned-3c47e66b…
  ```
  최근 ci 5 건과 publish 5 건 모두 같은 줄이 나온다(아래 [F]).
- 환경에는 `UV_PYTHON_INSTALL_DIR: /home/runner/work/_temp/uv-python-dir` 가 잡혀 있다.
  하지만 관리형 파이썬은 쓰이지 않았다. uv 기본값은 관리형을 선호하되, 이미
  깔린 시스템 파이썬이 있으면 그것을 다운로드보다 먼저 쓴다(아래 [D]).

---

## [A] Playwright 1.62.0 의 Ubuntu 26.04 취급

### A1. 플랫폼 판정 — [실측]

`packages/utils/hostPlatform.ts` L84-L99 (v1.62.0):
https://github.com/microsoft/playwright/blob/e3950d9c140d007bd52853b45813c6274b24e36f/packages/utils/hostPlatform.ts#L84-L99

```ts
      if (major < 26)
        return { hostPlatform: ('ubuntu24.04' + archSuffix) as HostPlatform, isOfficiallySupportedPlatform: isUbuntu && version === '24.04' };
      if (major < 28)
        return { hostPlatform: ('ubuntu26.04' + archSuffix) as HostPlatform, isOfficiallySupportedPlatform: isUbuntu && version === '26.04' };
```

- 26.04 러너(`/etc/os-release` 의 ID=ubuntu, VERSION_ID=26.04) → **`ubuntu26.04-x64`**,
  `isOfficiallySupportedPlatform = true`.
- 알려지지 않은 버전으로 떨어지지 않는다. 폴백 경로는 다른 경우에만 탄다.
  - 28 이상: `'ubuntu' + version`, 비공식(L98).
  - 판정 불가 리눅스: `ubuntu24.04`, 비공식(L122).
- 경고는 비공식일 때만 난다. `registry/index.ts` L1271-L1272 의
  `BEWARE: your OS is not officially supported…` 다. 26.04 에서는 나지 않는다.
- 파이썬 패키지가 실제로 싣는 드라이버도 같다. 로컬 `.venv` 의
  `playwright/driver/package/package.json` 은 `"version": "1.62.0"` 이다. 번들
  `lib/coreBundle.js` 에도 `"ubuntu26.04" + archSuffix` 판정과
  `"ubuntu26.04-x64": cftUrl("linux64/chrome-headless-shell-linux64.zip")` 가 있다
  (`grep` 로 확인).

### A2. 받는 headless-shell 빌드 — [실측] **24.04 와 동일**

`registry/index.ts` L181-L187:
https://github.com/microsoft/playwright/blob/e3950d9c140d007bd52853b45813c6274b24e36f/packages/playwright-core/src/server/registry/index.ts#L181-L187

```ts
  'chromium-headless-shell': {
    ...
    'ubuntu24.04-x64': cftUrl('linux64/chrome-headless-shell-linux64.zip'),
    'ubuntu26.04-x64': cftUrl('linux64/chrome-headless-shell-linux64.zip'),
```

- `cftUrl` 은 `builds/cft/${browserVersion}/${suffix}` 다(L133-L143).
  `browserVersion` 은 `browsers.json` 이 정한다(L11-L17):
  `chromium-headless-shell` revision `1234`, browserVersion `151.0.7922.34`.
- 따라서 두 플랫폼 모두
  `https://cdn.playwright.dev/builds/cft/151.0.7922.34/linux64/chrome-headless-shell-linux64.zip`
  **한 파일**을 받는다.
- `browsers.json` 에서 `revisionOverrides` 는 webkit 항목 하나에만 있다(`grep -c` = 1,
  L50). headless-shell 에는 OS 별 리비전 분기가 없다.
- 설치 디렉터리 이름 `chromium_headless_shell-1234` 에도 플랫폼이 들어가지 않는다
  (`readDescriptors` L571-L592, override 가 없으면 접두사는 이름뿐이다).
- 참고로 플랫폼별로 다른 zip 을 받는 것은 webkit·firefox 다. webkit 은
  `webkit-ubuntu-26.04.zip`, firefox 는 26.04 에서도 `firefox-ubuntu-24.04.zip` 이다.
  이 레포는 둘 다 쓰지 않는다.

### A3. 26.04 네이티브 의존 목록 — [실측] **있음, chromium 목록은 24.04 와 동일**

`registry/nativeDeps.ts`. 24.04 는 L472-L494, 26.04 는 L687-L709 다:
https://github.com/microsoft/playwright/blob/e3950d9c140d007bd52853b45813c6274b24e36f/packages/playwright-core/src/server/registry/nativeDeps.ts#L687-L709

두 `chromium:` 배열을 잘라 `diff` 했다. 출력은 비었다(차이 0). 21 개 패키지는 다음과 같다.

`libasound2t64 libatk-bridge2.0-0t64 libatk1.0-0t64 libatspi2.0-0t64 libcairo2 libcups2t64
libdbus-1-3 libdrm2 libgbm1 libglib2.0-0t64 libnspr4 libnss3 libpango-1.0-0 libx11-6 libxcb1
libxcomposite1 libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2`

`lib2package` 맵은 다르다. 다만 차이는 chromium 이 쓰지 않는 soname 에만 있다.

```
< libicu*.so.74 → libicu74        > libicu*.so.78 → libicu78
< libvpx.so.9   → libvpx9         > libvpx.so.12  → libvpx12
< libxml2.so.2  → libxml2         > libxml2.so.16 → libxml2-16
< libx264.so    → libx264-164     > libx264.so    → libx264-165
```

### A4. 공식 서술 — [실측] (복사 인용)

- `docs/src/intro-python.md` L141, 「System requirements」 절:
  > "Debian 12 / 13, Ubuntu 22.04 / 24.04 / 26.04 (x86-64 or arm64)."

  https://github.com/microsoft/playwright/blob/e3950d9c140d007bd52853b45813c6274b24e36f/docs/src/intro-python.md?plain=1#L141
- `docs/src/release-notes-python.md` L53, 「Version 1.61」 절:
  > "Playwright now supports Ubuntu 26.04."

  https://github.com/microsoft/playwright/blob/e3950d9c140d007bd52853b45813c6274b24e36f/docs/src/release-notes-python.md?plain=1#L53

  26.04 지원은 1.61 부터이고, 1.62.0 은 그 안에 든다.

---

## [B] 캐시 교차 복원

### 판정 — [실측·소스 판독] **복원된 바이너리가 그대로 쓰인다. 다만 불일치가 없으므로 "모른 채 넘어가는" 경우도 아니다.**

1. **불일치 자체가 없다.** [A]2 에 따라 26.04 에서 받을 zip 은 24.04 에서 받은 zip 과
   같은 URL 의 같은 파일이다. 설치 디렉터리 경로(`…/ms-playwright/chromium_headless_shell-1234`)
   도 같다. 캐시 키에 OS 버전이 없다는 사실이 여기서는 오류를 만들지 않는다.
2. **설치 스텝은 다시 받지 않는다.**
   - `browserFetcher.ts` L35-L43 은 `INSTALLATION_COMPLETE` 마커가 있으면
     `// Already downloaded.` 후 return 한다.
     https://github.com/microsoft/playwright/blob/e3950d9c140d007bd52853b45813c6274b24e36f/packages/playwright-core/src/server/registry/browserFetcher.ts#L35-L43
   - 마커는 브라우저 디렉터리 안에 있다(`index.ts` L1491-L1493). 그래서 캐시에 같이
     실려 복원된다.
   - 설치 코드에 플랫폼·빌드를 대조하는 로직은 없다. 설령 불일치가 있었어도 감지하지
     못했을 것이다. 지금은 그 약점이 드러나지 않을 뿐이다.
3. **대신 의존 검사는 설치·launch 양쪽에서 돈다. 조건이 붙는다.**
   - `installActions.ts` L137-L141: 설치 뒤 `validateHostRequirementsForExecutablesIfNeeded`
     를 부른다. 실패는 `Playwright Host validation warning` 으로 **출력만 하고 스텝을
     실패시키지 않는다**.
     https://github.com/microsoft/playwright/blob/e3950d9c140d007bd52853b45813c6274b24e36f/packages/playwright-core/src/cli/installActions.ts#L137-L141
   - `browserType.ts` L193: launch 직전에 같은 검사를 한다. 여기서는 예외가 나서
     테스트가 빨개진다.
   - `index.ts` L1214-L1234: 검사는 브라우저 디렉터리의 `DEPENDENCIES_VALIDATED` 마커가
     **30 일 이내면 건너뛴다**.

### 부수 관찰 — [추론]

- 이 캐시는 2026-09-16T01:23:42Z 에 만들어졌다([실측] `gh cache list`:
  `playwright-Linux-X64-1.62.0`, 108 MB, main). 만든 run 은 테스트에서 launch 를
  거친 뒤 post 단계에서 저장했다. 그러니 `DEPENDENCIES_VALIDATED` 마커가 캐시에 들어
  있을 공산이 크다. actions/cache 의 tar 복원이 mtime 을 보존한다면, 마커는
  **2026-10-16 께부터 30 일을 넘긴다.**
- 그 뒤로는 매 run 마다 ldd 기반 검사가 다시 돈다. 적중 시 캐시는 재저장되지 않으므로
  마커도 계속 낡은 상태로 남는다.
- 결과는 둘 중 하나다.
  - 26.04 에서 라이브러리가 빠졌다면: 설치 스텝에 경고가 **먼저 찍히고**, launch 에서
    빠진 라이브러리 목록과 함께 실패한다.
  - 빠진 것이 없다면: 경고 없이 통과한다.
- 이행 시작일(10-19)이 이 30 일 경계 뒤라서, 진단 메시지가 친절한 쪽으로 나올
  공산이 크다. 캐시 안의 마커 존재와 mtime 은 캐시를 받아 보지 않는 한 확인할 수
  없다(미확인).

---

## [C] 26.04 러너 이미지의 라이브러리

### C1. 이미지 문서 — [실측]

`images/ubuntu/Ubuntu2604-Readme.md` @ `7ef9dd0`:
https://github.com/actions/runner-images/blob/7ef9dd0112f1827264dbca2dff8b13eb9f1a5534/images/ubuntu/Ubuntu2604-Readme.md

- OS 26.04.1 LTS, Image Version `20260920.143.1`.
- `### Installed apt packages` 표(71 행)는 이미지 스크립트가 **명시 설치한** 패키지만
  적는다. 전이 의존은 적지 않는다.

### C2. 의존 목록과의 대조 — [실측]

- [A]3 의 21 개를 두 이미지의 apt 표에서 이름으로 찾았다.
  - 26.04: **0 건**
  - 24.04: **0 건** (`Ubuntu2404-Readme.md`, 75 행)
- 24.04 에서도 0 건인데 launch 는 성립했다. 그러니 이 표로는 충족 여부를 판정할 수
  없다. 문서 대조는 **판정 불가**다.
- 두 apt 표의 차이:
  - 26.04 에 추가: `7zip`, `7zip-rar`, `bind9-dnsutils`
  - 26.04 에서 빠짐: `dnsutils`, `haveged`, `mediainfo`, `mercurial`, `p7zip-full`,
    `p7zip-rar`, `sphinxsearch`

  모두 브라우저와 무관하다.

### C3. 러너의 브라우저 — [실측] + [추론]

- [실측] 26.04 Readme 의 「Browsers and Drivers」 절(L133-L141): Google Chrome
  153.0.8010.52, Chromium 153.0.8010.0, Microsoft Edge 153.0.4234.48, Mozilla Firefox 156.0.
  24.04 도 같은 구성이다(L148-L154).
- [실측] 26.04 빌드 템플릿 `images/ubuntu/templates/build.ubuntu-26_04.pkr.hcl` L122 가
  `install-google-chrome.sh` 를 부른다. 그 스크립트 L38-L40 은
  `google-chrome-stable_current_amd64.deb` 를 받아 `apt-get install "$chrome_deb_path" -f`
  로 깐다. 즉 **deb 의 Depends 가 apt 로 해소된다.**
- [실측] Google 저장소 인덱스
  `https://dl.google.com/linux/chrome/deb/dists/stable/main/binary-amd64/Packages` 의
  `google-chrome-stable` 154.0.8037.57-1 `Depends:` 에 다음이 모두 있다(t64 접미사 제외
  이름 기준).
  `libasound2, libatk-bridge2.0-0, libatk1.0-0, libatspi2.0-0, libcairo2, libcups2,
  libdbus-1-3, libgbm1, libglib2.0-0, libnspr4, libnss3, libpango-1.0-0, libx11-6,
  libxcb1, libxcomposite1, libxdamage1, libxext6, libxfixes3, libxkbcommon0, libxrandr2`
  - 21 개 중 20 개가 직접 있다.
  - `libdrm2` 는 직접 목록에 없다. 다만 `libgbm1` 의 의존으로 들어온다 — 이 부분은
    [추론].
- [추론] Chrome deb 가 이미지 빌드 시점에 설치에 성공했다면, Playwright 가 요구하는
  21 개도 26.04 이미지에 있다고 볼 근거가 강하다. 24.04 에서 launch 가 성립한 것과
  같은 메커니즘이다. 이미지 빌드 시점의 deb 버전은 지금 인덱스의 154 가 아니라 153
  이다. Depends 가 버전 사이에 크게 바뀌지 않는다는 것도 추론이다.

### C4. 로컬 컨테이너 대조 — **수행 못 함**

- 이 머신에 `docker`·`podman`·`colima` 가 없다(`which` 결과 없음). `ubuntu:26.04` ldd
  대조는 하지 않았다.
- 했더라도 한계는 남는다. 컨테이너는 Chrome deb 를 깔지 않은 최소 이미지라, 빠진
  라이브러리가 러너보다 훨씬 많이 나온다. 러너 판정의 근거로는 약하다.

---

## [D] 파이썬 — 시스템 파이썬 경로이므로 조사

### D1. 26.04 기본 파이썬 — [실측]

- `Ubuntu2604-Readme.md` L27: `Python 3.14.4`. 24.04 는 `Python 3.12.3`
  (`Ubuntu2404-Readme.md` L28) 이고, 지금 run 이 쓰는 `/usr/bin/python3.12` 가 그것이다.
- 26.04 toolcache(L187-L193)에는 3.10.21 / 3.11.16 / **3.12.14** / 3.13.15 / 3.14.7 이
  있다.

### D2. 호환 — [실측] + [추론]

- 3.14 는 `requires-python = ">=3.12"` 를 만족한다. `uv.lock` 헤더도
  `requires-python = ">=3.12"` 다.
- `uv.lock` 24 개 패키지의 wheel 태그를 훑었다. 네이티브 wheel 은 `greenlet 3.5.6`
  (cp312–cp315), `pyyaml 6.0.3` (cp312–cp314) 둘뿐이고, 둘 다 cp314 wheel 이 있다.
  나머지는 py3 순수 wheel 또는 플랫폼 wheel(`playwright`, `ruff` — 파이썬 버전 무관)이다.
  **3.14 로 가도 lock 은 깨지지 않는다.** [실측]
- **그러나 uv 는 3.14 를 쓰지 않는다.** `.python-version` 이 `3.12` 를 요구하기 때문이다.
  - [추론] 26.04 에는 시스템 `python3.12` 가 없다. toolcache 는 기본 PATH 에 없고,
    uv 는 toolcache 를 탐색하지 않는다. 그러면 uv 는 **관리형 CPython 3.12 를 받아
    쓴다.** 근거는 uv 0.12.19 문서
    `docs/concepts/python-versions.md` 두 곳이다.
    - L50:
      > "uv will automatically download Python versions if they cannot be found on the system"
    - L407-L408:
      > "system Python installations are still preferred over downloading a managed Python"

      (L407-L408 은 줄바꿈을 이어 붙였다.)

    https://github.com/astral-sh/uv/blob/0.12.19/docs/concepts/python-versions.md?plain=1#L50
  - 결과 1: **매 run 네트워크 의존이 하나 는다** — 관리형 파이썬 배포처.
    `setup-uv` 에 `cache-python` 을 켜지 않았으므로 매번 받는다.
  - 결과 2: 파이썬 패치 버전이 3.12.3 → 3.12.x(관리형 최신)로 바뀐다.
  - 결과 3: setup-uv 캐시 키(`…-ubuntu-24.04-3.12.3-…`)가 바뀌어 첫 run 은 미스가 난다.
    이것은 무해하다.
- 이 경로는 **발행 차단 가능성이 있는 두 번째 외부 의존**이다. 브라우저 캐시와 달리
  캐시로 막혀 있지 않다. `docs/browser-smoke.md` §「대가와 그 처리」가 경계한
  "네트워크 의존이 는다" 와 같은 성격이다.

---

## [E] 레이블 고정 시의 수명

### E1. `ubuntu-24.04` 제공 기간 — [실측] + [추론]

[실측] runner-images `README.md` @ `7ef9dd0`:
- L90-L91:
  > "we only support the latest 2 versions of an OS"

  (줄바꿈을 이어 붙였다.)
- L120:
  > "We begin the deprecation process of the oldest image label once the newest"

  (15 단어에서 자름.)
- L97:
  > "To avoid unwanted migration, users can specify a specific OS version in the yaml file"

https://github.com/actions/runner-images/blob/7ef9dd0112f1827264dbca2dff8b13eb9f1a5534/README.md?plain=1#L90-L120

[실측] 22.04 의 전례:

| 사건 | 날짜 | 근거 |
|---|---|---|
| 24.04 GA 공지 | 2024-05-14 | #9848 |
| `ubuntu-latest` → 24.04 이행 | 2024-12-05 ~ 2025-01-17 목표 (이슈 닫힘 2025-01-09) | #10636 |
| 26.04 GA 공지 | 2026-09-17 | #14747 |
| 22.04 deprecation 개시 | "Deprecation: September 17th, 2026" | #14254 |
| 22.04 retirement | "Retirement: April 17th, 2027" | #14254 |

22.04 는 `-latest` 를 잃은 뒤(2025-01) 약 27 개월 뒤(2027-04)에 은퇴한다. 은퇴 앞에는
brownout(해당 레이블 job 의도적 실패)이 4 회 예정돼 있다(#14254 본문).

[추론] 정책대로라면 24.04 의 deprecation 은 **다음 LTS(28.04) 러너 이미지 GA 때**
시작된다.
- 전례: 22.04 deprecation 이 26.04 GA 와 같은 날 시작됐다.
- 26.04 는 Canonical 출시(2026-04)에서 러너 GA(2026-09)까지 약 5 개월 걸렸다.
- 이 간격을 28.04 에 적용하면 deprecation 개시는 2028 년 가을께, 은퇴는 그 약 7 개월
  뒤인 2029 년 봄께다.
- 이 날짜들은 공지된 것이 아니다.

### E2. 공지 원문의 완화책 — [실측] (#14748 「Mitigation ways」, 복사 인용)

https://github.com/actions/runner-images/issues/14748

> "File an issue in this repository."
>
> "Switch back to Ubuntu 24.04 by specifying the `ubuntu-24.04` label."
>
> "Use `ubuntu-26.04` to test against the new image explicitly."

같은 공지의 일정은 다음과 같다.

> "rolled out over a period of several weeks beginning October 19, 2026."
>
> "We plan to complete the migration by November 19, 2026."

---

## [F] 이행 중 관측 방법

### F1. 사용 이미지를 알려 주는 줄 — [실측]

publish run 36360030875, 「Set up job」 스텝 머리(`gh run view 36360030875 --log`):

```
##[group]Operating System
Ubuntu
24.04.5
LTS
##[group]Runner Image
Image: ubuntu-24.04
Version: 20260920.314.1
Included Software: https://github.com/actions/runner-images/blob/ubuntu24/20260920.314/images/ubuntu/Ubuntu2404-Readme.md
Image Release: https://github.com/actions/runner-images/releases/tag/ubuntu24%2F20260920.314
```

- `Runner Image Provisioner` 그룹에도 `Version: 20260828.587` 이 있다. 이것은 Hosted
  Compute Agent 버전이지 이미지 버전이 아니다. 헷갈리기 쉬워 적어 둔다.
- 보조 신호: 의존성 스텝의 `Using CPython … interpreter at: /usr/bin/python3.12` 줄이다.
  26.04 에서는 관리형 경로(`…/uv-python-dir/…`)로 바뀔 것이다([추론]). setup-uv 캐시
  키의 `ubuntu-24.04` 토막도 바뀐다.
- 같은 run 의 annotation(check-run API)은 notice 1 건이다.
  > "The ubuntu-latest label will migrate to Ubuntu 26 beginning October 19, 2026."

### F2. 26.04 배정 여부 — [실측] **없음 (10/10 이 24.04)**

| 워크플로 | run id | 생성 (UTC) | 이벤트 | Image | Image Version | 파이썬 |
|---|---|---|---|---|---|---|
| publish | 36360030875 | 09-27 23:50 | schedule | ubuntu-24.04 | 20260920.314.1 | /usr/bin/python3.12 (3.12.3) |
| publish | 36075024932 | 09-24 23:54 | schedule | ubuntu-24.04 | 20260920.314.1 | 〃 |
| publish | 35798314868 | 09-22 23:37 | schedule | ubuntu-24.04 | 20260920.314.1 | 〃 |
| publish | 35544229946 | 09-20 23:18 | schedule | ubuntu-24.04 | 20260907.300.1 | 〃 |
| publish | 35287439874 | 09-17 23:34 | schedule | ubuntu-24.04 | 20260907.300.1 | 〃 |
| ci | 35216826060 | 09-17 11:39 | push main | ubuntu-24.04 | 20260907.300.1 | 〃 |
| ci | 35210862203 | 09-17 10:30 | pull_request | ubuntu-24.04 | 20260907.300.1 | 〃 |
| ci | 35206660529 | 09-17 09:43 | push main | ubuntu-24.04 | 20260907.300.1 | 〃 |
| ci | 35203751555 | 09-17 09:11 | pull_request | ubuntu-24.04 | 20260907.300.1 | 〃 |
| ci | 35199662770 | 09-17 08:26 | pull_request | ubuntu-24.04 | 20260907.300.1 | 〃 |

10 건 모두 브라우저 캐시는 `Cache restored from key: playwright-Linux-X64-1.62.0` 로
적중했다. 이행 시작 전이므로 예상대로다.

---

## 선택지 표

| 축 | A: `ubuntu-24.04` 고정 | B: `ubuntu-latest` 유지(무조치) | C: `ubuntu-26.04` 명시 전환 |
|---|---|---|---|
| 발행 차단 위험 | 이번 이행과 무관해진다. 이미지 계열이 지금과 같다 | 10-19~11-19 사이 run 이 무작위로 26.04 에 배정된다. 라이브러리 충족은 26.04 실측이 없다([C] 는 판정 불가, 정황만 있음). 파이썬이 관리형 다운로드로 바뀌어 외부 의존이 하나 는다. 첫 26.04 배정이 schedule 발행 run 일 수 있다 | 26.04 에 결정적으로 고정된다. 라이브러리 위험과 파이썬 다운로드 의존은 B 와 같다. 전환은 PR 로 들어가므로 PR 의 ci run 이 발행보다 먼저 26.04 를 겪는다 |
| 캐시 키 변경 필요 여부 | 불필요 | 기능상 불필요([B]: 받는 zip·경로 동일). OS 버전이 키에 없어 두 OS 가 한 캐시를 공유한다 | 기능상 불필요([B]). 24.04 에서 만든 캐시가 그대로 복원된다 |
| 고쳐야 할 문서·주석 위치 | `ci.yml:48`, `publish.yml:52`(runs-on). `docs/browser-smoke.md:151`(「`ubuntu-latest` 에서 uv 를 깔고」) | 필수 수정 없음. 다만 `ci.yml:80-82`·`publish.yml:96-98` 의 「이 스텝을 들인 PR 의 CI 에서 확인했다」와 `docs/browser-smoke.md:173-175` 는 24.04 에서만 참이다. `docs/holiday_18.md:153` 의 「러너 이미지(ubuntu-24.04)」도 같다 | `ci.yml:48`, `publish.yml:52`. `docs/browser-smoke.md:151`. 두 워크플로 주석 L80-82/L96-98 의 확인 근거(어느 OS 에서 확인했는지) |
| 언젠가 다시 해야 하는 일 | 24.04 deprecation 공지 때(정책상 다음 LTS 러너 GA 시점) 이행을 해야 한다. 그때 brownout 이 먼저 온다. 이번 조사 결과를 다시 써야 한다 | 다음 LTS 때 같은 무작위 이행이 또 온다(이번과 같은 조사) | 26.04 deprecation 때 레이블을 다시 바꾼다. 다음 LTS 의 `-latest` 이행에는 영향받지 않는다 |

---

## [추론] 권고와 남은 미확인

### 권고 (CC 의견, 결정은 사람)

1. **두 위험 경로 모두 정황상 통과 쪽이다.**
   - 브라우저: 같은 빌드이고, Playwright 가 26.04 를 공식 지원하며, 러너에 Chrome deb 가
     있어 의존이 해소된다.
   - 파이썬: lock 과 호환되고, uv 가 3.12 를 받아 온다.
   다만 어느 쪽도 26.04 에서 실측된 적이 없다.
2. 그래서 **B(무조치)는 권하지 않는다.** 실패가 나면 첫 발견자가 schedule 발행 run 일
   수 있다. 이행 중에는 run 마다 OS 가 달라 빨강·초록이 섞인다. 이것은
   `docs/browser-smoke.md` 가 가장 나쁜 결과로 꼽은 「빨간 신호를 믿지 못하게 되는 것」
   과 같은 모양이다.
3. 순서 제안:
   - 먼저 아래 「실 러너 실행」 제안으로 26.04 스모크를 실측한다.
   - 초록이면 **C** 를 PR 로 들인다(PR ci 가 한 번 더 확인한다).
   - 빨강이거나 실측을 10-19 전에 못 하면 **A** 로 고정해 이행에서 빠진다.
   - 기한 여유: 오늘(09-28)부터 이행 개시까지 3 주다.
4. C 를 택하면 [D] 의 관리형 파이썬 다운로드를 받아들일지도 함께 정해야 한다.
   - 대안 1: setup-uv 의 `python-version` 입력으로 toolcache 3.12.14 를 가리킨다.
   - 대안 2: `cache-python` 을 켠다.
   - 둘 다 이 조사에서 동작을 확인하지 않았다(미확인).

### 결정에 필요한 남은 미확인

- 26.04 러너에서 headless-shell launch 가 실제로 성립하는가(라이브러리 충족). 문서로는
  판정 불가였다.
- 26.04 러너에서 uv 가 실제로 무엇을 고르는가. 관리형 다운로드인지, 혹시 PATH 상의
  다른 3.12 인지.
- 캐시 안 `DEPENDENCIES_VALIDATED` 마커의 존재와 mtime(설치 스텝 경고가 나올지 여부).
- `ubuntu:26.04` 컨테이너 ldd 대조(도구 부재로 미수행).

---

## 사람 승인 뒤에만 — 실 러너 실행 제안 (이번에 실행하지 않음)

- **어느 레포:** 사용자 개인 계정의 별도 스크래치 레포. **public 권장** — 표준 러너
  분이 무료다. `lunalism/holidays` 에는 브랜치를 올리지 않는다. 캐시는 레포 스코프라
  본 레포의 캐시는 건드리지 않는다.
- **필요한 최소 파일:**
  - 스모크 테스트가 `landing`, `rules.status` 등 레포 모듈을 import 하고 실제 locale
    YAML 을 읽는다(`tests/test_landing_smoke.py` L69, L280-L291). 사실상 파이썬 트리
    전체가 필요하다.
  - 가장 적은 손은 `main` 스냅숏을 히스토리 없이 복사하는 것이다: `git archive` →
    새 레포 첫 커밋. 여기에 워크플로 한 파일을 둔다.
  - 워크플로는 `workflow_dispatch` 만 두고, job 둘을 `needs:` 로 잇는다.
    1. `seed` (`runs-on: ubuntu-24.04`): 지금 ci.yml 의 uv·브라우저 스텝을 그대로 쓰고,
       `pytest tests/test_landing_smoke.py` 를 돌린 뒤 캐시를 저장한다.
    2. `probe` (`runs-on: ubuntu-26.04`): 같은 스텝을 돌려 seed 의 캐시를 복원한다.
       설치 스텝 출력, `uv sync` 의 `Using CPython` 줄, 스모크 결과를 본다.
  - (선택) `probe-cold`: 26.04 에서 캐시 없이 설치한다. ldd 결과
    (`ldd …/chrome-headless-shell | grep "not found"`)를 대조군으로 남긴다.
  - 발행 스텝·KASI 키는 넣지 않는다. 시크릿이 필요 없다.
- **예상 비용:**
  - [추론] 지금 publish job 은 약 75 초다. 스모크만 돌리면 job 당 1~2 분, 세 job 합계
    5 분 안쪽이다.
  - public 레포면 0 원이다. private 이어도 Free 플랜 월 포함 분(2,000 분) 안이다.
  - 사람 시간: 레포 생성·dispatch 1 회, 로그 확인 10 분.
- **확인할 신호:**
  1. launch 성공: 스모크 3 테스트 통과, `Host validation` 경고 없음.
  2. 세 면 통과: `test_the_page_runs_without_errors_and_settles` 의 lang 파라미터 전부
     PASSED.
  3. 캐시 교차 복원 재현: probe 에서
     `Cache restored from key: playwright-Linux-X64-1.62.0` 가 나오고, 설치 스텝이
     `Downloading …` 없이 끝나며, 러너 머리에 `Image: ubuntu-26.04` 가 찍힌다.
  4. 부수 신호: probe 의 `Using CPython` 경로. [D] 의 관리형 다운로드 추론을 여기서
     확인한다.
