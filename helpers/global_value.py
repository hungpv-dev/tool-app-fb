
import threading


global_theard_event = None
def get_global_theard_event():
    global global_theard_event 
    if global_theard_event is None:
        global_theard_event = threading.Event()
    return global_theard_event