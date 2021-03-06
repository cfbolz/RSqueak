import py, math
from spyvm import model, constants, storage_contexts, wrapper, primitives, interpreter, error
from .util import read_image, open_reader, copy_to_module, cleanup_module, TestInterpreter, slow_test, very_slow_test

pytestmark = slow_test

def setup_module():
    space, interp, _, _ = read_image("mini.image")
    w = space.w
    def perform_wrapper(receiver, selector, *args):
        w_selector = None if isinstance(selector, str) else selector
        return interp.perform(receiver, selector, w_selector, list(args))
    perform = perform_wrapper
    copy_to_module(locals(), __name__)

def teardown_module():
    cleanup_module(__name__)

# ------ tests ------------------------------------------

def test_load_image():
    pass

@very_slow_test
def test_compile_method():
    sourcecode = """fib
                        ^self < 2
                            ifTrue: [ 1 ]
                            ifFalse: [ (self - 1) fib + (self - 2) fib ]"""
    perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))
    assert perform(w(10), "fib").is_same_object(w(89))

@very_slow_test
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

def test_cached_methoddict():
    sourcecode = """fib
                        ^self < 2
                            ifTrue: [ 1 ]
                            ifFalse: [ ((self - 1) fib + (self - 2) fib) + 1 ]"""
    perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))
    assert perform(w(5), "fib").is_same_object(w(15))
    sourcecode = """fib
                        ^self < 2
                            ifTrue: [ 1 ]
                            ifFalse: [ (self - 1) fib + (self - 2) fib ]"""
    perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))
    assert perform(w(10), "fib").is_same_object(w(89))

def test_compiling_float():
    sourcecode = """aFloat
                        ^ 1.1"""
    perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))
    w_result = perform(w(10), "aFloat")
    assert isinstance(w_result, model.W_Float)
    assert w_result.value == 1.1

def test_compiling_large_positive_integer():
    sourcecode = """aLargeInteger
                        ^ 16rFFFFFFFF"""
    perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))
    w_result = perform(w(10), "aLargeInteger")
    assert isinstance(w_result, model.W_LargePositiveInteger1Word)


def test_simulate_numericprim():
    sourcecode = """absentPrimitive: anInt with: anotherInt
        <primitive: 97>
        ^'numeric fallback for ', anInt asString, ' ', anotherInt asString"""
    perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))

    sourcecode = """simulatePrimitive: aPrimitive args: args
        ^'numeric simulation for ', args first asString, ' ', args second asString"""
    w_sim = perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))

    # XXX the lookup for that selector is static so the simulation lookup would be failing
    interp.image.w_simulatePrimitive = w_sim

    w_result = perform(w(10), "absentPrimitive:with:", w(3), w(4))
    assert isinstance(w_result, model.W_BytesObject)
    assert w_result.unwrap_string(space) == 'numeric simulation for 3 4'

def test_simulate_numericprim_fallback():
    sourcecode = """absentPrimitive: anInt with: anotherInt
        |errorCode|
        <primitive: 97> "error: errorCode> is not implemented in the mini.image yet"
        ^'numeric fallback for ', anInt asString, ' ', anotherInt asString, ' because of ', errorCode asString"""
    perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))

    sourcecode = """metaPrimFailed: errorCode
        <primitive: 255>"""
    perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))

    sourcecode = """simulatePrimitive: aPrimitive args: args
        ^self metaPrimFailed: 123"""
    w_sim = perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))

    # XXX the lookup for that selector is static so the simulation lookup would be failing
    interp.image.w_simulatePrimitive = w_sim

    w_result = perform(w(10), "absentPrimitive:with:", w(3), w(4))
    assert isinstance(w_result, model.W_BytesObject)
    assert w_result.unwrap_string(space) == 'numeric fallback for 3 4 because of 123'

def test_simulate_externalcall():
    sourcecode = """absentPrimitive: anInt with: anotherInt
        | externalCallTarget |
        "do not use <primitive: 'primitiveSimulation' module: 'MyPlugin'> as mini.image doesn't have that yet"
        <primitive: 117>
        externalCallTarget := #(MyPlugin primitiveSimulation).
        ^'externalcall fallback for ', anInt asString, ' ', anotherInt asString"""
    perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))
    sourcecode = """simulatePrimitive: aPrimitive args: args
        ^'externalcall simulation for ', args first asString, ' ', args second asString"""
    w_sim = perform(w(10).getclass(space), "compile:classified:notifying:", w(sourcecode), w('pypy'), w(None))

    # XXX the lookup for that selector is static so the simulation lookup would be failing
    interp.image.w_simulatePrimitive = w_sim

    w_result = perform(w(10), "absentPrimitive:with:", w(3), w(4))
    assert isinstance(w_result, model.W_BytesObject)
    assert w_result.unwrap_string(space) == 'externalcall simulation for 3 4'