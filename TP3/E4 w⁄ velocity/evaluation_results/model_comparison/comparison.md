# Comparacion de Experimentos

Nota: las pruebas multiclase y binarias no miden exactamente la misma dificultad.
La comparacion mas justa es por pares:
- `Multiclase ReLU` vs `Multiclase Sigmoid`
- `Binario Sigmoid/Sigmoid` vs `Binario ReLU/Sigmoid`

| Experimento | Tarea | Ocultas | Salida | Dataset | Accuracy | Error | Log loss | F1 macro | F1 down | Params | Train s |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Multiclase ReLU | Multiclase | relu | softmax | 3 clases, split original | 0.8268 | 0.1732 | 0.4121 | 0.8081 |  | 877859 | 30.5243 |
| Multiclase Sigmoid | Multiclase | sigmoid | softmax | 3 clases, split original | 0.4022 | 0.5978 | 1.0841 | 0.1912 |  | 877859 | 14.7032 |
| Binario Sigmoid/Sigmoid | Binario | sigmoid | sigmoid | up/down balanceado | 0.5000 | 0.5000 | 0.6931 |  | 0.6667 | 877601 | 21.1917 |
| Binario ReLU/Sigmoid | Binario | relu | sigmoid | up/down balanceado | 0.9628 | 0.0372 | 0.0880 |  | 0.9620 | 877601 | 25.2283 |

## Lectura Rapida

- En multiclase, `ReLU` supera ampliamente a `Sigmoid` con la misma arquitectura liviana.
- En binario, `sigmoid` en la salida funciona bien solo cuando las capas ocultas usan `ReLU`.
- `Sigmoid` en las capas ocultas tiende a saturarse y termina colapsando a una clase dominante o a soluciones cercanas al azar.