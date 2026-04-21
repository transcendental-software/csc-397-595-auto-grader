`timescale 1ns / 1ps

module fw_tb;

    // Inputs
    reg clk;
    reg reset;
    reg valid_in;
    reg [7:0] data_in;

    // Outputs
    wire accept;
    wire drop;
    wire invalid;
    wire done;

    integer scan_count;
    integer packet_len;
    integer i;
    integer j;
    reg [7:0] packet_buffer [0:255];

    // Instantiate the Unit Under Test (UUT)
    fw uut (
        .clk(clk),
        .reset(reset),
        .valid_in(valid_in),
        .data_in(data_in),
        .accept(accept),
        .drop(drop),
        .invalid(invalid),
        .done(done)
    );

    // Clock generation (10ns period)
    always #5 clk = ~clk;

    initial begin
        $dumpfile("fw.vcd");
        $dumpvars(0, fw_tb);

        // Initialize inputs
        clk = 0;
        reset = 1;
        valid_in = 0;
        data_in = 8'd0;

        // Wait for global reset to settle
        #20;
        @(negedge clk);
        reset = 0;

        // Read input packet stream from standard input (stdin)
        $display("Please enter packet bytes in hex format separated by spaces:");
        
        packet_len = 0;
        // Read all bytes into the buffer first
        scan_count = $fscanf(32'h8000_0000, "%h", packet_buffer[packet_len]);
        while (scan_count == 1 && packet_len < 256) begin
            packet_len = packet_len + 1;
            scan_count = $fscanf(32'h8000_0000, "%h", packet_buffer[packet_len]);
        end

        // Pass the buffered bytes to the FSM sequentially
        for (i = 0; i < packet_len; i = i + 1) begin
            valid_in = 1;
            data_in = packet_buffer[i];
            @(negedge clk); // Hold data valid for one clock cycle
        end

        valid_in = 0;
    end

    // Output monitoring and evaluation
    initial begin
        wait(reset == 1'b0);
        wait(done == 1'b1);
        
        $display("\n==================================================");
        $display(" Firewall FSM Packet Testbench");
        $display("==================================================");
        $display(" Input Packet:");
        $write("   ");
        for (j = 0; j < packet_len; j = j + 1) begin
            $write("%02h ", packet_buffer[j]);
        end
        $display("\n");
        $display(" Outputs:");
        $display("   accept   = %0b", accept);
        $display("   drop     = %0b", drop);
        $display("   invalid  = %0b", invalid);
        $display("   done     = %0b", done);
        $display("==================================================\n");

        // Allow one more cycle to observe fall of done signal in VCD before finishing
        @(negedge clk);
        $finish;
    end

    // Watchdog timer to prevent infinite loops if FSM is broken
    initial begin
        #5000;
        $display("\n[ERROR] Simulation timeout. FSM never asserted 'done'.\n");
        $finish;
    end

endmodule