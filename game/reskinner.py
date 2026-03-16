import random

class Reskinner():
    def __init__(self, context, list_objects, time_to_wait):
        print("Reskinner initialized with time to wait: ", time_to_wait)
        self.context = context

        # randomize the list of objects
        random.shuffle(list_objects)

        self.list_objects = list_objects
        self.time_to_wait = time_to_wait
        self.current_wait = 0
        if self.time_to_wait == 0:
            self.reskin_all()
        else:
            self.reskin(0)

        self.id_to_reskin = 0

        # for obj in self.list_objects:
        #     print("Reskinner object: ", obj.body)

    def reskin(self, i):
        # print("Reskinner called for object id: ", i)
        reskinned = None
        if i < len(self.list_objects) and self.list_objects[i] != None:
            # print("Reskinner toggling reskin for object: ", self.list_objects[i].body)
            self.list_objects[i].update_skin()
    
    def reskin_all(self):
        for i in range(len(self.list_objects)):
            self.reskin(i)
        self.id_to_reskin = len(self.list_objects)
            
    def update(self):
        # print("Reskinner updated in frame: ", self.context.current_frame)

        if len(self.list_objects) == 0:
            return

        if self.id_to_reskin < len(self.list_objects):
            self.current_wait += 1
            if self.current_wait >= self.time_to_wait:
                self.current_wait -= self.time_to_wait
                self.id_to_reskin += 1
                self.reskin(self.id_to_reskin)

        # print("Reskinner current_wait: ", self.current_wait)


    