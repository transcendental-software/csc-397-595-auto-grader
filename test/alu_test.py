import os
import re
import subprocess
import unittest

class TestALU(unittest.TestCase):
    def run_simulation(self, op, a, b):
        """Helper method to run the ALU simulation and parse the outputs."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        vvp_file = os.path.join(project_root, 'alu.vvp')
        
        # Ensure the simulation executable exists before running
        if not os.path.exists(vvp_file):
            subprocess.run(['make', 'compile-alu'], cwd=project_root, capture_output=True)
            
        input_str = f"{op:03b} {a:08b} {b:08b}\n"
        result = subprocess.run(
            ['vvp', 'alu.vvp'],
            input=input_str,
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        # Parse outputs using regex
        out_match = re.search(r'out\s+=\s+\d+\s+\(8\'b([01]{8})\)', result.stdout)
        cout_match = re.search(r'cout\s+=\s+([01])', result.stdout)
        zero_match = re.search(r'zero\s+=\s+([01])', result.stdout)
        neg_match = re.search(r'neg\s+=\s+([01])', result.stdout)
        overflow_match = re.search(r'overflow\s+=\s+([01])', result.stdout)
        
        if not all([out_match, cout_match, zero_match, neg_match, overflow_match]):
            self.fail(f"Failed to parse simulation output for inputs op={op}, a={a}, b={b}:\n{result.stdout}")
            
        return {
            'out': int(out_match.group(1), 2),
            'cout': int(cout_match.group(1)),
            'zero': int(zero_match.group(1)),
            'neg': int(neg_match.group(1)),
            'overflow': int(overflow_match.group(1))
        }

    def test_compilation(self):
        """Test that the ALU RTL and testbench compile successfully."""
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
        self.assertEqual(result.returncode, 0, f"Compilation failed:\n{result.stderr}\n{result.stdout}")
        
        # Verify the compiled executable was created
        vvp_file = os.path.join(project_root, 'alu.vvp')
        self.assertTrue(os.path.exists(vvp_file), "Compiled alu.vvp file not found.")

    def test_and_operation(self):
        """Test bitwise AND (op=000) checking output and all possible flags."""
        # Test 1: Standard AND (no zero, no negative)
        res = self.run_simulation(0, 0b00001111, 0b00000101)
        self.assertEqual(res['out'], 0b00000101)
        self.assertEqual(res['zero'], 0)
        self.assertEqual(res['neg'], 0)
        self.assertEqual(res['cout'], 0)
        self.assertEqual(res['overflow'], 0)
        
        # Test 2: AND resulting in Zero flag
        res = self.run_simulation(0, 0b00001111, 0b11110000)
        self.assertEqual(res['out'], 0b00000000)
        self.assertEqual(res['zero'], 1)
        self.assertEqual(res['neg'], 0)
        self.assertEqual(res['cout'], 0)
        self.assertEqual(res['overflow'], 0)
        
        # Test 3: AND resulting in Negative flag
        res = self.run_simulation(0, 0b10101010, 0b11001100)
        self.assertEqual(res['out'], 0b10001000)
        self.assertEqual(res['zero'], 0)
        self.assertEqual(res['neg'], 1)
        self.assertEqual(res['cout'], 0)
        self.assertEqual(res['overflow'], 0)

if __name__ == '__main__':
    unittest.main()