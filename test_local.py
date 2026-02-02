"""
Local test script for the Legal Agent.

Run with: python test_local.py
"""

import os
import sys

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
from dotenv import load_dotenv
load_dotenv()

import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_ai_hub():
    """Test AI Hub with available providers."""
    logger.info("=" * 60)
    logger.info("Testing AI Hub")
    logger.info("=" * 60)

    try:
        from app.lib.ai_hub import get_hub, ask_ai

        hub = get_hub()
        available = hub.list_available_providers()

        logger.info(f"Available providers: {available}")
        logger.info(f"Default provider: {hub.default_provider}")

        if not available:
            logger.error("No providers available!")
            return False

        # Test with first available provider
        response = ask_ai(
            prompt="Say 'AI Hub is working!' in exactly those words.",
            system="You are a test assistant. Reply briefly.",
        )

        logger.info(f"AI Response: {response}")
        logger.info("[OK] AI Hub test PASSED")
        return True

    except Exception as e:
        logger.error(f"[FAIL] AI Hub test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_contract_analysis():
    """Test contract analysis with a sample contract."""
    logger.info("=" * 60)
    logger.info("Testing Contract Analysis")
    logger.info("=" * 60)

    sample_contract = """
    SERVICE AGREEMENT

    This Service Agreement ("Agreement") is entered into as of January 15, 2026,
    by and between AIssential Pro ("Provider") and ACME Corporation ("Client").

    1. SERVICES
    Provider agrees to provide AI consulting services to Client for a period of 12 months.

    2. PAYMENT
    Client shall pay Provider $10,000 per month, due on the 1st of each month.
    Late payments shall incur a 5% penalty.

    3. TERMINATION
    Either party may terminate this Agreement with 30 days written notice.
    Upon termination, Client shall pay for all services rendered.

    4. LIMITATION OF LIABILITY
    Provider's total liability shall not exceed the fees paid in the last 3 months.
    Provider is not liable for indirect, incidental, or consequential damages.

    5. INTELLECTUAL PROPERTY
    All work product created by Provider shall be owned by Client upon full payment.

    6. CONFIDENTIALITY
    Both parties agree to keep confidential all proprietary information shared.
    This obligation survives termination of this Agreement.

    7. GOVERNING LAW
    This Agreement shall be governed by the laws of the State of California.

    SIGNATURES:
    _____________________     _____________________
    AIssential Pro            ACME Corporation
    """

    try:
        from app.services.contract_analyzer import analyze_contract

        result = analyze_contract(sample_contract, "test_service_agreement.txt")

        logger.info("\n" + "=" * 60)
        logger.info("ANALYSIS RESULT:")
        logger.info("=" * 60)

        if isinstance(result, dict):
            logger.info(f"Risk Score: {result.get('risk_score', 'N/A')}")
            logger.info(f"Risks: {result.get('risks', [])}")
            logger.info(f"Missing Clauses: {result.get('missing_clauses', [])}")
            logger.info(f"Recommendations: {result.get('recommendations', [])}")
        else:
            logger.info(f"Raw result: {result}")

        logger.info("\n[OK] Contract analysis test PASSED")
        return True

    except Exception as e:
        logger.error(f"[FAIL] Contract analysis test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AIssential Legal Agent - Local Test Suite")
    print("=" * 60 + "\n")

    # Check environment
    providers = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Mistral": os.getenv("MISTRAL_API_KEY"),
        "Gateway": os.getenv("GATEWAY_API_KEY"),
    }

    print("API Keys configured:")
    for name, key in providers.items():
        status = "[OK] Set" if key else "[--] Not set"
        print(f"  {name}: {status}")
    print()

    if not any(providers.values()):
        print("[ERROR] No AI provider configured!")
        print("Please set at least one API key in your .env file")
        print("  - OPENAI_API_KEY (recommended for testing)")
        print("  - ANTHROPIC_API_KEY")
        print("  - GATEWAY_API_KEY")
        sys.exit(1)

    results = []

    # Test 1: AI Hub
    results.append(("AI Hub", test_ai_hub()))

    # Test 2: Contract analysis
    results.append(("Contract Analysis", test_contract_analysis()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "[OK] PASSED" if passed else "[FAIL] FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("All tests passed!")
    else:
        print("Some tests failed. Check the logs above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
