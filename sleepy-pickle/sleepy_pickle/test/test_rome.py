from ..attacks.rome import main
import pytest
import os

# TODO: generate proper random file for testing
# Do a full run-through - note this only tests for crashes
@pytest.mark.skipif('RUNNING_IN_CI' in os.environ,
                    reason="Github runner doesn't have enough memory")
def test_rome_gpt2():
    main("/tmp/lsdkjfsdlkfj")