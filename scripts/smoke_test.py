import httpx


def main() -> None:
    with httpx.Client(base_url="http://localhost:8000", timeout=10.0) as client:
        live = client.get("/health/live")
        print("/health/live", live.status_code, live.text)


if __name__ == "__main__":
    main()
