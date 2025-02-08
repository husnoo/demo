# Simple usage
```
python display_camera.py
python
>>> from src.robot import Robot
>>> robot = Robot()
>>> robot.drive_forward(1.0)
>>> robot.drive_backward(1.0)
>>> robot.spin_cw(0.5)
>>> robot.spin_ccw(0.5)
>>> robot.stop()
```

# Running the end-to-end demo
```
nix-shell -p realvnc-vnc-viewer
vncviewer 192.168.0.23
cd ~/demo/devastator/

(base) nawal@raspberrypi:~/demo/devastator $ /usr/bin/pip install -U pynng
(base) nawal@raspberrypi:~/demo/devastator $ sudo apt-get install python3-msgpack

/usr/bin/python run_camera.py
/usr/bin/python run_ui.py
/usr/bin/python run_controller.py
/usr/bin/python run_display.py
/usr/bin/python run_motors.py


On rita:
/home/nawal/storage/demo/vlm/run_paligemma_server.sh
watch -n1 nvidia-smi

```

# Plan

- `run_camera.py`
  - in a loop,
    - get image from camera
    - send image to `/camera`

- `run_motors.py`
  - in a loop,
    - get control from `/motor_left` and `/motor_right`
    - set control values to motors
    - if no new controls in the last 0.5 seconds, stop for safety

- `run_ui.py`
  - simple loop to take inputs and publish user targets to `/target`
  - also displays any images from  `/camera_labelled`

- `run_controller.py`
  - takes text targets from `/target`
  - takes image from `/camera`
  - calls paligemma server for location information
  - publishes `/camera_labelled`
  - publishes `/motor_left` and `/motor_right`




# playground
```
nix-shell -p conda -p libglvnd -p libGLU -p mesa -p freeglut -p glxinfo
conda-shell
conda activate test_opencv
cd ~/data/demo/devastator/playground
```

- Figuring out pynng on mac:
```
python pubsub_recv.py
python pubsub_send.py
```



