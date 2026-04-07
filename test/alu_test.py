import os
import re
import subprocess
import unittest

class TestALU(unittest.TestCase):
    score = 0

    @classmethod
    def tearDownClass(cls):
        print(f"\n======================================\nFINAL SCORE: {cls.score}\n======================================")

    def run_simulation(self, op, a, b):
        """Helper method to run the ALU simulation and parse the outputs."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        vvp_file = os.path.join(project_root, 'bin', 'alu.vvp')
        
        # Ensure the simulation executable exists before running
        if not os.path.exists(vvp_file):
            subprocess.run(['make', 'compile-alu'], cwd=project_root, capture_output=True)
            
        input_str = f"{op:03b} {a:08b} {b:08b}\n"
        result = subprocess.run(
            ['vvp', 'bin/alu.vvp'],
            input=input_str,
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        # Parse outputs using regex
        out_match = re.search(r'out\s+=\s+8\'b([01xXzZ]{8})\s+\([^)]+\)', result.stdout)
        cout_match = re.search(r'cout\s+=\s+([01xXzZ])', result.stdout)
        zero_match = re.search(r'zero\s+=\s+([01xXzZ])', result.stdout)
        neg_match = re.search(r'neg\s+=\s+([01xXzZ])', result.stdout)
        overflow_match = re.search(r'overflow\s+=\s+([01xXzZ])', result.stdout)
        
        if not all([out_match, cout_match, zero_match, neg_match, overflow_match]):
            self.fail(f"Failed to parse simulation output for inputs op={op}, a={a}, b={b}:\n{result.stdout}")
            
        def safe_int(val_str):
            return int(val_str, 2) if all(c in '01' for c in val_str) else val_str

        return {
            'out': safe_int(out_match.group(1)),
            'cout': safe_int(cout_match.group(1)),
            'zero': safe_int(zero_match.group(1)),
            'neg': safe_int(neg_match.group(1)),
            'overflow': safe_int(overflow_match.group(1))
        }

    def assert_alu_result(self, op, a, b, expected_out, expected_zero, expected_neg, expected_cout, expected_overflow):
        """Helper to check simulation results and provide detailed pass/fail messages."""
        res = self.run_simulation(op, a, b)
        expected = {
            'out': expected_out,
            'cout': expected_cout,
            'zero': expected_zero,
            'neg': expected_neg,
            'overflow': expected_overflow
        }
        
        for key in expected:
            if res[key] != expected[key]:
                error_msg = (
                    f"\n[FAILED] ALU Test Failed for op={op:03b}, a={a:08b}, b={b:08b}\n"
                    f"Mismatch in '{key}':\n"
                    f"  Expected {key} = {expected[key]}\n"
                    f"  Received {key} = {res[key]}\n"
                    f"Full Expected: {expected}\n"
                    f"Full Received: {res}"
                )
                self.fail(error_msg)
        
        TestALU.score += 1
        print(f"[PASSED] op={op:03b}, a={a:08b}, b={b:08b} -> out={res['out']:08b} (flags matched expected) | +1 Point (Current Score: {TestALU.score})")

    def run_operation_tests(self, op_name, test_cases):
        """Runs a list of test cases for a specific operation and handles scoring/printing."""
        print(f"\n--- Testing {op_name} ---")
        op_score = 0
        total_points = len(test_cases)
        try:
            for args in test_cases:
                self.assert_alu_result(*args)
                op_score += 1
            print(f"[OPERATION PASSED] {op_name} - Scored {op_score}/{total_points} points.")
        except AssertionError as e:
            print(f"[OPERATION FAILED] {op_name} - Scored {op_score}/{total_points} points.")
            raise e

    def test_00_compilation(self):
        """Test that the ALU RTL and testbench compile successfully."""
        print("\n--- Testing Compilation ---")
        op_score = 0
        total_points = 10
        try:
            # Determine the project root directory (one level up from the test directory)
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            
            # Clean any previous builds
            subprocess.run(['make', 'clean'], cwd=project_root, capture_output=True)
            
            # Run the compilation target using the provided Makefile
            result = subprocess.run(
                ['make', 'compile-alu'],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            
            # Verify the command succeeded (return code 0)
            self.assertEqual(result.returncode, 0, f"\n[FAILED] Compilation failed:\n{result.stderr}\n{result.stdout}")
            
            # Verify the compiled executable was created
            vvp_file = os.path.join(project_root, 'bin', 'alu.vvp')
            self.assertTrue(os.path.exists(vvp_file), "\n[FAILED] Compiled bin/alu.vvp file not found.")
            
            TestALU.score += 10
            op_score += 10
            print(f"[OPERATION PASSED] Compilation - Scored {op_score}/{total_points} points.")
        except AssertionError as e:
            print(f"[OPERATION FAILED] Compilation - Scored {op_score}/{total_points} points.")
            raise e

    def test_01_and_operation(self):
        """Test bitwise AND (op=000) checking output and all possible flags."""
        test_cases = [
            (0, 0b00001111, 0b00000101, 0b00000101, 0, 0, 0, 0), # Standard AND (no zero, no negative)
            (0, 0b00001111, 0b11110000, 0b00000000, 1, 0, 0, 0), # AND resulting in Zero flag
            (0, 0b10101010, 0b11001100, 0b10001000, 0, 1, 0, 0)  # AND resulting in Negative flag
        ]
        self.run_operation_tests("Bitwise AND (op=000)", test_cases)

    def test_02_or_operation(self):
        """Test bitwise OR (op=001) checking output and all possible flags."""
        test_cases = [
            (1, 0b00001111, 0b00000101, 0b00001111, 0, 0, 0, 0), # Standard OR (no zero, no negative)
            (1, 0b00000000, 0b00000000, 0b00000000, 1, 0, 0, 0), # OR resulting in Zero flag
            (1, 0b10000000, 0b00001111, 0b10001111, 0, 1, 0, 0)  # OR resulting in Negative flag
        ]
        self.run_operation_tests("Bitwise OR (op=001)", test_cases)

if __name__ == '__main__':
    unittest.main()