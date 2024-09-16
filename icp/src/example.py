import os
from pycpd import AffineRegistration, RigidRegistration
import numpy as np
import rerun as rr


def main(true_affine=True):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    fish_target = np.loadtxt(os.path.join(script_dir, "data/fish_target.txt"))
    X1 = np.zeros((fish_target.shape[0], fish_target.shape[1] + 1))
    X1[:, :-1] = fish_target
    X2 = np.ones((fish_target.shape[0], fish_target.shape[1] + 1))
    X2[:, :-1] = fish_target
    X = np.vstack((X1, X2))

    if true_affine is True:
        theta = np.pi / 6.0
        R = np.array(
            [
                [np.cos(theta), -np.sin(theta), 0],
                [np.sin(theta), np.cos(theta), 0],
                [0, 0, 1],
            ]
        )
        t = np.array([0.5, 1.0, 0.0])

        # Create shear matrix
        shear_matrix = [[1, 0, 0.5], [0, 1, 4], [0, 1, 1]]

        R = np.dot(R, shear_matrix)

        Y = np.dot(X, R) + t
    else:
        fish_source = np.loadtxt(os.path.join(script_dir, "data/fish_source.txt"))
        Y1 = np.zeros((fish_source.shape[0], fish_source.shape[1] + 1))
        Y1[:, :-1] = fish_source
        Y2 = np.ones((fish_source.shape[0], fish_source.shape[1] + 1))
        Y2[:, :-1] = fish_source
        Y = np.vstack((Y1, Y2))
    rr.init("rerun_ICP_pointCloud")
    rr.spawn()
    rr.log("source points", rr.Points3D(X, radii=0.05))
    rr.log("target points", rr.Points3D(Y, radii=0.05))

    affine = AffineRegistration(**{"X": X, "Y": Y})
    # reg = RigidRegistration(X=X, Y=Y)
    TY, reg = affine.register()
    rr.log("transformed", rr.Points3D(TY, radii=0.05))


if __name__ == "__main__":
    main(true_affine=True)
