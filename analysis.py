from __future__ import annotations

import csv
import argparse
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List


DATA_FILE = Path(__file__).with_name("RealEstateDB.csv")


@dataclass
class RentalRecord:
    id: int
    price: float
    bedrooms: float
    bathrooms: float
    size: int
    minutes_to_subway: int
    building_age: int
    has_washer: bool
    has_elevator: bool
    has_dishwasher: bool
    has_gym: bool

    @property
    def price_per_square_foot(self) -> float:
        return self.price / self.size if self.size else 0.0


def _parse_bool(value: str) -> bool:
    return value.strip() == "1"


def load_rentals(path: Path = DATA_FILE) -> List[RentalRecord]:
    if not path.exists():
        raise FileNotFoundError(f"Could not find dataset at {path}")

    records: List[RentalRecord] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                RentalRecord(
                    id=int(row["ID"]),
                    price=float(row["price"]),
                    bedrooms=float(row["countofbedrooms"]),
                    bathrooms=float(row["countofbathrooms"]),
                    size=int(row["size"]),
                    minutes_to_subway=int(row["minimumtosubway"]),
                    building_age=int(row["buildingage"]),
                    has_washer=_parse_bool(row["haswasher"]),
                    has_elevator=_parse_bool(row["haselevator"]),
                    has_dishwasher=_parse_bool(row["hasdishwasher"]),
                    has_gym=_parse_bool(row["hasgym"]),
                )
            )
    return records


def summarize_price(records: Iterable[RentalRecord]) -> Dict[str, float]:
    prices = [record.price for record in records]
    sizes = [record.size for record in records]
    price_per_sqft = [record.price_per_square_foot for record in records]

    return {
        "count": len(prices),
        "average_price": mean(prices),
        "median_price": _median(prices),
        "average_size": mean(sizes),
        "average_price_per_sqft": mean(price_per_sqft),
    }


def average_price_by_bedrooms(records: Iterable[RentalRecord]) -> Dict[float, float]:
    grouped: Dict[float, List[float]] = {}
    for record in records:
        grouped.setdefault(record.bedrooms, []).append(record.price)
    return {bedrooms: mean(prices) for bedrooms, prices in sorted(grouped.items())}


def top_listings(records: Iterable[RentalRecord], limit: int = 5) -> List[RentalRecord]:
    return sorted(records, key=lambda record: record.price, reverse=True)[:limit]


def format_report(records: List[RentalRecord], *, language: str = "en", top_limit: int = 5) -> str:
    summary = summarize_price(records)
    averages = average_price_by_bedrooms(records)
    top = top_listings(records, limit=top_limit)

    strings = {
        "en": {
            "title": "Rental market summary",
            "count": "Listings analyzed: {count}",
            "avg_price": "Average monthly rent: ${value:,.0f}",
            "median_price": "Median monthly rent: ${value:,.0f}",
            "avg_size": "Average size: {value:,.0f} sqft",
            "avg_psf": "Average price per sqft: ${value:.2f}",
            "by_beds": "Average price by bedroom count:",
            "by_beds_line": "  {bedrooms} BR: ${price:,.0f}",
            "top_title": "Top listings by price:",
            "top_line": (
                "  ID {id}: ${price:,.0f} | {bedrooms} BR / {bathrooms} BA | "
                "{size} sqft | ${psf:.2f}/sqft"
            ),
        },
        "tr": {
            "title": "Kira piyasası özeti",
            "count": "İncelenen ilan sayısı: {count}",
            "avg_price": "Ortalama aylık kira: ${value:,.0f}",
            "median_price": "Medyan aylık kira: ${value:,.0f}",
            "avg_size": "Ortalama büyüklük: {value:,.0f} ft²",
            "avg_psf": "Metrekare başına ortalama fiyat: ${value:.2f}",
            "by_beds": "Oda sayısına göre ortalama kira:",
            "by_beds_line": "  {bedrooms} oda: ${price:,.0f}",
            "top_title": "Fiyata göre en pahalı ilanlar:",
            "top_line": (
                "  ID {id}: ${price:,.0f} | {bedrooms} oda / {bathrooms} banyo | "
                "{size} ft² | ${psf:.2f}/ft²"
            ),
        },
    }

    text = strings.get(language, strings["en"])

    lines = [
        text["title"],
        "=" * len(text["title"]),
        text["count"].format(count=summary["count"]),
        text["avg_price"].format(value=summary["average_price"]),
        text["median_price"].format(value=summary["median_price"]),
        text["avg_size"].format(value=summary["average_size"]),
        text["avg_psf"].format(value=summary["average_price_per_sqft"]),
        "",
        text["by_beds"],
    ]

    for bedrooms, price in averages.items():
        lines.append(text["by_beds_line"].format(bedrooms=bedrooms, price=price))

    lines.extend(["", text["top_title"]])
    for record in top:
        lines.append(
            text["top_line"].format(
                id=record.id,
                price=record.price,
                bedrooms=record.bedrooms,
                bathrooms=record.bathrooms,
                size=record.size,
                psf=record.price_per_square_foot,
            )
        )

    return "\n".join(lines)


def _median(values: List[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    length = len(ordered)
    midpoint = length // 2
    if length % 2:
        return float(ordered[midpoint])
    return mean(ordered[midpoint - 1 : midpoint + 1])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize the rental dataset.")
    parser.add_argument("--lang", choices=["en", "tr"], default="en", help="Dil / language")
    parser.add_argument("--top", type=int, default=5, help="Gösterilecek en pahalı ilan sayısı")
    parser.add_argument(
        "--file",
        type=Path,
        default=DATA_FILE,
        help="Kullanılacak CSV dosyasının yolu",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = load_rentals(args.file)
    print(format_report(records, language=args.lang, top_limit=args.top))


if __name__ == "__main__":
    main()
