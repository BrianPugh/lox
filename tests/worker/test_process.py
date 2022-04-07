from random import random
from time import sleep, time

import pytest
from tqdm import tqdm

import lox

SLEEP_TIME = 0.01
N_WORKERS = 2


def test_basic_args():
    in_x = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
    ]
    in_y = [
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
    ]

    @lox.process(N_WORKERS)  # specifying maximum number of processes
    def worker_task(x, y):
        sleep(SLEEP_TIME)
        return x * y

    # Vanilla function execution still works
    assert 10 == worker_task(2, 5)

    assert len(worker_task) == 0
    print("test_process: %s" % (worker_task))

    for _ in range(2):
        for x, y in zip(in_x, in_y):
            worker_task.scatter(x, y)

        res = worker_task.gather()
        assert len(res) == len(in_x)

        for r, x, y in zip(res, in_x, in_y):
            assert (x * y) == r


def test_basic_noargs():
    in_x = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
    ]
    in_y = [
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
    ]

    @lox.process  # maximum number of processes = # cores
    def worker_task(x, y):
        sleep(SLEEP_TIME)
        return x * y

    # Vanilla function execution still works
    assert 10 == worker_task(2, 5)

    assert len(worker_task) == 0
    print("test_process: %s" % (worker_task))

    for _ in range(2):
        for x, y in zip(in_x, in_y):
            worker_task.scatter(x, y)

        res = worker_task.gather()
        assert len(res) == len(in_x)

        for r, x, y in zip(res, in_x, in_y):
            assert (x * y) == r


class Class1:
    def __init__(self, z):
        self.z = z

    @lox.process(2)
    def test_method1(self, x, y):
        sleep(SLEEP_TIME)
        return x * y + self.z

    @lox.process
    def test_method2(self, x, y):
        sleep(SLEEP_TIME)
        return x * y + self.z


def test_method_1():
    in_x = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
    ]
    in_y = [
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
    ]
    z = 5

    test_obj = Class1(z)

    assert (2 * 5 + z) == test_obj.test_method1(2, 5)
    assert (2 * 5 + z) == test_obj.test_method2(2, 5)

    for i in range(2):
        for x, y in zip(in_x, in_y):
            test_obj.test_method1.scatter(x, y)
        res = test_obj.test_method1.gather()
        assert len(res) == len(in_x), f"iteration {i}"

        for r, x, y in zip(res, in_x, in_y):
            assert (x * y + z) == r

        for x, y in zip(in_x, in_y):
            test_obj.test_method2.scatter(x, y)
        res = test_obj.test_method2.gather()
        assert len(res) == len(in_x), f"iteration {i}"

        for r, x, y in zip(res, in_x, in_y):
            assert (x * y + z) == r


@pytest.fixture
def mock_tqdm(mocker):
    return mocker.patch("lox.worker.process.TQDM")


def test_tqdm_bool(mock_tqdm):

    in_x = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
    ]
    in_y = [
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
    ]

    @lox.process(N_WORKERS)  # specifying maximum number of processes
    def worker_task(x, y):
        sleep(random())
        return x * y

    for x, y in zip(in_x, in_y):
        worker_task.scatter(x, y)
    res = worker_task.gather(tqdm=True)

    mock_tqdm.assert_called_once_with(total=len(in_x))

    assert len(res) == len(in_x)

    for r, x, y in zip(res, in_x, in_y):
        assert (x * y) == r


def test_tqdm_tqdm(mocker):
    in_x = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
    ]
    in_y = [
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
    ]

    @lox.process(N_WORKERS)  # specifying maximum number of processes
    def worker_task(x, y):
        sleep(random())
        return x * y

    pbar = mocker.MagicMock()
    for x, y in zip(in_x, in_y):
        worker_task.scatter(x, y)
    res = worker_task.gather(tqdm=pbar)

    n_update = 0
    for args, _kwargs in pbar.update.call_args_list:
        n_update += args[0]
    assert n_update == len(in_x)

    assert len(res) == len(in_x)

    for r, x, y in zip(res, in_x, in_y):
        assert (x * y) == r


@pytest.mark.visual
def test_tqdm_bool_visual():
    """Primarily for visually asserting our tqdm mocks are correct."""

    in_x = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
    ]
    in_y = [
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
    ]

    @lox.process(N_WORKERS)  # specifying maximum number of processes
    def worker_task(x, y):
        sleep(random())
        return x * y

    for x, y in zip(in_x, in_y):
        worker_task.scatter(x, y)
    res = worker_task.gather(tqdm=True)

    assert len(res) == len(in_x)

    for r, x, y in zip(res, in_x, in_y):
        assert (x * y) == r
