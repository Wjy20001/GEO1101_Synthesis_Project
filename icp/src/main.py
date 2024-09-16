import os
import open3d as o3d
import numpy as np
import laspy


def read_pc(filepath):
    print("start loading---")
    print("path", filepath)
    las = laspy.read(filepath)
    print(f"Loaded {filepath} with {len(las.points)} points.")
    return las


def las_to_o3d_point_cloud(las):
    """
    Convert laspy point cloud to Open3D point cloud.
    """
    points = np.vstack((las.x, las.y, las.z)).transpose().astype(np.float64)
    # colors = np.vstack((las.red, las.green, las.blue)).transpose() / 65535.0
    pcd = o3d.geometry.PointCloud()
    print("points", points[:3])
    print("shape", points.shape)

    np_points = np.random.rand(100, 3)
    print("shape:", np_points.shape)
    print("np points", np_points[:3])
    points2 = o3d.utility.Vector3dVector(points.astype(np.float32))
    points3 = o3d.utility.Vector3dVector(np_points)

    print("points2", points2)

    # pcd.points = o3d.utility.Vector3dVector(
    #     [
    #         [
    #             1,
    #             1,
    #             1,
    #         ],
    #         [
    #             2,
    #             2,
    #             2,
    #         ],
    #     ]
    # )
    # pcd.points = o3d.utility.Vector3dVector(points)
    print("eeeee")
    # pcd.colors = o3d.utility.Vector3dVector(colors)

    return pcd


def icp_registration(source, target, threshold, trans_init):
    reg_p2p = o3d.pipelines.registration.registration_icp(
        source,
        target,
        threshold,
        trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(),
    )
    return reg_p2p


def visualize_point_clouds(source, target):
    source.paint_uniform_color([1, 0, 0])  # Red for source
    target.paint_uniform_color([0, 1, 0])  # Green for target
    o3d.visualization.draw_geometries([source, target])


def preprocess_point_cloud(pcd, voxel_size):
    pcd_down = pcd.voxel_down_sample(voxel_size)
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size * 2, max_nn=30)
    )
    return pcd_down


def main():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(script_dir, "data/geolab_iphone_thinned.las")
    # target_path = os.path.join(script_dir, "data/geolab_iphone_thinned_clipped.las")
    source = las_to_o3d_point_cloud(read_pc(source_path))
    # target = las_to_o3d_point_cloud(read_pc(target_path))
    print("source---", source)
    print("here1111")
    # Visualize original point clouds
    visualize_point_clouds(source, target)
    print("hoge------")
    # Preprocess point clouds
    voxel_size = 0.05  # Adjust based on your data
    source_down = preprocess_point_cloud(source, voxel_size)
    target_down = preprocess_point_cloud(target, voxel_size)

    # Initial alignment - you might need to adjust this
    initial_transform = np.identity(4)

    # Perform ICP
    threshold = 0.02  # Adjust based on your data
    reg_result = icp_registration(
        source_down, target_down, threshold, initial_transform
    )

    # Apply transformation
    source_transformed = source.transform(reg_result.transformation)

    # Visualize result
    visualize_point_clouds(source_transformed, target)

    print(f"Transformation matrix:\n{reg_result.transformation}")
    print(f"Fitness: {reg_result.fitness}")
    print(f"Inlier RMSE: {reg_result.inlier_rmse}")


if __name__ == "__main__":
    main()
