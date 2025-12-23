# fix_my_csv
Fix My CSV repairs common csv related issues from 1st principles

This is a recreation of a client project to resolve issues creating a data application from csv data exported from a SaaS platform's MySQL database. The platform runs in a Microsoft Azure environment. Development team uses Windows, MacOS, and Linux systems. The team experienced data discrepancies.


### Workflow
*Experiment #1*
Can we fix the problem by directly modifying files?

- Phase 1: Binary
  - Standardize byte information, including remove null bytes, BOM, and more.
- Phase 2: Data
  - Standardize data, including use one type for newlines, trim spacing, and use comma delimiter.
- Phase 3: File
  - Standardize file, including establish a max size, max rows, and max columns.

*Experiment #2*
Can we quanitify the problem and track effectiveness and efficiency of solutions?

1. Understand
2. Model
3. Hypothesize
4. Experiment
5. Refine

*Experiment #3*
Is there a simpler, easy to modify way to solve the problem?

- Use python to initially process the data
- Use Chardet for encoding
- Leverage existing tools
- Write an easy to maintain implementation of lessons learned

## NOTES:
- Initial approach involved processing the file in 3-phases: binary, structure, and data.
- Revised the approach to start by understanding the problem quantiatively
- Discovered chardet library and linux csvkit that help simplify the approach
