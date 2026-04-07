// Bitwise AND
module bitwise_and(
    input [7:0] a,
    input [7:0] b,
    output [7:0] out
);
    // TODO: Implement bitwise AND
endmodule

// Bitwise OR
module bitwise_or(
    input [7:0] a,
    input [7:0] b,
    output [7:0] out
);
    // TODO: Implement bitwise OR
endmodule

// Bitwise XOR
module bitwise_xor(
    input [7:0] a,
    input [7:0] b,
    output [7:0] out
);
    // TODO: Implement bitwise XOR
endmodule

module bitwise_not(
    input [7:0] a,
    output [7:0] out
);

    // TODO: Implement bitwise NOT

endmodule

// 1-bit Full Adder
module full_adder(
    input a,
    input b,
    input cin,
    output out,
    output cout
);

    // TODO: Implement a 1-bit full adder strictly using logic gates

endmodule

// 8-bit Adder
module adder_8bit(
    input [7:0] a,
    input [7:0] b,
    input cin,
    output [7:0] out,
    output cout,
    output zero,
    output neg,
    output overflow
);
    // TODO: Implement an 8-bit adder using 8 full_adder modules
endmodule

// 8-bit Subtractor
module subtractor_8bit(
    input [7:0] a,
    input [7:0] b,
    output [7:0] out,
    output cout,
    output zero,
    output neg,
    output overflow
);
    // TODO: Implement an 8-bit subtractor using the adder_8bit module
endmodule

// Signed Equal
module signed_eq(input zero, output [7:0] out);
    // TODO: Implement Signed Equal using flags
endmodule

// Signed Greater Than
module signed_gt(input neg, input overflow, input zero, output [7:0] out);
    // TODO: Implement Signed Greater Than using flags
endmodule

// Signed Less Than
module signed_lt(input neg, input overflow, output [7:0] out);
    // TODO: Implement Signed Less Than using flags
endmodule

// 1-bit 8-to-1 Multiplexer
module mux8_1bit(input [7:0] d, input [2:0] sel, output out);
    // TODO: Implement a 1-bit 8-to-1 multiplexer using logic gates
endmodule

// 8-bit Arithmetic Logic Unit
module alu(
    input [7:0] a,
    input [7:0] b,
    input [2:0] op,
    output [7:0] out,
    output cout,
    output zero,
    output neg,
    output overflow
);

    // TODO: Implement the top-level 8-bit ALU
    // 1. Instantiate the individual operation modules (bitwise_and, adder_8bit, etc.)
    // 2. Instantiate 8 mux8_1bit modules to select the final combinational result
    // 3. Compute and route the correct flags (cout, zero, neg, overflow) for the selected operation to the top-level outputs

endmodule