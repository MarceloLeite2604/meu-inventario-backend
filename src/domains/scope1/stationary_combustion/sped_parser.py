"""Parser for Brazilian SPED (Sistema Público de Escrituração Digital) fiscal files.

Extracts fuel purchase items from Bloco C (Fiscal Documents):
- C170: NF-e invoice items
- C425: ECF daily summary items
"""

from dataclasses import dataclass

FUEL_KEYWORDS: dict[str, list[str]] = {
    "Óleo Diesel": ["diesel", "oleo diesel", "óleo diesel"],
    "GLP": ["glp", "gas liquefeito", "gás liquefeito", "botijao", "botijão"],
    "Gasolina Automotiva": ["gasolina"],
    "Gás Natural": ["gas natural", "gás natural", "gnv"],
    "Querosene": ["querosene"],
    "Óleo Combustível": ["oleo combustivel", "óleo combustível"],
    "Carvão Mineral": ["carvao mineral", "carvão mineral"],
    "Lenha": ["lenha"],
    "Bagaço de Cana": ["bagaco", "bagaço", "cana"],
    "Etanol": ["etanol", "alcool", "álcool"],
}


@dataclass
class SpedParsedItem:
    codigo: str
    descricao: str
    quantidade: float
    unidade: str
    combustivel_fossil_sugerido: str | None


def _auto_map_combustivel(text: str) -> str | None:
    text_lower = text.lower()
    for combustivel, keywords in FUEL_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return combustivel
    return None


def parse_sped(content: bytes) -> list[SpedParsedItem]:
    """Parse a SPED file and return fuel-related items from Bloco C.

    Aggregates quantities for items with the same codigo+descricao key.
    Brazilian SPED files use Latin-1 encoding and comma as decimal separator.
    """
    text = content.decode("latin-1", errors="replace")
    items_map: dict[str, SpedParsedItem] = {}

    for line in text.splitlines():
        fields = line.split("|")
        if len(fields) < 2:
            continue

        record_type = fields[1]

        if record_type == "C170" and len(fields) >= 7:
            # C170: |C170|NUM_ITEM|COD_ITEM|DESCR_COMPL|QTD|UNID|...
            codigo = fields[3].strip()
            descricao = fields[4].strip()
            try:
                quantidade = float(fields[5].strip().replace(",", "."))
            except ValueError:
                continue
            unidade = fields[6].strip()

            if not codigo or quantidade <= 0:
                continue

            key = f"{codigo}-{descricao}"
            if key in items_map:
                items_map[key].quantidade += quantidade
            else:
                items_map[key] = SpedParsedItem(
                    codigo=codigo,
                    descricao=descricao,
                    quantidade=quantidade,
                    unidade=unidade,
                    combustivel_fossil_sugerido=_auto_map_combustivel(descricao),
                )

        elif record_type == "C425" and len(fields) >= 5:
            # C425: |C425|COD_ITEM|QTD|UNID|VL_ITEM|...
            codigo = fields[2].strip()
            try:
                quantidade = float(fields[3].strip().replace(",", "."))
            except ValueError:
                continue
            unidade = fields[4].strip()

            if not codigo or quantidade <= 0:
                continue

            key = codigo
            if key in items_map:
                items_map[key].quantidade += quantidade
            else:
                items_map[key] = SpedParsedItem(
                    codigo=codigo,
                    descricao=codigo,  # C425 has no description field
                    quantidade=quantidade,
                    unidade=unidade,
                    combustivel_fossil_sugerido=_auto_map_combustivel(codigo),
                )

    return list(items_map.values())
