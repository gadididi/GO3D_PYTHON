from take_frame.loadframe import load_frame
from take_frame.takeframe import FrameTaker
from unit_testing.framecapturetest import start_test

#FrameTaker(scan_name="test").start_stream()
#load_frame("test_0")

print(f"Frame taking and reloading test accuracy is: {start_test()}")
