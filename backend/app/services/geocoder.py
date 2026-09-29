"""Geocoding provider abstraction and service."""

import abc
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
from rapidfuzz import fuzz, process
from app.config import settings
from app.schemas.address import Coordinates, GeocodingResult

logger = logging.getLogger(__name__)


class GeocoderProvider(abc.ABC):
    """Abstract geocoder provider interface."""

    @abc.abstractmethod
    async def geocode(
        self,
        query: str,
        locality: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None
    ) -> Optional[GeocodingResult]:
        """Geocode an address into latitude, longitude, and confidence."""
        pass


class MockGeocoder(GeocoderProvider):
    """High-fidelity local development geocoder using curated Indian reference datasets."""

    def __init__(self):
        data_dir = Path(__file__).parent.parent.parent.parent / "data" / "processed"
        self.localities = []
        self.districts = []
        self.states = []
        self.pincodes = {}

        if (data_dir / "localities.json").exists():
            with open(data_dir / "localities.json", "r", encoding="utf-8") as f:
                self.localities = json.load(f)

        if (data_dir / "districts.json").exists():
            with open(data_dir / "districts.json", "r", encoding="utf-8") as f:
                self.districts = json.load(f)

        if (data_dir / "states.json").exists():
            with open(data_dir / "states.json", "r", encoding="utf-8") as f:
                self.states = json.load(f)

        if (data_dir / "pincodes.json").exists():
            with open(data_dir / "pincodes.json", "r", encoding="utf-8") as f:
                pins = json.load(f)
                for p in pins:
                    self.pincodes[p["pincode"]] = p

    async def geocode(
        self,
        query: str,
        locality: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None
    ) -> Optional[GeocodingResult]:
        search_target = locality or query

        # 1. Match against known localities
        if locality or search_target:
            for loc in self.localities:
                # Check locality name & aliases
                names_to_check = [loc["name"].lower()] + [a.lower() for a in loc.get("aliases", [])]
                for name in names_to_check:
                    if name in search_target.lower() or fuzz.ratio(name, search_target.lower()) >= 85:
                        return GeocodingResult(
                            coordinates=Coordinates(
                                latitude=loc["coordinates"]["latitude"],
                                longitude=loc["coordinates"]["longitude"]
                            ),
                            display_name=f"{loc['name']}, {loc['district']}, {loc['state']}",
                            source="Local Reference Catalog",
                            confidence=0.95,
                            match_level="locality"
                        )

        # 2. Match against PIN codes
        if pincode and pincode in self.pincodes:
            pin_data = self.pincodes[pincode]
            if "centroid" in pin_data and pin_data["centroid"]:
                return GeocodingResult(
                    coordinates=Coordinates(
                        latitude=pin_data["centroid"]["latitude"],
                        longitude=pin_data["centroid"]["longitude"]
                    ),
                    display_name=f"PIN {pincode}, {pin_data.get('district', '')}, {pin_data.get('state', '')}",
                    source="Postal Code Centroid Database",
                    confidence=0.85,
                    match_level="pincode"
                )

        # 3. Match against District
        target_dist = district or query
        for dist in self.districts:
            names_to_check = [dist["name"].lower()] + [a.lower() for a in dist.get("aliases", [])]
            for name in names_to_check:
                if name in target_dist.lower() or fuzz.ratio(name, target_dist.lower()) >= 85:
                    # Calculate center from bbox
                    bbox = dist["bbox"]
                    center_lat = (bbox[1] + bbox[3]) / 2.0
                    center_lon = (bbox[0] + bbox[2]) / 2.0
                    return GeocodingResult(
                        coordinates=Coordinates(latitude=center_lat, longitude=center_lon),
                        display_name=f"{dist['name']}, {dist['state_name']}",
                        source="District Administrative Database",
                        confidence=0.75,
                        match_level="district"
                    )

        # 4. Match against State
        target_state = state or query
        for st in self.states:
            names_to_check = [st["name"].lower()] + [a.lower() for a in st.get("aliases", [])]
            for name in names_to_check:
                if name in target_state.lower() or fuzz.ratio(name, target_state.lower()) >= 85:
                    bbox = st["bbox"]
                    center_lat = (bbox[1] + bbox[3]) / 2.0
                    center_lon = (bbox[0] + bbox[2]) / 2.0
                    return GeocodingResult(
                        coordinates=Coordinates(latitude=center_lat, longitude=center_lon),
                        display_name=f"{st['name']}, India",
                        source="State Administrative Database",
                        confidence=0.60,
                        match_level="state"
                    )

        # Default fallback for unresolvable location
        return None


class NominatimGeocoder(GeocoderProvider):
    """Live OpenStreetMap Nominatim Geocoder provider with rate-limiting."""

    def __init__(self):
        self.base_url = settings.GEOCODER_BASE_URL
        self.user_agent = settings.GEOCODER_USER_AGENT
        self.last_call_time = 0.0

    async def geocode(
        self,
        query: str,
        locality: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None
    ) -> Optional[GeocodingResult]:
        # Enforce rate limit
        elapsed = time.time() - self.last_call_time
        if elapsed < settings.GEOCODER_RATE_LIMIT_DELAY:
            time.sleep(settings.GEOCODER_RATE_LIMIT_DELAY - elapsed)

        headers = {"User-Agent": self.user_agent}
        params = {
            "q": query,
            "format": "json",
            "countrycodes": "in",
            "limit": 1,
            "addressdetails": 1
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                self.last_call_time = time.time()
                resp = await client.get(f"{self.base_url}/search", params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    if data and len(data) > 0:
                        first = data[0]
                        return GeocodingResult(
                            coordinates=Coordinates(
                                latitude=float(first["lat"]),
                                longitude=float(first["lon"])
                            ),
                            display_name=first.get("display_name", query),
                            source="OpenStreetMap Nominatim",
                            confidence=float(first.get("importance", 0.7)),
                            match_level=first.get("type", "address")
                        )
        except Exception as e:
            logger.warning(f"Nominatim geocoding failed for '{query}': {e}. Falling back to mock geocoder.")

        # Fallback to Mock
        mock = MockGeocoder()
        return await mock.geocode(query, locality, district, state, pincode)


class GeocoderService:
    """Factory and cache manager for geocoding services."""

    def __init__(self):
        self.cache: Dict[str, GeocodingResult] = {}
        if settings.GEOCODER_PROVIDER.lower() == "nominatim":
            self.provider: GeocoderProvider = NominatimGeocoder()
        else:
            self.provider = MockGeocoder()

    async def geocode(
        self,
        query: str,
        locality: Optional[str] = None,
        district: Optional[str] = None,
        state: Optional[str] = None,
        pincode: Optional[str] = None
    ) -> Optional[GeocodingResult]:
        cache_key = f"{query}|{locality}|{district}|{state}|{pincode}".lower()
        if cache_key in self.cache:
            return self.cache[cache_key]

        res = await self.provider.geocode(
            query=query,
            locality=locality,
            district=district,
            state=state,
            pincode=pincode
        )
        if res:
            self.cache[cache_key] = res
        return res


geocoder_service = GeocoderService()
