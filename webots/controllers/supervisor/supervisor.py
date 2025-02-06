from controller import Supervisor
from controller import Robot, Receiver

#import pynng


supervisor = Supervisor()
robot_node = supervisor.getFromDef("robot")

if robot_node is None:
    print("Robot not found! Make sure to set the DEF name in Webots.")
    exit()

trans_field = robot_node.getField("translation")
rot_field = robot_node.getField("rotation")
timestep = int(supervisor.getBasicTimeStep())

print("supervisor here")

#rep = pynng.Rep0()
#rep.listen("tcp://127.0.0.1:5555")  # Bind to an address
#print("Server listening on port 5555...")

receiver = supervisor.getDevice("receiver")
receiver.enable(10)  # Enable receiver with a 10ms sampling period

while supervisor.step(timestep) != -1:
    #try:
    #    msg = rep.recv(block=False)
    #    print(f"Received: {msg.decode()}")
    #    response = f"Hello, {msg.decode()}!"
    #    rep.send(response.encode())  # Send response
    #except pynng.TryAgain:
    #    pass

    if receiver.getQueueLength() > 0:
        data = receiver.getData()
        print("Received:", data)
        receiver.nextPacket()
        
        position = trans_field.getSFVec3f()
        rotation = rot_field.getSFVec3f()
        print(f"Robot position: {position}, rotation={rotation}")
        new_position = [0.0, 0.0, 0.0]
        new_rotation = [0.0, 0.0, 1.0, -3.13]
        trans_field.setSFVec3f(new_position)
        rot_field.setSFRotation(new_rotation)
        
        supervisor.step(timestep )







