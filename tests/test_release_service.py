from src.release_service import VendorHealth, choose_vendor


def test_backup_vendor_is_selected_when_primary_is_unavailable() -> None:
    selected = choose_vendor(VendorHealth("openai", available=False), VendorHealth("qwen"))
    assert selected.name == "qwen"
