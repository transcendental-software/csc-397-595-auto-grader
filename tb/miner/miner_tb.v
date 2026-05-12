// ================================================================================ //
// NEORV32 - Verilog testbench                                                      //
// -------------------------------------------------------------------------------- //
// Simple testbench for the auto-generated all-Verilog version of NEORV32.          //
// Checks for the initial UART output of the bootloader ("NEORV32").                //
// -------------------------------------------------------------------------------- //
// The NEORV32 RISC-V Processor - https://github.com/stnolting/neorv32              //
// Copyright (c) NEORV32 contributors.                                              //
// Copyright (c) 2020 - 2026 Stephan Nolting. All rights reserved.                  //
// Licensed under the BSD-3-Clause license, see LICENSE for details.                //
// SPDX-License-Identifier: BSD-3-Clause                                            //
// ================================================================================ //

`timescale 1 ns/100 ps // time-unit = 1 ns, precision = 100 ps

module neorv32_verilog_tb;

  reg clk, nrst; // generators
  wire uart_txd; // serial TX line (default baud rate is 19200)
  reg uart_rxd;  // serial RX line
  wire [7:0] char_data; // character detected by the UART receiver
  wire char_valid; // valid character
  integer i;

  integer c;
  reg [7:0] in_buf [0:127];
  integer in_len;
  integer k;

  reg [55:0] match_prompt;
  reg prompt_detected;
  reg [79:0] match_complete;

  // XBUS (Wishbone) signals
  wire [31:0] xbus_adr;
  wire [31:0] xbus_dat_o;
  wire [31:0] xbus_dat_i;
  wire        xbus_we;
  wire [3:0]  xbus_sel;
  wire        xbus_stb;
  wire        xbus_cyc;
  wire        xbus_ack;
  wire        xbus_err;

  // generator setup
  initial begin
`ifdef DUMP_WAVE
    $dumpfile("wave.vcd"); // write waveform data
    $dumpvars(neorv32_verilog_tb);
`endif
    $display ("[TB] NEORV32 Verilog testbench\n");
    clk = 0;
    nrst = 0;
    #100; // active reset for 100 * timescale = 100 ns
    nrst = 1;
    for (i = 0; i < 30; i = i + 1) begin
      #1_000_000_000; // run for 1 second (10^9 ns) per iteration
    end
    $display("\n[TB] Simulation completed after 30 seconds.");
    $finish; // terminate
  end

  initial begin
    match_prompt = 0;
    prompt_detected = 0;
    match_complete = 0;
  end

  always @(posedge clk) begin
    if (char_valid) begin
      match_prompt = {match_prompt[47:0], char_data};
      if (match_prompt == "spaces:") begin
        prompt_detected = 1;
      end

      match_complete = {match_complete[71:0], char_data};
      if (match_complete == "Complete!\n") begin
        $finish;
      end
    end
  end

  task uart_send_char;
    input [7:0] char_in;
    integer b;
    begin
      uart_rxd = 0; // start bit
      #(1_000_000_000 / 19200);
      for (b = 0; b < 8; b = b + 1) begin
        uart_rxd = char_in[b];
        #(1_000_000_000 / 19200);
      end
      uart_rxd = 1; // stop bit
      #(1_000_000_000 / 19200);
    end
  endtask

  initial begin
    uart_rxd = 1;
    in_len = 0;
    c = $fgetc(32'h8000_0000);
    while (c != 10 && c != 13 && c != -1 && in_len < 127) begin
      in_buf[in_len] = c;
      in_len = in_len + 1;
      c = $fgetc(32'h8000_0000);
    end
    in_buf[in_len] = 10; // add newline
    in_len = in_len + 1;

    wait(prompt_detected == 1);
    #1000000; // wait 1ms

    for (k = 0; k < in_len; k = k + 1) begin
      uart_send_char(in_buf[k]);
    end
  end

  // clock generator
  always begin
    #5 clk = !clk; // T = 2*5ns -> f = 100MHz
  end

  // unit under test
  // note that there are NO parameters available - the configuration has to be done
  // in the NEORV32 VHDL wrapper *before* synthesizing the generated Verilog code
  neorv32_verilog_wrapper neorv32_verilog_inst (
    .clk_i       (clk),
    .rstn_i      (nrst),
    .uart0_rxd_i (uart_rxd),
    .uart0_txd_o (uart_txd),
    // XBUS (Wishbone)
    .xbus_adr_o  (xbus_adr),
    .xbus_dat_o  (xbus_dat_o),
    .xbus_dat_i  (xbus_dat_i),
    .xbus_we_o   (xbus_we),
    .xbus_sel_o  (xbus_sel),
    .xbus_stb_o  (xbus_stb),
    .xbus_cyc_o  (xbus_cyc),
    .xbus_ack_i  (xbus_ack),
    .xbus_err_i  (xbus_err)
  );

  // Hardware Miner Accelerator Wrapper
  xbus_miner_wrapper miner_inst (
    .clk_i      (clk),
    .rstn_i     (nrst),
    .xbus_adr_i (xbus_adr),
    .xbus_dat_i (xbus_dat_o),
    .xbus_dat_o (xbus_dat_i),
    .xbus_we_i  (xbus_we),
    .xbus_sel_i (xbus_sel),
    .xbus_stb_i (xbus_stb),
    .xbus_cyc_i (xbus_cyc),
    .xbus_ack_o (xbus_ack),
    .xbus_err_o (xbus_err)
  );

  // simulation UART receiver - outputs all received characters to the simulator console
  uart_sim_receiver #(
    .CLOCK_FREQ (100000000), // clock frequency of the core
    .BAUD_RATE  (19200)      // default baud rate of the NEORV32 bootloader
  ) uart_sim_receiver_inst(
    .clk_i   (clk),
    .txd_i   (uart_txd),
    .data_o  (char_data),
    .valid_o (char_valid)
  );

endmodule

// ****************************************************************************
// Simulation UART receiver
//
// Outputs printable characters to the simulator console.
// Character data is also returned to the top entity for further processing.
// ****************************************************************************

// by Stephan Nolting, BSD 3-Clause License
// https://github.com/stnolting/neorv32-verilog

module uart_sim_receiver
#(
  parameter CLOCK_FREQ = 100000000, // clock frequency of <clk_i> in Hz
  parameter BAUD_RATE  = 19200      // target baud rate
)(
  input        clk_i,  // clock input, triggering on rising edge
  input        txd_i,  // UART transmit data
  output [7:0] data_o, // character data
  output       valid_o // character data valid when set
);

  // duration of a single bit
  localparam UART_BAUD_VAL = CLOCK_FREQ / BAUD_RATE;

  // receiver
  reg  [4:0] uart_rx_sync;     // synchronizer shift register
  reg  [8:0] uart_rx_sreg;     // data shift register
  reg        uart_rx_busy;     // busy flag
  integer    uart_rx_baud_cnt; // bit-sample counter for baud rate
  integer    uart_rx_bitcnt;   // bit counter: 8 data bits, 1 start bit

  // initialize because we don't have a real reset
  initial begin
    uart_rx_sync     = 5'b11111;
    uart_rx_busy     = 1'b0;
    uart_rx_sreg     = 9'b000000000;
    uart_rx_baud_cnt = UART_BAUD_VAL / 2;
    uart_rx_bitcnt   = 0;
  end

  // UART receiver
  always @(posedge clk_i) begin
    // synchronizer
    uart_rx_sync <= {uart_rx_sync[3:0], txd_i};
    // arbiter
    if (!uart_rx_busy) begin // idle
      uart_rx_busy     <= 0;
      uart_rx_baud_cnt <= UART_BAUD_VAL / 2;
      uart_rx_bitcnt   <= 9;
      if (uart_rx_sync[4:1] == 4'b1100) begin // start bit (falling edge)?
        uart_rx_busy <= 1;
      end
    end else begin
      if (uart_rx_baud_cnt == 0) begin
        if (uart_rx_bitcnt == 1) begin
          uart_rx_baud_cnt <= UART_BAUD_VAL / 2;
        end else begin
          uart_rx_baud_cnt <= UART_BAUD_VAL;
        end
        // sample 8 data bits and 1 start bit
        if (uart_rx_bitcnt == 0) begin
          uart_rx_busy <= 1'b0; // done
          if ((uart_rx_sreg[8:1] >= 32) && (uart_rx_sreg[8:1] <= 127)) begin // is a printable char?
            $write("%c", uart_rx_sreg[8:1]);
          end else if (uart_rx_sreg[8:1] == 10) begin // Linux line break?
            $display(""); // force terminal line break
          end
        end else begin
          uart_rx_sreg   <= {uart_rx_sync[4], uart_rx_sreg[8:1]};
          uart_rx_bitcnt <= uart_rx_bitcnt - 1;
        end
      end else begin
        uart_rx_baud_cnt <= uart_rx_baud_cnt - 1;
      end
    end
  end

  // character output
  assign data_o  = uart_rx_sreg[8:1];
  assign valid_o = ((uart_rx_baud_cnt == 0) && (uart_rx_bitcnt == 0)) ? 1'b1 : 1'b0; // valid

endmodule
