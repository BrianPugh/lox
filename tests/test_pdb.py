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

def test_pdb_set_trace_multi_1(mock_pdb_lock, mock_cmd_continue):
    lox.set_trace()
    mock_pdb_lock.acquire.assert_called_once()
    mock_pdb_lock.release.assert_called_once()
    lox.set_trace()
    assert mock_pdb_lock.acquire.call_count == 2
    assert mock_pdb_lock.release.call_count == 2

def test_pdb_set_trace_multi_2(mocker, mock_pdb_lock):
    mock_cmd = mocker.patch('cmd.input', side_effect=('n', 'c', 'c', 'c', 'c', 'c'))
    lox.set_trace()
    a_noop_statement_that_pdb_will_stop_on_unlike_pass = None  # Will pause here
    a_noop_statement_that_pdb_will_stop_on_unlike_pass = None  # 'n' brings us here, the 'c' will cause us to release the mutex
    lox.set_trace()                                            # mutex reacquired
    a_noop_statement_that_pdb_will_stop_on_unlike_pass = None  # will pause here, the 'c' will cause us to release the mutex
    a_noop_statement_that_pdb_will_stop_on_unlike_pass = None
    assert mock_pdb_lock.acquire.call_count == 2
    assert mock_pdb_lock.release.call_count == 2

def test_pdb_set_trace_multi_3(mocker, mock_pdb_lock):
    mock_cmd = mocker.patch('cmd.input', side_effect=('n', 'n', 'c', 'c', 'c', 'c', 'c'))
    lox.set_trace()
    a_noop_statement_that_pdb_will_stop_on_unlike_pass = None
    lox.set_trace()                                           # should not be reacquired since we're already debugging
    a_noop_statement_that_pdb_will_stop_on_unlike_pass = None
    a_noop_statement_that_pdb_will_stop_on_unlike_pass = None
    assert mock_pdb_lock.acquire.call_count == 1
    assert mock_pdb_lock.release.call_count == 1

def test_pdb_set_trace_multi_4(mocker, mock_pdb_lock):
    mock_cmd = mocker.patch('cmd.input', side_effect=('n', 'n', 'c', 'c', 'c', 'c', 'c'))
    lox.set_trace()  # obtain
    lox.set_trace()  # not obtained since we're in session
    lox.set_trace()  # not obtained since we're in session
    lox.set_trace()  # Released and reobtained because of 'c'
    lox.set_trace()  # Released and reobtained because of 'c'
    assert mock_pdb_lock.acquire.call_count == 3
    assert mock_pdb_lock.release.call_count == 3


@pytest.mark.skip(reason="Not Implemented")
def test_pdb_set_trace_multithread_basic(mock_pdb_lock, mock_cmd_continue):
    pass

@pytest.mark.skip(reason="Not Implemented")
def test_pdb_set_trace_multithread_lox(mock_pdb_lock, mock_cmd_continue):
    pass
