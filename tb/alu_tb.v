`timescale 1ns / 1ps

module alu_tb;

    // Inputs
    reg [7:0] a;
    reg [7:0] b;
    reg [2:0] op;

    // Outputs
    wire [7:0] out;
    wire cout;
    wire zero;
    wire neg;
    wire overflow;

    integer scan_count;

    // Instantiate the Unit Under Test (UUT)
    alu uut (
        .a(a),
        .b(b),
        .op(op),
        .out(out),
        .cout(cout),
        .zero(zero),
        .neg(neg),
        .overflow(overflow)
    );

    initial begin
        // Initialize inputs to default values
        a = 8'd0;
        b = 8'd0;
        op = 3'd0;

        // Read inputs from standard input (stdin)
        $display("Please enter inputs in binary format (op, a, b) separated by spaces:");
        scan_count = $fscanf(32'h8000_0000, "%b %b %b", op, a, b);
        if (scan_count != 3)
            $display("Note: Failed to read all 3 inputs from stdin. Using defaults for missing values.");

        // Wait for combinational logic to settle
        #10;

        // Display the results
        $display("\n==================================================");
        $display(" ALU Single-Input Testbench");
        $display("==================================================");
        $display(" Inputs:");
        $display("   a        = %0d (8'b%08b)", a, a);
        $display("   b        = %0d (8'b%08b)", b, b);
        $display("   op       = %0d (3'b%03b)", op, op);
        $display("\n Outputs:");
        $display("   out      = %0d (8'b%08b)", out, out);
        $display("   cout     = %0b", cout);
        $display("   zero     = %0b", zero);
        $display("   neg      = %0b", neg);
        $display("   overflow = %0b", overflow);
        $display("==================================================\n");

        $finish;
    end

endmodule