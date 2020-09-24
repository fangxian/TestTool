import multiprocessing
import time
import numpy as np
import matplotlib.pyplot as plt

def man(queue, shv, t):
    plt.figure()
    plt.ion()
    while t.value:
        if shv.value == 1:
            data = np.zeros(10000)
            queue.put(data)
            img = np.random.randint(1,100,size=100)
            plt.plot(img)
            plt.show()
            plt.pause(0.005)
            plt.clf()
            shv.value = 0
        time.sleep(0.01)
    plt.close()
def girl(queue, shv,t):
    while t.value:
        if shv.value == 0:
            data = queue.get()
            print(data)
            shv.value = 1
        time.sleep(0.01)
def test1():
    pass


if __name__ == "__main__":
    queue = multiprocessing.Queue()
    shv = multiprocessing.Value('i', 1)
    shvt =  multiprocessing.Value('i', 1)
    p1 = multiprocessing.Process(target=man, args=(queue, shv, shvt))
    p2 = multiprocessing.Process(target=girl,args=(queue, shv, shvt))
    p1.start()
    p2.start()
    time.sleep(10)
    shvt.value = 0
    p1.join()
    p2.join()