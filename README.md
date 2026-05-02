# Django Sync/Async View 및 WSGI/ASGI 서버 성능 비교 분석

본 프로젝트는 Django 환경에서 동기(Sync) 뷰와 비동기(Async) 뷰의 성능을 다양한 조건 하에서 비교 분석하는 것을 목표로 합니다. 또한, 대표적인 WSGI 서버인 Gunicorn과 ASGI 서버인 Uvicorn 환경에서의 성능 차이를 측정하고, 여러 가지 부하 시나리오(네트워크 I/O, CPU 연산)를 통해 Django 애플리케이션의 성능 최적화 방안을 연구합니다.

## 🚀 프로젝트 목표

- Django의 동기/비동기 처리 방식에 따른 성능 차이 비교
- Gunicorn(WSGI)과 Uvicorn(ASGI) 서버 환경에서의 성능 비교
- 다양한 부하 유형에 따른 성능 특성 분석
    - **네트워크 I/O 지연**: 외부 API 호출, 데이터베이스 조회 등 I/O Bound 작업 시의 응답 속도 비교
    - **CPU 지연**: 복잡한 연산, 데이터 처리 등 CPU Bound 작업 시의 처리량 비교
    - **JSON 파싱**: 대용량 JSON 데이터 직렬화/역직렬화 속도 비교
- TCP 레벨에서의 성능 최적화 방법 연구

## 🛠️ 기술 스택

- **Framework**: Django (3.2)
- **Web Server**:
    - Gunicorn (WSGI)
    - Uvicorn (ASGI)
- **Language**: Python 3.8+

## 📊 성능 측정 시나리오

1.  **Sync View + Gunicorn**: 전통적인 Django 동기 방식
2.  **Async View + Uvicorn**: Django 3.1부터 지원되는 비동기 방식
3.  **Sync-to-Async Wrapper View + Uvicorn**: `sync_to_async` 래퍼를 사용한 하이브리드 방식

각 시나리오별로 아래와 같은 테스트를 진행합니다.

- **I/O Bound 테스트**:
    - `asyncio.sleep` 또는 외부 HTTP 요청을 통해 인위적인 I/O 지연을 발생시키고 응답 시간(latency)과 초당 요청 수(RPS)를 측정합니다.
- **CPU Bound 테스트**:
    - 복잡한 수학적 계산이나 데이터 정렬 등 CPU를 많이 사용하는 작업을 수행하고 처리 시간을 측정합니다.
- **JSON 처리 테스트**:
    - 대규모 JSON 데이터를 생성하고, 이를 직렬화하여 응답으로 반환하는 과정의 속도를 측정합니다.

## ⚙️ 프로젝트 설정 및 실행 방법

본 프로젝트는 `uv`를 사용하여 가상환경 및 의존성을 관리합니다.

1.  **가상환경 생성 및 활성화**:
    ```bash
    # Python 3.8+ 환경에서 실행
    uv venv
    source .venv/bin/activate
    ```

2.  **의존성 설치**:
    `pyproject.toml` 파일에 명시된 의존성을 설치합니다.
    ```bash
    uv pip sync
    ```

### 서버 실행

아래 명령어를 통해 Gunicorn(WSGI) 또는 Uvicorn(ASGI) 서버를 실행할 수 있습니다.

1.  **Gunicorn (WSGI 서버)**:
    ```bash
    uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
    ```

2.  **Uvicorn (ASGI 서버)**:
    ```bash
    uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers 4
    ```

### Locust를 이용한 부하 테스트 방법

프로젝트 루트에 위치한 `locustfile.py`를 사용하여 Locust로 부하 테스트를 진행할 수 있습니다.

#### 웹 UI 모드로 실행하기

실시간 모니터링이 필요할 경우 웹 UI를 사용하는 것이 편리합니다. 테스트를 위해서는 **두 개의 터미널**이 필요합니다.

1.  **터미널 1: Django 서버 실행**
    - 위에 안내된 **Gunicorn** 또는 **Uvicorn** 서버 실행 명령어 중 하나를 선택하여 실행합니다.
    - 서버가 실행된 상태로 이 터미널을 유지합니다.

2.  **터미널 2: Locust 실행**
    - 새로운 터미널을 열고, 다음 명령어를 실행하여 Locust를 시작합니다.
    ```bash
    uv run locust
    ```
    - 웹 브라우저에서 `http://localhost:8089`로 접속하여 테스트를 시작합니다.

#### Headless (Non-UI) 모드로 실행하기

k6처럼 스크립트 기반으로 간단하게 테스트를 실행하고 싶을 때는 Headless 모드를 사용합니다. 이 모드는 자동화된 테스트에 매우 유용합니다.

커맨드 라인에서 모든 옵션을 지정하여 즉시 테스트를 시작하고, 지정된 시간이 지나면 자동으로 종료됩니다.

-   `--headless`: UI 없이 실행
-   `-u`, `--users`: 시뮬레이션할 총 사용자 수
-   `-r`, `--spawn-rate`: 초당 생성할 사용자 수
-   `-t`, `--run-time`: 총 테스트 실행 시간 (예: `1m30s`, `1h`, `30s`)
-   `-T`, `--tags`: 실행할 태그 지정 (개별 엔드포인트 테스트 시)
-   `--host`: 테스트 대상 서버의 기본 URL (예: `http://localhost:8000`)
-   `--csv`: 결과를 CSV 파일로 저장

**명령어 예시:**

`async_cpu` 엔드포인트를 **100명의 유저**가 **초당 10명씩** 접속하여 **30초 동안** 테스트하고 결과를 `results`라는 이름의 CSV 파일로 저장하는 명령어는 다음과 같습니다.

```bash
uv run locust --headless -u 100 -r 10 -t 30s -T async_cpu --host http://localhost:8000 --csv results
```

위 명령을 실행하면 테스트가 진행된 후 `results_stats.csv`, `results_history.csv` 등의 파일이 생성됩니다.

#### 테스트 엔드포인트 및 태그

`locustfile.py`에 정의된 태그를 사용하여 특정 엔드포인트를 테스트할 수 있습니다.

-   **sync-io**: `--tags sync_io`
-   **async-io**: `--tags async_io`
-   **sync-cpu**: `--tags sync_cpu`
-   **async-cpu**: `--tags async_cpu`
-   **sync-json**: `--tags sync_json`
-   **async-json**: `--tags async_json`

---

## 📈 결과 분석

각 테스트 시나리오별 성능 측정 결과와 상세 분석은 `docs` 디렉터리에 별도로 기록됩니다.

-   **[CPU-Bound 테스트 결과 분석](./docs/cpu_bound_analysis.md)**

---

> 성능 측정 결과는 이 섹션에 표와 그래프 형태로 정리될 예정입니다. 각 시나리오별 RPS, 평균 응답 시간, CPU 및 메모리 사용량 등을 비교 분석합니다.

- **Sync vs. Async**:
    - I/O Bound 작업에서 `async` 뷰가 `sync` 뷰에 비해 얼마나 뛰어난 성능을 보이는가?
    - CPU Bound 작업에서는 어떤 차이가 있는가?
- **Gunicorn vs. Uvicorn**:
    - 동일한 조건에서 두 서버의 성능 차이는 어느 정도인가?
    - Uvicorn이 비동기 환경에서 제공하는 이점은 무엇인가?
- **최적화 방안**:
    - JSON 파싱 라이브러리(e.g., `orjson`) 변경 시 성능 향상 정도
    - TCP 소켓 옵션 (`TCP_NODELAY` 등) 설정에 따른 미세한 성능 변화 분석

## 📝 결론

> 모든 실험 결과를 종합하여 Django 애플리케이션의 특성에 맞는 최적의 아키텍처(Sync/Async, WSGI/ASGI) 선택 가이드라인을 제시합니다.
