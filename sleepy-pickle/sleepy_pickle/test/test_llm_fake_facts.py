from ..demos.llm_fake_facts import main
import os
import pytest

# Do a full run-through - note this only tests for crashes
@pytest.mark.skipif('RUNNING_IN_CI' in os.environ,
                    reason="Github runner doesn't have enough memory")
def test_run_llm_fake_facts():
    main("./sleepy_pickle/demos/data/steve_jobs_nvidia.json")