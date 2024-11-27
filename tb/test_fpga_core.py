import numpy as np
import logging

from scapy.layers.l2 import Ether, ARP
from scapy.layers.inet import IP, UDP
from scapy.all import wrpcap

import cocotb
from cocotb.log import SimLog
from cocotb.triggers import RisingEdge, Timer

from cocotbext.eth import GmiiFrame, RgmiiPhy

from scipy.signal import correlate2d
class TB:
    def __init__(self, dut, speed=1000e6):
        self.dut = dut

        self.log = SimLog("cocotb.tb")
        self.log.setLevel(logging.DEBUG)

        self.rgmii_phy0 = RgmiiPhy(dut.phy0_txd, dut.phy0_tx_ctl, dut.phy0_tx_clk,
            dut.phy0_rxd, dut.phy0_rx_ctl, dut.phy0_rx_clk, speed=speed)

        self.rgmii_phy1 = RgmiiPhy(dut.phy1_txd, dut.phy1_tx_ctl, dut.phy1_tx_clk,
            dut.phy1_rxd, dut.phy1_rx_ctl, dut.phy1_rx_clk, speed=speed)

        dut.phy0_int_n.setimmediatevalue(1)
        dut.phy1_int_n.setimmediatevalue(1)

        dut.btn.setimmediatevalue(0)
        dut.sw.setimmediatevalue(0)

        dut.clk.setimmediatevalue(0)
        dut.clk90.setimmediatevalue(0)

        cocotb.start_soon(self._run_clk())

    async def init(self):

        self.dut.rst.setimmediatevalue(0)

        for k in range(10):
            await RisingEdge(self.dut.clk)

        self.dut.rst.value = 1

        for k in range(10):
            await RisingEdge(self.dut.clk)

        self.dut.rst.value = 0

    async def _run_clk(self):
        t = Timer(2, 'ns')
        while True:
            self.dut.clk.value = 1
            await t
            self.dut.clk90.value = 1
            await t
            self.dut.clk.value = 0
            await t
            self.dut.clk90.value = 0
            await t


@cocotb.test()
async def run_test(dut):

    tb = TB(dut)

    await tb.init()

    tb.log.info("test UDP RX packet")
    
    submatrices = []

    # 生成 3x3 的卷积核，值在 0 到 5 之间
    conv_kernel = np.random.randint(0, 6, size=(3, 3), dtype=np.uint8)
    conv_kernel_r = conv_kernel
    submatrices.append(conv_kernel.tobytes())
    
    # 输出卷积核
    tb.log.info("Generated 3x3 Convolution Kernel:\n%s", np.array2string(conv_kernel, separator=', '))
    # 生成12*12的矩阵取值在[0,5]
    matrix = np.random.randint(230, 231, size=(12, 12), dtype=np.uint8)
    tb.log.info("Generated 12x12 matrix:\n%s", np.array2string(matrix, separator=', '))

    # 遍历矩阵，提取所有的 3x3 子矩阵
    for i in range(matrix.shape[0] - 2):
        for j in range(matrix.shape[1] - 2):
            conv_kernel = matrix[i:i+3, j:j+3]
            submatrices.append(conv_kernel.tobytes())
    
    # 将所有的子矩阵字节流拼接成一个完整的字节流
    final_byte_stream = b''.join(submatrices)
    tb.log.info(f"Total byte stream length: {len(final_byte_stream)} bytes")

    payload = final_byte_stream

    eth = Ether(src='5a:51:52:53:54:55', dst='02:00:00:00:00:00')
    ip = IP(src='192.168.1.100', dst='192.168.1.128')
    udp = UDP(sport=5678, dport=1234)
    test_pkt = eth / ip / udp / payload
    
    ### 记录第一次发送的UDP包
    packets = []
    packets.append(test_pkt)


    test_frame = GmiiFrame.from_payload(test_pkt.build())

    await tb.rgmii_phy0.rx.send(test_frame)

    tb.log.info("receive ARP request")

    rx_frame = await tb.rgmii_phy0.tx.recv()

    rx_pkt = Ether(bytes(rx_frame.get_payload()))

    ### 记录来自fpga的ARP请求
    packets.append(rx_pkt)

    tb.log.info("RX packet: %s", repr(rx_pkt))

    assert rx_pkt.dst == 'ff:ff:ff:ff:ff:ff'
    assert rx_pkt.src == test_pkt.dst
    assert rx_pkt[ARP].hwtype == 1
    assert rx_pkt[ARP].ptype == 0x0800
    assert rx_pkt[ARP].hwlen == 6
    assert rx_pkt[ARP].plen == 4
    assert rx_pkt[ARP].op == 1
    assert rx_pkt[ARP].hwsrc == test_pkt.dst
    assert rx_pkt[ARP].psrc == test_pkt[IP].dst
    assert rx_pkt[ARP].hwdst == '00:00:00:00:00:00'
    assert rx_pkt[ARP].pdst == test_pkt[IP].src

    tb.log.info("send ARP response")

    eth = Ether(src=test_pkt.src, dst=test_pkt.dst)
    arp = ARP(hwtype=1, ptype=0x0800, hwlen=6, plen=4, op=2,
        hwsrc=test_pkt.src, psrc=test_pkt[IP].src,
        hwdst=test_pkt.dst, pdst=test_pkt[IP].dst)
    resp_pkt = eth / arp

    ### 记录来自模拟的主机的ARP回复
    packets.append(resp_pkt)
    
    resp_frame = GmiiFrame.from_payload(resp_pkt.build())

    await tb.rgmii_phy0.rx.send(resp_frame)

    tb.log.info("receive UDP packet")

    rx_frame = await tb.rgmii_phy0.tx.recv()

    rx_pkt = Ether(bytes(rx_frame.get_payload()))
    
    # ### 记录来自模拟的fpga的UDP包
    packets.append(rx_pkt)
    
    tb.log.info("RX packet: %s", repr(rx_pkt))

    assert rx_pkt.dst == test_pkt.src
    assert rx_pkt.src == test_pkt.dst
    assert rx_pkt[IP].dst == test_pkt[IP].src
    assert rx_pkt[IP].src == test_pkt[IP].dst
    assert rx_pkt[UDP].dport == test_pkt[UDP].sport
    assert rx_pkt[UDP].sport == test_pkt[UDP].dport
    # assert rx_pkt[UDP].payload == test_pkt[UDP].payload
    corr_result = correlate2d(matrix, conv_kernel_r, mode='valid')
    corr_bytes = corr_result.astype(np.uint8).tobytes()
    tb.log.info(f"answer: {corr_bytes}")
    tb.log.info(f"output: {rx_pkt[UDP].payload.load}")
    # assert corr_bytes == rx_pkt[UDP].payload.load
    
    tb.log.info("TTTTEEEESSSSTTTT")
    await tb.rgmii_phy0.rx.send(test_frame)
    rx_frame = await tb.rgmii_phy0.tx.recv()
    rx_pkt = Ether(bytes(rx_frame.get_payload()))
    tb.log.info(f"answer: {corr_bytes}")
    tb.log.info(f"output: {rx_pkt[UDP].payload.load}")
    # assert corr_bytes == rx_pkt[UDP].payload.load
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    
    # 保存所有捕获的包到PCAP文件
    wrpcap('output.pcap', packets)

    tb.log.info("Data captured and saved to output.pcap")