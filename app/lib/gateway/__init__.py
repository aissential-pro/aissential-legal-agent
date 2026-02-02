"""
Gateway client library for LLM Gateway integration.

Provides authenticated access to the AIssential LLM Gateway API.
"""

from lib.gateway.client import GatewayClient
from lib.gateway.modules import MODULES

__all__ = ["GatewayClient", "MODULES"]
