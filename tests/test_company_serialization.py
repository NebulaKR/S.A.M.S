import sys
from pathlib import Path

# ensure project root on path
sys.path.append(str(Path(__file__).parent.parent))

from core.entities import Company
from core.serializers import company_to_dict, company_from_dict


def test_company_total_shares_serialization():
    comp = Company(industry="IT", orientation=0.1, size="대기업", rnd_focus=0.2, volatility=0.3, total_shares=1000000)
    d = company_to_dict(comp)
    assert d["total_shares"] == 1000000
    comp2 = company_from_dict(d)
    assert comp2.total_shares == 1000000
    assert comp2.industry == "IT"


if __name__ == "__main__":
    print("running company serialization tests...")
    test_company_total_shares_serialization()
    print("company serialization test passed")
