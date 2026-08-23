"""일본 공휴일 규칙.

수집과 data/jp/ 생성은 여기 없다. sources/jp/ 가 그쪽이다
(sources/jp/__init__.py 의 마지막 줄 참조).

발행 범위 상수(RANGE_START·RANGE_END)를 여기서 새로 정하지 않는다.
sources.jp.build_data 에서 가져온다 — 그 상한은 内閣府 CSV 가 담고 있는
마지막 날짜이고, data/jp/ 에 그 구간만 쓰인다. 두 곳에 적으면 CSV 가 한 해
늘어날 때 한쪽만 갱신되어 갈린다.
"""
