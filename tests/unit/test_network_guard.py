"""The autouse network guard must stop connectionless UDP sends too."""

import socket

import pytest


def test_sendto_is_blocked() -> None:
    """A UDP ``sendto`` without ``connect`` raises the guard error."""
    with (
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock,
        pytest.raises(RuntimeError, match="reach the network"),
    ):
        sock.sendto(b"x", ("127.0.0.1", 9))


@pytest.mark.skipif(
    not hasattr(socket.socket, "sendmsg"), reason="socket.sendmsg is absent on Windows"
)
def test_sendmsg_is_blocked() -> None:
    """A UDP ``sendmsg`` without ``connect`` raises the guard error."""
    with (
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock,
        pytest.raises(RuntimeError, match="reach the network"),
    ):
        sock.sendmsg([b"x"], [], 0, ("127.0.0.1", 9))


@pytest.mark.allow_network
def test_allow_network_keeps_sendto_working() -> None:
    """An ``allow_network`` test still sends a datagram (loopback, no listener needed)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        assert sock.sendto(b"x", ("127.0.0.1", 9)) == 1


@pytest.mark.allow_network
@pytest.mark.skipif(
    not hasattr(socket.socket, "sendmsg"), reason="socket.sendmsg is absent on Windows"
)
def test_allow_network_keeps_sendmsg_working() -> None:
    """An ``allow_network`` test still sends a datagram through ``sendmsg``."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        assert sock.sendmsg([b"x"], [], 0, ("127.0.0.1", 9)) == 1
