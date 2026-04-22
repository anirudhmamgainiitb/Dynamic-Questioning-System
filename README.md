User input
   ↓
State updater (extract structured info)
   ↓
Retriever
   ├── Filter (remove irrelevant questions)
   ├── Scorer (rank by usefulness)
   └── Selector (avoid repetition)
   ↓
Next question
   ↓
Termination policy (decide when to stop)
