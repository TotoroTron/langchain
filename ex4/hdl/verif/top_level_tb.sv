`timescale 1ns/1ps

module top_level_tb;

   // Testbench signals
   reg  i_a;
   reg  i_b;
   wire o_dout;

   // Instantiate the design under test (DUT)
   top_level dut (
      .i_a(i_a),
      .i_b(i_b),
      .o_dout(o_dout)
   );

   // Error counter
   integer error_count;

   // Apply test vectors
   initial begin
      $display("Starting test...");

      // Initialize error_count to zero
      error_count = 0;

      // Test 1: i_a=0, i_b=0 --> Expect o_dout=0
      i_a = 1'b0;
      i_b = 1'b0;
      #5;
      $display("Input: i_a=0, i_b=0 --> Output = %b (Expected: 0)", o_dout);
      if (o_dout !== 1'b0) begin
         $display("ERROR: Output mismatch!");
         error_count++;
      end

      // Test 2: i_a=0, i_b=1 --> Expect o_dout=0
      i_a = 1'b0;
      i_b = 1'b1;
      #5;
      $display("Input: i_a=0, i_b=1 --> Output = %b (Expected: 0)", o_dout);
      if (o_dout !== 1'b0) begin
         $display("ERROR: Output mismatch!");
         error_count++;
      end

      // Test 3: i_a=1, i_b=0 --> Expect o_dout=0
      i_a = 1'b1;
      i_b = 1'b0;
      #5;
      $display("Input: i_a=1, i_b=0 --> Output = %b (Expected: 0)", o_dout);
      if (o_dout !== 1'b0) begin
         $display("ERROR: Output mismatch!");
         error_count++;
      end

      // Test 4: i_a=1, i_b=1 --> Expect o_dout=1
      i_a = 1'b1;
      i_b = 1'b1;
      #5;
      $display("Input: i_a=1, i_b=1 --> Output = %b (Expected: 1)", o_dout);
      if (o_dout !== 1'b1) begin
         $display("ERROR: Output mismatch!");
         error_count++;
      end

      // Display total errors
      $display("Total Errors: %0d", error_count);
      $display("Test completed.");
      $stop;
   end

endmodule
