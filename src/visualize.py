# -*-coding:utf-8-*-
"""
@Version: 1.0
@Date: 2021-10-27
"""
import numpy as np
import threading
import mayavi.mlab as mlab
import glob
import time
import argparse
from pathlib import Path

class Dataset(object):
    def __init__(self, data_path=None, ext=".bin"):
        self.samples = []
        if data_path is not None:
            data_path = Path(data_path)
            self.samples = glob.glob(str(data_path / f'*{ext}'))
            self.samples.sort()
    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        points = np.fromfile(self.samples[index], dtype=np.float32).reshape(-1, 4)
        pts = points[...,0:3]
        intensity = points[...,-1]
        return pts,intensity


def args_parse():
    argparser = argparse.ArgumentParser(description=" Using mayavi for point cloud visualization ")
    argparser.add_argument("--data_path", default="/media/zlin/T4/Datasets/KITTI/velodyne/sequences/00/velodyne",
                           help="data path for lidar point cloud files, e.g: xxx.bin")
    argparser.add_argument("--ext", default=".bin", help="data format: 000001.bin")
    args = argparser.parse_args()
    return args

def EventLoop(dataset:Dataset, interval=0.005):
    while True:
        for i in range(len(dataset)):
            time.sleep(interval)
            points,intensity = dataset[i]
            buf['pts'] = points
            buf['intensity'] = intensity

def main():
    args = args_parse()

    # create dataset
    dataset = Dataset(data_path=args.data_path,ext=args.ext)

    # create a mayavi figure
    fig = mlab.figure(size=(960, 540), bgcolor=(0.05, 0.05, 0.05))
    mlab.view(azimuth=-172.8,elevation=45.3,distance=72.3,focalpoint=np.array([0.,0.,0.]))

    vis = mlab.points3d(0, 0, 0, 0, mode='point', figure=fig)

    # multi thread
    interval = 0.005
    loopThread = threading.Thread(target=EventLoop,args=[dataset,interval], daemon=True)
    loopThread.start()

    # 10 <= delay <= 100,000
    @mlab.animate(delay=10)
    def anim():
        while True:
            vis.mlab_source.reset(
                x=buf['pts'][:, 0],
                y=buf['pts'][:, 1],
                z=buf['pts'][:, 2],
                scalars=buf['intensity'])
            # view_param = mlab.view()
            # print('view_param: ',view_param)
            yield

    # start visualisation loop in the main-thread, blocking other executions
    anim()
    mlab.show()

if __name__ == '__main__':
    # buffer for updating lidar points
    buf = {'pts': np.zeros((1, 3)), 'intensity': np.zeros(1)}
    main()
