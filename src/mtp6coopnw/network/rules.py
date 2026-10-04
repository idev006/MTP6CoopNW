from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from ipaddress import ip_address, ip_network


class Protocol(StrEnum):
    TCP = "TCP"
    UDP = "UDP"


class Direction(StrEnum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


@dataclass(frozen=True, slots=True)
class PortRule:
    protocol: Protocol
    port: int
    direction: Direction
    destination: str
    allowed: bool = True

    def __post_init__(self) -> None:
        if not 1 <= self.port <= 65535:
            raise ValueError("port must be in 1..65535")
        if not self.destination:
            raise ValueError("destination is required")


@dataclass(frozen=True, slots=True)
class NetworkPolicy:
    internet_allowed: bool
    database_allowed: bool
    rules: tuple[PortRule, ...]

    def validate_db_safety(
        self,
        *,
        db_server_ip: str,
        sql_port: int = 1433,
        lan_cidr: str = "192.168.1.0/24",
    ) -> None:
        db = ip_address(db_server_ip)
        lan = ip_network(lan_cidr, strict=False)
        if db not in lan:
            raise ValueError("database server must be inside managed LAN")
        for rule in self.rules:
            if (
                rule.port == sql_port
                and rule.direction is Direction.INBOUND
                and rule.allowed
                and rule.destination.upper() in {"ANY", "INTERNET", "WAN", "0.0.0.0/0"}
            ):
                raise ValueError("SQL WAN exposure is forbidden")

    def allows(
        self,
        *,
        protocol: Protocol,
        port: int,
        direction: Direction,
        destination: str,
    ) -> bool:
        exact = [
            rule
            for rule in self.rules
            if rule.protocol is protocol
            and rule.port == port
            and rule.direction is direction
            and rule.destination == destination
        ]
        return exact[-1].allowed if exact else False
