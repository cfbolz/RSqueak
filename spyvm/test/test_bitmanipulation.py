from spyvm.util.bitmanipulation import splitter
from spyvm.model_display import map_word_bgra

def test_simple_splitbits():
    assert ((1, ) * 4) == splitter[8,8,8,8](0x01010101)
    assert ((255, ) * 4) == splitter[8,8,8,8](0xFfFfFfFf)

def test_fancy_splitbits():
    assert (4,3,2,1) == splitter[8,8,8,8](0x01020304)
    assert (1,3,7,15) == splitter[1,2,3,4](0xFfFfFfFf)
    
def test_format_splitbits():
    x = 0xAA
    assert (x & 3, ) == splitter[2](x)
 
def test_map_word_bgra():
    x = 0xaabbccdd
    assert map_word_bgra(x) == 0xddccbbaa