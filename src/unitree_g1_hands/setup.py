import rclpy
from rclpy.node import Node
import mujoco
import mujoco.viewer
import time

class QuickTestNode(Node):
    def __init__(self):
        super().__init__('quick_test_node')
        # Load your Unitree G1 model file
        self.model = mujoco.MjModel.from_xml_path('/ros2/third_party/unitree_mujoco/unitree_robots/g1/scene.xml')
        self.data = mujoco.MjData(self.model)
        self.get_logger().info('G1 Test Movement Active! Watch your browser!')

def main(args=None):
    rclpy.init(args=args)
    node = QuickTestNode()
    
    # Opens the browser-linkable passive viewer window
    with mujoco.viewer.launch_passive(node.model, node.data) as viewer:
        while rclpy.ok() and viewer.is_running():
            
            # --- THE VISIBLE MOVEMENT JOLT ---
            # If the simulation has been running for less than 0.4 seconds,
            # slam a massive force command into the robot's arms/shoulders.
            if node.data.time < 0.4:
                node.data.ctrl[:] = 3.0  # Force actuators outward aggressively
            else:
                node.data.ctrl[:] = 0.0  # Relax motors and let it freefall
            
            # Step the physical engine forward and refresh browser UI
            mujoco.mj_step(node.model, node.data)
            viewer.sync()
            
            time.sleep(node.model.opt.timestep)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

