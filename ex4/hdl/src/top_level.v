module top_level
(
    input wire i_a,
    input wire i_b,
    output wire o_dout
);

assign o_dout = i_a & i_b;

endmodule
