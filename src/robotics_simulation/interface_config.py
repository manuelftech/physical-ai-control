from movement_config import move_forward, move_backwards, move_left, move_right, stop_movement
import config

def add_gui_movement_buttons(viewer=None):
    # Add forward button
    forward_button = viewer._server.gui.add_button(config.UP)
    forward_button.on_click(move_forward)
    
    # Add left button
    left_button = viewer._server.gui.add_button(config.LEFT)
    left_button.on_click(move_left)

    # Add right button
    right_button = viewer._server.gui.add_button(config.RIGHT)
    right_button.on_click(move_right)

    # Add backwards button
    forward_button = viewer._server.gui.add_button(config.DOWN)
    forward_button.on_click(move_backwards)

    # Add stop button
    stop_button = viewer._server.gui.add_button(config.STOP)
    stop_button.on_click(stop_movement)
    return viewer