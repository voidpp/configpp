
import pytest
from collections import OrderedDict
from configpp.soil.transform import JSONTransform, YamlTransform

@pytest.mark.parametrize('data, keys', [
    ('{"a":7, "k":8, "b": 42}', ['a', 'k', 'b']),
    ('{"f":7, "e":8, "42": "a"}', ['f', 'e', '42']),
    ('{"o":7, "a":8, "r": 42}', ['o', 'a', 'r']),
    ('{"r":7, "8":8, "b": 42}', ['r', '8', 'b']),

])
def test_load_json_ordered(data, keys):

    transform = JSONTransform()

    res = transform.deserialize(data)

    assert list(res.keys()) == keys

@pytest.mark.parametrize('data, res', [
    (OrderedDict([("a",7), ("k",8), ("b", 42)]), '{"a": 7, "k": 8, "b": 42}'),
    (OrderedDict([("f",7), ("e",8), ("42", "a")]), '{"f": 7, "e": 8, "42": "a"}'),
    (OrderedDict([("o",7), ("a",8), ("r", 42)]), '{"o": 7, "a": 8, "r": 42}'),
    (OrderedDict([("r",7), ("8",8), ("b", 42)]), '{"r": 7, "8": 8, "b": 42}'),
])
def test_dump_json_ordered(data, res):

    transform = JSONTransform()

    assert transform.serialize(data) == res

@pytest.mark.parametrize('data, keys', [
    ('f: 7\ne: 8\n42: a', ['f', 'e', 42]),
    ('o: 7\na: 8\nr: 42', ['o', 'a', 'r']),

])
def test_load_yaml_ordered(data, keys):

    transform = YamlTransform()

    res = transform.deserialize(data)

    assert list(res.keys()) == keys

@pytest.mark.parametrize('data, res', [
    (OrderedDict([("a",7), ("k",8), ("b", 42)]), "a: 7\nk: 8\nb: 42\n"),
    (OrderedDict([("f",7), ("e",8), ("42", "a")]), "f: 7\ne: 8\n'42': a\n"),
    (OrderedDict([("o",7), ("a",8), ("r", 42)]), "o: 7\na: 8\nr: 42\n"),
    (OrderedDict([("r",7), ("8",8), ("b", 42)]), "r: 7\n'8': 8\nb: 42\n"),
])
def test_dump_yaml_ordered(data, res):

    transform = YamlTransform()

    assert transform.serialize(data) == res
