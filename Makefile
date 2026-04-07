# Makefile for Lab 1: 8-Bit ALU

# Tools
IV = iverilog
VVP = vvp

# Files
RTL_SRC = rtl/alu.v
TB_SRC = tb/alu_tb.v

# Output executable
OUT-ALU = alu.vvp

.PHONY: all compile-alu test-alu clean

all: compile-alu

compile-alu: $(RTL_SRC) $(TB_SRC)
	$(IV) -o $(OUT-ALU) $(RTL_SRC) $(TB_SRC)

test-alu: compile-alu
	$(VVP) $(OUT-ALU)

clean:
	rm -f $(OUT-ALU) *.vcd