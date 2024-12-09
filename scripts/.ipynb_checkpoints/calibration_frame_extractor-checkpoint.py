import cv2
import dpkt
import numpy as np
from pathlib import Path

class SyncExtractor:
    def __init__(self, video_path, pcap_path, video_sync_time, lidar_sync_time):
        """
        Initialize the synchronization extractor.
        
        Args:
            video_path (str): Path to the video file
            pcap_path (str): Path to the LiDAR PCAP file
            video_sync_time (float): Time in seconds when the sync event (clap) occurs in video
            lidar_sync_time (float): Time in seconds when the sync event (clap) occurs in LiDAR data
        """
        self.video_path = Path(video_path)
        self.pcap_path = Path(pcap_path)

def main():
    video_path = '../data/calibration_test/WIN_20241028_15_51_35_Pro_rachel_1_small.mp4.mp4'
    pcap_path = '../data/calibration_test/2024-10-28-15-51-37_Velodyne-VLP-32C-Data_rachel_1_small.pcap'

    save_dir = '../data/calibration_test'
    
    # Sync point (clap) times in each recording
    video_sync_time = 23.0
    lidar_sync_time = 11.48
    
    # Initialize extractor
    extractor = SyncExtractor(video_path, pcap_path, video_sync_time, lidar_sync_time)
    
    # Example timestamps where you want to extract frames (in seconds from video start)
    # For example, if you want frames at 2 seconds after the clap:
    timestamps = [27.0, 31.0]  # This would be 7.0 seconds into the video
    
    # Extract matched frames
    matched_frames = extractor.extract_frames(timestamps)
    
    # Process the matched frames
    for ts, frames in matched_frames.items():
        video_frame = frames['video_frame']
        lidar_frame = frames['lidar_frame']
        
        # Save or process the frames as needed
        cv2.imwrite(f"video_frame_{ts}.jpg", video_frame)
        # Save LiDAR frame in your preferred format
        
    extractor.cleanup()

if __name__ == "__main__":
    main()