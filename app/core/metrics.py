from dataclasses import dataclass


@dataclass
class InMemoryMetrics:
    requests_total: int = 0
    create_success_total: int = 0
    create_failure_total: int = 0


metrics = InMemoryMetrics()
