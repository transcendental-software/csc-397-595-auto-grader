# General Makefile

# Tools
IV = iverilog
PYTHON = python3.14

# ALU Files
ALU_RTL_SRC = rtl/alu.v
ALU_TB_SRC = tb/alu_tb.v
ALU_OUT = bin/alu.vvp
ALU_TEST = test/alu_test.py

.PHONY: all compile-alu test test-alu clean

all: compile-alu

compile-alu: $(ALU_RTL_SRC) $(ALU_TB_SRC)
	mkdir -p bin
	$(IV) -o $(ALU_OUT) $(ALU_RTL_SRC) $(ALU_TB_SRC)

test: test-alu

test-alu:
	$(PYTHON) $(ALU_TEST)

clean:
	rm -rf bin *.vcd