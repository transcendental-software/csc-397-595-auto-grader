import os
import re
import subprocess
import sys
import unittest
import random

# Import the test cases from the specified file
from fw_testcases import test_cases

# Suppress stack trace printing when a test fails
sys.tracebacklimit = 0

class TestFW(unittest.TestCase):
    score = 0
    max_score = 0

    @classmethod
    def tearDownClass(cls):
        print(f"\n======================================\nFINAL SCORE: {cls.score} / {cls.max_score}\n======================================")

    def run_simulation(self, packet):
        """Helper method to run the FW simulation and parse the outputs."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        vvp_file = os.path.join(project_root, 'bin', 'fw.vvp')
        
        # Ensure the simulation executable exists before running
        if not os.path.exists(vvp_file):
            subprocess.run(['make', 'compile'], cwd=project_root, capture_output=True)
            
        # Format packet bytes as space-separated hex strings
        input_str = " ".join(f"{b:02x}" for b in packet) + "\n"
        result = subprocess.run(
            ['vvp', 'bin/fw.vvp'],
            input=input_str,
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        # Parse outputs using regex based on the fw_tb.v output format
        accept_match = re.search(r'accept\s+=\s+([01xXzZ])', result.stdout)
        drop_match = re.search(r'drop\s+=\s+([01xXzZ])', result.stdout)
        invalid_match = re.search(r'invalid\s+=\s+([01xXzZ])', result.stdout)
        
        if not all([accept_match, drop_match, invalid_match]):
            self.fail(f"Failed to parse simulation output for packet {input_str}:\n{result.stdout}")
            
        def safe_int(val_str):
            return int(val_str, 2) if val_str and all(c in '01' for c in val_str) else val_str

        return {
            'accept': safe_int(accept_match.group(1) if accept_match else None),
            'drop': safe_int(drop_match.group(1) if drop_match else None),
            'invalid': safe_int(invalid_match.group(1) if invalid_match else None)
        }

    def test_00_compilation(self):
        """Test that the FW RTL and testbench compile successfully."""
        print("\n--- Testing Compilation ---")
        op_score = 0
        total_points = 20
        TestFW.max_score += total_points
        try:
            # Determine the project root directory
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            
            # Clean any previous builds
            subprocess.run(['make', 'clean'], cwd=project_root, capture_output=True)
            
            # Run the compilation target 
            result = subprocess.run(
                ['make', 'compile-fw'],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            
            # Verify the command succeeded
            self.assertEqual(result.returncode, 0, f"\n[FAILED] Compilation failed:\n{result.stderr}\n{result.stdout}")
            
            # Verify the compiled executable was created
            vvp_file = os.path.join(project_root, 'bin', 'fw.vvp')
            self.assertTrue(os.path.exists(vvp_file), "\n[FAILED] Compiled bin/fw.vvp file not found.")
            
            TestFW.score += 20
            op_score += 20
            print(f"[OPERATION PASSED] Compilation - Scored {op_score}/{total_points} points.")
        except AssertionError as e:
            print(f"[OPERATION FAILED] Compilation - Scored {op_score}/{total_points} points.")
            raise e

    def test_01_firewall_scenarios(self):
        """Run 20 random tests: 1 from each of the 13 original scenarios + 7 random variations."""
        print("\n--- Testing Firewall Packet Scenarios ---")
        selected_tests = []
        remaining_tests = []
        
        # Group the 52 testcases into 13 chunks of 4
        # Pick exactly 1 random test from each chunk to satisfy the "13 original test scenarios" rule
        for i in range(13):
            chunk = test_cases[i*4 : i*4 + 4]
            chosen = random.choice(chunk)
            selected_tests.append(chosen)
            for t in chunk:
                if t != chosen:
                    remaining_tests.append(t)
                    
        # Pick 7 additional distinct random tests from the remaining pool
        selected_tests.extend(random.sample(remaining_tests, 7))
        
        # Shuffle so the test execution order is fully random
        random.shuffle(selected_tests)
        
        op_score = 0
        total_points = len(selected_tests) * 4 # 20 tests * 4 points = 80 points
        TestFW.max_score += total_points
        
        try:
            for idx, tc in enumerate(selected_tests):
                res = self.run_simulation(tc['packet'])
                
                for key in tc['expected']:
                    if res[key] != tc['expected'][key]:
                        packet_hex = " ".join(f"{b:02x}" for b in tc['packet'])
                        self.fail(f"\n[FAILED] Test {idx+1}: {tc['name']}\n"
                                  f"Packet: {packet_hex}\n"
                                  f"Mismatch in '{key}': Expected {tc['expected'][key]} but received {res[key]}")
                
                op_score += 4
                TestFW.score += 4
                
            print(f"[OPERATION PASSED] Packet Filtering - Scored {op_score}/{total_points} points.")
        except AssertionError as e:
            print(f"[OPERATION FAILED] Packet Filtering - Scored {op_score}/{total_points} points.")
            raise e

if __name__ == '__main__':
    unittest.main()