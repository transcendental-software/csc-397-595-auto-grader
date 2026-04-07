# General Makefile

# Tools
IV = iverilog

# Files
ALU_RTL_SRC = rtl/alu.v
ALU_TB_SRC = tb/alu_tb.v

# Output executable
ALU-OUT = alu.vvp

.PHONY: all compile-alu clean

all: compile-alu

compile-alu: $(ALU_RTL_SRC) $(ALU_TB_SRC)
	$(IV) -o $(ALU-OUT) $(ALU_RTL_SRC) $(ALU_TB_SRC)

clean:
	rm -f $(ALU-OUT) *.vcd