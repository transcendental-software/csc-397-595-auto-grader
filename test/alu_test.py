import os
import re
import subprocess
import sys
import unittest

# Suppress stack trace printing when a test fails
sys.tracebacklimit = 0

class TestALU(unittest.TestCase):
    score = 0
    max_score = 0

    @classmethod
    def tearDownClass(cls):
        print(f"\n======================================\nFINAL SCORE: {cls.score} / {cls.max_score}\n======================================")

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
            return int(val_str, 2) if val_str and all(c in '01' for c in val_str) else val_str

        return {
            'out': safe_int(out_match.group(1) if out_match else None),
            'cout': safe_int(cout_match.group(1) if cout_match else None),
            'zero': safe_int(zero_match.group(1) if zero_match else None),
            'neg': safe_int(neg_match.group(1) if neg_match else None),
            'overflow': safe_int(overflow_match.group(1) if overflow_match else None)
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
        
        def format_bin(k, v):
            if isinstance(v, int):
                return f"{v:08b}" if k == 'out' else f"{v:01b}"
            return str(v)

        for key in expected:
            if res[key] != expected[key]:
                exp_fmt = {k: format_bin(k, v) for k, v in expected.items()}
                res_fmt = {k: format_bin(k, v) for k, v in res.items()}
                error_msg = (
                    f"\n[FAILED] ALU Test Failed for op={op:03b}, a={a:08b}, b={b:08b}\n"
                    f"Mismatch in '{key}':\n"
                    f"  Expected {key} = {format_bin(key, expected[key])}\n"
                    f"  Received {key} = {format_bin(key, res[key])}\n"
                    f"Full Expected: {exp_fmt}\n"
                    f"Full Received: {res_fmt}"
                )
                self.fail(error_msg)
        
        TestALU.score += 2

    def run_operation_tests(self, op_name, test_cases):
        """Runs a list of test cases for a specific operation and handles scoring/printing."""
        print(f"\n--- Testing {op_name} ---")
        op_score = 0
        total_points = len(test_cases) * 2
        TestALU.max_score += total_points
        try:
            for args in test_cases:
                self.assert_alu_result(*args)
                op_score += 2
            print(f"[OPERATION PASSED] {op_name} - Scored {op_score}/{total_points} points.")
        except AssertionError as e:
            print(f"[OPERATION FAILED] {op_name} - Scored {op_score}/{total_points} points.")
            raise e

    def test_00_compilation(self):
        """Test that the ALU RTL and testbench compile successfully."""
        print("\n--- Testing Compilation ---")
        op_score = 0
        total_points = 10
        TestALU.max_score += total_points
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
            (0, 0b10101010, 0b11001100, 0b10001000, 0, 1, 0, 0), # AND resulting in Negative flag
            (0, 0b10101010, 0b01010101, 0b00000000, 1, 0, 0, 0), # Alternating bits AND (Zero flag)
            (0, 0b11111111, 0b00000000, 0b00000000, 1, 0, 0, 0)  # AND with zero
        ]
        self.run_operation_tests("Bitwise AND (op=000)", test_cases)

    def test_02_or_operation(self):
        """Test bitwise OR (op=001) checking output and all possible flags."""
        test_cases = [
            (1, 0b00001111, 0b00000101, 0b00001111, 0, 0, 0, 0), # Standard OR (no zero, no negative)
            (1, 0b00000000, 0b00000000, 0b00000000, 1, 0, 0, 0), # OR resulting in Zero flag
            (1, 0b10000000, 0b00001111, 0b10001111, 0, 1, 0, 0), # OR resulting in Negative flag
            (1, 0b10101010, 0b01010101, 0b11111111, 0, 1, 0, 0), # Alternating bits OR (Negative flag)
            (1, 0b11111111, 0b00000000, 0b11111111, 0, 1, 0, 0)  # OR with zero
        ]
        self.run_operation_tests("Bitwise OR (op=001)", test_cases)

    def test_03_xor_operation(self):
        """Test bitwise XOR (op=010) checking output and all possible flags."""
        test_cases = [
            (2, 0b00001111, 0b00000101, 0b00001010, 0, 0, 0, 0), # Standard XOR (no zero, no negative)
            (2, 0b10101010, 0b10101010, 0b00000000, 1, 0, 0, 0), # XOR resulting in Zero flag
            (2, 0b10000000, 0b00001111, 0b10001111, 0, 1, 0, 0), # XOR resulting in Negative flag
            (2, 0b11110000, 0b00001111, 0b11111111, 0, 1, 0, 0), # Inverse halves XOR (Negative flag)
            (2, 0b11111111, 0b00000000, 0b11111111, 0, 1, 0, 0)  # XOR with zero
        ]
        self.run_operation_tests("Bitwise XOR (op=010)", test_cases)

    def test_04_add_operation(self):
        """Test addition (op=011) checking output and all possible flags."""
        test_cases = [
            (3, 0b00001111, 0b00000101, 0b00010100, 0, 0, 0, 0), # Standard addition (15 + 5 = 20)
            (3, 0b00000000, 0b00000000, 0b00000000, 1, 0, 0, 0), # Zero flag (0 + 0 = 0)
            (3, 0b01111111, 0b10000000, 0b11111111, 0, 1, 0, 0), # Negative flag (127 + (-128) = -1)
            (3, 0b11111111, 0b00000001, 0b00000000, 1, 0, 1, 0), # Carry out flag (255 + 1 = 0)
            (3, 0b01111111, 0b00000001, 0b10000000, 0, 1, 0, 1), # Overflow flag (Positive + Positive = Negative)
            (3, 0b10000000, 0b11111111, 0b01111111, 0, 0, 1, 1), # Overflow flag (Negative + Negative = Positive)
            (3, 0b11111111, 0b11111111, 0b11111110, 0, 1, 1, 0), # Carry out flag (-1 + -1 = -2, valid neg)
            (3, 0b10000000, 0b01111111, 0b11111111, 0, 1, 0, 0)  # Max negative + Max positive (-128 + 127 = -1)
        ]
        self.run_operation_tests("Addition (op=011)", test_cases)

    def test_05_sub_operation(self):
        """Test subtraction (op=100) checking output and all possible flags."""
        test_cases = [
            (4, 0b00001111, 0b00000101, 0b00001010, 0, 0, 1, 0), # Standard subtraction (15 - 5 = 10, cout=1 means no borrow)
            (4, 0b00000101, 0b00000101, 0b00000000, 1, 0, 1, 0), # Zero flag (5 - 5 = 0)
            (4, 0b00000101, 0b00001111, 0b11110110, 0, 1, 0, 0), # Negative flag (5 - 15 = -10, cout=0 means borrow)
            (4, 0b01111111, 0b11111011, 0b10000100, 0, 1, 0, 1), # Overflow flag (Positive - Negative = Negative)
            (4, 0b10000000, 0b00000101, 0b01111011, 0, 0, 1, 1), # Overflow flag (Negative - Positive = Positive)
            (4, 0b00000000, 0b00000001, 0b11111111, 0, 1, 0, 0), # Borrow flag (0 - 1 = -1, cout=0 means borrow)
            (4, 0b00000000, 0b10000000, 0b10000000, 0, 1, 0, 1)  # Overflow on 0 - (-128) = 128
        ]
        self.run_operation_tests("Subtraction (op=100)", test_cases)

    def test_06_signed_eq_operation(self):
        """Test signed equal (op=101) checking output and all possible flags."""
        test_cases = [
            (5, 0b00000101, 0b00000101, 0b00000001, 0, 0, 0, 0), # Equal positive numbers
            (5, 0b11110110, 0b11110110, 0b00000001, 0, 0, 0, 0), # Equal negative numbers
            (5, 0b00000101, 0b11111011, 0b00000000, 1, 0, 0, 0), # Not equal
            (5, 0b10000000, 0b01111111, 0b00000000, 1, 0, 0, 0), # Not equal (-128 == 127 is False)
            (5, 0b00000000, 0b00000000, 0b00000001, 0, 0, 0, 0)  # Equal zeros
        ]
        self.run_operation_tests("Signed Equal (op=101)", test_cases)

    def test_07_signed_gt_operation(self):
        """Test signed greater than (op=110) checking output and all possible flags."""
        test_cases = [
            (6, 0b00001111, 0b00000101, 0b00000001, 0, 0, 0, 0), # Positive > Positive (15 > 5)
            (6, 0b00000101, 0b11110110, 0b00000001, 0, 0, 0, 0), # Positive > Negative (5 > -10)
            (6, 0b11110110, 0b00000101, 0b00000000, 1, 0, 0, 0), # Negative < Positive (-10 > 5 is False)
            (6, 0b00000101, 0b00000101, 0b00000000, 1, 0, 0, 0), # Equal (5 > 5 is False)
            (6, 0b11111111, 0b11111110, 0b00000001, 0, 0, 0, 0)  # Negative > Smaller Negative (-1 > -2 is True)
        ]
        self.run_operation_tests("Signed Greater Than (op=110)", test_cases)

    def test_08_signed_lt_operation(self):
        """Test signed less than (op=111) checking output and all possible flags."""
        test_cases = [
            (7, 0b11110110, 0b00000101, 0b00000001, 0, 0, 0, 0), # Negative < Positive (-10 < 5)
            (7, 0b00000101, 0b00001111, 0b00000001, 0, 0, 0, 0), # Positive < Positive (5 < 15)
            (7, 0b00000101, 0b11110110, 0b00000000, 1, 0, 0, 0), # Positive < Negative (5 < -10 is False)
            (7, 0b00000101, 0b00000101, 0b00000000, 1, 0, 0, 0), # Equal (5 < 5 is False)
            (7, 0b11111110, 0b11111111, 0b00000001, 0, 0, 0, 0)  # Negative < Larger Negative (-2 < -1 is True)
        ]
        self.run_operation_tests("Signed Less Than (op=111)", test_cases)

if __name__ == '__main__':
    unittest.main()