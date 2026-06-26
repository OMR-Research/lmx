# `OnsetVisitor` utility

When processing MusicXML, you often need to know onset of various elements (`<note>`, `<attributes>`) but this information is not explicitly encoded in the XML itself. Instead, it must be tracked by adding up `<duration>` values, whose unit also depends on the specified `<divisions>`. Therefore you very often end up with this pattern in your code:

```py
onset = 0

for child in measure_element:
    if child.tag == "note":
        handle_note(child, onset)
    elif child.tag == "attributes":
        handle_attributes(child, onset)
    
    # update onset
    duration = int(child.findtext("duration", "0"))
    if child.tag == "backup":
        duration = -duration
    onset += duration
```

As you can see, the onset tracking code pollutes the business logic. Moreover, onset tracking is not as simple as adding up durations: not all elements have durations; not all `<note>` elements have duration; `<backup>` elements decrease onset; chord notes have duration which should be ignored; etc. Implementing this manually each time you need to track onsets is a guaranteed way to introduce bugs in more complicated music notation documents.

The solution is to extract this logic to one place and reuse it. Which is exactly what `OnsetVisitor` is. It transforms the above code into something like this:

```py
import xml.etree.ElementTree as ET
from lmx.musicxml.time.OnsetVisitor import OnsetVisitor

part_element = load_part("my-sample.musicxml") # <part> ET.Element
divisions = int(part_element.findtext("measure/attributes/divisions"))

class MyVisitor(OnsetVisitor):
    def __init__(self):
        nonlocal divisions
        super().__init__(divisions=divisions, record_onsets=False)

        self.note_count = 0
        self.attributes_count = 0

    def visit_note(self, note_element: ET.Element):
        print("Found a note at onset", self.part_onset)
        self.note_count += 1

    def visit_attributes(self, attributes_element: ET.Element):
        print("Found attributes at onset", self.part_onset)
        self.attributes_count += 1

visitor = MyVisitor()
visitor.run(part_element)

print("Total notes:", visitor.note_count)
print("Total attributes:", visitor.attributes_count)
```

The visitor can also record onsets of direct measure child elements it encounters, which can then be queried later:

```py
import xml.etree.ElementTree as ET
from lmx.musicxml.time.OnsetVisitor import OnsetVisitor

# load MusicXML <part>
part_element = load_part("my-sample.musicxml") # <part> ET.Element
divisions = int(part_element.findtext("measure/attributes/divisions"))

# run the visitor to record the onset tape
visitor = OnsetVisitor(
    divisions=divisions,
    record_onsets=True
)
visitor.run(part_element)

# have an interesting element
second_attributes_element = part_element.find("measure/attributes[2]")

# query its onset later
onset = visitor.onset_of(second_attributes_element)
print("Second attributes element starts having effect after", onset)
```
