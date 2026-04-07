## CSC 397/595 Hardware Design and Programming using FPGAs  
**Jarvis College of Computing and Digital Media - DePaul University**

This repository contains the source code and files for the autograder programs.

### Software Requirements

This autograder is designed to run on a standard Ubuntu 24.04 LTS Server Edition OS. You will need to use **Make** (to run the provided Makefile), **Icarus Verilog** (to compile and simulate the Verilog files), and **Python 3.14** (to run the testing setup script).

To install the necessary software packages, including Python 3.14 from the deadsnakes PPA, open a terminal and run the following commands:

```shell
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y make iverilog python3.14
```