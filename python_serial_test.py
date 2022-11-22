#!/usr/bin/env python
"""
 * python_serial_test.hpp
 *
 * License: BSD-3-Clause
 *
 * Copyright (c) 2012-2022 Shoun Corporation <research.robosho@gmail.com>
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of RT Corporation nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 """

# attention : python 3.5 above needed for print f format support

import serial
import struct
import time
import sys
import io

TEST_TIMES = 10000
SLEEP_1S = 3 # 3s
SLEEP_3S = 3 # 3s
SLEEP_1MS = 0.001 # 1ms
BYTES_128 = 128 # 128bytes
BYTES_126 = 126 # 128bytes
serial_port="/dev/ttyACM0"
count_128 = 0
count_others = 0
total_latency_tx = 0
total_latency_rx = 0
total_latency = 0
max_latency_tx = 0
max_latency_rx = 0

# Parepare buffer for output to MCU through USB CDC
tx_data = list(range(BYTES_128))
len_tx = len(bytes(tx_data))
print(f'tx_data({len_tx}bytes): {tx_data}')

# Open COM port for serial communication
seri = serial.Serial(port=serial_port, baudrate=4000000, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)

# Sleep for 3sw
time.sleep(SLEEP_3S)

# Set buffer size, working on WINDOWS but not working on UBUNTU?
#seri.set_buffer_size(rx_size = size, tx_size = size)

# Flush buffer for new input and output
seri.reset_input_buffer()
seri.reset_output_buffer()
seri._CHUNK_SIZE = 1

# Test TEST_TIMES times for 128bytes Tx&Rx echo
for i_rxtx in range(TEST_TIMES):
    time_start = time.time()
    # Output data
    seri.write(tx_data)
    # Wait for end of Tx
    seri.flush()
    latency_tx = time.time() - time_start

    time_start = time.time()
    # Wait for echo data
    while True:
        inwaiting_bytes = seri.inWaiting()
        if inwaiting_bytes > 0: break

    # Input data
    rx_data = seri.read(inwaiting_bytes)
    latency_rx = time.time() - time_start
    total_latency_tx += latency_tx
    total_latency_rx += latency_rx
    total_latency += latency_tx + latency_rx
    len_rx = len(bytes(rx_data))

    if len_rx == BYTES_128:# case 128bytes received
        count_128 += 1
        if latency_tx > max_latency_tx:
            max_latency_tx = latency_tx
        if latency_rx > max_latency_rx:
            max_latency_rx = latency_rx
        print (f'{len_rx}bytes echoed, latency_tx: {latency_tx*1000:.3f}ms, max_latency_tx: {max_latency_tx*1000:.3f}ms, latency_rx: {latency_rx*1000:.3f}ms, max_latency_rx: {max_latency_rx*1000:.3f}ms, {count_128}times counted, average_latency_tx+rx: {total_latency*1000/count_128:.3f}ms')
        #print (f'rx_data: {[hex(i) for i in list(rx_data)]}')

    else:# case other than 128byes
        count_others += 1
        print (f'{len_rx}bytes received, latency_rx: {latency_rx*1000:.3f}s, time other than 128bytes received: {count_others}times counted')
    
    # Flush buffer for new input and output
    seri.reset_input_buffer()
    seri.reset_output_buffer()

    #print (f'rx_data: {rx_data}')
    #time.sleep(SLEEP_1S)

print (f'{len_rx}bytes {TEST_TIMES}times echoed, average_latency_tx: {latency_tx*1000:.3f}ms, max_latency_tx: {max_latency_tx*1000:.3f}ms, average_latency_rx: {latency_rx*1000:.3f}ms, max_latency_rx: {max_latency_rx*1000:.3f}ms, {count_128}times counted')
# Close COM port
seri.close()
