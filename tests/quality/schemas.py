"""Schemas Pandera utilizados nos testes de integração."""

try:  # pragma: no cover - dependência opcional
    import pandera as pa  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - dependência opcional
    pa = None  # type: ignore[var-annotated]

if pa:  # pragma: no branch - simples guarda de import
    customer_schema = pa.DataFrameSchema(
        {
            "id": pa.Column(int, checks=pa.Check.ge(0)),
            "name": pa.Column(str, nullable=False),
        },
        strict=True,
    )

    invalid_schema = pa.DataFrameSchema(
        {
            "id": pa.Column(int, checks=pa.Check.gt(10)),
        },
        strict=True,
    )
