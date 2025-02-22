import pytest
import asyncio
import time
import random
from protocol import Packet, Message

class GroundStation:
    def __init__(self, name, channel, max_retries=254):
        self.name = name
        self.channel = channel
        self.max_retries = max_retries
        self.seq = 0
        self.ack = 0

    async def send_packet(self, packet, timeout=1):
        """
        Sends a packet and waits for the corresponding ACK packet.
        Resends if no ACK is received before the timeout.
        """
        retries = 0
        start_time = time.time()

        while retries <= self.max_retries:
            # Send the packet
            self.channel.send(packet)
            print(f"Sent packet with seq={packet.seq} ack={packet.ack}")

            # Wait for the ACK packet
            ack_packet = await self._wait_for_ack(timeout)
            if ack_packet:
                print(f"Received ACK for packet seq={packet.seq} ack={ack_packet.ack}")
                return ack_packet  # Successfully received ACK

            retries += 1
            self.seq += 1
            packet.increment_seq()  # Increment the sequence number on resend
            print(f"Timeout, retrying... (attempt {retries}/{self.max_retries})")

        raise TimeoutError(f"Exceeded max retries ({self.max_retries}) for packet seq={packet.seq}")

    async def _wait_for_ack(self, timeout):
        """
        Waits for an ACK packet. If no ACK is received before the timeout, returns None.
        """
        try:
            ack_packet = await asyncio.wait_for(self.channel.receive(), timeout)
            if ack_packet and ack_packet.seq == self.seq + 1:  # Ensure ACK is for the correct sequence
                return ack_packet
        except asyncio.TimeoutError:
            return None

    def create_packet(self, msg, flags=0):
        message = Message("TEST", msg)
        packet = Packet(message, flags, seq=self.seq, ack=self.ack)
        return packet


class Balloon:
    def __init__(self, name, channel):
        self.name = name
        self.seq = 0
        self.ack = 0

    def receive_packet(self, packet):
        """
        Simulates receiving a packet. Handles SYN/ACK, ACK, and duplicates.
        """
        if packet.flags == 0:  # SYN packet
            print(f"Balloon received SYN packet seq={packet.seq}")
            # Send SYN/ACK back to Ground Station
            response_packet = packet.increment_ack()  # Increment ack for SYN
            response_packet.set_flags(0b101)  # SYN/ACK flag
            return response_packet
        elif packet.flags == 0b101:  # SYN/ACK packet
            print(f"Balloon received SYN/ACK packet seq={packet.seq} ack={packet.ack}")
            if packet.ack == self.seq + 1:  # Duplicate SYN/ACK
                return self.create_ack_packet(packet)  # Send duplicate ACK
            else:
                self.seq = packet.seq  # Update balloon's sequence number
                ack_packet = self.create_ack_packet(packet)  # Send ACK for the received SYN/ACK
                return ack_packet
        elif packet.flags == 0b10:  # ACK packet
            print(f"Balloon received ACK packet seq={packet.seq} ack={packet.ack}")
            return packet

    def create_ack_packet(self, packet):
        ack_packet = packet.increment_ack()
        ack_packet.set_flags(0b10)  # ACK flag
        return ack_packet


class CommunicationChannel:
    def __init__(self, packet_loss_rate=0.2, latency_range=(0.1, 0.5)):
        self.packet_loss_rate = packet_loss_rate
        self.latency_range = latency_range

    async def send(self, packet):
        """Simulate sending a packet (with potential packet loss and latency)."""
        if self._is_packet_lost():
            print("Packet lost during transmission")
            return None  # Simulate packet loss

        await asyncio.sleep(self._get_latency())  # Simulate latency
        print(f"Packet sent: seq={packet.seq} ack={packet.ack}")
        return packet  # Simulate successful transmission

    async def receive(self):
        """Simulate receiving a packet."""
        await asyncio.sleep(self._get_latency())  # Simulate network latency
        return Packet(Message("TEST"), 0, seq=1, ack=1)  # Return a dummy packet

    def _is_packet_lost(self):
        """Randomly decide if the packet is lost based on the packet loss rate."""
        return random.random() < self.packet_loss_rate

    def _get_latency(self):
        """Randomly decide a latency within the specified range."""
        return random.uniform(self.latency_range[0], self.latency_range[1])
