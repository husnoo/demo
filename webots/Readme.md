# description of the worlds and controllers
## webots/worlds/01-simple-world.wbt
  - This simple world has a robot with tracks, camera, gps, accelerometer, gyroscope.
  - It was used to test paligemma as a vision AI and also some basic tests on webots
### webots/controllers/01_world_01_simple_controller/01_world_01_simple_controller.py
    - this is a simple controller with a VLMProxy where we can call an LLM with a picture from the camera and ask for location of the rubber duck and drive to it.
    - used paligemma2 on rita
    - ./run/run_paligemma_server.sh which runs src/paligemma/paligemma_server.py
    - this seems to be the version I tested last: google/paligemma-3b-mix-224 (instead of paligemma2)
 
### webots/controllers/01_world_02_simple_controller/01_world_02_simple_controller.py
    - This is a more basic test for the robot to just go forwards.
### webots/controllers/01_world_03_controller_gps_acc01_world_03_controller_gps_acc.py
    - This stores acceletometer, gps, gyro, gpsvel and plots them

## webots/worlds/02_calibrate_mujoco.wbt
  The aim of this world is to have a "realistic" track robot be driven from Mujoco - we need to calibrate the mujoco sim first
### webots/controllers/02_calibrate_mujoco_01_controller/02_calibrate_mujoco_01_controller.py
- simple controller for new world

### webots/controllers/02_calibrate_mujoco_01_controller/02_calibrate_mujoco_02_controller.py
- now we try to match a mujoco sim with the webots sim

### webots/controllers/02_calibrate_mujoco_01_controller/02_calibrate_mujoco_03_controller.py
- Now we add camera, object recognition and try to add same object in mujoco to match location (x,y,z) and drive to it














  
