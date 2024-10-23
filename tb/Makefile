TOPLEVEL_LANG = verilog

SIM ?= icarus
WAVES ?= 0

COCOTB_HDL_TIMEUNIT = 1ns
COCOTB_HDL_TIMEPRECISION = 1ps

DUT      = fpga_core
TOPLEVEL = $(DUT)
MODULE   = test_$(DUT)
VERILOG_SOURCES += ../rtl/$(DUT).v

# the acceleration_module
VERILOG_SOURCES += ../rtl/acceleration_module.v

VERILOG_SOURCES += ../rtl/hex_display.v
VERILOG_SOURCES += ../lib/eth_mac_1g_rgmii_fifo.v
VERILOG_SOURCES += ../lib/eth_mac_1g_rgmii.v
VERILOG_SOURCES += ../lib/iddr.v
VERILOG_SOURCES += ../lib/oddr.v
VERILOG_SOURCES += ../lib/ssio_ddr_in.v
VERILOG_SOURCES += ../lib/rgmii_phy_if.v
VERILOG_SOURCES += ../lib/eth_mac_1g.v
VERILOG_SOURCES += ../lib/axis_gmii_rx.v
VERILOG_SOURCES += ../lib/axis_gmii_tx.v
VERILOG_SOURCES += ../lib/lfsr.v
VERILOG_SOURCES += ../lib/eth_axis_rx.v
VERILOG_SOURCES += ../lib/eth_axis_tx.v
VERILOG_SOURCES += ../lib/udp_complete.v
VERILOG_SOURCES += ../lib/udp_checksum_gen.v
VERILOG_SOURCES += ../lib/udp.v
VERILOG_SOURCES += ../lib/udp_ip_rx.v
VERILOG_SOURCES += ../lib/udp_ip_tx.v
VERILOG_SOURCES += ../lib/ip_complete.v
VERILOG_SOURCES += ../lib/ip.v
VERILOG_SOURCES += ../lib/ip_eth_rx.v
VERILOG_SOURCES += ../lib/ip_eth_tx.v
VERILOG_SOURCES += ../lib/ip_arb_mux.v
VERILOG_SOURCES += ../lib/arp.v
VERILOG_SOURCES += ../lib/arp_cache.v
VERILOG_SOURCES += ../lib/arp_eth_rx.v
VERILOG_SOURCES += ../lib/arp_eth_tx.v
VERILOG_SOURCES += ../lib/eth_arb_mux.v
VERILOG_SOURCES += ../lib/arbiter.v
VERILOG_SOURCES += ../lib/priority_encoder.v
VERILOG_SOURCES += ../lib/axis_fifo.v
VERILOG_SOURCES += ../lib/axis_async_fifo.v
VERILOG_SOURCES += ../lib/axis_async_fifo_adapter.v

include $(shell cocotb-config --makefiles)/Makefile.sim

clean::
	@rm -rf iverilog_dump.v
	@rm -rf dump.fst $(TOPLEVEL).fst
