# CPU-Bound 테스트 결과 분석

Locust 테스트 결과, CPU-Bound 작업에서는 Gunicorn이 Uvicorn보다 더 나은 성능을 보이는 것으로 확인되었습니다.

### 테스트 결과 요약 (CPU-Bound Task)

| 서버 | 뷰 종류 | **Requests/s (RPS)** ⬆️ | **평균 응답 시간 (ms)** ⬇️ |
| :--- | :--- | :--- | :--- |
| **Gunicorn** | Sync (동기) | **7.59** | **7,416** |
| Gunicorn | Async (비동기) | **7.82** | **7,234** |
| Uvicorn | Sync (동기) | 6.46 | 9,988 |
| Uvicorn | Async (비동기) | 6.54 | 8,724 |

(RPS는 높을수록 좋고, 응답 시간은 낮을수록 좋습니다.)

### 분석 요점

1.  **작업의 종류**: 현재 테스트는 `sum(i * i for i in range(10_000_000))`과 같이 순수하게 CPU 연산만을 요구하는 **CPU-Bound** 작업입니다. 외부 I/O(네트워크, 디스크 등) 대기 시간이 전혀 없습니다.
2.  **Gunicorn (WSGI 서버)의 강점**:
    *   Gunicorn은 동기 워커 프로세스 기반으로, 요청이 들어오면 워커 프로세스가 해당 요청의 CPU 작업을 처음부터 끝까지 전담하여 처리합니다.
    *   CPU-Bound 작업은 다른 무엇을 기다릴 필요가 없으므로, 이러한 직접적인 처리 방식이 가장 효율적입니다. Context Switching이나 비동기 이벤트 루프 관리와 같은 추가적인 오버헤드가 거의 없습니다.
    *   Gunicorn에서 Async 뷰를 실행했을 때도 성능 차이가 크지 않은 것은, Django의 WSGI 핸들러가 Async 뷰를 실행하기 위해 내부적으로 작은 이벤트 루프를 생성하지만, 결국 `sync_to_async`를 통해 스레드 풀에서 CPU 작업을 처리하기 때문입니다.
3.  **Uvicorn (ASGI 서버)의 한계점 (CPU-Bound 작업에서)**:
    *   Uvicorn과 같은 ASGI 서버는 **I/O-Bound 작업**의 효율성을 극대화하기 위해 설계되었습니다. 즉, DB 쿼리나 외부 API 호출처럼 오래 걸리는 I/O 작업을 기다리는 동안 다른 요청을 처리하는 데 강점이 있습니다.
    *   하지만 CPU-Bound 작업은 I/O 대기 없이 CPU를 계속 점유합니다.
    *   `async_cpu_view`에서 `repository.get_cpu_bound_data()`와 같은 동기(blocking) CPU 작업을 직접 실행하면 Uvicorn의 메인 이벤트 루프가 멈춰버리는(blocking) 문제가 발생합니다.
    *   이를 해결하기 위해 우리는 `@sync_to_async` 데코레이터를 사용하여 CPU-Bound 작업을 별도의 **스레드 풀**에서 실행하도록 했습니다.
    *   문제는 **이 스레드 풀로 작업을 보내고, 결과를 다시 이벤트 루프로 받아오는 과정에서 발생하는 추가적인 오버헤드**입니다. Uvicorn의 이벤트 루프 관리, 스레드 풀과의 통신 비용이 Gunicorn의 직접적인 CPU 처리 방식보다 더 크기 때문에, CPU-Bound 작업에서는 오히려 성능이 낮게 측정됩니다.
    *   동일한 이유로 Uvicorn에서 Sync 뷰(`sync_cpu`)를 실행할 때도 Django/Uvicorn 내부적으로 `sync_to_async`와 유사한 방식으로 스레드 풀을 사용하게 되며, 이로 인한 오버헤드가 발생합니다.

### 결론 (CPU-Bound 작업)

이 결과는 "비동기 프로그래밍이 항상 빠른 것은 아니다"라는 중요한 사실을 보여줍니다. **순수 CPU-Bound 작업에서는 동기 방식과 WSGI 서버(Gunicorn)가 더 효율적일 수 있습니다.** 비동기 서버(Uvicorn)는 I/O 대기 시간이 긴 작업에서 진정한 강점을 발휘하며, CPU-Bound 작업에 비동기 패러다임을 무리하게 적용하면 오히려 불필요한 오버헤드만 추가될 수 있습니다.
