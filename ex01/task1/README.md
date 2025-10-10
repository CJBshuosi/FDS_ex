

## Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py
```

### Visualizing Graphs

You can visualize the DOT files using Graphviz:

```bash
dot -Tpng full_edges.dot -o full_graph.png
dot -Tpng reduced_edges.dot -o reduced_graph.png
```
