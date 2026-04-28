# File Registry System - Visual Guide

## 🔄 Complete File Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                    UPLOAD PHASE                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  User uploads:  sales_2024.csv                                       │
│       ↓                                                               │
│  ┌────────────────────────────────┐                                  │
│  │ csv_documents                  │                                  │
│  ├────────────────────────────────┤                                  │
│  │ id: 1                          │                                  │
│  │ filename: sales_2024.csv       │                                  │
│  │ full_data: [all rows]          │  ← Complete data stored          │
│  │ row_count: 500                 │                                  │
│  │ is_described: false            │                                  │
│  └────────────────────────────────┘                                  │
│       ↓                                                               │
│  ┌────────────────────────────────┐                                  │
│  │ file_registry                  │  ← NEW                            │
│  ├────────────────────────────────┤                                  │
│  │ document_id: 1                 │                                  │
│  │ filename: sales_2024.csv       │                                  │
│  │ is_described: false            │  ← Waiting for review            │
│  │ dynamic_table_name: NULL       │  ← No table yet                  │
│  │ data_category: NULL            │                                  │
│  │ upload_date: 2025-01-15...     │                                  │
│  │ verified_at: NULL              │                                  │
│  └────────────────────────────────┘                                  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                   REVIEW PHASE                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  User reviews preview:  [Product | Sales | Date]                     │
│                         [Widget A | 1000  | 01/15]                   │
│                         [Widget B | 1500  | 01/15]                   │
│       ↓                                                               │
│  User saves metadata:                                                │
│  - Product: "Product name"                                           │
│  - Sales: "Sales amount in dollars"                                  │
│  - Date: "Transaction date"                                          │
│       ↓                                                               │
│  ┌────────────────────────────────┐                                  │
│  │ document_metadata              │                                  │
│  ├────────────────────────────────┤                                  │
│  │ document_id: 1                 │                                  │
│  │ column_metadata: [...]         │  ← User descriptions stored      │
│  └────────────────────────────────┘                                  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                 PROCESSING PHASE                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  User clicks: \"Process with AI\"                                     │
│       ↓                                                               │
│  ┌────────────────────────────────┐                                  │
│  │ LLM Analysis                   │                                  │
│  ├────────────────────────────────┤                                  │
│  │ • Generate schema              │                                  │
│  │ • Detect data types            │                                  │
│  │ • Determine category: \"Sales\" │                                 │
│  │ • Create insights              │                                  │
│  └────────────────────────────────┘                                  │
│       ↓                                                               │
│  ┌────────────────────────────────┐                                  │
│  │ knowledge_base                 │                                  │
│  ├────────────────────────────────┤                                  │
│  │ document_id: 1                 │                                  │
│  │ summary: \"Sales data for...\" │                                  │
│  │ data_category: \"Sales\"        │                                 │
│  │ insights: [...]                │                                  │
│  │ recommendations: [...]         │                                  │
│  └────────────────────────────────┘                                  │
│       ↓                                                               │
│  ┌────────────────────────────────┐                                  │
│  │ Dynamic Table Created:          │                                  │
│  │ sales_2024_1                   │                                  │
│  ├────────────────────────────────┤                                  │
│  │ id | created_at | product  | sales | date   │                    │
│  ├────────────────────────────────┤                                  │
│  │ 1  | ...        | Widget A | 1000  | 01/15 │                    │
│  │ 2  | ...        | Widget B | 1500  | 01/15 │                    │
│  │ 3  | ...        | Widget C | 800   | 01/15 │                    │
│  │... (500 rows total)           │                                  │
│  └────────────────────────────────┘                                  │
│       ↓                                                               │
│  ┌────────────────────────────────┐                                  │
│  │ file_registry UPDATED          │  ← UPDATED                       │
│  ├────────────────────────────────┤                                  │
│  │ document_id: 1                 │                                  │
│  │ is_described: true             │  ✅ Verified!                    │
│  │ dynamic_table_name: sales_2024_1 │  ✅ Table created!            │
│  │ data_category: \"Sales\"        │  ✅ Category determined         │
│  │ table_created_at: 2025-01-15...|  ✅ Creation timestamp          │
│  │ verified_at: 2025-01-15...     │  ✅ Verification timestamp      │
│  └────────────────────────────────┘                                  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                  TRACKING PHASE                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Query API Endpoints:                                                │
│                                                                       │
│  1. GET /registry/summary                                            │
│     ┌──────────────────────────┐                                     │
│     │ Total files: 10          │                                     │
│     │ Verified: 7              │                                     │
│     │ With tables: 7           │                                     │
│     │ Unverified: 3            │                                     │
│     └──────────────────────────┘                                     │
│                                                                       │
│  2. GET /registry/files                                              │
│     ┌──────────────────────────┐                                     │
│     │ • sales_2024.csv         │ ← sales_2024_1                      │
│     │ • budget_2024.csv        │ ← budget_2024_2 [UNVERIFIED]       │
│     │ • customers.csv          │ ← customers_3                       │
│     │ ...                      │                                     │
│     └──────────────────────────┘                                     │
│                                                                       │
│  3. GET /registry/files?verified_only=false                          │
│     ┌──────────────────────────┐                                     │
│     │ • budget_2024.csv        │ ← Needs review!                     │
│     │ • expense_report.csv     │ ← Needs review!                     │
│     │ • payroll.csv            │ ← Needs review!                     │
│     └──────────────────────────┘                                     │
│                                                                       │
│  4. GET /registry/category/Sales                                     │
│     ┌──────────────────────────┐                                     │
│     │ • sales_2024.csv         │                                     │
│     │ • sales_2023.csv         │                                     │
│     │ • regional_sales.csv     │                                     │
│     └──────────────────────────┘                                     │
│                                                                       │
│  5. GET /registry/file/1                                             │
│     ┌──────────────────────────┐                                     │
│     │ filename: sales_2024     │                                     │
│     │ rows: 500, cols: 12      │                                     │
│     │ category: Sales          │                                     │
│     │ verified: ✅ Yes          │                                     │
│     │ table: sales_2024_1      │                                     │
│     │ uploaded: 01/15 09:00    │                                     │
│     │ processed: 01/15 10:30   │                                     │
│     └──────────────────────────┘                                     │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## 📊 Verification Status Flow

```
           UPLOAD
             ↓
    [Not in Registry]
             ↓
    File Registered
    is_described = ❌
    table_name = 🚫
             ↓
          REVIEW
      User saves metadata
             ↓
         PROCESS
      AI creates table
             ↓
    Registry Updated
    is_described = ✅
    table_name = 📊
             ↓
         TRACKED
   Available for queries
```

## 🗂️ Data Organization

```
By Upload Date (Recent First)
├─ 2025-01-15 10:30
│  ├─ sales_2024.csv [✅ verified, Sales category]
│  └─ customer_data.csv [❌ unverified]
│
├─ 2025-01-14 15:00
│  ├─ budget_2024.csv [✅ verified, Financial category]
│  └─ expenses.csv [✅ verified, Operations category]
│
└─ 2025-01-13 09:00
   └─ archive_2023.csv [✅ verified, Historical category]

By Category
├─ Sales (7 files)
│  ├─ sales_2024.csv [verified ✅]
│  ├─ sales_2023.csv [verified ✅]
│  └─ regional_sales.csv [unverified ❌]
│
├─ Financial (5 files)
│  ├─ budget_2024.csv [verified ✅]
│  ├─ budget_2023.csv [verified ✅]
│  └─ budget_forecast.csv [unverified ❌]
│
└─ Operations (3 files)
   ├─ expenses.csv [verified ✅]
   ├─ inventory.csv [verified ✅]
   └─ shipping.csv [unverified ❌]

By Verification Status
├─ Verified ✅ (12 files)
│  └─ All have dynamic tables
│
└─ Pending ❌ (3 files)
   └─ Awaiting user review
```

## 🔍 Index Performance

```
Fast Queries (Using Indexes):
✅ Find all verified files
   WHERE is_described = true

✅ Find all unverified files
   WHERE is_described = false

✅ Search by filename
   WHERE filename LIKE '%sales%'

✅ Find by category
   WHERE data_category = 'Financial'

✅ Get recent uploads
   ORDER BY upload_date DESC
   LIMIT 10

Slow Queries (No index):
❌ Find by file size (not indexed)
❌ Search in full_data content (too large)
```

## 📈 System Metrics

```
Total Files Registered: 15
├─ Verified: 12 (80%)
├─ Unverified: 3 (20%)
└─ With Dynamic Tables: 12

By Category:
├─ Sales: 7
├─ Financial: 5
├─ Operations: 3
└─ Other: 0

Rows Stored (Total):
├─ sales_2024_1: 500 rows
├─ budget_2024_2: 1200 rows
├─ customers_3: 5000 rows
└─ ... Total: 15,000+ rows across all files
```

## 🚀 Performance Characteristics

```
Registry Size: ~500 bytes per file
Indexes: ~5 KB per index (4 indexes)
Typical Query: < 10ms (with index)
Scan all files: ~100ms (15 files)
Full table dump: < 1 second

Growth Pattern:
100 files → ~50 KB storage
1000 files → ~500 KB storage
10000 files → ~5 MB storage
```

## ✅ Status Dashboard (Example)

```
╔════════════════════════════════════════════╗
║        FILE REGISTRY STATUS                ║
╠════════════════════════════════════════════╣
║                                            ║
║  Total Files Uploaded:        15           ║
║  ├─ Verified:                  12  [80%]   ║
║  └─ Pending Review:             3  [20%]   ║
║                                            ║
║  Dynamic Tables Created:       12           ║
║  Data Rows Stored:          15,000+        ║
║                                            ║
║  By Category:                               ║
║  ├─ Sales:                      7          ║
║  ├─ Financial:                  5          ║
║  └─ Operations:                 3          ║
║                                            ║
║  Recent Uploads:                            ║
║  ├─ sales_2024.csv [verified ✅]           ║
║  └─ customer_data.csv [pending ❌]         ║
║                                            ║
╚════════════════════════════════════════════╝
```

---

This visual guide helps understand how the file registry system works from upload to tracking. See documentation files for detailed information.
