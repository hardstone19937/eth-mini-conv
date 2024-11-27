`resetall
`timescale 1 ns / 1 ps
`default_nettype none

module acceleration_module # (
    // Width of AXI stream interfaces in bits
    parameter DATA_WIDTH = 8,
    // tuser signal width
    parameter USER_WIDTH = 1
) (
    input  wire                   clk,
    input  wire                   rst,

    /*
     * AXI input
     */
    input  wire [DATA_WIDTH-1:0]  s_axis_tdata,
    input  wire                   s_axis_tvalid,
    output wire                   s_axis_tready,
    input  wire                   s_axis_tlast,
    input  wire [USER_WIDTH-1:0]  s_axis_tuser,

    /*
     * AXI output
     */
    output wire [DATA_WIDTH-1:0]  m_axis_tdata,
    output wire                   m_axis_tvalid,
    input  wire                   m_axis_tready,
    output wire                   m_axis_tlast,
    output wire [USER_WIDTH-1:0]  m_axis_tuser
);


reg [3:0] byte_counter;
// counter
always @(posedge clk) begin
    if (rst)
        byte_counter <= 0;
    else if (s_axis_tvalid) begin
        if (byte_counter == 'd8)
            byte_counter <= 0;
        else
            byte_counter <= byte_counter + 'd1;
    end
end

//automation

reg signed [DATA_WIDTH-1:0] param_matrix [0:8];
reg signed [DATA_WIDTH-1:0] conv_matrix [0:8];
reg [2 :0] state, next_state;

//state
localparam IDLE = 4'b0000;
localparam LOAD_PARAM = 4'b0001;
localparam LOAD_DATA = 4'b0010;
localparam LOAD_DATA_COMPUTE = 4'b0011;
localparam LAST = 4'b0100;
localparam DUMMY = 4'b0101;
localparam DUMMY1 = 4'b0110;

always @(posedge clk) begin
    if (rst)
        state <= IDLE;
    else
        state <= next_state;
end

always @(*) begin
    case (state)
        IDLE : begin
            next_state = s_axis_tvalid ? LOAD_PARAM : IDLE;
        end
        LOAD_PARAM : begin
            next_state = byte_counter == 'd8 ? LOAD_DATA : LOAD_PARAM;
        end
        LOAD_DATA : begin
            if (s_axis_tlast) begin
                next_state = LAST;
            end else begin
                next_state = byte_counter == 'd8 ? LOAD_DATA_COMPUTE : LOAD_DATA;
            end
        end
        LOAD_DATA_COMPUTE : begin
            next_state = s_axis_tlast ? LAST : LOAD_DATA_COMPUTE;
        end
        LAST: next_state = DUMMY;
        DUMMY: next_state = DUMMY1;
        DUMMY1: next_state = IDLE;
    endcase
end


wire [7:0] check_0;
wire [7:0] check_1;
wire [7:0] check_2;
wire [7:0] check_3;
wire [7:0] check_4;
wire [7:0] check_5;
wire [7:0] check_6;
wire [7:0] check_7;
wire [7:0] check_8;

assign check_0 = param_matrix[0];
assign check_1 = param_matrix[1];
assign check_2 = param_matrix[2];
assign check_3 = param_matrix[3];
assign check_4 = param_matrix[4];
assign check_5 = param_matrix[5];
assign check_6 = param_matrix[6];
assign check_7 = param_matrix[7];
assign check_8 = param_matrix[8];

wire [7:0] d_check_0;
wire [7:0] d_check_1;
wire [7:0] d_check_2;
wire [7:0] d_check_3;
wire [7:0] d_check_4;
wire [7:0] d_check_5;
wire [7:0] d_check_6;
wire [7:0] d_check_7;
wire [7:0] d_check_8;

assign d_check_0 = conv_matrix[0];
assign d_check_1 = conv_matrix[1];
assign d_check_2 = conv_matrix[2];
assign d_check_3 = conv_matrix[3];
assign d_check_4 = conv_matrix[4];
assign d_check_5 = conv_matrix[5];
assign d_check_6 = conv_matrix[6];
assign d_check_7 = conv_matrix[7];
assign d_check_8 = conv_matrix[8];



reg signed [DATA_WIDTH * 2 + 2 :0] result;

always @(posedge clk) begin
    if (rst)
        result <= 0;
    else begin
        if (state == LOAD_PARAM || next_state == LOAD_PARAM) begin
            param_matrix[byte_counter] <= s_axis_tdata;
        end else if (state == LOAD_DATA) begin
            conv_matrix[byte_counter] <= s_axis_tdata;
        end else if (state == LOAD_DATA_COMPUTE) begin
            conv_matrix[byte_counter] <= s_axis_tdata;
            if (byte_counter == 0) begin
                result <= 
                        param_matrix[0] * conv_matrix[0] +
                        param_matrix[1] * conv_matrix[1] +
                        param_matrix[2] * conv_matrix[2] +
                        param_matrix[3] * conv_matrix[3] +
                        param_matrix[4] * conv_matrix[4] +
                        param_matrix[5] * conv_matrix[5] +
                        param_matrix[6] * conv_matrix[6] +
                        param_matrix[7] * conv_matrix[7] +
                        param_matrix[8] * conv_matrix[8];
            end
        end else if (state == LAST) begin
            result <= 
            param_matrix[0] * conv_matrix[0] +
            param_matrix[1] * conv_matrix[1] +
            param_matrix[2] * conv_matrix[2] +
            param_matrix[3] * conv_matrix[3] +
            param_matrix[4] * conv_matrix[4] +
            param_matrix[5] * conv_matrix[5] +
            param_matrix[6] * conv_matrix[6] +
            param_matrix[7] * conv_matrix[7] +
            param_matrix[8] * conv_matrix[8];
        end 
    end
end
wire tvalid = (state == LOAD_DATA_COMPUTE && byte_counter == 'd1) || (state == DUMMY1);
wire tlast = (state == DUMMY1);
assign m_axis_tvalid = tvalid;
assign m_axis_tlast = tlast;

assign m_axis_tdata = (result > 127) ? 127 : 
                       (result < -128) ? -128 : 
                       result[7:0];  // result 的低 8 位

//////
assign s_axis_tready = m_axis_tready;
assign m_axis_tuser = 0;
//////

endmodule

`resetall