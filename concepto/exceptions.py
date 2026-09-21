class ConceptoEnUsoEnLiquidacionAbierta(Exception):
    default_message = (
        "No se puede eliminar el concepto porque está siendo "
        "utilizado en una liquidación abierta."
    )

    def __init__(self, message=None):
        super().__init__(message or self.default_message)
