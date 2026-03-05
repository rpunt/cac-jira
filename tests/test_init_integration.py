"""
Integration tests for cac_jira module initialization.

Tests the successful initialization of the module including:
- Config loading
- Credential retrieval
- JiraClient instantiation
"""

import importlib
import sys

import pytest


class TestModuleInitialization:
    """Integration tests for module initialization."""

    def test_initialize_success(self):
        """Test that _initialize() successfully sets up module state."""
        # Import cac_jira fresh to trigger initialization
        if "cac_jira" in sys.modules:
            # Force reimport to test initialization
            importlib.reload(sys.modules["cac_jira"])

        import cac_jira

        # Call _initialize() directly
        cac_jira._initialize()

        # Verify initialization flag is set
        assert cac_jira._initialized is True

        # Verify module state contains expected keys
        assert "CONFIG" in cac_jira._module_state
        assert "JIRA_CLIENT" in cac_jira._module_state

        # Verify CONFIG object is properly initialized
        config = cac_jira._module_state["CONFIG"]
        assert config is not None
        assert config.get("server") == "test.atlassian.net"
        assert config.get("username") == "test@example.com"
        assert config.get("project") == "TEST"

        # Verify JIRA_CLIENT object is created
        jira_client = cac_jira._module_state["JIRA_CLIENT"]
        assert jira_client is not None

    def test_lazy_attribute_access(self):
        """Test that lazy initialization works when accessing module attributes."""
        # Import cac_jira fresh
        if "cac_jira" in sys.modules:
            # Reset module state
            mod = sys.modules["cac_jira"]
            mod._initialized = False
            mod._module_state.clear()

        import cac_jira

        # Accessing JIRA_CLIENT should trigger initialization
        client = cac_jira.JIRA_CLIENT
        assert client is not None
        assert cac_jira._initialized is True

        # Accessing CONFIG should return the config object
        config = cac_jira.CONFIG
        assert config is not None
        assert config.get("server") == "test.atlassian.net"

    def test_invalid_attribute_access(self):
        """Test that accessing invalid attributes raises AttributeError."""
        import cac_jira

        with pytest.raises(AttributeError, match="has no attribute 'INVALID_ATTR'"):
            _ = cac_jira.INVALID_ATTR

    def test_initialize_idempotent(self):
        """Test that calling _initialize() multiple times is safe."""
        import cac_jira

        # Call initialize multiple times
        cac_jira._initialize()
        cac_jira._initialize()
        cac_jira._initialize()

        # Should still be initialized and have the same state
        assert cac_jira._initialized is True
        assert "CONFIG" in cac_jira._module_state
        assert "JIRA_CLIENT" in cac_jira._module_state
