import os
import random
import numpy as np
import pandas as pd
from pathlib import Path



def point_is_in_an_roi_box(point, roi_box_list):
    # Extract the point coordinates
    x, y, z = point
    
    for bbox in roi_box_list:
        # Extract the box parameters
        # dz, dy, dx, cx, cy, cz, yaw = bbox
        cx, cy, cz, dx, dy, dz, yaw = bbox
        
        # Create the rotation matrix for the yaw angle
        cos_yaw = np.cos(-yaw)  # Negative for the inverse rotation
        sin_yaw = np.sin(-yaw)
        
        rotation_matrix = np.array([
            [cos_yaw, -sin_yaw, 0],
            [sin_yaw,  cos_yaw, 0],
            [0,       0,       1]
        ])
        
        # Translate the point to the box's coordinate frame
        translated_point = np.array([x - cx, y - cy, z - cz])
        
        # Rotate the point to align with the box
        rotated_point = rotation_matrix.dot(translated_point)
        
        # Check if the point is within the box dimensions
        half_lengths = [dz / 2, dy / 2, dx / 2]
        in_box = all([
            -half_lengths[i] <= rotated_point[i] <= half_lengths[i] for i in range(3)
        ])
    
        if in_box:
            return True
    
    return False


def get_roi_boxes(label_file):
    bboxes = []
    with open(label_file, 'r') as file:
        for line in file:
            parts = line.strip().split()
            bbox = [float(value) for value in parts[8:15]]  # Extract the bounding box dimensions and location            
            bboxes.append(bbox)
    return np.array(bboxes)


def is_label_point(point, label_file_path):
    list_roi_boxes = get_roi_boxes(label_file_path)
    if point_is_in_an_roi_box(point, list_roi_boxes):
        return True
    return False


def convert_to_dataframe(bin_path):
    pre_filtered_data = np.fromfile(bin_path, dtype=np.float32).reshape(-1, 4) 
    columns = ['x', 'y', 'z', 'intensity']
    df = pd.DataFrame(pre_filtered_data, columns=columns)
    return df


def get_frame_point_statistics(data_file_path, label_file_path):
    # Running totals
    total_points = 0
    label_points = 0

    points_df = convert_to_dataframe(data_file_path)
    
    # For each point in the data
    for index, row in points_df.iterrows():
    # for index, row in points_df.iloc[:100].iterrows():
        # Increment the total
        total_points += 1
        point = (row['x'], row['y'], row['z'])
        # If the point is a label point
        if is_label_point(point, label_file_path):
            # Increment the label total
            label_points += 1

    return total_points, label_points


def get_dataset_point_statistics(data_path, label_path, subset_size):
    # Running totals
    num_frames = 0
    total_num_points = 0
    total_num_label_points = 0
    
    # Get just the file names
    files = [f for f in os.listdir(data_path) if f.endswith('.bin')]

    # Get subset of files to check
    random.shuffle(files)
    total_files = len(files)
    subset_num = int(total_files * subset_size)
    
    # For each file
    for filename in files[:subset_num]:
        # Get file index
        file_id, extension = os.path.splitext(filename)
        print(file_id, end=' ')
        
        # Append file name to locations
        data_file_path = Path(data_path, filename)
        label_filename = file_id + '.txt'
        label_file_path = Path(label_path, label_filename)

        # Get the number of points, and the number of points inside the labels
        num_frame_points, num_frame_label_points = get_frame_point_statistics(data_file_path, label_file_path)
        # Add to running total
        num_frames += 1
        total_num_points += num_frame_points
        total_num_label_points += num_frame_label_points

    # return total_num_points / num_frames, total_num_label_points / num_frames
    return num_frames, total_num_points, total_num_label_points


def evaluate_filter(dir, dataset_name, subset_size=1):
    # Create directory path
    data_path = Path(BASE_DIR, dir)
    label_path = Path(BASE_DIR, ARCS_LABEL_DIR)

    # Get the dataset statistics
    num_frames, total_num_points, total_num_label_points = get_dataset_point_statistics(data_path, label_path, subset_size)

    results = {
        'dataset_name': dataset_name,
        'num_frames': num_frames,
        'total_num_points': total_num_points,
        'total_num_label_points': total_num_label_points,
        'total_num_non_label_points': total_num_points - total_num_label_points,
        'avg_frame_pts': total_num_points / num_frames,
        'avg_frame_label_pts': total_num_label_points / num_frames,
        'avg_frame_non_label_pts': (total_num_points - total_num_label_points) / num_frames
    }

    return results