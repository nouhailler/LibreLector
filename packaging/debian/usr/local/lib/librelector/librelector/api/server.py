"""Entry point: python3 -m librelector.api.server"""
import uvicorn


def main() -> None:
    uvicorn.run(
        "librelector.api.app:app",
        host="127.0.0.1",
        port=7531,
        log_level="info",
    )


if __name__ == "__main__":
    main()
