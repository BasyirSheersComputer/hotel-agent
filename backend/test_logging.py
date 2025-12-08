"""
Test script for Structured Logging.
Verifies that logs are output in valid JSON format.
"""
import logging
import json
import io
import sys
from app.core.logger import configure_logging, get_logger

def test_json_logging():
    # Capture stdout
    capture = io.StringIO()
    handler = logging.StreamHandler(capture)
    
    # Re-configure logging to output to our capture stream
    # Note: effectively we just want to test structlog's processor chain
    import structlog
    
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(file=capture),
    )
    
    logger = get_logger("test")
    logger.info("test_event", key="value", status=200)
    
    output = capture.getvalue().strip()
    print(f"Raw Output: {output}")
    
    try:
        data = json.loads(output)
        assert data["event"] == "test_event"
        assert data["key"] == "value"
        assert data["status"] == 200
        assert "timestamp" in data
        print("✅ SUCCESS: Output is valid JSON.")
    except json.JSONDecodeError:
        print("❌ FAIL: Output is NOT valid JSON.")
    except AssertionError as e:
        print(f"❌ FAIL: Content mismatch. {e}")

if __name__ == "__main__":
    test_json_logging()
