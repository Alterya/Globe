"""
Lookalike domains module for finding scam duplicates from URLScan data.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Import the database handler system
try:
    from sqlalchemy import text

    from common.database.global_db_handler import get_db_handler

    DB_HANDLER_AVAILABLE = True
except ImportError:
    DB_HANDLER_AVAILABLE = False
    logger.warning("get_db_handler not available - lookalike domain functionality disabled")


class LookalikeDomains:
    """Handles finding lookalike domains using URLScan scam duplicates data."""

    def __init__(self):
        """Initialize the lookalike domains finder."""
        self.db_handler = None

        if DB_HANDLER_AVAILABLE:
            try:
                self.db_handler = get_db_handler()
                logger.info("Initialized lookalike domains finder with database handler")
            except Exception as e:
                logger.error(f"Failed to initialize database handler: {e}")
                self.db_handler = None
        else:
            logger.error("Database handler not available - lookalike domain functionality disabled")

    def find_lookalike_domains(self, source_domains: List[str]) -> List[Dict[str, Any]]:
        """
        Find lookalike domains using URLScan scam duplicates data.

        Args:
            source_domains: List of domain names to search for lookalikes

        Returns:
            List of dictionaries containing lookalike domain data
        """
        if not source_domains:
            logger.warning("No source domains provided for lookalike search")
            return []

        if not self.db_handler:
            logger.error("No database handler available for lookalike domain search")
            return []

        logger.info(f"Searching for lookalike domains for {len(source_domains)} domains")

        # Format domains for SQL query
        domain_list_text = self._format_domains_for_sql(source_domains)

        query = f"""
        SELECT source_domain, domain, screenshot
        FROM domain_raw.urlscan_domains_scam_duplicates
        WHERE domain IN ({domain_list_text})
        """

        try:
            results = self._execute_query(query)
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

    def _execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results using get_db_handler.

        Args:
            query: SQL query string

        Returns:
            List of dictionaries containing query results
        """
        logger.debug(f"Executing lookalike query: {query[:200]}...")

        if not self.db_handler:
            raise RuntimeError("No database handler available")

        try:
            # Use SQLAlchemy text() wrapper
            sql_query = text(query)

            # Try using the engine attribute with pandas (most common pattern)
            if hasattr(self.db_handler, "engine"):
                import pandas as pd

                df = pd.read_sql(sql_query, self.db_handler.engine)
                return [dict(row) for row in df.to_dict("records")]
            # Try using pandas read_sql method (common pattern)
            elif hasattr(self.db_handler, "connection"):
                import pandas as pd

                df = pd.read_sql(sql_query, self.db_handler.connection)
                return [dict(row) for row in df.to_dict("records")]
            # Try direct pandas read_sql if handler is an engine/connection
            else:
                try:
                    import pandas as pd

                    df = pd.read_sql(query, self.db_handler)
                    return [dict(row) for row in df.to_dict("records")]
                except Exception:
                    # Log available attributes for debugging
                    attrs = [attr for attr in dir(self.db_handler) if not attr.startswith("_")]
                    logger.error(f"Available attributes on db_handler: {attrs}")
                    raise Exception("No suitable execution method found on database handler")

        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise

    def extract_new_domains(self, lookalike_results: List[Dict[str, Any]], original_domains: List[str]) -> List[str]:
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
        new_domains = set()

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
        logger.info(f"Found {len(result_list)} new domains from lookalike analysis not in original list")

        return result_list

    def get_lookalike_summary(self, source_domains: List[str]) -> Dict[str, Any]:
        """
        Get a comprehensive summary of lookalike domain analysis.

        Args:
            source_domains: List of domains to analyze

        Returns:
            Dictionary containing detailed lookalike analysis
        """
        try:
            lookalike_results = self.find_lookalike_domains(source_domains)
            new_domains = self.extract_new_domains(lookalike_results, source_domains)

            # Extract source domains and target domains separately
            source_domains_found = set()
            target_domains_found = set()

            for result in lookalike_results:
                if "source_domain" in result and result["source_domain"]:
                    source_domains_found.add(result["source_domain"].lower())
                if "domain" in result and result["domain"]:
                    target_domains_found.add(result["domain"].lower())

            summary = {
                "input_domains_count": len(source_domains),
                "lookalike_records_found": len(lookalike_results),
                "unique_source_domains": len(source_domains_found),
                "unique_target_domains": len(target_domains_found),
                "new_domains_discovered": len(new_domains),
                "new_domains_sample": new_domains[:10],  # First 10 for preview
                "source_domains_sample": sorted(list(source_domains_found))[:10],
                "target_domains_sample": sorted(list(target_domains_found))[:10],
            }

            return summary

        except Exception as e:
            logger.error(f"Failed to generate lookalike analysis summary: {e}")
            return {"error": str(e), "input_domains_count": len(source_domains)}
