module PC(
	input wire clk,
	input wire [31:0] pcIn,
	output reg [31:0] pcOut
);

always @(posedge clk) begin
	pcOut <= pcIn;
end

endmodule