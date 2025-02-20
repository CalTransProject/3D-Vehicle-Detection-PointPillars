# Repository Overview

Welcome to the PointPillars with Background Filtering repository. This collection is organized and and will be maintained by Rachel Gilyard. Below, you'll find descriptions of each file and directory to help you understand their purpose and usage. If you have questions or need assistance, feel free to reach out at **gilyardrachel.com**.

This repository is divided into two main sections:
- **scripts**: Primarily focused on preprocessing the raw data and creating the background map.  
- **server_scripts**: Responsible for filtering data, running object detection inference, and related evaluations.

To use these files, you will generally follow these steps:
1. **[Download the data](#data-download--setup)** from the project’s Google Drive.  
2. **[Preprocess the data and Create a background map](#preprocessing--background-filtering)** using the notebooks in the scripts folder.  
3. **[Run filtering and inference](#run-the-time-test-for-filtering--inference)** on the processed data (in server_scripts).  

You can find more details on each file’s function and setup below. **[Jump to File Descriptions](#directory-structure-and-file-descriptions)**

## Data Download & Setup

1. **Locate the Dataset in Google Drive**  
   Navigate to the Google Drive folder at:

   `3D Vehicle Detection for Real Time Traffic Monitoring > CS Group 2023-2024 > Data Collection 2023-2024 > Final Datasets for Complex YOLO > Zelzah and Plummer 10:45 Minutes - Complex YOLO`

2. **Download Required Data**  
   From this folder, download the following:
   - **Labels** (Ground-truth label files)
   - **2D Camera Images** (Needed if you plan to use or calibrate with camera data)  
   - **3D Camera Binary Data** (The LiDAR point clouds)

3. **Place the Data in the Repository**  
   - In the root directory of this repository, create a new folder named `data`.
   - Move or copy the downloaded files/folders into the `data` folder.
   - Change the file names:
      - "Labels" => "labels"
      - "2D Camera Images" => "images"
      - "3D Camera Binary Data" => "velodyne_points"
   - Your directory should look like:
     ```
     PointPillars_with_Background_Filtering/
     ├── data/
     │   ├── labels/
     │   ├── images/
     │   └── velodyne_points/
     ├── scripts/
     ├── server_scripts/
     └── ...other files and folders...
     ```
## Preprocessing & Background Filtering

The goal of this section is to preprocess the data so it’s compatible with the MMDetection3D library and then generate a background filter.

1. **Correct the Label Format**  
   - Open `correct_arcs_labels.ipynb`.  
   - Update the file paths if you’re on macOS or Linux (this script was written for Windows file paths).  
   - Run the notebook. It will convert the labels to the format expected by the library and provide visualizations to confirm that labels are accurately placed.

2. **Create the Background Filter & Filtered Velodyne Dataset**  
   - Open `filter_bg_arcs.ipynb`.  
   - Again, adjust the file paths for non-Windows systems if needed.  
   - This notebook accomplishes two main tasks:
     1. **Creates the Background Filter** that can be used for real-time filtering.  
     2. **Generates a new Velodyne dataset** containing only the filtered points (points that lie outside of the the labeled bounding boxes are removed).

## Run the Time Test for Filtering & Inference  
   - Open `filter_time_test_bin.ipynb`. (This was designed to run on Linux, so you may need to adjust the paths if you’re on a different platform.)  
   - Make sure you set:
     - `data_dir` to point to where your Velodyne frames are located (e.g., `data/velodyne_points`).
     - `background_map_path` to the path where your background map is stored (created in the previous step).
   - Run all cells in the notebook to generate speed test results.  
     - Note there are **two versions** of the speed tests in the notebook:
       - One that uses Numba
       - One that does not use Numba  
     - The second version (with Numba) demonstrates the speed improvement gained from background filtering.


## Transferring Files via SCP

If you need to move files (like the background filter or Velodyne files) between your local machine and a remote server, you can use `scp`. I would zip my velodyne files if before transferring. Here are some examples:

- **Copying a File from Local to Remote**  
  ```bash
  scp /path/to/local/file username@server_ip:/path/to/remote/directory
  ```
- **Copying a File from Remote to Local**  
  ```bash
  scp username@server_ip:/path/to/remote/file /path/to/local/directory
  ```


## Directory Structure and File Descriptions

There are other notebooks in the repository that may be useful. Here are some descriptions, but most of the notebooks are heavily commented as well.

### **scripts**
- **default_files**:  
  Has files for an early test of making a training dataset from the Zelzah and Plummer dataset. I tried to make placeholder calibration files. This did not work, but these files will still be used when making a test set with the current scripts.

- **exploratory_scripts**:  
  - `check_bin_file_dimensions.ipynb`: This goes through each file in the raw Zelzah and Plummer dataset (can be downloaded from the team Google Drive) and deletes any corrupted files, or any files associated with frames without labels.  
  - `find_label)area)arcs.ipynb`: This notebook goes through all of the labels from the Zelzah and Plummer dataset and finds out the area where the labels have been placed. This is used to restrict the evaluation of the filter and the evaluation of the PointPillars model on the Zelzah and Plummer dataset (i.e. points and predictions outside of this area are not considered in the evaluations).  
  - `find_sensor_movements.ipynb`: This notebook did not lead to anything. Delete.  
  - `object_count.ipynb`: This notebook counts all of the objects in the labels and makes a figure of the distribution of labels.  
  - `receive_packets_test.ipynb`: This notebook was meant to test receiving LiDAR packets via a port on my local machine (with a .pcap playback file sending them from the server). Possibly delete.  
  - `visualize_roi_arcs.ipynb`: This script was used to view the point clouds after different types of preprocessing to make sure the frames still looked intact. It was also used to compare the format of labels files.  
  - There are also various figure images in this directory.

- **figure_scripts**
  - `evaluate_filter.ipynb`: Counts how many points lie inside and outside of label bounding boxes. Can be used to compare the effectiveness of different filters.  
  - `gif_maker.ipynb`: Makes a gif out of an .mp4. Used for a presentation slide.  
  - `point_clouds_for_pillars_arch_fig.ipynb`: A notebook to make part of a figure. This figure needed a frame with and without labels. This can be safely deleted if it's not needed.

- **utils**
  - `filter_eval.py`: Contains functions to help evaluate the filters. I need to check if this is being used in the filter evaluation currently and delete unused functions there.

- Root-Level Files
  - `Untitled.ipynb`: Delete this.  
  - `calib_extractor.ipynb`: A notebook to extract correlated LiDAR and RGB video files to get calibration data using MATLAB's LiDAR-camera calibration tool (add link).  
  - `correct_arcs_labels.ipynb`: Goes through each Zelzah and Plummer labels and changes the yaw so they are in the format that the model expects.  
  - `create_eval_datasets.ipynb`: Copies files from their various folders and puts them into one evaluation dataset. This was used so a .zip file could be made of the corresponding datasets and secure copied to the server for further evaluation.  
  - `create_time_test_dataset.ipynb`: Convert files from x, y, z, intensity format, to azimuth, height distance format. I didn't end up using this- I for the time test in my thesis I get the azimuth angle in real time. But I may have used this to create test background maps.  
  - `filter_bg_arcs.ipynb`: This is a messy file that creates the background filter map and save background filtered point cloud frames. It contains a lot of trial and error code and functions that are not used anymore.  
  - `format_data_for_pointpillars.ipynb`: This notebook was an attempt to put the data into the format expected for MMDetection3D library. It read the number of files, and makes a randomly sampled train and test set, then copies the appropriate files to the file structure shown in the third cell.  
  - `label_filter_bg_arcs.ipynb`: This notebook makes a dataset of point cloud frames that only include the points that lie inside the ground truth boxes. This was used as a proof of concept dataset, and later for comparison with the background filtered dataset.  
  - `unfiltered_arcs_point_cound.ipynb`: This notebook went through each unfiltered frame and counted the number of points inside and outside of the labels. This was to make it faster to compare against the filtered data, as it takes a lot of time to see if a point is inside any ground truth box for a particular frame, and for each frame, around 50k points need to be considered. Since the number doesn't change for the unfiltered data, I did this count beforehand.

---

### **server_scripts**
- **figure_scripts**
  - `gif_images/`: This folder contains the images to be used for a gif of the recorded scene shown with point clouds and ground truth labels.  
  - `azimuth height binning.ipynb`: This notebook just generates an image illustrating the idea between azimuth height binning. (Also this should be renamed).  
  - `inference_gif_images.ipynb`: This notebook makes a gif of ground truth boxes in point clouds. It was intended to show the prediction boxes (hence the title), but I ran out of time.

- **test_notebooks**
  - `work_dirs/pointpillars_hv_secfpn_8xb6-160e_kitti-3d-3class_unfiltered`: Contains some files from the failed training attempts. These files are generated from the MMDetection3D library.  
  - `compare_point_cloud_files.ipynb`: This notebook was used to look at differences between KITTI dataset frames and the Zelzah and Plummer frames to see if I could find out why Zelzah and Plummer wasn't training. This problem is still not solved, but may have something to do with the missing calibration data.  
  - `make_test_pcap_file.ipynb`: This notebook takes a .pcap file, and returns a smaller .pcap file. This is because some libraries will read the entire pcap before proceeding, and this can take a long time, so it's helpful to have a smaller file to work with when testing and debugging.  
  - `test_velodyne_decoder.ipynb`: This file was used to test the velodyne_decoder library to see how it parsed .pcap data from the sensor.  
  - `try_label_permutations.py`: While trying to get the MMDetection3D PointPillars model to train on the Zelzah and Plummer dataset, I thought I would see if the problem could be that the labels were encoded differently than expected. So I tried to train on a bunch of different permutations of columns (interpreting the different columns as x, y, z, dx, dy, dz, and yaw). It was unsuccessful.

- Other Scripts
  - `arcs_inference_evaluation_test.ipynb`: This notebook was a test on how to use the MMDetection3D pre-trained model on the Zelzah and Plummer dataset. It was also used to test out IoU functions and to make figures showing the difference in sizes of the ground truth bounding boxes of the Zelzah and Plummer dataset and the KITTI dataset.  
  - `filter_time_tests_bin.ipynb`: This notebook was used to time the speed of the inference on unfiltered frames and the speed of the filtering functions and inference on the filtered frames. The speeds saved in the file are actually just the inference on the unfiltered frames, and just the filtering of the frames. I will run it again so it shows the correct data. Bin refers to this test being done on the saved binary files, rather than the .pcap files.  
  - `filter_time_tests_pcap.ipynb`: This notebook was an attempt to decode the .pcap data more manually, but it is mostly a failure. It may be useful for people to see what you can do with .pcap data.  
  - `filter_time_tests_pcap_test.ipynb`: Similar to above.  
  - `pcap_playback_test.ipynb`: This notebook reads and sends pcap data via port 2368 to simulate the incoming live sensor data from the Velodyne sensor.  
  - `pcap_receive_test.ipynb`: This notebook receives the .pcap playback from the notebook described above to simulate a program that can read the .pcap data in real time.  
  - `test_pointpillars_on_arcs.ipynb`: This notebook gets the inference results of the MMDetection3D pretrained pointpillars model on the Zelzah and Plummer unfiltered and filtered datasets.  
  - `view_bin.ipynb`: This notebook is a simple way to view a point cloud that has been saved in a binary file.

