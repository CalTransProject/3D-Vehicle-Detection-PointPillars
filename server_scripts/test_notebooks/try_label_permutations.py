import os
import time
import shutil
import itertools
import subprocess
from pathlib import Path
import numpy as np
from typing import List, Tuple

class LabelPermutationTester:
    def __init__(self, 
                 source_label_dir: str,
                 working_dir: str,
                 ground_truth_dir: str,
                 data_creation_command: str,
                 training_command: str):
        self.source_label_dir = Path(source_label_dir)
        self.working_dir = Path(working_dir)
        self.test_label_dir = self.working_dir / "label_2"
        self.ground_truth_dir = ground_truth_dir
        self.data_creation_command = data_creation_command
        self.training_command = training_command
        self.results_file = Path("permutation_results_kitti.txt")
        self.current_attempt = 0
        
    def setup_workspace(self):
            """Create working directory and results file"""
            self.working_dir.mkdir(exist_ok=True)
            self.test_label_dir.mkdir(exist_ok=True)

            if not self.results_file.exists():
                with open(self.results_file, 'w') as f:
                    f.write("KITTI Label Index Permutation Testing Results\n")
                    f.write("=======================================\n")

    def get_label_files(self) -> List[Path]:
        """Get all .txt label files from source directory"""
        return list(self.source_label_dir.glob("*.txt"))

    def parse_kitti_line(self, line: str) -> List[str]:
        """Parse a KITTI label line into its components"""
        return line.strip().split()

    def generate_index_permutations(self) -> List[List[int]]:
        """Generate permutations of indices 8-14 while keeping other indices fixed"""
        # Indices 8-14 represent: h, w, l, x, y, z, yaw
        dimension_indices = [8, 9, 10]  # h, w, l
        position_indices = [11, 12, 13]  # x, y, z
        yaw_index = 14

        perms = []
        # Generate permutations of dimension indices
        for dim_perm in itertools.permutations(dimension_indices):
            # Generate permutations of position indices
            for pos_perm in itertools.permutations(position_indices):
                # Create full index mapping
                base_mapping = list(range(8))  # Keep first 8 indices as is
                base_mapping.extend(dim_perm)  # Add dimension permutation
                base_mapping.extend(pos_perm)  # Add position permutation
                base_mapping.append(yaw_index)  # Add yaw at the end

                perms.append(base_mapping)

                # Add version with negated y coordinate
                neg_mapping = base_mapping.copy()
                # Get former y position
                former_y_index = neg_mapping.index(12)
                neg_mapping[former_y_index] = -neg_mapping[former_y_index]  # Negative index indicates negation
                perms.append(neg_mapping)

                # Add version with negated yaw
                neg_yaw_mapping = base_mapping.copy()
                neg_yaw_mapping[14] = -neg_yaw_mapping[14]  # Negative index indicates negation
                perms.append(neg_yaw_mapping)

                # Add version with both negated
                both_neg_mapping = base_mapping.copy()
                both_neg_mapping[former_y_index] = neg_mapping[former_y_index]
                both_neg_mapping[14] = neg_yaw_mapping[14]
                perms.append(both_neg_mapping)

        return perms

    def apply_index_permutation(self, line_parts: List[str], index_mapping: List[int]) -> str:
        """Apply an index permutation to a KITTI label line"""
        result = line_parts[:8].copy()  # Keep first 8 values unchanged
        line_parts[2] = int(line_parts[2])

        # Apply the permutation for indices 8-15
        for i, idx in enumerate(index_mapping[8:], start=8):
            abs_idx = abs(idx)
            value = float(line_parts[abs_idx])
            if idx < 0:  # Negative index indicates we should negate the value
                value = -value
            # Special handling for index 2 which must remain an integer
            result.append(str(int(value)) if i == 2 else f"{value:.2f}")

        return " ".join(result)

    def create_test_labels(self, index_mapping: List[int]) -> None:
        """Create a new set of label files with the given index permutation"""
        self.test_label_dir.mkdir(exist_ok=True)

        for label_file in self.get_label_files():
            new_lines = []
            with open(label_file, 'r') as f:
                for line in f:
                    line_parts = self.parse_kitti_line(line)
                    new_line = self.apply_index_permutation(line_parts, index_mapping)
                    new_lines.append(new_line + "\n")

            new_file = self.test_label_dir / label_file.name
            with open(new_file, 'w') as f:
                f.writelines(new_lines)
                          
    def print_file_comparison(self, original_dir: Path, new_dir: Path, filename: str):
        original_file = Path(original_dir, filename)
        new_file = Path(new_dir, filename)
        
        with open(self.results_file, 'a') as results_file:   
            print(f"\nOriginal file ({original_file.name}):")
            results_file.write(f"\nOriginal file ({original_file.name}):")
            with open(original_file, 'r') as f:
                for i, line in enumerate(f, 1):
                    print(f"Line {i}: {line.strip()}")
                    results_file.write(f"\nLine {i}: {line.strip()}")

            print(f"\nNew file ({new_file.name}):")
            results_file.write(f"\nNew file ({new_file.name}):")
            with open(new_file, 'r') as f:
                for i, line in enumerate(f, 1):
                    print(f"Line {i}: {line.strip()}")
                    results_file.write(f"\nLine {i}: {line.strip()}")
                
    def test_permutation(self, index_mapping: List[int]) -> bool:
        """Test a single index permutation"""
        self.current_attempt += 1
        print(f"\nTesting permutation {self.current_attempt}")
        print(f"Index mapping: {index_mapping[8:]}")  # Only show relevant indices

        try:
            # Create new label files with this permutation
            self.create_test_labels(index_mapping)
            
            # Run data creation command command
            creation_result = subprocess.run(
                self.data_creation_command,
                shell=True,
                capture_output=True,
                text=True
            )
            
            creation_success = creation_result.returncode == 0
            
            # Log the result
            with open(self.results_file, 'a') as f:
                f.write(f"\nAttempt {self.current_attempt}\n")
                f.write(f"Index mapping: {index_mapping[8:]}\n")
                
            # Sanity check
            self.print_file_comparison(self.source_label_dir, self.test_label_dir, '000036.txt')
            
            # Analyze ground truth .bin files
            if hasattr(self, 'ground_truth_dir'):
                bin_files = list(Path(self.ground_truth_dir).glob('*.bin'))
                non_empty_files = []
                total_size = 0

                with open(self.results_file, 'a') as f:
                    f.write("\nGround Truth Analysis:\n")
                    f.write(f"Total .bin files found: {len(bin_files)}\n")

                    for bin_file in bin_files:
                        size = bin_file.stat().st_size
                        total_size += size
                        if size > 0:
                            non_empty_files.append(bin_file.name)

                    f.write(f"Non-empty files: {len(non_empty_files)} out of {len(bin_files)}\n")
                    f.write(f"Total size of all files: {total_size/1024:.2f} KB\n")
#                     f.write("Non-empty files:\n")
#                     for file in non_empty_files:
#                         f.write(f"  - {file}\n")
#                     f.write("\n")
            
            with open(self.results_file, 'a') as f:
                f.write(f"\n\nData creation Success: {creation_success}\n")
                if not creation_success:
                    f.write(f"\nError: {creation_result.stderr}\n")
#                 f.write("-" * 50 + "\n")

            # See how many ground truths are not empty
            # See what the total size is
            
            # Run training command
            training_result = subprocess.run(
                self.training_command,
                shell=True,
                capture_output=True,
                text=True
            )

            training_success = training_result.returncode == 0

            # Log the result
            with open(self.results_file, 'a') as f:
#                 f.write(f"\nAttempt {self.current_attempt}\n")
#                 f.write(f"Index mapping: {index_mapping[8:]}\n")
                f.write(f"Training Success: {training_success}\n")
                if not training_success:
                    f.write(f"Error: {training_result.stderr}\n")
                f.write("-" * 50 + "\n")

            return creation_success and training_success

        except Exception as e:
            with open(self.results_file, 'a') as f:
                f.write(f"\nAttempt {self.current_attempt}\n")
                f.write(f"Index mapping: {index_mapping[8:]}\n")
                f.write(f"Error: {str(e)}\n")
                f.write("-" * 50 + "\n")
            return False
        finally:
            # Clean up test labels
            if self.test_label_dir.exists():
                shutil.rmtree(self.test_label_dir)

    def run_permutation_tests(self):
        """Main method to run all index permutation tests"""
        self.setup_workspace()

        # Generate all index permutations
        index_permutations = self.generate_index_permutations()

        print(f"Generated {len(index_permutations)} permutations to test")
        for index_mapping in index_permutations:
            if self.test_permutation(index_mapping):
                print(f"\nSuccess! Found working index mapping: {index_mapping[8:]}")
                return True

        print("\nNo successful permutations found")
        with open(self.results_file, 'a') as f:
            f.write("*" * 50 + "\n")
        return False

# Example usage
if __name__ == "__main__":
    # Configuration
    SOURCE_LABELS = "../../../mmdetection3d/data/st_kitti_unfiltered_orig/training/label_2"
    WORKING_DIR = "../../../mmdetection3d/data/st_kitti_unfiltered/training"
    DATA_CREATION_COMMAND = "python ../../../mmdetection3d/tools/create_data.py kitti --root-path ../../../mmdetection3d/data/st_kitti_unfiltered --out-dir ../../../mmdetection3d/data/st_kitti_unfiltered --extra-tag st_kitti_unfiltered"
    TRAINING_COMMAND = "python ../../../mmdetection3d/tools/train.py ../../../mmdetection3d/configs/pointpillars/pointpillars_hv_secfpn_8xb6-160e_kitti-3d-3class_unfiltered.py"
    
    
    # Try running from inside mmdetection3d
    SOURCE_LABELS = "./data/st_kitti_unfiltered_orig/training/label_2"
    WORKING_DIR = "./data/st_kitti_unfiltered/training"
    GROUND_TRUTH_DIR = './data/st_kitti_unfiltered/st_kitti_unfiltered_gt_database'
    DATA_CREATION_COMMAND = "python ./tools/create_data.py kitti --root-path ./data/st_kitti_unfiltered --out-dir ./data/st_kitti_unfiltered --extra-tag st_kitti_unfiltered"
    TRAINING_COMMAND = "python ./tools/train.py ./configs/pointpillars/pointpillars_hv_secfpn_8xb6-160e_kitti-3d-3class_unfiltered.py"
    
    # Try running from inside mmdetection3d
    SOURCE_LABELS = "./data/arcs/training/label_2_orig"
    WORKING_DIR = "./data/arcs/training"
    GROUND_TRUTH_DIR = './data/arcs/arcs_gt_database'
    DATA_CREATION_COMMAND = "python ./tools/create_data.py kitti --root-path ./data/arcs --out-dir ./data/arcs --extra-tag arcs"
    TRAINING_COMMAND = "python ./tools/train.py ./configs/pointpillars/pointpillars_hv_secfpn_8xb6-160e_kitti-3d-3class_on_arcs.py"

    # Try running from inside mmdetection3d
    SOURCE_LABELS = "./data/arcs/training/label_2_orig"
    WORKING_DIR = "./data/arcs/training"
    GROUND_TRUTH_DIR = './data/arcs/arcs_gt_database'
    DATA_CREATION_COMMAND = "python ./tools/create_data.py kitti --root-path ./data/arcs --out-dir ./data/arcs --extra-tag arcs"
    TRAINING_COMMAND = "python ./tools/train.py ./configs/pointpillars/pointpillars_hv_secfpn_8xb6-160e_kitti-3d-3class_mod_0.py"


    # Create and run tester
    tester = LabelPermutationTester(
        source_label_dir=SOURCE_LABELS,
        working_dir=WORKING_DIR,
        ground_truth_dir=GROUND_TRUTH_DIR,
        data_creation_command=DATA_CREATION_COMMAND,
        training_command=TRAINING_COMMAND
    )
    
    tester.run_permutation_tests()