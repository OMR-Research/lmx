from pathlib import Path
from ..TokenizationTestCase import TokenizationTestCase


class TestClefs(TokenizationTestCase):
    @property
    def samples_folder_path(self) -> Path:
        return Path(__file__).parent

    #######################################
    # G, F, C clefs in single-staff music #
    #######################################

    def test_basic_clef_encoding(self):
        self.encode_part("g-clef-mono")
        self.encode_part("f-clef-mono")
        self.encode_part("c-clef-mono")
    
    def test_basic_clef_decoding(self):
        self.decode_part("g-clef-mono")
        self.decode_part("f-clef-mono")
        self.decode_part("c-clef-mono")
    
    ########################
    # Piano part G,F clefs #
    ########################
    
    def test_piano_clef_encoding(self):
        self.encode_part("piano-clefs")
    
    def test_piano_clef_decoding(self):
        self.decode_part("piano-clefs")
    
    ##################################
    # C-clefs on unusual staff lines #
    ##################################

    def test_moved_c_clef_encoding(self):
        self.encode_part("moved-c-clef-at-1")
        self.encode_part("moved-c-clef-at-4")
    
    def test_moved_c_clef_decoding(self):
        self.decode_part("moved-c-clef-at-1")
        self.decode_part("moved-c-clef-at-4")

    ################
    # Clef changes #
    ################

    # TODO: test clef changes

    ########################
    # Invisible head clefs #
    ########################

    def test_invisible_clefs_encoding(self):
        self.encode_part("g-clef-mono-invisible")
        self.encode_part("piano-clefs-invisible")
    
    def test_invisible_clefs_decoding(self):
        self.decode_part("g-clef-mono-invisible")
        self.decode_part("piano-clefs-invisible")

    ####################
    # Full score clefs #
    ####################

    # (when score-level transcription exists)
    # TODO: piano + voice clefs
    # TODO: string quartet clefs
