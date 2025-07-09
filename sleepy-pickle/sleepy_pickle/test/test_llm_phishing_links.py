from ..demos.llm_phishing_links import main
import pytest
import os

# Do a full run-through - note this only tests for crashes
@pytest.mark.skipif('RUNNING_IN_CI' in os.environ,
                    reason="Github runner doesn't have enough memory")
def test_run_llm_phishing_links():
    main()