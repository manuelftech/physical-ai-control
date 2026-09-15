import rclpy
from rclpy.node import Node
import mujoco
import time
import viser
from mjviser import ViserMujocoScene

class QuickTestNode(Node):
    def __init__(self):
        super().__init__('quick_test_node')
        self.model = mujoco.MjModel.from_xml_path('/ros2/third_party/unitree_mujoco/unitree_robots/g1/scene.xml')
        self.data = mujoco.MjData(self.model)
        self.get_logger().info('G1 Test Movement Active! Open http://localhost:8080 in your browser!')

def main(args=None):
    rclpy.init(args=args)
    node = QuickTestNode()
    
    # Initialize the Viser web server explicitly targeting port 8080
    server = viser.ViserServer(port=8080)
    scene = ViserMujocoScene(server, node.model, num_envs=1)
    
    while rclpy.ok():
        if node.data.time < 0.4:
            node.data.ctrl[:] = 3.0  
        else:
            node.data.ctrl[:] = 0.0  
        
        # Advance physics step
        mujoco.mj_step(node.model, node.data)
        
        # Update the visualizer web state
        scene.update_from_mjdata(node.data)
        
        time.sleep(node.model.opt.timestep)

    node.destroy_node()
    rclpy.shutdown()


