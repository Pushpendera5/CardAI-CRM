from app.ml.field_extractor import BusinessCardFieldExtractor


def test_field_extractor_gets_core_fields():
    text = """Rahul Sharma
Sales Manager
ABC Technologies Pvt Ltd
Mobile 9876543210
rahul@abctech.com
www.abctech.com
Sector 18, Noida, India"""
    result = BusinessCardFieldExtractor().extract(text)
    assert result.name == "Rahul Sharma"
    assert "Sales" in result.designation
    assert "ABC" in result.company
    assert result.email == "rahul@abctech.com"
    assert result.mobile.endswith("9876543210")

