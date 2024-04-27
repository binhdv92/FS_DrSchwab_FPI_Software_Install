

import threading
import datetime
import keyboard

class ScreenKeeper(threading.Thread):

    def __init__(self,name = 'sk',increase=1):
        threading.Thread.__init__(self)
        self.can_run = threading.Event()
        self.can_run.set()

        self.thing_done = threading.Event()
        self.thing_done.set()        

        self.name = name
        self.tic =  datetime.datetime.now()
        self.timer= datetime.datetime.now()
        self.toc = datetime.datetime.now()
        self.threshold = datetime.timedelta(seconds=increase)
        self._stop = threading.Event()


    def pause(self):
        self.can_run.clear()
        self.thing_done.wait()
        print('ScreenKeeper paused')

    def resume(self):
        self.can_run.set()
        print('ScreenKeeper resumed')

    def printStatus(self):
        print(f'isEnable: {self.isEnable}')

    def run(self):
        self.tic = datetime.datetime.now()
        while True:
            self.can_run.wait()
            try:
                self.toc = datetime.datetime.now()
                self.timer = self.toc - self.tic
                if (self.timer > self.threshold):
                    self.tic = self.toc
                    keyboard.press_and_release('F15')
                    print(f'ScreenKeeper:{self.name}({self.threshold}): Press F15 @{self.toc}')
            finally:
                self.thing_done.set()
                
            

# screenKeeper = ScreenKeeper('sk1',3)
# screenKeeper.start()
# while True:
#     key = input()
#     if(key=='q'):
#         screenKeeper.pause()
#     elif(key=='s'):
#         screenKeeper.resume()
#     else:
#         pass