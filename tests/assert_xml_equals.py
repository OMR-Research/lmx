import xml.dom.minidom
import xml.etree.ElementTree as ET
from pathlib import Path, PurePath


def assert_xml_equals(
        given: str | ET.ElementTree | ET.Element | Path,
        expected: str | ET.ElementTree | ET.Element | Path,
):
    expected = prepare_xml_value(expected)
    given = prepare_xml_value(given)
    
    # pytest with -vv flag will show you exactly what's missing or added
    assert given == expected, "Given XML is incorrect ('+' contains unexpected, '-' is missing)"


def prepare_xml_value(value: str | ET.ElementTree | ET.Element | Path) -> str:
    # stringify XML element
    if isinstance(value, ET.Element):
        xml_string = str(ET.tostring(value), "utf-8")
    # stringify XML element tree
    elif isinstance(value, ET.ElementTree):
        xml_string = str(ET.tostring(value.getroot()), "utf-8")
    # load file
    elif isinstance(value, PurePath):
        xml_string = value.read_text("utf-8")
    # nothing necessary
    elif type(value) is str:
        xml_string = value
    else:
        raise ValueError(
            f"Given 'value' argument is of invalid type {type(value)}"
        )

    # canonicalize
    canonicalized_xml_string = ET.canonicalize(
        xml_string,
        strip_text=True,
    )

    # pretty-print
    dom = xml.dom.minidom.parseString(canonicalized_xml_string)
    pretty_xml_string = dom.toprettyxml(indent="  ")

    return pretty_xml_string
