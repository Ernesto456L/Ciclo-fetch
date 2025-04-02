module Sumador (
    input wire [31:0] adderIn,  
    output reg [31:0] adderOut  
);
	always @(*) begin
		adderOut = adderIn + 4;  
	end

endmodule