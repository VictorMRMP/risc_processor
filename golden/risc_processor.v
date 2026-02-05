module risc
(
  input  wire clk,
  input  wire rst,
  output wire halt
);

  localparam integer AWIDTH=5, DWIDTH=8 ;


  /////////////////////
  // CLOCK GENERATOR //
  /////////////////////

  wire [2:0] phase ;

  counter
  #(
    .WIDTH   ( 3  ) 
   )
    counter_inst_1
   (
    .clk     ( clk   ),
    .rst     ( rst   ),
    .load    ( 1'b0  ),
    .enab    ( !halt ),
    .cnt_in  ( 3'b0  ),
    .cnt_out ( phase ) 
   ) ;


  ////////////////
  // CONTROLLER //
  ////////////////

  wire [2:0] opcode ;

  controller controller_inst
  (
    .opcode  ( opcode ), // operation code
    .phase   ( phase  ), // instruction phase
    .zero    ( zero   ), // accumulator is zero
    .sel     ( sel    ), // select instruction address to memory
    .rd      ( rd     ), // enable memory output onto data bus
    .ld_ir   ( ld_ir  ), // load instruction register
    .inc_pc  ( inc_pc ), // increment program counter
    .halt    ( halt   ), // halt machine
    .ld_pc   ( ld_pc  ), // load program counter
    .data_e  ( data_e ), // enable accumulator output onto data bus
    .ld_ac   ( ld_ac  ), // load accumulator from data bus
    .wr      ( wr     )  // write data bus to memory
  ) ;


  /////////////////////
  // PROGRAM COUNTER //
  /////////////////////

  wire [AWIDTH-1:0] ir_addr, pc_addr ;

  counter
  #(
    .WIDTH   ( AWIDTH  ) 
   )
    counter_inst_2
   (
    .clk     ( clk     ),
    .rst     ( rst     ),
    .load    ( ld_pc   ),
    .enab    ( inc_pc  ),
    .cnt_in  ( ir_addr ),
    .cnt_out ( pc_addr ) 
   ) ;


  /////////////////////
  // ADDESS SELECTOR //
  /////////////////////

  wire [AWIDTH-1:0] addr ;

  multiplexor
  #(
    .WIDTH   ( AWIDTH  ) 
   )
    multiplexor_inst
   (
    .sel     ( sel     ),
    .in0     ( ir_addr ),
    .in1     ( pc_addr ),
    .mux_out ( addr    ) 
   ) ;


  /////////////////////////
  // DATA/PROGRAM MEMORY //
  /////////////////////////

  wire [DWIDTH-1:0] data ;

  memory
  #(
    .AWIDTH ( AWIDTH ),
    .DWIDTH ( DWIDTH ) 
   )
    memory_inst
   (
    .clk    ( clk    ),
    .wr     ( wr     ),
    .rd     ( rd     ),
    .addr   ( addr   ),
    .data   ( data   ) 
   ) ;


  //////////////////////////
  // INSTRUCTION REGISTER //
  //////////////////////////

  register
  #(
    .WIDTH    ( DWIDTH ) 
   )
    register_inst_1
   (
    .clk      ( clk    ),
    .rst      ( rst    ),
    .load     ( ld_ir  ),
    .data_in  ( data   ),
    .data_out ( {opcode,ir_addr} )
   ) ;


  ////////////////////////
  // ARITHMETIC & LOGIC //
  ////////////////////////

  wire [DWIDTH-1:0] acc_out, alu_out ;

  alu
  #(
    .WIDTH     ( DWIDTH ) 
   )
    alu_inst
   (
    .opcode    ( opcode  ),
    .in_a      ( acc_out ),
    .in_b      ( data    ),
    .a_is_zero ( zero    ),
    .alu_out   ( alu_out ) 
   ) ;


  //////////////////////////
  // ACCUMULATOR REGISTER //
  //////////////////////////

  register
  #(
    .WIDTH    ( DWIDTH  ) 
   )
    register_inst_2
   (
    .clk      ( clk     ),
    .rst      ( rst     ),
    .load     ( ld_ac   ),
    .data_in  ( alu_out ),
    .data_out ( acc_out ) 
   ) ;


  //////////////////////////
  // BUS DRIVER           //
  //////////////////////////

  driver
  #(
    .WIDTH    ( DWIDTH  ) 
   )
    driver_inst
   (
    .data_en  ( data_e  ),
    .data_in  ( alu_out ),
    .data_out ( data    ) 
   ) ;

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
always@(posedge clk)
begin
if(load)
	data_out=data_in;
if(rst)
	data_out=8'b00000000;
else
 	data_out<=data_out;
end
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
always @*
begin
	if(sel==0)
		mux_out=in0;
	else
		mux_out=in1;
end
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
  reg [DWIDTH-1:0] mem_array [0:2**AWIDTH-1];
  always @(posedge clk)
    if ( wr ) mem_array[addr] = data;
  assign data = rd ? mem_array[addr] : 'bz;
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
always @*
begin
if(data_en==1)
		data_out=data_in;
else
		data_out=8'dz;
end
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
  

function [WIDTH-1:0] cnt_func(input rst,load,enab,input[WIDTH-1:0] cnt_in,input [WIDTH-1:0] cnt_out);
begin
cnt_func=cnt_out;
if(rst)
	cnt_func=0;
	
else
	if(load)
		cnt_func=cnt_in;
	else if(enab)
		cnt_func=cnt_func+1;
end
endfunction


  always @(posedge clk)
     cnt_out <= cnt_func (rst, load, enab ,cnt_in,cnt_out); //function call

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
reg ALU_OP;
reg [8:0] out;
always@*
begin
if(opcode==3'b010 || opcode==3'b011 || opcode==3'b100||opcode==3'b101)
	 ALU_OP=1;
else
	 ALU_OP=0;

case(phase)
		0: out=9'b100000000;
		1: out=9'b110000000;
		2: out=9'b111000000;
		3: out=9'b111000000;
		4: out={3'b000,opcode==3'b000,5'b10000};
		5: out={1'b0,ALU_OP,7'b00000000};
		6: out={1'b0,ALU_OP,2'b00,((opcode==3'b001)&&zero),1'b0,opcode==3'b111,1'b0,opcode==3'b110};
		7: out={1'b0,ALU_OP,3'b000,ALU_OP,opcode==3'b111,opcode==3'b110,opcode==3'b110};
endcase
	sel=out[8];
	rd=out[7];
	ld_ir=out[6];
	halt=out[5];
	inc_pc=out[4];
	ld_ac=out[3];
	ld_pc=out[2];
	wr=out[1];
	data_e=out[0];
end
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

always @*
begin
a_is_zero= !in_a ? 1'b1 : 1'b0;

if((opcode==3'b0)||(opcode==3'b001)||(opcode==3'b110)||(opcode==3'b111))
	alu_out=in_a;
if(opcode==3'b010)
	alu_out=in_a+in_b;
if(opcode==3'b011)
	alu_out=in_a&in_b;
if(opcode==3'b100)
	alu_out=in_a^in_b;
if(opcode==3'b101)
	alu_out=in_b;

end
endmodule


