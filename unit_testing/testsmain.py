from unit_testing import databasetest, framecapturetest, configtest

print(f"Database tests:{databasetest.run_all_tests()}")
print(f"Configs tests:{configtest.run_all_tests()}")
print(f"Frame capture tests:{framecapturetest.run_all_tests()}")
