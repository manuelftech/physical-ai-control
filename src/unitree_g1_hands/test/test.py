from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_
from unitree_sdk2py.core.channel import ChannelSubscriber
import time

def low_state_callback(msg: LowState_):
    # Print the positions of the first few joints/actuators
    print("Step 6: low_state_callback")
    print(f"Motor 0 Position: {msg.motor_state[0].q}")
    print("Step 7: Motor")

if __name__ == "__main__":
    print("Step 1: Initializing")
    # Initialize using the same network interface you configured
    ChannelFactoryInitialize(1, "lo") 
    print("Step 2: Validation")
    
    # Subscribe to the simulation's low-level state topic
    sub = ChannelSubscriber("rt/lowstate_g1", LowState_)
    print("Step 3: sub")
    sub.Init(low_state_callback, 10)
    print("Step 4: callback")
    
    while True:
        print("Step 5: sleep")
        time.sleep(1)