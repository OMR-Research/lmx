from dataclasses import dataclass


@dataclass
class StaffLocation:
    """Represents the location of a staff in all various coordinate systems"""
    
    page_index: int
    """What page is this staff part of"""

    global_system_index: int
    """What system is this staff part of (out of all systems in the document)"""

    page_system_index: int
    """What system is this staff part of (out of systems on the page)"""

    part_index: int
    """What part is this staff part of (out of parts in the document)"""

    page_staff_index: int
    """What staff is this within its page"""

    system_staff_index: int
    """What staff is this within its system"""

    part_staff_index: int
    """What staff is this within its part (0 or 1, rarely more)"""
