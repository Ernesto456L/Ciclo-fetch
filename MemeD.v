module MemD (
    input wire [31:0] Dir,
    output reg [31:0] Instruccion  
);
    reg [7:0] memoria [0:999];
	
	initial begin
        $readmemb("datos.txt", memoria); 
    end
	
	always @(*) begin
        Instruccion = {memoria[Dir], memoria[Dir+1], memoria[Dir+2], memoria[Dir+3]};
    end

endmodule
