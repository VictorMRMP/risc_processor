module risc
(
  input  wire clk,
  input  wire rst,
  output wire halt
);


endmodule

module register
#(
 parameter WIDTH=8
)
(
 input [WIDTH-1:0] data_in,
 output reg [WIDTH-1:0] data_out,
 input load,
 input clk,
 input rst
);


endmodule

module multiplexor
#(
 parameter WIDTH=5
)
(
 input sel,
 output reg[WIDTH-1:0] mux_out,
 input wire [WIDTH-1:0] in0,
 input wire [WIDTH-1:0] in1
);

endmodule

module memory
#(
  parameter integer AWIDTH=5,
  parameter integer DWIDTH=8
 )
 (
  input  wire              clk  ,
  input  wire              wr   ,
  input  wire              rd   ,
  input  wire [AWIDTH-1:0] addr ,
  inout  wire [DWIDTH-1:0] data  
 );
reg [DWIDTH-1:0] mem [0:2**AWIDTH-1];


endmodule

module driver
#(
 parameter WIDTH=8
)
(
 input data_en,
 input [WIDTH-1:0] data_in,
 output reg [WIDTH-1:0] data_out
);

endmodule



module counter
#(
  parameter integer WIDTH=5
 )
 (
  input  wire clk  ,
  input  wire rst  ,
  input  wire load ,
  input  wire enab ,
  input  wire [WIDTH-1:0] cnt_in ,
  output reg  [WIDTH-1:0] cnt_out 
 );

endmodule

module controller
(
 input zero,
 input [2:0]phase,
 input [2:0] opcode,
 output reg sel,
 output reg rd,
 output reg ld_ir,
 output reg halt,
 output reg inc_pc,
 output reg ld_ac,
 output reg wr,
 output reg ld_pc,
 output reg data_e
);



endmodule

module alu
#(
 parameter WIDTH=8
)
(
 input [WIDTH-1:0] in_a,
 in_b,
 input [2:0] opcode,
 output reg [WIDTH-1:0] alu_out,
 output reg a_is_zero
 );


endmodule


