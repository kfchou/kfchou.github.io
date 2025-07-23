from unittest.mock import patch, MagicMock, ANY, Mock
import pytest


def get_database_object():
    return None

def check_object_attributes():
    obj = get_database_object()
    
    if obj is None:
        raise Exception("object is None")
    
    # obj.attr could be None for a varierty of reasons
    if obj.attr is None:
        raise ValueError('attribute is not set')
    
    # in production, obj.attr is expected to be some data type
    if isinstance(obj.attr,dict):
        raise TypeError("the attribute is a dict instance")
    
    # obj.method returns some value
    if obj.method() == "magical":
        raise Exception("a magical string was returned")
    
# from your_module import check_object_attributes
@patch('kfchou.mocking.get_database_object')
def test_check_object_is_not_none(mock_get_db_obj):
    mock_obj = MagicMock()
    mock_get_db_obj.return_value = mock_obj

    check_object_attributes()  # should not raise
    
    
def test_check_object_is_none():
    with pytest.raises(Exception, match="object is None"):
        check_object_attributes()

@patch('kfchou.mocking.get_database_object')
def test_check_object_attributes_none_attr(mock_get_db_obj):
    mock_obj = MagicMock()
    mock_obj.attr = None
    mock_get_db_obj.return_value = mock_obj

    with pytest.raises(ValueError, match='attribute is not set'):
        check_object_attributes()

@patch('kfchou.mocking.get_database_object')
def test_check_object_attributes_missing_key(mock_get_db_obj):
    mock_obj = MagicMock()
    mock_obj.method.return_value = "magical"
    mock_get_db_obj.return_value = mock_obj

    with pytest.raises(Exception, match="a magical string was returned"):
        check_object_attributes()

@patch('kfchou.mocking.get_database_object')
def test_check_object_attributes_none_attr(mock_get_db_obj):
    # Similarly, manually set the object's .attr to be a dict
    mock_obj = MagicMock()
    mock_obj.attr = {}

    # get_database_object() -> mock_obj, and mock_obj.attr == {}
    mock_get_db_obj.return_value = mock_obj

    # this check passes
    with pytest.raises(TypeError, match='the attribute is a dict instance'):
        check_object_attributes()