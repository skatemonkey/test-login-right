from ua_parser import parse as parse_user_agent

MAX_DEVICE_LENGTH = 255


def summarize_device(device: str | None) -> str | None:
    if device is None:
        return None

    normalized = " ".join(device.split())
    if not normalized:
        return None
    if not _looks_like_user_agent(normalized):
        return normalized[:MAX_DEVICE_LENGTH]

    parsed = parse_user_agent(normalized)
    browser = parsed.user_agent
    os_info = parsed.os

    if browser is None and os_info is None:
        return normalized[:MAX_DEVICE_LENGTH]

    browser_family = browser.family if browser else ""
    os_family = os_info.family if os_info else ""
    if browser_family == "Other" and os_family == "Other":
        return normalized[:MAX_DEVICE_LENGTH]

    browser_label = browser_family or ""
    if browser and browser.major:
        browser_label = f"{browser_label} {browser.major}"

    os_label = os_family or ""
    if os_info and os_info.major:
        os_label = f"{os_label} {os_info.major}"
        if os_info.minor:
            os_label = f"{os_label}.{os_info.minor}"

    arch = _detect_architecture(normalized)
    if browser_label and os_label and arch:
        return f"{browser_label} on {os_label} ({arch})"[:MAX_DEVICE_LENGTH]
    if browser_label and os_label:
        return f"{browser_label} on {os_label}"[:MAX_DEVICE_LENGTH]
    if browser_label:
        return browser_label[:MAX_DEVICE_LENGTH]
    if os_label and arch:
        return f"{os_label} ({arch})"[:MAX_DEVICE_LENGTH]
    if os_label:
        return os_label[:MAX_DEVICE_LENGTH]

    return normalized[:MAX_DEVICE_LENGTH]


def _detect_architecture(user_agent: str) -> str | None:
    lowered = user_agent.lower()
    if any(token in lowered for token in ("arm64", "aarch64")):
        return "ARM64"
    if any(token in lowered for token in ("win64", "x64", "wow64", "amd64", "x86_64")):
        return "x64"
    if any(token in lowered for token in ("i686", "i386", "x86")):
        return "x86"
    return None


def _looks_like_user_agent(value: str) -> bool:
    lowered = value.lower()
    return any(
        token in lowered
        for token in (
            "mozilla/",
            "applewebkit/",
            "chrome/",
            "firefox/",
            "safari/",
            "edg/",
            "trident/",
            "windows nt",
            "android",
            "iphone",
            "ipad",
            "mac os x",
        )
    )
