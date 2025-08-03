import pytest
import src.website as website

def test_hw():
    assert website.hello_world() == "hello world"