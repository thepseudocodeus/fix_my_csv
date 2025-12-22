# fix_my_csv
Fix My CSV repairs common csv related issues from 1st principles

This is a recreation of a client project to resolve issues creating a data application from csv data exported from a SaaS platform's MySQL database. The platform runs in a Microsoft Azure environment. Development team uses Windows, MacOS, and Linux systems. The team experienced data discrepencies.


## Process
1. Binary
2. Data
3. Structure

### Binary
Standardize byte information, including remove null bytes, BOM, and more.

### Data
Standardize data, including use one type for newlines, trim spacing, and use comma delimiter.

### Structure
Standardize file, including establish a max size, max rows, and max columns.


#### TODOs
- [ ] TODO: convert potential formulas to text
