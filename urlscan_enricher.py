"""
URLScan enrichment module for finding lookalike domains and scam duplicates.
Enhanced with URLScan API integration for same-IP domain discovery.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Set, cast

import requests
from sql_loader import SQLLoader

logger = logging.getLogger(__name__)

# URLScan API configuration
URLSCAN_API_URL = "https://urlscan.io/api/v1"
URLSCAN_SEARCH_API = f"{URLSCAN_API_URL}/search/"
URLSCAN_API_KEY = "1e765603-a7d8-46ff-bd0e-8679273a7919"
URLSCAN_REQUEST_HEADERS = {"Content-Type": "application/json", "API-Key": URLSCAN_API_KEY}
URLSCAN_DELAY = 2  # Delay between requests to be respectful


class URLScanEnricher:
    """Handles URLScan-based domain enrichment and lookalike detection."""

    def __init__(self, sql_loader: SQLLoader):
        """
        Initialize the URLScan enricher.

        Args:
            sql_loader: SQLLoader instance for database queries
        """
        self.sql_loader = sql_loader

    def find_lookalike_domains(self, domains: List[str]) -> List[Dict[str, Any]]:
        """
        Find lookalike domains using URLScan scam duplicates data.

        Args:
            domains: List of domain names to search for lookalikes

        Returns:
            List of dictionaries containing lookalike domain data
        """
        if not domains:
            logger.warning("No domains provided for lookalike search")
            return []

        logger.info(f"Searching for lookalike domains for {len(domains)} domains")

        # Format domains as text for SQL query (same approach as linked addresses)
        domain_list_text = self._format_domains_for_sql(domains)

        query = f"""
        SELECT source_domain, domain, screenshot
        FROM domain_raw.urlscan_domains_scam_duplicates
        WHERE domain IN ({domain_list_text})
        """

        try:
            results = self.sql_loader._execute_query(query)
            logger.info(f"Found {len(results)} lookalike domain records")
            return results
        except Exception as e:
            logger.error(f"Failed to find lookalike domains: {e}")
            return []

    def _format_domains_for_sql(self, domains: List[str]) -> str:
        """
        Format domains list for SQL query, ensuring values are sent as text.

        Args:
            domains: List of domain names

        Returns:
            Formatted string for SQL IN clause
        """
        # Escape single quotes and format as text strings
        escaped_domains = []
        for domain in domains:
            # Convert to string and escape single quotes
            domain_text = str(domain).replace("'", "''")
            escaped_domains.append(f"'{domain_text}'")

        return ", ".join(escaped_domains)

    def find_new_domains(self, lookalike_results: List[Dict[str, Any]], original_domains: List[str]) -> List[str]:
        """
        Extract new domains from lookalike results that are not in the original list.

        Args:
            lookalike_results: Results from lookalike domain query
            original_domains: Original list of input domains

        Returns:
            List of new domains found in lookalike results
        """
        if not lookalike_results:
            logger.info("No lookalike results to process")
            return []

        original_domains_set = set(domain.lower() for domain in original_domains)
        new_domains: Set[str] = set()

        # Extract domains from both 'source_domain' and 'domain' columns in results
        for result in lookalike_results:
            # Check the 'domain' column (this contains the domains that match our input)
            if "domain" in result and result["domain"]:
                domain = result["domain"].lower()
                if domain not in original_domains_set:
                    new_domains.add(domain)

            # Check the 'source_domain' column (this contains the lookalike domains)
            if "source_domain" in result and result["source_domain"]:
                source_domain = result["source_domain"].lower()
                if source_domain not in original_domains_set:
                    new_domains.add(source_domain)

        result_list = sorted(list(new_domains))
        logger.info(
            f"Found {len(result_list)} new domains (from both source_domain and domain columns) not in original list"
        )

        return result_list

    def analyze_domain_similarity(self, original_domain: str, candidate_domains: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze similarity between an original domain and candidate domains.

        This is a basic implementation - can be enhanced with more sophisticated
        similarity algorithms like Levenshtein distance, visual similarity, etc.

        Args:
            original_domain: The original domain to compare against
            candidate_domains: List of candidate domains to analyze

        Returns:
            List of dictionaries with similarity analysis
        """
        results = []

        for candidate in candidate_domains:
            similarity_score = self._calculate_basic_similarity(original_domain, candidate)

            analysis = {
                "original_domain": original_domain,
                "candidate_domain": candidate,
                "similarity_score": similarity_score,
                "analysis_type": "basic_string_similarity",
            }

            # Add specific similarity flags
            analysis.update(self._get_similarity_flags(original_domain, candidate))

            results.append(analysis)

        # Sort by similarity score (highest first)
        results.sort(key=lambda x: cast(float, x["similarity_score"]), reverse=True)

        return results

    def _calculate_basic_similarity(self, domain1: str, domain2: str) -> float:
        """
        Calculate basic string similarity between two domains.

        Args:
            domain1: First domain
            domain2: Second domain

        Returns:
            Similarity score between 0 and 1
        """
        if domain1 == domain2:
            return 1.0

        # Simple character overlap calculation
        chars1 = set(domain1.lower())
        chars2 = set(domain2.lower())

        overlap = len(chars1.intersection(chars2))
        total_unique = len(chars1.union(chars2))

        if total_unique == 0:
            return 0.0

        return overlap / total_unique

    def _get_similarity_flags(self, original: str, candidate: str) -> Dict[str, bool]:
        """
        Get various similarity flags between two domains.

        Args:
            original: Original domain
            candidate: Candidate domain

        Returns:
            Dictionary of similarity flags
        """
        orig_lower = original.lower()
        cand_lower = candidate.lower()

        return {
            "same_length": len(orig_lower) == len(cand_lower),
            "contains_original": orig_lower in cand_lower or cand_lower in orig_lower,
            "same_tld": (
                orig_lower.split(".")[-1] == cand_lower.split(".")[-1]
                if "." in orig_lower and "." in cand_lower
                else False
            ),
            "character_substitution": self._has_character_substitution(orig_lower, cand_lower),
            "homograph_attack": self._possible_homograph_attack(orig_lower, cand_lower),
        }

    def _has_character_substitution(self, domain1: str, domain2: str) -> bool:
        """
        Check if domains might involve character substitution.

        Args:
            domain1: First domain
            domain2: Second domain

        Returns:
            True if possible character substitution detected
        """
        if len(domain1) != len(domain2):
            return False

        differences = sum(1 for a, b in zip(domain1, domain2) if a != b)
        return 1 <= differences <= 2  # 1-2 character differences might indicate substitution

    def _possible_homograph_attack(self, domain1: str, domain2: str) -> bool:
        """
        Basic check for possible homograph attacks (visually similar characters).

        Args:
            domain1: First domain
            domain2: Second domain

        Returns:
            True if possible homograph attack detected
        """
        # Simple homograph pairs (can be extended)
        homograph_pairs = {("0", "o"), ("1", "l"), ("1", "i"), ("rn", "m"), ("vv", "w"), ("cl", "d"), ("nn", "m")}

        for pair in homograph_pairs:
            if (pair[0] in domain1 and pair[1] in domain2) or (pair[1] in domain1 and pair[0] in domain2):
                return True

        return False

    def get_all_lookalike_domains_summary(self, domains: List[str]) -> Dict[str, Any]:
        """
        Get a comprehensive summary of lookalike domain analysis.

        Args:
            domains: List of domains to analyze

        Returns:
            Dictionary containing detailed lookalike analysis
        """
        try:
            lookalike_results = self.find_lookalike_domains(domains)
            new_domains = self.find_new_domains(lookalike_results, domains)

            # Extract source domains and target domains separately
            source_domains = set()
            target_domains = set()

            for result in lookalike_results:
                if "source_domain" in result and result["source_domain"]:
                    source_domains.add(result["source_domain"].lower())
                if "domain" in result and result["domain"]:
                    target_domains.add(result["domain"].lower())

            summary = {
                "input_domains_count": len(domains),
                "lookalike_records_found": len(lookalike_results),
                "unique_source_domains": len(source_domains),
                "unique_target_domains": len(target_domains),
                "new_domains_discovered": len(new_domains),
                "new_domains_sample": new_domains[:10],  # First 10 for preview
                "source_domains_sample": sorted(list(source_domains))[:10],
                "target_domains_sample": sorted(list(target_domains))[:10],
            }

            return summary

        except Exception as e:
            logger.error(f"Failed to generate lookalike analysis summary: {e}")
            return {"error": str(e), "input_domains_count": len(domains)}

    def get_domain_ip_from_urlscan(self, domain: str) -> Optional[str]:
        """
        Get the IP address of a domain using URLScan API.

        Args:
            domain: Domain name to look up

        Returns:
            IP address if found, None otherwise
        """
        try:
            # Search for recent scans of this domain
            query = f"domain:{domain}"
            params = {
                "q": query,
                "size": 1,  # We only need one result to get the IP
            }

            logger.debug(f"Searching URLScan for domain IP: {domain}")
            response = requests.get(URLSCAN_SEARCH_API, params=params, headers=URLSCAN_REQUEST_HEADERS, timeout=30)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                if results:
                    # Get the first result and extract IP
                    first_result = results[0]
                    page_info = first_result.get("page", {})
                    ip_address = page_info.get("ip")

                    if ip_address:
                        logger.debug(f"Found IP {ip_address} for domain {domain}")
                        return ip_address
                    else:
                        logger.debug(f"No IP found in URLScan result for {domain}")
                        return None
                else:
                    logger.debug(f"No URLScan results found for domain {domain}")
                    return None

            elif response.status_code == 429:
                logger.warning(f"URLScan rate limit hit for domain {domain}")
                time.sleep(URLSCAN_DELAY * 2)  # Wait longer on rate limit
                return None
            else:
                logger.warning(f"URLScan API error {response.status_code} for domain {domain}")
                return None

        except Exception as e:
            logger.error(f"Error getting IP from URLScan for domain {domain}: {e}")
            return None

    def find_same_ip_domains_urlscan(self, domain: str, limit: int = 10000) -> List[str]:
        """
        Find domains that share the same IP as the given domain using URLScan API.

        Args:
            domain: Domain to find same-IP domains for
            limit: Maximum number of results to return

        Returns:
            List of domain names sharing the same IP
        """
        try:
            # First get the IP of the domain
            ip_address = self.get_domain_ip_from_urlscan(domain)

            if not ip_address:
                logger.warning(f"Could not get IP for domain {domain} from URLScan")
                return []

            logger.info(f"Found IP {ip_address} for {domain}, searching for same-IP domains")

            # Now search for other domains with the same IP, excluding the original domain
            query = f'page.ip:"{ip_address}" AND NOT page.domain:"{domain}"'
            params = {
                "q": query,
                "size": limit,
            }

            # Add delay to be respectful to the API
            time.sleep(URLSCAN_DELAY)

            logger.debug(f"URLScan query: {query}")
            response = requests.get(URLSCAN_SEARCH_API, params=params, headers=URLSCAN_REQUEST_HEADERS, timeout=30)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                same_ip_domains = set()
                for result in results:
                    page_info = result.get("page", {})
                    result_domain = page_info.get("domain")

                    if result_domain and result_domain.lower() != domain.lower():
                        same_ip_domains.add(result_domain)

                same_ip_list = sorted(list(same_ip_domains))
                logger.info(f"Found {len(same_ip_list)} domains sharing IP {ip_address} with {domain}")

                return same_ip_list

            elif response.status_code == 429:
                logger.warning(f"URLScan rate limit hit when searching for same-IP domains")
                time.sleep(URLSCAN_DELAY * 2)
                return []
            else:
                logger.warning(f"URLScan API error {response.status_code} when searching for same-IP domains")
                return []

        except Exception as e:
            logger.error(f"Error finding same-IP domains for {domain}: {e}")
            return []

    def find_same_ip_domains_batch(self, domains: List[str], limit_per_domain: int = 1000) -> Dict[str, List[str]]:
        """
        Find same-IP domains for multiple domains using URLScan API.

        Args:
            domains: List of domains to find same-IP domains for
            limit_per_domain: Maximum results per domain

        Returns:
            Dictionary mapping each domain to its same-IP domains
        """
        if not domains:
            logger.warning("No domains provided for same-IP search")
            return {}

        logger.info(f"Finding same-IP domains for {len(domains)} domains using URLScan API")

        same_ip_mapping = {}

        for i, domain in enumerate(domains, 1):
            logger.info(f"Processing domain {i}/{len(domains)}: {domain}")

            same_ip_domains = self.find_same_ip_domains_urlscan(domain, limit_per_domain)
            same_ip_mapping[domain] = same_ip_domains

            # Log progress
            if same_ip_domains:
                logger.info(f"  Found {len(same_ip_domains)} same-IP domains for {domain}")
                logger.debug(f"  Sample domains: {same_ip_domains[:3]}")
            else:
                logger.info(f"  No same-IP domains found for {domain}")

        total_found = sum(len(domains) for domains in same_ip_mapping.values())
        logger.info(f"Completed same-IP search: {total_found} total same-IP domains found")

        return same_ip_mapping
