from movement_config import move_forward, move_backwards, move_left_up, move_left_down, move_right_up, move_right_down, stop_movement
import config

def add_gui_movement_buttons(viewer=None):
    # Add forward button
    forward_button = viewer._server.gui.add_button(config.FORWARD)
    forward_button.on_click(move_forward)

    # Add left up button
    left_button = viewer._server.gui.add_button(config.LEFT_UP)
    left_button.on_click(move_left_up)

    # Add right up button
    right_button = viewer._server.gui.add_button(config.RIGHT_UP)
    right_button.on_click(move_right_up)

    # Add left down button
    left_button = viewer._server.gui.add_button(config.LEFT_DOWN)
    left_button.on_click(move_left_down)

    # Add right down button
    right_button = viewer._server.gui.add_button(config.RIGHT_DOWN)
    right_button.on_click(move_right_down)

    # Add backwards button
    forward_button = viewer._server.gui.add_button(config.BACKWARDS)
    forward_button.on_click(move_backwards)

    # Add stop button
    stop_button = viewer._server.gui.add_button(config.STOP)
    stop_button.on_click(stop_movement)
    return viewer