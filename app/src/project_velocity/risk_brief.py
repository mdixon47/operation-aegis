from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Incident:
    title: str
    summary: str
    business_concern: str


@dataclass(frozen=True)
class BusinessRisk:
    name: str
    description: str


INCIDENTS = [
    Incident(
        title="Public AWS credential exposure",
        summary="A junior developer pushed a live AWS access key into a public repository.",
        business_concern="Credential leakage can lead to unauthorized cloud access and incident response costs.",
    ),
    Incident(
        title="Quick-Transfer SQL injection",
        summary="A critical SQL injection flaw was discovered in the production Quick-Transfer API.",
        business_concern="Payment manipulation or account data disclosure would threaten transaction integrity.",
    ),
]

BUSINESS_RISKS = [
    BusinessRisk("Customer trust", "Repeated security failures would erode confidence in Skyline's digital banking platform."),
    BusinessRisk("Account data exposure", "Sensitive balance, profile, and transfer data could be leaked or tampered with."),
    BusinessRisk("Financial transaction integrity", "Attackers could alter quick-transfer behavior or create fraudulent movement of funds."),
    BusinessRisk("Regulatory scrutiny", "Control failures increase the likelihood of escalations, audits, and compliance findings."),
    BusinessRisk("Deployment shutdown risk", "Leadership may halt releases until automated safeguards prove the delivery pipeline is trustworthy."),
]


def build_project_velocity_brief() -> str:
    lines = [
        "Skyline Financial Tech - Project Velocity",
        "Ship new banking features every hour without compromising security.",
        "",
        "Recent incidents:",
    ]
    lines.extend(f"- {incident.title}: {incident.summary}" for incident in INCIDENTS)
    lines.append("")
    lines.append("Business risks:")
    lines.extend(f"- {risk.name}: {risk.description}" for risk in BUSINESS_RISKS)
    lines.append("")
    lines.append("This mock project demonstrates a secured Quick-Transfer service backed by automated DevSecOps controls.")
    return "\n".join(lines)
