"""
Stream Pupil gaze coordinate data using zmq to control a mouse with your eye. 
Please note that marker tracking must be enabled, and in this example we have named the surface "screen." 
You can name the surface what you like in Pupil capture and then write the name of the surface you'd like to use on line 17. 
"""
import zmq
from pymouse import PyMouse

#mouse setup
m = PyMouse()
x_dim, y_dim = m.screen_size()

#network setup
port = "5000"
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:"+port)
#filter by messages by stating string 'STRING'. '' receives all messages
socket.setsockopt(zmq.SUBSCRIBE, '')
smooth_x, smooth_y = 0.5, 0.5

# specify the name of the surface you want to use
surface_name = "screen"

while True:
    msg = socket.recv()
    items = msg.split("\n") 
    msg_type = items.pop(0)
    items = dict([i.split(':') for i in items[:-1] ])
    if msg_type == 'Gaze':
        try:
            gaze_on_screen = items["realtime gaze on "+surface_name]
            raw_x,raw_y = map(float,gaze_on_screen[1:-1].split(','))
            
            # smoothing out the gaze so the mouse has smoother movement
            smooth_x += 0.5 * (raw_x-smooth_x)
            smooth_y += 0.5 * (raw_y-smooth_y)

            x = smooth_x
            y = smooth_y

            y = 1-y # inverting y so it shows up correctly on screen
            x *= x_dim
            y *= y_dim
            # PyMouse or MacOS bugfix - can not go to extreme corners because of hot corners?
            x = min(x_dim-10, max(10,x))
            y = min(y_dim-10, max(10,y))

            m.move(x,y)
        except KeyError:
            pass
    else:
        # process non gaze position events from plugins here
        pass
