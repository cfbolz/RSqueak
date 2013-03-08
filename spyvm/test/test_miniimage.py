# ----- mini.image productline -------------------------------
#       NOT relying on order of methods
#       using setup_module(module) now
import py
from spyvm import squeakimage
from spyvm import model
from spyvm import constants
from spyvm import interpreter
from spyvm import shadow
from spyvm import objspace
# lazy initialization of test data, ie ImageReader and Float class

def setup_module(module, filename='mini.image'):
    space = objspace.ObjSpace()
    from spyvm.tool.analyseimage import image_dir
    module.mini_image = image_dir.join(filename)
    module.reader = open_miniimage(space)
    reader.initialize()
    module.image = squeakimage.SqueakImage()
    module.image.from_reader(space, reader)
    module.space = space
    module.interp = interpreter.Interpreter(space, image)

def find_symbol(name):
    if name == "asSymbol":
        return image.w_asSymbol
    return perform(space.wrap_string(name), "asSymbol")

def open_miniimage(space):
    return squeakimage.reader_for_image(space, squeakimage.Stream(mini_image.open()))

def get_reader():
    return reader
    
def get_image():
    return image
    
def get_float_class():
    image = get_image()
    return image.special(constants.SO_FLOAT_CLASS)

# ------ tests ------------------------------------------
        
def test_miniimageexists():
    assert mini_image.check(dir=False)

def test_read_header():
    reader = open_miniimage(space)
    reader.read_header()
    assert reader.endofmemory == 655196
    assert reader.oldbaseaddress == -1220960256
    assert reader.specialobjectspointer == -1220832384

def test_read_all_header(): 
    reader = open_miniimage(space)
    reader.read_header()
    next = reader.stream.peek()
    assert next != 0 #expects object header, which must not be 0x00000000 
      
      
def test_all_pointers_are_valid():
    reader = get_reader()
    for each in reader.chunks.itervalues():
        if each.format < 5: 
            for pointer in each.data:
                if (pointer & 1) != 1:
                    assert pointer in reader.chunks   
    
    
def test_there_are_31_compact_classes():
    reader = get_reader()
    assert len(reader.compactclasses) == 31
    
def test_float_class_size():
    w_float_class = get_float_class()
    assert w_float_class.size() == 9

def test_float_class_name():
    w_float_class = get_float_class()
    w_float_class_name = w_float_class.fetch(space, 6)
    assert isinstance(w_float_class_name, model.W_BytesObject)
    assert w_float_class_name.bytes == list("Float")
    
def test_str_w_object():
    w_float_class = get_float_class()
    w_float_class.as_class_get_shadow(space)
    assert str(w_float_class) == "Float class"
    w_float_class.shadow_of_my_class(space)
    #assert str(w_float_class.getclass(space)) == "a Metaclass" #yes, with article
    w_float_class.getclass(space).shadow_of_my_class(space)
    #assert str(w_float_class.getclass(space).getclass(space)) == "Metaclass class"

def test_nil_true_false():
    image = get_image()
    w = image.special(constants.SO_NIL)
    w.shadow_of_my_class(space)
    assert str(w) == "a UndefinedObject" #yes, with article
    w = image.special(constants.SO_FALSE)
    w.shadow_of_my_class(space)
    assert str(w) == "a False" #yes, with article
    w = image.special(constants.SO_TRUE)
    w.shadow_of_my_class(space)
    assert str(w) == "a True" #yes, with article
    
def test_scheduler():
    image = get_image()
    w = image.special(constants.SO_SCHEDULERASSOCIATIONPOINTER)
    w0 = w.fetch(space, 0)
    assert str(w0) == "Processor" 
    w0 = w.fetch(space, 1)
    w0.shadow_of_my_class(space)
    assert str(w0) == "a ProcessorScheduler" 
   
def test_special_classes0():
    image = get_image()
    w = image.special(constants.SO_BITMAP_CLASS)
    assert str(w) == "Bitmap class" 
    w = image.special(constants.SO_SMALLINTEGER_CLASS)
    assert str(w) == "SmallInteger class" 
    w = image.special(constants.SO_STRING_CLASS)
    assert str(w) == "String class" 
    w = image.special(constants.SO_ARRAY_CLASS)
    assert str(w) == "Array class" 
    w = image.special(constants.SO_FLOAT_CLASS)
    assert str(w) == "Float class" 
    w = image.special(constants.SO_METHODCONTEXT_CLASS)
    assert str(w) == "MethodContext class" 
    w = image.special(constants.SO_BLOCKCONTEXT_CLASS)
    assert str(w) == "BlockContext class" 
    w = image.special(constants.SO_POINT_CLASS)
    assert str(w) == "Point class" 
    w = image.special(constants.SO_LARGEPOSITIVEINTEGER_CLASS)
    assert str(w) == "LargePositiveInteger class" 

    # to be continued

    """SO_SMALLTALK = 8
     SO_DISPLAY_CLASS = 14
    SO_MESSAGE_CLASS = 15
    SO_COMPILEDMETHOD_CLASS = 16
    SO_LOW_SPACE_SEMAPHORE = 17
    SO_SEMAPHORE_CLASS = 18
    SO_CHARACTER_CLASS = 19"""
    
def test_name_of_shadow_of_specials():
    image = get_image()
    w_doesnot = image.special(constants.SO_DOES_NOT_UNDERSTAND)
    assert repr(w_doesnot.shadow_of_my_class(space)) == "<ClassShadow Symbol>"
    assert repr(space.w_nil.shadow_of_my_class(space)) == "<ClassShadow UndefinedObject>"
    assert repr(space.w_minus_one.shadow_of_my_class(space)) == "<ClassShadow SmallInteger>"
    assert repr(space.w_zero.shadow_of_my_class(space)) == "<ClassShadow SmallInteger>"
    assert repr(space.w_one.shadow_of_my_class(space)) == "<ClassShadow SmallInteger>"
    assert repr(space.w_two.shadow_of_my_class(space)) == "<ClassShadow SmallInteger>"
    assert repr(space.w_true.shadow_of_my_class(space)) == "<ClassShadow True>"
    assert repr(space.w_false.shadow_of_my_class(space)) == "<ClassShadow False>"

def test_special_classes0():
    image = get_image()
    w = image.special(constants.SO_DOES_NOT_UNDERSTAND)
    assert str(w) == "doesNotUnderstand:"
    assert str(w.getclass(space)) == "Symbol class" # for some strange reason not a symbol
    
    
    """
    SO_DOES_NOT_UNDERSTAND = 20
    SO_CANNOT_RETURN = 21
    SO_PROCESS_SIGNALIGN_LOW_SPACE = 22 # the process that triggered the low space semaphore. mostly nil
    SO_SPECIAL_SELECTORS_ARRAY = 23
    SO_CHARACTER_TABLE_ARRAY = 24
    SO_MUST_BE_BOOLEAN = 25
    SO_BYTEARRAY_CLASS = 26
    SO_PROCESS_CLASS = 27
    SO_COMPACT_CLASSES_ARRAY = 28
    SO_DELAY_SEMAPHORE = 29
    SO_USER_INTERRUPT_SEMAPHORE = 30
    SO_FLOAT_ZERO = 31
    SO_LARGEPOSITIVEINTEGER_ZERO = 32
    SO_A_POINT = 33
    SO_CANNOT_INTERPRET = 34
    SO_A_METHODCONTEXT = 35 # deprecated in closure images
    SO_BLOCKCLOSURE_CLASS = 36 
    SO_A_BLOCKCONTEXT = 37 # deprecated in closure images
    SO_EXTERNAL_OBJECTS_ARRAY = 38
    SO_PSEUDOCONTEXT_CLASS = 39
    SO_TRANSLATEDMETHOD_CLASS = 40
    SO_FINALIZATION_SEMPAHORE = 41
    SO_LARGENEGATIVEINTEGER_CLASS = 42
    """



def test_lookup_abs_in_integer():
    for value in [10, -3, 0]:

        w_object = model.W_SmallInteger(value)
        w_res = interp.perform(w_object, "abs")
        assert w_res.value == abs(value)


def test_map_mirrors_to_classtable():
    w_compiledmethod_class = image.special(constants.SO_COMPILEDMETHOD_CLASS)
    assert w_compiledmethod_class.is_same_object(space.w_CompiledMethod)
    w_nil = image.special(constants.SO_NIL)
    assert w_nil.is_same_object(space.w_nil)
    w_true = image.special(constants.SO_TRUE)
    assert w_true.is_same_object(space.w_true)
    w_false = image.special(constants.SO_FALSE)
    assert w_false.is_same_object(space.w_false)
    
def test_runimage():
    py.test.skip("This method actually runs an image. Fails since no graphical primitives yet")
    from spyvm import wrapper
    ap = wrapper.ProcessWrapper(space, wrapper.scheduler(space).active_process())
    w_ctx = ap.suspended_context()
    ap.store_suspended_context(space.w_nil)

    interp = interpreter.Interpreter(space)
    interp.interpret_with_w_frame(w_ctx)

def test_compile_method():
    sourcecode = """fib 
                        ^self < 2 
                            ifTrue: [ 1 ] 
                            ifFalse: [ (self - 1) fib + (self - 2) fib ]"""
    perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))
    assert perform(w(10), "fib").is_same_object(w(89))


def w(any): 
    # XXX could put this on the space?
    if any is None:
        return space.w_nil
    if isinstance(any, str):
        # assume never have strings of length 1
        if len(any) == 1: 
            return space.wrap_chr(any)
        else:
            return space.wrap_string(any)
    if isinstance(any, bool):
        return space.wrap_bool(any)
    if isinstance(any, int):    
        return space.wrap_int(any)
    if isinstance(any, float):
        return space.wrap_float(any)
    else:
        raise Exception    

def test_become():
    sourcecode = """
    testBecome
      | p1 p2 a |
      p1 := 1@2.
      p2 := #(3 4 5).
      a := p1 -> p2.
      (1@2 = a key)        ifFalse: [^1].
      (#(3 4 5) = a value) ifFalse: [^2].
      (p1 -> p2 = a)       ifFalse: [^3].
      (p1 == a key)        ifFalse: [^4].
      (p2 == a value)      ifFalse: [^5].
      p1 become: p2.
      (1@2 = a value)      ifFalse: [^6].
      (3 = (a key at: 1))  ifFalse: [^7].
      (4 = (a key at: 2))  ifFalse: [^8].
      (5 = (a key at: 3))  ifFalse: [^9].
      (p1 -> p2 = a)       ifFalse: [^10].
      (p1 == a key)        ifFalse: [^11].
      (p2 == a value)      ifFalse: [^12].
  
      ^42"""
    perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))
    w_result = perform(w(10), "testBecome")
    assert space.unwrap_int(w_result) == 42
       
def perform(w_receiver, selector, *arguments_w):
    return interp.perform(w_receiver, selector, *arguments_w)


def test_step_forged_image():
    from spyvm import wrapper
    ap = wrapper.ProcessWrapper(space, wrapper.scheduler(space).active_process())
    s_ctx = ap.suspended_context().as_context_get_shadow(space)
    assert isinstance(s_ctx, shadow.MethodContextShadow)
    assert s_ctx.top().is_same_object(space.w_true)

def test_step_run_something():
    from spyvm.test import test_miniimage
    setup_module(test_miniimage, filename='running-something-mini.image')
    from spyvm import wrapper
    ap = wrapper.ProcessWrapper(space, wrapper.scheduler(space).active_process())
    w_ctx = ap.suspended_context()
    s_ctx = w_ctx.as_context_get_shadow(space)
    ap.store_suspended_context(space.w_nil)

    interp = interpreter.Interpreter(space)
    assert isinstance(s_ctx, shadow.MethodContextShadow)
    assert s_ctx.top().is_same_object(space.w_true)
    interp.step(s_ctx)
    interp.step(s_ctx)
    assert s_ctx.top().value == 1
    interp.step(s_ctx)
    assert s_ctx.top().value == 2
    interp.step(s_ctx)
    assert s_ctx.top().value == 3

def test_create_new_symbol():
    w_result = perform(w("someString"), "asSymbol")
    assert w_result is not None
    assert w_result.as_string() == "someString"
