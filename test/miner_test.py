import os
import re
import subprocess
import time
import select
import sys
import unittest
import random

# Suppress stack trace printing when a test fails
sys.tracebacklimit = 0

def simple_hash(d0, d1, d2, d3, nonce):
    """Python implementation of the simple_hash function used in the C code."""
    # XOR data and nonce
    h = d0 ^ d1 ^ d2 ^ d3 ^ nonce
    h &= 0xFFFFFFFF
    
    # Circular left shift by 7 bits
    h = ((h << 7) & 0xFFFFFFFF) | (h >> 25)
    
    # Add magic constant (simulating 32-bit overflow)
    h = (h + 0xDEADBEEF) & 0xFFFFFFFF
    
    # XOR with right-shifted nonce
    h = h ^ (nonce >> 1)
    
    return h

class TestMiner(unittest.TestCase):
    score = 0
    max_score = 0

    @classmethod
    def tearDownClass(cls):
        print(f"\n======================================\nFINAL SCORE: {cls.score} / {cls.max_score}\n======================================")

    def _interact_with_sim(self, cmd, cwd, input_str):
        """Handles interacting with the simulation via standard I/O streams with a timeout."""
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            text=False
        )
        
        try:
            start_time = time.time()
            timeout = 5400 # 90 minutes
            output_data = ""
            prompt_found = False
            
            while True:
                if time.time() - start_time > timeout:
                    self.fail("Simulation timed out after 60 minutes.")
                    
                # Wait for output data to become available
                ready, _, _ = select.select([proc.stdout], [], [], 1.0)
                if ready:
                    try:
                        chunk = os.read(proc.stdout.fileno(), 4096).decode('utf-8', errors='replace')
                    except OSError:
                        break
                        
                    if not chunk:
                        break # Reached EOF
                        
                    output_data += chunk
                    
                    # Wait for the input prompt before sending data
                    if not prompt_found and "Enter mode (sw or hw) and data (d0 d1 d2 d3 target) separated by spaces:" in output_data:
                        prompt_found = True
                        proc.stdin.write(input_str.encode('utf-8'))
                        proc.stdin.flush()
                        
                    # Stop reading upon completion and terminate gracefully
                    if prompt_found and "Processing complete!" in output_data:
                        break
        finally:
            proc.terminate()
            proc.wait()
            if proc.stdin:
                proc.stdin.close()
            if proc.stdout:
                proc.stdout.close()
            
        return output_data

    def run_simulation(self, mode, d0, d1, d2, d3, target):
        """Helper method to run the make sim simulation and parse the outputs."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # Format inputs space-separated (scanf expects hex strings without 0x prefix for %x)
        input_str = f"{mode} {d0:x} {d1:x} {d2:x} {d3:x} {target:x}\n"
        
        output_data = self._interact_with_sim(['make', 'sim'], project_root, input_str)
        
        # Parse output using regex based on main.c printf statements
        mode_upper = mode.upper()
        result_match = re.search(rf'{mode_upper} Mining Result:\s+0x([0-9a-fA-F]+)', output_data)
        exec_match = re.search(r'Execution Time:\s+(\d+)\s+cycles', output_data)
        
        if not result_match:
            self.fail(f"Failed to parse simulation output for inputs: '{input_str.strip()}'\n\nSimulation Output:\n{output_data}")
            
        return {
            'nonce': int(result_match.group(1), 16),
            'cycles': int(exec_match.group(1)) if exec_match else None,
            'raw_stdout': output_data
        }

    def test_00_compilation(self):
        """Test that the application compiles successfully."""
        print("\n--- Testing Compilation ---")
        op_score = 0
        total_points = 0
        TestMiner.max_score += total_points
        try:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            
            # Clean any previous builds
            subprocess.run(['make', 'clean'], cwd=project_root, capture_output=True)
            
            # Run the compilation target 
            result = subprocess.run(
                ['make', 'compile'],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            
            # Verify the command succeeded
            self.assertEqual(result.returncode, 0, f"\n[FAILED] Compilation failed:\n{result.stderr}\n{result.stdout}")
            
            TestMiner.score += 0
            op_score += 0
            print(f"[OPERATION PASSED] Compilation - Scored {op_score}/{total_points} points.")
        except AssertionError as e:
            print(f"[OPERATION FAILED] Compilation - Scored {op_score}/{total_points} points.")
            raise e

    def execute_miner_tests(self, mode):
        """Runs 5 random tests for the given mining mode with increasing difficulty."""
        print(f"\n--- Testing {mode.upper()} Miner ---")
        op_score = 0
        total_points = 50 # 5 tests * 10 points
        TestMiner.max_score += total_points
        
        # Increasing order of difficulty (Target gets smaller)
        # Expected hit probabilities per nonce attempt: 1/2, 1/4, 1/16, 1/64, 1/256
        targets = [0x7FFFFFFF, 0x3FFFFFFF, 0x0FFFFFFF, 0x03FFFFFF, 0x00FFFFFF]
        
        try:
            for idx, target in enumerate(targets):
                # Randomly generate 32-bit data inputs
                d0 = random.randint(0, 0xFFFFFFFF)
                d1 = random.randint(0, 0xFFFFFFFF)
                d2 = random.randint(0, 0xFFFFFFFF)
                d3 = random.randint(0, 0xFFFFFFFF)
                
                res = self.run_simulation(mode, d0, d1, d2, d3, target)
                nonce = res['nonce']
                
                # Compute the expected nonce deterministically
                expected_nonce = 0
                while simple_hash(d0, d1, d2, d3, expected_nonce) > target:
                    expected_nonce += 1

                # Dynamically calculate the resulting hash using our Python model
                hash_val = simple_hash(d0, d1, d2, d3, nonce)
                
                if nonce != expected_nonce:
                    self.fail(f"\n[FAILED] {mode.upper()} Test {idx+1}\n"
                              f"Inputs: d0={d0:#010x}, d1={d1:#010x}, d2={d2:#010x}, d3={d3:#010x}, target={target:#010x}\n"
                              f"Returned Nonce: {nonce:#010x}\n"
                              f"Expected Nonce: {expected_nonce:#010x}\n"
                              f"Cycles: {res['cycles']}\n"
                              f"Error: Returned Nonce does not match Expected Nonce")
                
                op_score += 10
                TestMiner.score += 10
                print(f"[PASSED] Test {idx+1} (Difficulty {idx+1}) - Inputs: d0={d0:#010x}, d1={d1:#010x}, d2={d2:#010x}, d3={d3:#010x}, target={target:#010x} | Nonce: {nonce:#010x} | Cycles: {res['cycles']}")
                
            print(f"[OPERATION PASSED] {mode.upper()} Mining - Scored {op_score}/{total_points} points.")
        except AssertionError as e:
            print(f"[OPERATION FAILED] {mode.upper()} Mining - Scored {op_score}/{total_points} points.")
            raise e

    def test_01_sw_miner(self):
        """Test the software implementation of the miner."""
        self.execute_miner_tests('sw')

    def test_02_hw_miner(self):
        """Test the hardware implementation of the miner."""
        self.execute_miner_tests('hw')

if __name__ == '__main__':
    unittest.main()
