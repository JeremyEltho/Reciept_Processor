# Project Structure

```
sedai_pet_project/
├── src/                    # Core application code (MVC)
│   ├── model/             # Business logic
│   ├── view/              # Output formatting  
│   ├── controller/        # Workflow orchestration
│   └── main.py           # MVC entry point
├── web/                   # Flask web interface
│   ├── app.py            # Web server
│   ├── templates/        # HTML templates
│   ├── uploads/          # Uploaded receipts
│   └── results/          # Web processing results
├── test_data/            # Test receipt images
├── results/              # CLI processing results
│   ├── single/          # Single receipt outputs
│   ├── events/          # Event-based outputs
│   └── batch/           # Batch processing outputs
├── run.py               # Python CLI runner
├── run.sh               # Shell script runner
└── README.md            # Main documentation
```

