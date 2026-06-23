import abc
from pathlib import Path
from ..assert_xml_equals import assert_xml_equals
from ..assert_lmx_equals import assert_lmx_equals
from .lmx_decode_part import lmx_decode_part
from .lmx_encode_part import lmx_encode_part
from .wrap_part_in_score import wrap_part_in_score


class TokenizationTestCase(abc.ABC):
    """
    Base class for test cases that text the LMX tokenizer
    (both encoding and decoding). It exposes the `.encode_part("sample")`
    and `.decode_part("sample")` methods, which will try to convert
    between "sample.musicxml" and "sample.lmx" (encoding) and
    vice versa (decoding). The folder path containing sample files
    must be provided in the constructor.

    If your test has any other setup than comparing files,
    please use the underlying functions used in the implementation
    of these methods.
    """
    @property
    @abc.abstractmethod
    def samples_folder_path(self) -> Path:
        """Path to the folder containing sample files"""
        raise NotImplementedError

    def encode_part(self, sample_name: str):
        """Encodes given sample's MusicXML file to LMX and
        checks it against the provided sample LMX file.
        
        :param sample_name: File name of the sample,
            WITHOUT the suffix (.lmx or .musicxml)
        """
        assert_lmx_equals(
            given=lmx_encode_part(
                self.samples_folder_path / f"{sample_name}.musicxml"
            ),
            expected=self.samples_folder_path / f"{sample_name}.lmx"
        )

    def decode_part(self, sample_name: str):
        """Decodes given sample's LMX file back to MusicXML and
        checks it against the provided sample MusicXML file.
        
        :param sample_name: File name of the sample,
            WITHOUT the suffix (.lmx or .musicxml)
        """
        assert_xml_equals(
            given=wrap_part_in_score(
                lmx_decode_part(
                    self.samples_folder_path / f"{sample_name}.lmx"
                )
            ),
            expected=self.samples_folder_path / f"{sample_name}.musicxml",
        )
    
    # TODO: encode_score
    # TODO: decode_score ... for full-score tokenization
    