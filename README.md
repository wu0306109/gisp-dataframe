# gisp

Generalized Interval-extended Sequential Pattern mining (GISP)


## Usage

```python
import gisp

a, b, c, d, e, f = 'a', 'b', 'c', 'd', 'e', 'f'
sequences = [
    [(0, {a}), (86400, {a, b, c}), (259200, {a, c})],
    [(0, {a, d}), (259200, {c})],
    [(0, {a, e, f}), (172800, {a, b})],
]

patterns = gisp.mine(
    itemize=lambda i: i // 86400,
    min_support=2, max_interval=172800,
)
```
