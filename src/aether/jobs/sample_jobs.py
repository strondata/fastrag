"""
Implementações de Jobs de exemplo para uso em testes e demonstrações.
"""

from typing import Any, Dict

from aether.core.interfaces import AbstractJob


class UpperCaseJob(AbstractJob):
    """
    Um job simples que converte uma string de entrada para maiúsculas.
    """

    def _execute(self, **loaded_inputs: Any) -> Dict[str, Any]:
        input_data = loaded_inputs.get("input_str")
        if not isinstance(input_data, str):
            raise TypeError("A entrada 'input_str' deve ser uma string.")

        output_data = input_data.upper()
        return {"output_str": output_data}


class ConcatJob(AbstractJob):
    """
    Um job que concatena duas strings de entrada em uma única string de saída.
    """

    def _execute(self, **loaded_inputs: Any) -> Dict[str, Any]:
        str_a = loaded_inputs.get("str_a")
        str_b = loaded_inputs.get("str_b")

        if not isinstance(str_a, str) or not isinstance(str_b, str):
            raise TypeError("As entradas 'str_a' e 'str_b' devem ser strings.")

        output_data = str_a + str_b
        return {"output_str": output_data}


class CreateDataFrameJob(AbstractJob):
    """Constrói um DataFrame pandas a partir dos dados informados nos parâmetros."""

    def _execute(self, **loaded_inputs: Any) -> Dict[str, Any]:
        try:
            import pandas as pd  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - depende de instalação opcional
            raise RuntimeError(
                "O job CreateDataFrameJob requer a dependência opcional 'pandas'."
            ) from exc

        data = self.params.get("data")
        if data is None:
            raise ValueError("O parâmetro 'data' é obrigatório para CreateDataFrameJob.")

        dataframe = pd.DataFrame(data)
        return {"dataframe": dataframe}
