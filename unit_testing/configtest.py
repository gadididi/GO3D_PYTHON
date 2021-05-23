from src.infra import config


def run_all_tests():
    test_score = 0
    test_cases = 0

    # init configs
    config.load_configs_for_tests()

    # Rendering distance test:
    test_cases += 1
    original_render_distance = config.get_float("LIDAR", "lidar.render.distance")
    config.set_value("LIDAR", "lidar.render.distance", "2.0")

    if config.get_float("LIDAR", "lidar.render.distance") == 2.0:
        test_score += 1
    else:
        print("Rendering test has failed")

    config.set_value("LIDAR", "lidar.render.distance", str(original_render_distance))

    # Screen columns test:
    test_cases += 1
    original_cols = config.get_integer('LIDAR', 'lidar.cols')
    config.set_value("LIDAR", "lidar.cols", "100")

    if config.get_integer("LIDAR", 'lidar.cols') == 100:
        test_score += 1
    else:
        print("Screen columns test has failed")

    config.set_value("LIDAR", 'lidar.cols', str(original_cols))

    if test_cases - test_score == 0:
        return True
    return False
