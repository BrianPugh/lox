import pytest
import lox


@pytest.fixture
def mock_pdb_lock(mocker):
    return mocker.patch('lox.pdb._pdb_lock')

@pytest.fixture
def mock_cmd_continue(mocker):
    """ Makes it so the first command when entering pdb is "continue" """
    return mocker.patch('cmd.input', return_value='continue')

def test_pdb_set_trace_basic(mock_pdb_lock, mock_cmd_continue):
    lox.set_trace()
    mock_pdb_lock.acquire.assert_called_once()
    mock_pdb_lock.release.assert_called_once()

@pytest.mark.skip(reason="For manual testing during development.")
def test_pdb_set_trace_manual():
    """ No mocking for manual testing to confirm our mocks are appropriate """
    lox.set_trace()

@pytest.mark.skip(reason="Not Implemented")
def test_pdb_set_trace_multi(mock_pdb_lock, mock_cmd_continue):
    pass

@pytest.mark.skip(reason="Not Implemented")
def test_pdb_set_trace_multithread_basic(mock_pdb_lock, mock_cmd_continue):
    pass

@pytest.mark.skip(reason="Not Implemented")
def test_pdb_set_trace_multithread_lox(mock_pdb_lock, mock_cmd_continue):
    pass
