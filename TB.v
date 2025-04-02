`timescale 1ns / 1ps

module Fetch;
    reg clk;
    
    always #5 clk = ~clk; 
 
    initial begin
	    clk = 0;
        #100; 
    end

endmodule
