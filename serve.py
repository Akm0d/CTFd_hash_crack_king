#!/usr/bin/env python3
from kingofthehill import create_app

app = create_app()
app.run(debug=True, threaded=True, host="0.0.0.0", port=5000)
