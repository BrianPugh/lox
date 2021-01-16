import pytest
import lox


@pytest.fixture
def mock_pdb(mocker):
    return mocker.patch('lox.pdb._pdb_lock')

@pytest.fixture
def mock_continue(mocker):
    """ Makes it so the first command when entering pdb is "continue" """
    return mocker.patch('cmd.input', return_value='continue')

def test_pdb_set_trace_basic(mock_pdb, mock_continue):
    lox.set_trace()
    mock_pdb.acquire.assert_called_once()
    mock_pdb.release.assert_called_once()

# TODO: test multiple set_trace() in a row
# TODO: test multithread
