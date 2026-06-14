from evireview.models.audit import Decision


CLAIMCHECK_AGREEMENT_MAPPING_VERSION = "claimcheck-agreement-proxy-v1"


def claimcheck_agreement_to_decision(agreement: int) -> Decision:
    """Map expert validity agreement to an audit proxy without inventing rewrite Gold."""
    if agreement not in {1, 2, 3, 4, 5}:
        raise ValueError("CLAIMCHECK agreement must be in [1, 5]")
    if agreement <= 2:
        return "reject"
    if agreement == 3:
        return "uncertain"
    return "keep"
